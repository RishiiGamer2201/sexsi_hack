"""E13: our own models on a real benchmark. Spider dev (1034 questions, 20 real DBs), graded on the original DB (EX)
and on Zhong, Yu & Klein's distilled test-suite DBs (TS) -- published counterfactual copies we did not build.

Same agent loop as evaluate.py gen (AgentTune render / tool-call parser / fold, the run_sql tool, <= 5 steps), but
the system prompt carries the item's Spider schema instead of the retail schema, and run_sql opens the Spider DB.
Everything else in the prompt is word for word our training prompt. This is out of distribution for the trained
models (they only saw one retail schema), so read it as a transfer test of the reward effect, not as a Spider score.

Data: questions from HF xlangai/spider (validation split, CC BY-SA 4.0) in external/spider_hf/; gold SQL and DB order
from external/ESMp/spider_dev/gold.txt (checked identical: 1034/1034 db_id and query); DBs from external/testsuite_db.
Scoring is scripts/a2_spider_lucky.score (E6): EX = matches gold on the original DB, TS = also on every suite DB.

  bash scripts/local_spider.sh                                    # GPU: gen for base, sft_ho, B, C, then score
  python scripts/spider_eval.py score  ->  results/e13_spider_ours.json   (CPU, from results/spider_*.jsonl)
"""
import argparse
import json
import re
import sqlite3
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from a2_spider_lucky import DBROOT, score as ts_score  # noqa: E402
from sqlcf.agent import format_rows  # noqa: E402
from sqlcf.audit import wilson  # noqa: E402
from sqlcf.compare import SQLError, run  # noqa: E402
from sqlcf.rewards import final_sql  # noqa: E402

QUESTIONS = ROOT / "external/spider_hf/spider/validation-00000-of-00001.parquet"
GOLD = ROOT / "external/ESMp/spider_dev/gold.txt"
MODELS = ["base", "sft_ho", "B", "C", "B_cur", "Cmin_cur"]  # *_cur: E14 curriculum pilot
PAIRS = [("C", "B"), ("B", "sft_ho"), ("C", "sft_ho"), ("sft_ho", "base"),
         ("Cmin_cur", "B_cur"), ("B_cur", "sft_ho"), ("Cmin_cur", "sft_ho"), ("B_cur", "B"), ("Cmin_cur", "C")]
MAX_LEN, MAX_NEW = 8192, 1024
SYSTEM = """You are a careful data analyst working with a SQLite database.

Schema:
{schema}

Use the run_sql tool to explore the data and check your query before answering. Watch for
duplicate rows, joins that multiply rows, missing business filters and superseded records.
When you are done, reply with one short sentence and your final query in a ```sql block.
The final query must compute the answer from the tables; do not hard-code values."""


def items() -> list[dict]:
    import pyarrow.parquet as pq
    qs = pq.read_table(QUESTIONS).to_pylist()
    gold = [l.rstrip("\n").split("\t") for l in open(GOLD)]
    assert len(qs) == len(gold) == 1034 and all(q["db_id"] == g[1] for q, g in zip(qs, gold))
    return [{"id": i, "db_id": g[1], "question": q["question"], "gold": g[0]} for i, (q, g) in enumerate(zip(qs, gold))]


def db_file(db_id: str) -> Path:
    if not re.fullmatch(r"\w+", db_id or "") or not (DBROOT / db_id / f"{db_id}.sqlite").is_file():
        raise ValueError(f"unknown database id {db_id!r}")
    return DBROOT / db_id / f"{db_id}.sqlite"


def schema(db_id: str) -> str:
    con = sqlite3.connect(f"file:{db_file(db_id)}?mode=ro", uri=True)
    rows = con.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND sql IS NOT NULL ORDER BY rowid").fetchall()
    con.close()
    return "\n".join(" ".join(r[0].split()) + ";" for r in rows)


def run_sql(database: str, sql_command: str) -> str:
    """Run one read-only SQLite query on a database.

    Args:
        database: the database id given in the question, for example "concert_singer".
        sql_command: a single SELECT statement.

    Returns:
        Up to 20 result rows as text, or an error message.
    """
    try:
        return format_rows(run(str(db_file(database)), sql_command))
    except (SQLError, ValueError) as e:
        return f"ERROR: {e}"


def _call(fn) -> str:
    if fn.get("name") != "run_sql":
        return f"ERROR: unknown tool {fn.get('name')!r}"
    try:
        args = fn.get("arguments") or {}
        args = json.loads(args) if isinstance(args, str) else args
        return run_sql(**args)
    except (TypeError, ValueError) as e:
        return f"ERROR: bad arguments: {e}"


def gen(a):
    import os
    os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")
    from agenttune.agentic.rollout_engines.rollout_factory import (
        DEFAULT_TOOLS_FALLBACK_PROMPT, _build_tool_schema, _extract_tool_calls, _render_chat_template,
        _strip_special_tokens, fold_tool_messages_into_user)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    its = items()[: a.limit or None]
    tok = AutoTokenizer.from_pretrained(a.model)
    llm = LLM(a.model, dtype="float16", max_model_len=MAX_LEN, gpu_memory_utilization=a.gpu_mem, seed=a.seed)
    sp = SamplingParams(temperature=a.temperature, max_tokens=MAX_NEW)
    tools = [_build_tool_schema(run_sql)]
    fallback = DEFAULT_TOOLS_FALLBACK_PROMPT.format(tools=json.dumps(tools, indent=2))  # as train.fallback_system
    systems = {d: f"{SYSTEM.format(schema=schema(d))}\n\n{fallback}" for d in {it["db_id"] for it in its}}

    def ids(conv):
        out = _render_chat_template(tok, fold_tool_messages_into_user(conv), tools, tokenize=True, return_tensors=None)
        return list(out["input_ids"] if hasattr(out, "keys") else out)

    convs = [[{"role": "system", "content": systems[it["db_id"]]},
              {"role": "user", "content": f"Database: {it['db_id']}\nQuestion: {it['question']}"}]
             for it in its for _ in range(a.n)]
    live, too_long = list(range(len(convs))), 0
    for _ in range(a.max_steps):
        prompts = {i: ids(convs[i]) for i in live}
        fits = [i for i in live if len(prompts[i]) + MAX_NEW <= MAX_LEN]  # one long prompt would fail the whole batch
        too_long += len(live) - len(fits)
        if not fits:
            break
        outs = llm.generate([{"prompt_token_ids": prompts[i]} for i in fits], sp)
        nxt = []
        for i, o in zip(fits, outs):
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
    out = Path(a.out_dir) / f"spider_{a.name}.jsonl"
    with open(out, "w") as f:
        for j, conv in enumerate(convs):
            f.write(json.dumps({"model": a.name, "id": its[j // a.n]["id"], "sample": j % a.n, "messages": conv[2:]}) + "\n")
    print(f"{a.name}: {len(convs)} trajectories -> {out} (stopped for context length: {too_long})")


def _grade(task):
    gold, db_id, messages = task
    sql = final_sql(messages)
    ex, ts, _ = ts_score((sql or "", gold, db_id))
    return {"has_sql": sql is not None, "ex": bool(ex), "ts": bool(ts)}


def score(a):
    from evaluate import mcnemar_exact, paired_bootstrap
    its = items()
    out = {"what": "E13: our models on Spider dev; EX = original DB, TS = original + all Zhong test-suite DBs",
           "n_questions": len(its), "models": {}, "comparisons": {}}
    per_item = {}
    with Pool(16) as pool:
        for m in MODELS:
            p = Path(a.out_dir) / f"spider_{m}.jsonl"
            if not p.exists():
                continue
            rows = [json.loads(l) for l in open(p)]
            res = pool.map(_grade, [(its[r["id"]]["gold"], its[r["id"]]["db_id"], r["messages"]) for r in rows], chunksize=16)
            n, ex, ts = len(res), sum(r["ex"] for r in res), sum(r["ts"] for r in res)
            by = {}
            for r, g in zip(rows, res):
                by.setdefault(r["id"], {})[r["sample"]] = g
            per_item[m] = by
            out["models"][m] = {"samples": n, "has_sql": sum(r["has_sql"] for r in res) / n,
                                "EX": wilson(ex, n), "TS": wilson(ts, n), "lucky": ex - ts,
                                "lucky_share_of_EX": wilson(ex - ts, ex) if ex else None}
            v = out["models"][m]
            print(f"{m:7} EX {v['EX'][0]:.3f}  TS {v['TS'][0]:.3f}  lucky {ex - ts}/{ex}"
                  f" = {(ex - ts) / max(ex, 1):.3f}  has_sql {v['has_sql']:.3f}", flush=True)
    ids = range(len(its))
    mean = lambda m, k: [sum(g[k] for g in per_item[m][i].values()) / len(per_item[m][i]) for i in ids]
    for x, y in PAIRS:
        if x in per_item and y in per_item:
            s0 = lambda m: [per_item[m][i][0]["ts"] for i in ids]
            ax, ay = s0(x), s0(y)
            lucky = lambda m: [sum(g["ex"] and not g["ts"] for g in per_item[m][i].values()) / len(per_item[m][i]) for i in ids]
            out["comparisons"][f"{x}_vs_{y}"] = {
                "TS_diff_bootstrap95": paired_bootstrap(mean(x, "ts"), mean(y, "ts")),
                "EX_diff_bootstrap95": paired_bootstrap(mean(x, "ex"), mean(y, "ex")),
                "lucky_rate_diff_bootstrap95": paired_bootstrap(lucky(x), lucky(y)),
                "TS_mcnemar_p_sample0": mcnemar_exact(sum(u and not v for u, v in zip(ax, ay)), sum(v and not u for u, v in zip(ax, ay)))}
    Path(a.result).write_text(json.dumps(out, indent=1))
    print("->", a.result)


if __name__ == "__main__":
    assert db_file("concert_singer").name == "concert_singer.sqlite" and "CREATE TABLE" in schema("concert_singer")
    for bad in ["../x", "S_s101", ""]:
        assert run_sql(bad, "SELECT 1").startswith("ERROR")
    assert run_sql("concert_singer", "SELECT count(*) FROM singer").startswith("6")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["gen", "score", "check"])
    ap.add_argument("--model")
    ap.add_argument("--name")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-steps", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gpu-mem", type=float, default=0.75)
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--result", default="results/e13_spider_ours.json")
    a = ap.parse_args()
    if a.cmd == "check":
        it = items()
        print(len(it), it[0], "\n", max(len(schema(d)) for d in {x["db_id"] for x in it}), "max schema chars")
    else:
        {"gen": gen, "score": score}[a.cmd](a)
