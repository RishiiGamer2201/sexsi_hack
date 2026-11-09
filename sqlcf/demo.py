"""Demo core, no UI and no GPU: score a final query on an item's original DB and its counterfactual DBs, with
the reward each function gives. demo/index.html runs this module in the browser (Pyodide); the api_* functions
return JSON strings for it. Needs data/test (items + DBs) and results/traj_*.jsonl.
"""
import json
from collections import defaultdict
from pathlib import Path

from .rewards import REWARDS, _exec, final_sql

ROOT = Path(__file__).resolve().parent.parent
ITEMS = {x["id"]: x for x in map(json.loads, open(ROOT / "data/test/items.jsonl"))}
TRAJ = defaultdict(dict)  # item id -> {"model #sample": messages}
for p in sorted((ROOT / "results").glob("traj_*.jsonl")):
    for r in map(json.loads, open(p)):
        if r["id"] in ITEMS:
            TRAJ[r["id"]][f'{r["model"]} #{r.get("sample", 0)}'] = r["messages"]


def _reward(name, item, completion, dbs=None, gold=None):
    return REWARDS[name]([completion], dbs=[dbs or item["dbs"]], gold=[gold or item["gold"]], ordered=[item["ordered"]])[0]


def _blind_run(i):
    """First recorded run of item i that passes the original DB but fails a counterfactual, else None."""
    for run, msgs in sorted(TRAJ[i].items()):
        if _reward("R_exec_rex", ITEMS[i], msgs) and not _reward("R_cf_strict", ITEMS[i], msgs):
            return run


BLIND = {i: _blind_run(i) for i in ITEMS}
ORDER = sorted(ITEMS, key=lambda i: (BLIND[i] is None, i))  # showcase items first


def _short(rows, n=3):
    if rows is None:
        return "SQL error"
    s = "; ".join(", ".join(map(str, r)) for r in rows[:n])
    return s + (f" ... ({len(rows)} rows)" if len(rows) > n else "")


def score(item_id, sql):
    item = ITEMS[item_id]
    sql = (sql or "").strip().rstrip(";")
    comp = f"```sql\n{sql}\n```" if sql else ""
    edits = ["original (agent saw this)"] + [f"{e} ({k})" for e, k in zip(item["cf_edits"], item["cf_kinds"])]
    checks = []
    for db, gold, edit in zip(item["dbs"], item["gold"], edits):
        got = _exec(db, sql) if sql else None
        checks.append({"db": edit, "gold": _short([tuple(r) for r in gold]), "got": _short(got),
                       "ok": bool(_reward("R_cf_strict", item, comp, [db], [gold]))})
    return {"checks": checks, "rewards": {n: _reward(n, item, comp) for n in REWARDS}}


def item_view(item_id):
    item = ITEMS[item_id]
    runs = sorted(TRAJ[item_id])
    return {"family": item["family"], "template": item["template"], "question": item["question"],
            "db": item["dbs"][0].split("/")[-2], "gold_sql": item["gold_sql"], "runs": runs,
            "default": BLIND[item_id] or (runs[0] if runs else None)}


def run_view(item_id, run):
    msgs = TRAJ[item_id].get(run or "", [])
    return {"messages": [{"role": m["role"], "content": m.get("content") or ""} for m in msgs], "sql": final_sql(msgs) or ""}


def api_items():
    return json.dumps([{"id": i, "blind": BLIND[i] is not None} for i in ORDER])


def api_item(item_id):
    return json.dumps(item_view(item_id))


def api_run(item_id, run):
    return json.dumps(run_view(item_id, run))


def api_score(item_id, sql):
    return json.dumps(score(item_id, sql))


if __name__ == "__main__":  # self-check: a showcase item's blind run, gold SQL, junk SQL
    i = ORDER[0]
    v = item_view(i)
    s = score(i, run_view(i, v["default"])["sql"])
    assert s["rewards"]["R_exec_rex"] == 1.0 and s["rewards"]["R_cf_strict"] == 0.0, s
    assert all(x == 1.0 for x in score(i, v["gold_sql"])["rewards"].values())
    assert all(x == 0.0 for x in score(i, "SELEC nonsense")["rewards"].values())
    print("ok", len(ITEMS), "items,", sum(b is not None for b in BLIND.values()), "showcase;", i, v["default"], s["rewards"])
