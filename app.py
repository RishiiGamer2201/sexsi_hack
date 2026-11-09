"""Gradio demo, no GPU: pick a test question and a recorded trajectory (or type your own SQL), and see
the final query scored on the original DB and on each counterfactual DB, with the reward each
function gives. Needs data/test (items + DBs, 1.2 MB) and results/traj_*.jsonl.

  .venv-train/bin/python app.py            # http://localhost:7860
"""
import json
from collections import defaultdict
from pathlib import Path

import gradio as gr

from sqlcf.rewards import REWARDS, _exec, final_sql

ROOT = Path(__file__).resolve().parent
ITEMS = {x["id"]: x for x in map(json.loads, open(ROOT / "data/test/items.jsonl"))}
TRAJ = defaultdict(dict)  # item id -> {"model #sample": messages}
for p in sorted((ROOT / "results").glob("traj_*.jsonl")):
    for r in map(json.loads, open(p)):
        if r["id"] in ITEMS:
            TRAJ[r["id"]][f'{r["model"]} #{r.get("sample", 0)}'] = r["messages"]


def _checks(item, sql):
    return [REWARDS[n]([f"```sql\n{sql}\n```"], dbs=[item["dbs"]], gold=[item["gold"]], ordered=[item["ordered"]])[0]
            for n in REWARDS] if sql else [0.0] * len(REWARDS)


def _short(rows, n=3):
    if rows is None:
        return "SQL error"
    s = "; ".join(", ".join(map(str, r)) for r in rows[:n])
    return s + (f" ... ({len(rows)} rows)" if len(rows) > n else "")


def score(item_id, sql):
    item = ITEMS[item_id]
    sql = (sql or "").strip().rstrip(";")
    edits = ["original (agent saw this)"] + [f"{e} ({k})" for e, k in zip(item["cf_edits"], item["cf_kinds"])]
    table = []
    for db, gold, edit in zip(item["dbs"], item["gold"], edits):
        got = _exec(db, sql) if sql else None
        ok = REWARDS["R_cf_strict"]([f"```sql\n{sql}\n```"], dbs=[[db]], gold=[[gold]], ordered=[item["ordered"]])[0]
        table.append([edit, _short([tuple(r) for r in gold]), _short(list(got) if got is not None else None),
                      "pass" if ok else "FAIL"])
    rewards = [[n, s] for n, s in zip(REWARDS, _checks(item, sql))]
    return table, rewards


def show_item(item_id):
    item = ITEMS[item_id]
    runs = sorted(TRAJ[item_id])
    head = f"**{item['family']} / {item['template']}**\n\n{item['question']}\n\nDatabase: `{item['dbs'][0].split('/')[-2]}`"
    default = BLIND[item_id] or (runs[0] if runs else None)
    return head, gr.update(choices=runs, value=default), item["gold_sql"]


def show_run(item_id, run):
    msgs = TRAJ[item_id].get(run or "", [])
    text = "\n\n".join(f"**{m['role']}**\n```\n{m.get('content') or ''}\n```" for m in msgs)
    return text, final_sql(msgs) or ""


def _blind_run(i):
    """First recorded run of item i that passes the original DB but fails a counterfactual, else None."""
    it = ITEMS[i]
    col = dict(dbs=[it["dbs"]], gold=[it["gold"]], ordered=[it["ordered"]])
    for run_, msgs in sorted(TRAJ[i].items()):
        if REWARDS["R_exec_rex"]([msgs], **col)[0] and not REWARDS["R_cf_strict"]([msgs], **col)[0]:
            return run_


BLIND = {i: _blind_run(i) for i in ITEMS}


with gr.Blocks(title="Counterfactual SQL rewards") as demo:
    gr.Markdown("# Counterfactual SQL rewards\nA query can match the answer on the one DB the agent explored "
                "and still be wrong. Counterfactual DBs (never shown to the agent) catch it. "
                "Items at the top of the list have a recorded run that the single-DB reward accepts but a counterfactual rejects.")
    ids = sorted(ITEMS, key=lambda i: (BLIND[i] is None, i))
    item = gr.Dropdown(ids, value=ids[0], label="Test question")
    head = gr.Markdown()
    with gr.Row():
        with gr.Column():
            run = gr.Dropdown([], label="Recorded run (model #sample)")
            traj = gr.Markdown()
        with gr.Column():
            sql = gr.Code(language="sql", label="Final SQL (edit it and press Score)")
            gold_sql = gr.Code(language="sql", label="Gold SQL")
            btn = gr.Button("Score", variant="primary")
            per_db = gr.Dataframe(headers=["DB", "gold", "this query", "check"], label="Per-DB checks")
            rew = gr.Dataframe(headers=["reward", "score"], label="Reward each function gives")
    item.change(show_item, item, [head, run, gold_sql])
    run.change(show_run, [item, run], [traj, sql]).then(score, [item, sql], [per_db, rew])
    btn.click(score, [item, sql], [per_db, rew])
    demo.load(show_item, item, [head, run, gold_sql])

if __name__ == "__main__":
    demo.launch()
