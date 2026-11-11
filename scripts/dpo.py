"""DPO from one checkpoint (sft_ho): standard (single-DB labels) vs counterfactual (all-DB labels).

Source: sft_ho's own rollouts on the 445 GRPO prompts (runs/traj_sft_ho_grpoprompts.jsonl, G=6, T=1.0, the GRPO
signal check). Each rollout is graded V (verified: original + every copy), L (lucky: original only) or F (fails
the original). The two datasets differ only in how L is labelled:
  std: chosen in V+L, rejected in F        (what a single-DB verifier prefers)
  cf:  chosen in V,   rejected in L+F, L first   (what the counterfactual verifier prefers)
Both continue the sft_ho adapter on the bf16 base (the reference log-probs are sft_ho's, computed before any
update), with the same hyperparameters and seed.

  .venv-train/bin/python scripts/dpo.py pairs                       # -> data/dpo_{std,cf}.jsonl, results/dpo_pairs.json
  bash scripts/local_dpo.sh            # both runs on the local GPU: train, merge, E4 eval, score
"""
import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluate import grade  # noqa: E402

SRC = ROOT / "runs/traj_sft_ho_grpoprompts.jsonl"
ITEMS = ROOT / "data/train/grpo_items.jsonl"
PER_ITEM = 3  # pairs per prompt, so a few prompts with many mixed groups don't dominate
MAX_LEN = 3072


def prompt_of(it):
    from sqlcf.agent import SYSTEM, user_message
    from train import fallback_system
    return [{"role": "system", "content": fallback_system(SYSTEM)}, {"role": "user", "content": user_message(it)}]


def completion_of(prompt, msgs):
    """The rollout as the model saw it: tool results folded into user turns (same call as evaluate.gen)."""
    from agenttune.agentic.rollout_engines.rollout_factory import fold_tool_messages_into_user
    conv = fold_tool_messages_into_user(prompt + msgs)
    assert conv[:2] == prompt
    return conv[2:]


def label(g):
    return "V" if g["verified"] else "L" if g["single"] else "F"


def make_pairs(groups, kind, rng):
    """groups: {id: {"V": [...], "L": [...], "F": [...]}} -> [(id, chosen, rejected)]"""
    out = []
    for i, g in groups.items():
        good = g["V"] + g["L"] if kind == "std" else g["V"]
        tiers = [g["F"]] if kind == "std" else [g["L"], g["F"]]  # cf: lucky-rejected pairs first
        combos = []
        for bad in tiers:
            tier = [(c, r) for c in good for r in bad]
            rng.shuffle(tier)
            combos += tier
        out += [(i, c, r) for c, r in combos[:PER_ITEM]]
    return out


def pairs(_):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("CohereLabs/tiny-aya-global")
    items = {it["id"]: it for it in map(json.loads, open(ITEMS))}
    groups = defaultdict(lambda: {"V": [], "L": [], "F": []})
    for t in map(json.loads, open(SRC)):
        groups[t["id"]][label(grade(items[t["id"]], t["messages"]))].append(t["messages"])
    stats = {"source": str(SRC.relative_to(ROOT)), "rollouts": Counter(), "per_item_cap": PER_ITEM, "max_len": MAX_LEN}
    for g in groups.values():
        for k, v in g.items():
            stats["rollouts"][k] += len(v)
    for kind in ("std", "cf"):
        rows, too_long, n_lucky = [], 0, Counter()
        for i, c, r in make_pairs(groups, kind, random.Random(0)):
            p = prompt_of(items[i])
            row = {"id": i, "prompt": p, "chosen": completion_of(p, c), "rejected": completion_of(p, r)}
            if max(len(tok.apply_chat_template(p + row[k], tokenize=True)) for k in ("chosen", "rejected")) > MAX_LEN:
                too_long += 1
                continue
            g = groups[i]
            n_lucky["chosen_lucky"] += any(c is x for x in g["L"])
            n_lucky["rejected_lucky"] += any(r is x for x in g["L"])
            rows.append(row)
        (ROOT / f"data/dpo_{kind}.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows))
        stats[kind] = {"pairs": len(rows), "prompts": len({x["id"] for x in rows}), "dropped_too_long": too_long, **n_lucky}
    out = ROOT / "results/dpo_pairs.json"
    out.write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


def train(a):
    """Sigmoid DPO loss, written out instead of TRL's DPOTrainer: TRL materialises 262k-vocab logits for the whole
    ~1600-token sequence (the prompt alone is ~1270 tokens) and runs out of the 16 GB card at step 0. Here logits are
    kept only after the prefix chosen and rejected share; tokens in that prefix have the same policy and reference
    log-prob in both and cancel in the DPO margin, so the loss is the same. Reference log-probs are computed once,
    with the starting (sft_ho) adapter, before any update."""
    import torch
    import torch.nn.functional as F
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from train import MODEL

    tok = AutoTokenizer.from_pretrained(MODEL)
    rows = [json.loads(l) for l in open(ROOT / f"data/dpo_{a.kind}.jsonl")]
    random.Random(a.seed).shuffle(rows)
    data = []
    for r in rows:
        c, j = (tok.apply_chat_template(r["prompt"] + r[k], tokenize=True) for k in ("chosen", "rejected"))
        p = next((i for i, (x, y) in enumerate(zip(c, j)) if x != y), min(len(c), len(j)))
        assert 0 < p < min(len(c), len(j)) and max(len(c), len(j)) <= MAX_LEN, (r["prompt"][1]["content"][:80], p)
        data.append((c, j, p))
    torch.manual_seed(a.seed)
    policy = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).cuda(),
                                       str(a.init), is_trainable=True)
    policy.config.use_cache = False

    def logp(ids, p):  # summed log-prob of ids[p:] given ids[:p]
        x = torch.tensor([ids], device="cuda")
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = policy(input_ids=x, logits_to_keep=len(ids) - p + 1).logits[0, :-1].float()
        return torch.gather(F.log_softmax(logits, -1), 1, x[0, p:, None]).sum()

    policy.eval()
    with torch.no_grad():
        ref = [(logp(c, p).item(), logp(j, p).item()) for c, j, p in data]
    policy.train()
    policy.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    policy.enable_input_require_grads()
    params = [q for q in policy.parameters() if q.requires_grad]
    accum = 16
    steps = math.ceil(len(data) * a.epochs / accum)
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 1 - s / steps)  # linear decay, as TRL's default
    log, buf = [], defaultdict(list)
    order = [i for _ in range(math.ceil(a.epochs)) for i in range(len(data))][:steps * accum]
    for n, i in enumerate(order, 1):
        c, j, p = data[i]
        margin = (logp(c, p) - ref[i][0]) - (logp(j, p) - ref[i][1])
        loss = -F.logsigmoid(a.beta * margin)
        (loss / accum).backward()
        buf["loss"].append(loss.item()); buf["margin"].append(a.beta * margin.item()); buf["acc"].append(float(margin > 0))
        if n % accum == 0 or n == len(order):
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
            log.append({"step": len(log) + 1, **{k: sum(v) / len(v) for k, v in buf.items()}, "lr": sched.get_last_lr()[0]})
            print(json.dumps(log[-1]), flush=True)
            buf.clear()
    (a.out / "adapter").mkdir(parents=True, exist_ok=True)
    policy.save_pretrained(str(a.out / "adapter"))
    json.dump(log, open(a.out / "log_history.json", "w"), indent=1)
    # merge in a separate process (train.py merge): merging right after training crashed the WSL VM once (D2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pairs", "train"])
    ap.add_argument("--kind", choices=["std", "cf"], default="cf")
    ap.add_argument("--init", type=Path, default=ROOT / "runs/sft/adapter", help="sft_ho adapter")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--epochs", type=float, default=1)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--beta", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    {"pairs": pairs, "train": train}[a.cmd](a)
