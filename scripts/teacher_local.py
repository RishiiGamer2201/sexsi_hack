"""D3: the same teacher run as D1/D2, but Command A runs locally in int4 (vLLM) instead of through the Cohere API.

Same prompts as scripts/e5_command_a.py (SYS_PLAN for the distillation teacher, SYS for the E5 test eval), same
output format (one JSON line per item, evaluate.py trajectory format), so scripts/distil.py and evaluate.py score
read it unchanged. Resumes: ids already in --out are skipped.

Backends:
  vllm    the real run (GPU). Default model: gghfez/command-a-03-2025-AWQ (W4A16, group 128, compressed-tensors,
          68.2 GB on disk) -> needs one >= 94 GB GPU (H100 NVL, RTX PRO 6000) or two 80 GB with --tp 2.
  replay  dry run on CPU: copies answers from an existing teacher file (default: the API teacher). Tests every
          step around the model; distil.py score on the replayed file must reproduce results/d1_teacher_filter.json.
  hf      dry run for logit distillation (CPU): replayed answers, plus the top-K next-token log-probs a small
          Hugging Face model (--model) gives them, in the same --logprobs format vLLM writes.

--logprobs K also writes <out>.logprobs.jsonl: per answer, the sampled tokens as strings and the top-K
(token string, log-prob) pairs at each step. vLLM returns raw log-probs (T=1, before top_p), which is the
distribution logit distillation (scripts/logit_distil.py) matches.

  python scripts/teacher_local.py --backend replay --items runs/distil/items.jsonl --out runs/dry/teacher.jsonl --plan
  python scripts/teacher_local.py --items runs/distil/items.jsonl --out results/teacher_command_a_int4.jsonl \
      --plan --temperature 0.3                                       # D3 teacher (353 train items)
  python scripts/teacher_local.py --items data/test/items.jsonl --out results/traj_command_a_int4.jsonl \
      --temperature 0.7                                              # E5-int4: same test eval as the API teacher
  ... --plan --temperature 0.3 --logprobs 20                         # D4: also the teacher's top-20 log-probs
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from e5_command_a import SYS, SYS_PLAN  # noqa: E402
from sqlcf.agent import user_message  # noqa: E402

MODEL = "gghfez/command-a-03-2025-AWQ"


def vllm_answers(a, items, system):
    from vllm import LLM, SamplingParams

    llm = LLM(a.model, max_model_len=a.max_model_len, gpu_memory_utilization=a.gpu_mem, tensor_parallel_size=a.tp,
              enforce_eager=a.eager, seed=a.seed)
    # top_p 0.75 = the Cohere chat API default (the API teacher ran with it)
    sp = SamplingParams(temperature=a.temperature, top_p=0.75, max_tokens=a.max_tokens, seed=a.seed,
                        logprobs=a.logprobs or None)
    for i in range(0, len(items), a.batch):  # batches, so a crash keeps everything written so far
        chunk = items[i:i + a.batch]
        t = time.time()
        outs = llm.chat([[{"role": "system", "content": system}, {"role": "user", "content": user_message(it)}]
                         for it in chunk], sp, use_tqdm=False)
        lat = (time.time() - t) / len(chunk)
        for it, o in zip(chunk, outs):
            c = o.outputs[0]
            lp = None
            if a.logprobs:  # each step's dict holds the top-K and the sampled token (K+1 entries when it is not top-K)
                steps = [sorted(step.items(), key=lambda kv: kv[1].rank)[:a.logprobs] for step in c.logprobs]
                lp = {"tokens": [step[t].decoded_token for t, step in zip(c.token_ids, c.logprobs)],
                      "top": [[[x.decoded_token, round(x.logprob, 4)] for _, x in s] for s in steps],
                      # ids too: the strings can be re-decoded offline with the teacher's tokenizer if needed
                      "ids": list(c.token_ids), "top_ids": [[t for t, _ in s] for s in steps]}
            yield it, c.text, lat, {"input_tokens": len(o.prompt_token_ids), "output_tokens": len(c.token_ids)}, lp


def replay_answers(a, items, system):
    src = {r["id"]: r for r in map(json.loads, open(a.replay_from))}
    for it in items:
        if it["id"] in src:
            yield it, src[it["id"]]["messages"][-1]["content"], 0.0, {}, None
        else:
            print(f"replay: no answer for {it['id']}", flush=True)


def hf_answers(a, items, system):
    """Replayed text, scored token by token by a small HF model (teacher forcing): fake teacher log-probs."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float32).eval()
    for it, text, lat, usage, _ in replay_answers(a, items, system):
        ids = tok(text, add_special_tokens=False)["input_ids"]
        with torch.no_grad():
            logp = torch.log_softmax(model(input_ids=torch.tensor([[tok.bos_token_id or 0] + ids])).logits[0, :-1].float(), -1)
        top = logp.topk(a.logprobs or 5, -1)
        # decode one id at a time, as vLLM's decoded_token does
        lp = {"tokens": [tok.decode([t]) for t in ids],
              "top": [[[tok.decode([int(t)]), round(float(v), 4)] for v, t in zip(vs, ts)] for vs, ts in zip(top.values, top.indices)]}
        yield it, text, lat, usage, lp


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["vllm", "replay", "hf"], default="vllm")
    ap.add_argument("--items", type=Path, default=ROOT / "data/test/items.jsonl")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--name", default="command_a_int4", help="model name in the trajectory rows")
    ap.add_argument("--plan", action="store_true", help="teacher prompt: plan, then SQL (scripts/distil.py)")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--tp", type=int, default=1, help="tensor parallel GPUs")
    ap.add_argument("--max-model-len", type=int, default=4096, help="prompts are ~700 tokens, answers < 1k")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--gpu-mem", type=float, default=0.92)
    ap.add_argument("--eager", action="store_true", help="skip CUDA graphs: less memory, slower")
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--replay-from", type=Path, default=ROOT / "results/teacher_command_a.jsonl")
    ap.add_argument("--logprobs", type=int, default=0, help="also save the top-K next-token log-probs (logit distillation)")
    a = ap.parse_args()
    items = [json.loads(l) for l in open(a.items)][: a.limit or None]
    done = {json.loads(l)["id"] for l in open(a.out)} if a.out.exists() else set()
    todo = [it for it in items if it["id"] not in done]
    print(f"{a.backend}: {len(done)} done, {len(todo)} to go -> {a.out}", flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    gen = {"vllm": vllm_answers, "replay": replay_answers, "hf": hf_answers}[a.backend]
    lp_out = a.out.with_suffix(".logprobs.jsonl")
    t0, n = time.time(), 0
    with open(a.out, "a") as f, open(lp_out, "a") if a.logprobs else open("/dev/null", "w") as g:
        for it, text, lat, usage, lp in gen(a, todo, SYS_PLAN if a.plan else SYS):
            # log-probs first: an answer row only counts as done once its log-probs are on disk
            if lp is not None:
                g.write(json.dumps({"id": it["id"], **lp}) + "\n")
                g.flush()
            f.write(json.dumps({"model": a.name, "id": it["id"], "sample": 0, "latency_s": round(lat, 3),
                                "billed": usage, "messages": [{"role": "assistant", "content": text}]}) + "\n")
            f.flush()
            n += 1
            if n % 50 == 0:
                print(f"{n}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
    print(f"wrote {n} in {time.time() - t0:.0f}s", flush=True)
