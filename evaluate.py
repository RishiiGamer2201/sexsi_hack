"""E4 evaluation: generate agent trajectories on the test set (GPU, vLLM) and score them (CPU).

  # one model per call; adapters are pre-merged in fp32 and saved fp16 by train.py (vLLM 0.22 LoRA breaks on
  # Tiny Aya's tied embeddings: 'VocabParallelEmbeddingWithLoRA' has no 'quant_method')
  python evaluate.py gen --model CohereLabs/tiny-aya-global --name base
  python evaluate.py gen --model runs/sft/merged    --name sft
  python evaluate.py gen --model runs/grpo_B/merged --name B
  python evaluate.py gen --model runs/grpo_C/merged --name C
  python evaluate.py score --traj results/traj_*.jsonl          # -> results/e4_eval.json
  python evaluate.py selfcheck                                   # CPU: oracle/mutant trajectories

Generation uses AgentTune's own render / tool-call parser / fold so eval matches GRPO rollouts.
Verified = correct on the test original AND every test counterfactual (different generator).
"""
import argparse
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

from sqlcf.agent import SYSTEM, run_sql, user_message
from sqlcf.audit import literal_sql, wilson
from sqlcf.rewards import checks, final_sql

TABLES_RE = re.compile(r"\b(from|join)\s+(customers|products|orders|order_items|payments|refunds|tier_history|invoice_adjustments)\b", re.I)
IN_LIST_RE = re.compile(r"\bIN\s*\(\s*\d+(\s*,\s*\d+){2,}\s*\)", re.I)
PAIRS = [("C", "B"), ("B", "sft"), ("C", "sft"), ("sft", "base")]


# ---------------- generation (GPU) ----------------
def gen(a):
    from agenttune.agentic.rollout_engines.rollout_factory import (
        _build_tool_schema, _extract_tool_calls, _render_chat_template, _strip_special_tokens,
        fold_tool_messages_into_user)
    from transformers import AutoTokenizer
    import os
    os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")  # its JIT kernel build fails on the VM
    from vllm import LLM, SamplingParams

    from train import fallback_system

    items = [json.loads(l) for l in open(a.items)][: a.limit or None]
    tok = AutoTokenizer.from_pretrained(a.model)
    llm = LLM(a.model, dtype="float16", max_model_len=8192, gpu_memory_utilization=a.gpu_mem, seed=a.seed)  # fp16: see sqlcf/precision.py
    sp = SamplingParams(temperature=a.temperature, max_tokens=1024, seed=a.seed)
    schema = [_build_tool_schema(run_sql)]

    def ids(conv):  # token ids, not text: vLLM would add a second BOS to the rendered string
        out = _render_chat_template(tok, fold_tool_messages_into_user(conv), schema, tokenize=True, return_tensors=None)
        return {"prompt_token_ids": list(out["input_ids"] if hasattr(out, "keys") else out)}

    for name in [a.name]:
        convs = [[{"role": "system", "content": fallback_system(SYSTEM)}, {"role": "user", "content": user_message(it)}]
                 for it in items for _ in range(a.n)]
        live = list(range(len(convs)))
        for _ in range(a.max_steps):
            if not live:
                break
            outs = llm.generate([ids(convs[i]) for i in live], sp)
            nxt = []
            for i, o in zip(live, outs):
                raw = o.outputs[0].text
                text = _strip_special_tokens(raw, tok)
                convs[i].append({"role": "assistant", "content": text})
                calls = _extract_tool_calls({"role": "assistant", "content": text}, raw) or []
                for c in calls:
                    fn = c.get("function", {})
                    convs[i].append({"role": "tool", "name": fn.get("name"), "content": _call(fn)})
                if calls:
                    nxt.append(i)
            live = nxt
        out = Path(a.out_dir) / f"traj_{name}.jsonl"
        with open(out, "w") as f:
            for j, conv in enumerate(convs):
                it = items[j // a.n]
                f.write(json.dumps({"model": name, "id": it["id"], "sample": j % a.n, "messages": conv[2:]}) + "\n")
        print(f"{name}: {len(convs)} trajectories -> {out}")


def _call(fn) -> str:
    if fn.get("name") != "run_sql":
        return f"ERROR: unknown tool {fn.get('name')!r}"
    try:
        args = fn.get("arguments") or {}
        args = json.loads(args) if isinstance(args, str) else args
        return run_sql(**args)
    except (TypeError, ValueError) as e:
        return f"ERROR: bad arguments: {e}"


# ---------------- scoring (CPU) ----------------
def smuggled(sql: str | None) -> bool:
    """Final SQL reads no table, or hard-codes a list of >= 3 ids."""
    return bool(sql) and (not TABLES_RE.search(sql) or bool(IN_LIST_RE.search(sql)))


def grade(item, messages) -> dict:
    sql = final_sql(messages)
    v = checks(sql, item["dbs"], item["gold"], item["ordered"])
    tools = [m for m in messages if m.get("role") == "tool"]
    bad_tools = sum(str(m.get("content", "")).startswith("ERROR") for m in tools)
    return {"single": bool(v[0]), "verified": all(v), "has_sql": sql is not None,
            "silent_error": bool(tools) and bad_tools == 0 and sql is not None and not all(v),
            "smuggled": smuggled(sql), "tool_calls": len(tools), "bad_tool_calls": bad_tools}


def pass_hat_k(c: int, n: int, k: int) -> float:
    """tau-bench pass^k: probability that k i.i.d. samples are all correct."""
    return math.comb(c, k) / math.comb(n, k) if n >= k else float("nan")


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired_bootstrap(x: list[float], y: list[float], reps: int = 10_000, seed: int = 0):
    rng = random.Random(seed)
    n = len(x)
    d = [a - b for a, b in zip(x, y)]
    stats = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return [sum(d) / n, stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1]]


def score(traj_paths: list[Path], items_path: Path, out: Path) -> dict:
    items = {x["id"]: x for x in map(json.loads, open(items_path))}
    per = defaultdict(lambda: defaultdict(list))  # model -> item id -> [grade per sample]
    for p in traj_paths:
        for r in map(json.loads, open(p)):
            per[r["model"]][r["id"]].append(grade(items[r["id"]], r["messages"]))
    res = {}
    for model, by_item in per.items():
        g = [x for v in by_item.values() for x in v]
        fam = defaultdict(list)
        for iid, v in by_item.items():
            fam[items[iid]["family"]] += v
        n_min = min(len(v) for v in by_item.values())
        tools = sum(x["tool_calls"] for x in g)
        res[model] = {
            "items": len(by_item), "samples": len(g),
            **{k: wilson(sum(x[k] for x in g), len(g)) for k in ("verified", "single", "silent_error", "smuggled", "has_sql")},
            "inflation_single_minus_verified": (sum(x["single"] for x in g) - sum(x["verified"] for x in g)) / len(g),
            "invalid_tool_call_rate": sum(x["bad_tool_calls"] for x in g) / tools if tools else None,
            "tool_calls_per_traj": tools / len(g),
            "verified_by_family": {f: wilson(sum(x["verified"] for x in v), len(v)) for f, v in sorted(fam.items())},
            "pass^k": {k: sum(pass_hat_k(sum(x["verified"] for x in v[:n_min]), n_min, k) for v in by_item.values()) / len(by_item)
                       for k in (1, 2, 4) if k <= n_min},
        }
    res["comparisons"] = {}
    for a_, b_ in PAIRS:
        if a_ in per and b_ in per:
            ids = sorted(set(per[a_]) & set(per[b_]))
            s0a = [per[a_][i][0]["verified"] for i in ids]
            s0b = [per[b_][i][0]["verified"] for i in ids]
            ma = [sum(x["verified"] for x in per[a_][i]) / len(per[a_][i]) for i in ids]
            mb = [sum(x["verified"] for x in per[b_][i]) / len(per[b_][i]) for i in ids]
            res["comparisons"][f"{a_}_vs_{b_}"] = {
                "n_items": len(ids),
                "mcnemar_p_sample0": mcnemar_exact(sum(x and not y for x, y in zip(s0a, s0b)), sum(y and not x for x, y in zip(s0a, s0b))),
                "verified_diff_bootstrap95": paired_bootstrap(ma, mb)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    return res


def selfcheck(items_path: Path, tmp: Path):
    """Oracle (gold) trajectories must score verified=1; mutants lower; literals flagged."""
    items = [json.loads(l) for l in open(items_path)]
    rows = []
    for it in items:
        db_id = it["dbs"][0].split("/")[-2]
        pol = {"oracle": it["gold_sql"], "literal": literal_sql(it["gold"][0]),
               "mutant": next(iter(it["mutants"].values()), it["gold_sql"])}
        for name, sql in pol.items():
            msgs = [{"role": "assistant", "content": "[]"},
                    {"role": "tool", "name": "run_sql", "content": run_sql(db_id, sql)},
                    {"role": "assistant", "content": f"Answer.\n```sql\n{sql}\n```"}]
            rows.append({"model": name, "id": it["id"], "sample": 0, "messages": msgs})
    tmp.write_text("".join(json.dumps(r) + "\n" for r in rows))
    r = score([tmp], items_path, tmp.with_suffix(".score.json"))
    assert r["oracle"]["verified"][0] == 1.0 and r["oracle"]["smuggled"][0] == 0.0, r["oracle"]
    assert r["literal"]["verified"][0] < 0.1 and r["literal"]["smuggled"][0] == 1.0, r["literal"]
    assert r["mutant"]["verified"][0] < r["mutant"]["single"][0] <= 1.0, r["mutant"]
    assert pass_hat_k(2, 4, 2) == 1 / 6 and mcnemar_exact(0, 6) == 2 / 64
    for k in ("oracle", "literal", "mutant"):
        print(k, {m: round(r[k][m][0], 3) for m in ("verified", "single", "silent_error", "smuggled")})
    print("selfcheck ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["gen", "score", "selfcheck"])
    ap.add_argument("--items", type=Path, default=Path("data/test/items.jsonl"))
    ap.add_argument("--model", default="CohereLabs/tiny-aya-global")
    ap.add_argument("--name", default="base")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-steps", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gpu-mem", type=float, default=0.85, help="vLLM share of GPU memory (0.75 on a 16 GB desktop card)")
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--traj", type=Path, nargs="*", default=[])
    a = ap.parse_args()
    if a.cmd == "gen":
        gen(a)
    elif a.cmd == "score":
        print(json.dumps(score(a.traj, a.items, Path(a.out_dir) / "e4_eval.json"), indent=1)[:3000])
    else:
        selfcheck(a.items, Path(a.out_dir) / "_selfcheck_traj.jsonl")
