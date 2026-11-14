"""D4: logit distillation from the int4 Command A teacher into Tiny Aya (GPU; `stats` and the dry run on CPU).

D2/D3 train the student on the teacher's text only (sequence-level). Here the student also matches the teacher's
next-token distribution on the teacher's final answers: loss = CE on every assistant turn (as SFT) + alpha * KL
on the final turn, where the teacher's top-K log-probs come from scripts/teacher_local.py --logprobs.

The two models tokenise differently (Command A 256k vocab, Tiny Aya 262k), so the teacher's distribution is
moved onto the student's vocabulary:
  1. alignment: a student position takes part only where both tokenisations start a token at the same
     character of the answer text (both models are then predicting "what comes after this exact prefix");
  2. mapping: each of the teacher's top-K candidate strings that is exactly one student token keeps its
     probability; the rest are dropped and the kept mass is renormalised;
  3. KL(teacher_mapped || student) at those positions, summed over the kept candidates.
  Positions must hold the same token in both tokenisations (--align exact). The first run (kd_a1, Nov 14) used
  --align start, which also kept split mismatches and taught broken token sequences: see align().
`stats` reports how many answer positions align and how much teacher probability mass survives the mapping;
low numbers mean the KL term carries little signal.

alpha = 0 is the control: the same code, data and steps, CE only. The comparison is kd_a1 vs kd_a0.
Both start from the base model with a fresh LoRA, like sft_ho and sft_distil (same LoRA, lr 1e-4, 2 epochs,
effective batch 16).

  python scripts/logit_distil.py stats --data data/sft_distil_int4_raw.jsonl --logprobs results/teacher_command_a_int4.logprobs.jsonl
  python scripts/logit_distil.py train --data ... --logprobs ... --alpha 1 --out runs/kd_a1
  python scripts/logit_distil.py train --data ... --logprobs ... --alpha 0 --out runs/kd_a0
  python train.py merge --init runs/kd_a1/adapter --out runs/kd_a1/merged      # then evaluate.py gen as usual
"""
import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from train import LORA, MODEL, to_rollout_form  # noqa: E402


def ids_of(tok, msgs, **kw):
    x = tok.apply_chat_template(msgs, tokenize=True, **kw)
    return list(x["input_ids"] if hasattr(x, "keys") else x)


def align(tok, comp, text, lp, st, cache, strict=True):
    """Teacher top-K at the student positions of the final turn -> [(k, [student ids], [teacher probs])].
    comp: the student's completion token ids; position k predicts comp[k].
    strict: keep a position only if the teacher's sampled token is exactly the student's token there. Matching
    starts alone (strict=False, the kd_a1 run) keeps positions where the two tokenisers split differently, e.g.
    teacher "." vs student ".custom": the target then puts most mass on "." while the text continues ".custom",
    so the KL term teaches token sequences the student never produces (22% of kd_a1's positions; broken SQL)."""
    dec = [tok.decode(comp[:k], skip_special_tokens=False) for k in range(len(comp) + 1)]
    base = dec[-1].find(text)
    if base < 0:
        st["text_not_found"] += 1
        return []
    # teacher token start offsets, up to the first token whose string does not continue the text
    # (a byte-level token that is half a UTF-8 character decodes to U+FFFD)
    starts, o = {}, 0
    for j, t in enumerate(lp["tokens"]):
        if not t or not text.startswith(t, o):
            st["teacher_tokens_cut"] += len(lp["tokens"]) - j
            break
        starts[o] = j
        o += len(t)
    out = []
    for k in range(len(comp)):
        s = len(dec[k]) - base
        if not 0 <= s < len(text):
            continue
        st["answer_positions"] += 1
        j = starts.get(s)
        if j is None:
            continue
        if strict and tok.decode([comp[k]], skip_special_tokens=False) != lp["tokens"][j]:
            st["dropped_split_mismatch"] += 1
            continue
        st["aligned_positions"] += 1
        sid, sp = [], []
        for c, l in lp["top"][j]:
            if c not in cache:
                e = tok.encode(c, add_special_tokens=False) if c else []
                cache[c] = e[0] if len(e) == 1 else None
            p = math.exp(l)
            st["mass_total"] += p
            if cache[c] is not None and cache[c] not in sid:
                sid.append(cache[c])
                sp.append(p)
                st["mass_mapped"] += p
        if sid:
            z = sum(sp)
            out.append((k, sid, [p / z for p in sp]))
    return out


def kd_loss(logp, kd):
    """Mean over aligned positions of KL(q || p_student) on the mapped candidates: sum_i q_i (log q_i - log p_i).
    logp: [positions, vocab] student log-probs; kd: [(k, [student ids], [teacher probs])]."""
    import torch
    out = []
    for k, s, q in kd:
        q = torch.tensor(q, device=logp.device)
        out.append((q * (q.log() - logp[k, torch.tensor(s, device=logp.device)])).sum())
    return torch.stack(out).mean()


def examples(a, tok):
    lps = {r["id"]: r for r in map(json.loads, open(a.logprobs))} if a.logprobs else {}
    st, cache, rows = Counter(), {}, []
    lines = open(a.data).read().splitlines()[: a.limit or None]
    for line in lines:
        r = json.loads(line)
        conv = to_rollout_form(r["messages"])
        last = max(i for i, m in enumerate(conv) if m["role"] == "assistant")
        for i, m in enumerate(conv):
            if m["role"] != "assistant":
                continue
            ids = ids_of(tok, conv[: i + 1])
            pre = ids_of(tok, conv[:i], add_generation_prompt=True)
            p = next((n for n, (x, y) in enumerate(zip(ids, pre)) if x != y), len(pre))
            if len(ids) > a.max_len or p >= len(ids):
                st["dropped"] += 1
                continue
            kd = []
            if i == last and r.get("teacher_final"):
                st["teacher_rows"] += 1
                if r["id"] in lps:
                    kd = align(tok, ids[p:], m["content"], lps[r["id"]], st, cache, strict=getattr(a, "align", "exact") == "exact")
                    st["rows_with_kd"] += bool(kd)
                else:
                    st["no_logprobs"] += 1
            rows.append((ids, p, kd))
    st["examples"] = len(rows)
    return rows, st


def report(st):
    ap = st["answer_positions"] or 1
    out = dict(st) | {"aligned_share": st["aligned_positions"] / ap,
                      "mapped_mass_share": st["mass_mapped"] / (st["mass_total"] or 1)}
    print(json.dumps(out, indent=1))
    return out


def stats(a):
    from transformers import AutoTokenizer
    _, st = examples(a, AutoTokenizer.from_pretrained(a.model))
    out = report(st)
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "kd_stats.json").write_text(json.dumps(out, indent=1))


def train(a):
    import torch
    import torch.nn.functional as F
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(a.model)
    rows, st = examples(a, tok)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "kd_stats.json").write_text(json.dumps(report(st), indent=1))
    torch.manual_seed(a.seed)
    dtype = torch.bfloat16 if dev == "cuda" else torch.float32
    model = get_peft_model(AutoModelForCausalLM.from_pretrained(a.model, dtype=dtype).to(dev), LoraConfig(**LORA))
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model.train()
    params = [q for q in model.parameters() if q.requires_grad]
    rng = random.Random(a.seed)
    order = []
    for _ in range(math.ceil(a.epochs)):
        e = list(range(len(rows)))
        rng.shuffle(e)
        order += e
    order = order[: round(len(rows) * a.epochs)]
    steps = math.ceil(len(order) / a.accum)
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 1 - s / steps)  # linear decay, as TRL's default
    log, buf = [], {"ce": [], "kl": []}
    for n, i in enumerate(order, 1):
        ids, p, kd = rows[i]
        x = torch.tensor([ids], device=dev)
        # logits only for the completion (Tiny Aya's 262k vocab over the whole prompt does not fit: see dpo.py)
        with torch.autocast(dev, dtype=dtype, enabled=dev == "cuda"):
            logits = model(input_ids=x, logits_to_keep=len(ids) - p + 1).logits[0, :-1].float()
        logp = F.log_softmax(logits, -1)
        ce = -logp.gather(1, x[0, p:, None]).mean()
        loss = ce
        if kd and a.alpha > 0:
            kl = kd_loss(logp, kd)
            loss = ce + a.alpha * kl
            buf["kl"].append(kl.item())
        elif kd:  # alpha = 0: log the KL the control would have had, no gradient
            with torch.no_grad():
                buf["kl"].append(kd_loss(logp, kd).item())
        (loss / a.accum).backward()
        buf["ce"].append(ce.item())
        if n % a.accum == 0 or n == len(order):
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
            log.append({"step": len(log) + 1, "ce": sum(buf["ce"]) / len(buf["ce"]),
                        "kl": sum(buf["kl"]) / len(buf["kl"]) if buf["kl"] else None, "lr": sched.get_last_lr()[0]})
            print(json.dumps(log[-1]), flush=True)
            buf = {"ce": [], "kl": []}
    model.save_pretrained(str(a.out / "adapter"))
    json.dump(log, open(a.out / "log_history.json", "w"), indent=1)
    # merge in a separate process (train.py merge), as dpo.py does


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stats", "train"])
    ap.add_argument("--data", type=Path, default=ROOT / "data/sft_distil_int4_raw.jsonl")
    ap.add_argument("--logprobs", type=Path, default=ROOT / "results/teacher_command_a_int4.logprobs.jsonl")
    ap.add_argument("--model", default=MODEL, help="student base model (a tiny one for the CPU dry run)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--alpha", type=float, default=1.0, help="KL weight; 0 = the CE-only control")
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--accum", type=int, default=16, help="examples per optimizer step (batch 1)")
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--limit", type=int, default=0, help="first N data rows only (dry runs)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--align", choices=["exact", "start"], default="exact",
                    help="KD positions: the same token in both tokenisers (exact) or only the same start (start, as kd_a1)")
    a = ap.parse_args()
    {"stats": stats, "train": train}[a.cmd](a)
