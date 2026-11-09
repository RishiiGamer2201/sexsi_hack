"""Manual audit labels: write results/manual_audit.jsonl + manual_audit_summary.json from runs/audit_sample.json
(scripts/audit_sample.py) and the hand labels below (assigned by reading runs/audit_sample.md, Nov 9).

  .venv/bin/python scripts/audit_sample.py && .venv/bin/python scripts/audit_labels.py
"""
import json, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.rewards import final_sql

CAT = {
    "extra_filter": ("Condition-related", "extra status filter the question does not ask for"),
    "wrong_date_col": ("Attribute-related", "order_date used where the question says payment date"),
    "count_for_sum": ("Function-related", "COUNT(*) instead of SUM(quantity)"),
    "missing_current": ("Condition-related", "no latest-row (current tier) filter on tier_history"),
    "missing_table": ("Table-related", "invoice_adjustments left out of net invoice"),
    "wrong_grain": ("Clause-related", "AVG over order items instead of per-order totals"),
    "value_linking": ("Value-related", "product category matched against customer columns, or hallucinated value"),
    "wrong_table": ("Table-related", "wrong table entirely"),
    "invalid_sql": ("Others", "does not run: undefined alias, unknown column or function"),
    "incoherent": ("Others", "incoherent query or exploratory query given as the answer"),
}
L = {0: "extra_filter", 1: "wrong_date_col", 2: "missing_current", 3: "extra_filter", 4: "count_for_sum", 5: "missing_table",
     6: "value_linking", 7: "wrong_date_col", 8: "wrong_grain", 9: "incoherent", 10: "value_linking", 11: "wrong_date_col",
     12: "incoherent", 13: "missing_table", 14: "value_linking", 15: "wrong_date_col",
     16: "extra_filter", 17: "wrong_date_col", 18: "missing_table", 19: "wrong_date_col", 20: "wrong_table", 21: "count_for_sum",
     22: "value_linking", 23: "wrong_date_col", 24: "wrong_grain", 25: "missing_current", 26: "value_linking", 27: "wrong_date_col",
     28: "wrong_grain", 29: "invalid_sql", 30: "value_linking", 31: "invalid_sql",
     32: "extra_filter", 33: "wrong_date_col", 34: "missing_current", 35: "extra_filter", 36: "count_for_sum", 37: "missing_table",
     38: "value_linking", 39: "wrong_date_col", 40: "wrong_grain", 41: "missing_current", 42: "invalid_sql", 43: "wrong_date_col",
     44: "wrong_grain", 45: "missing_current", 46: "extra_filter", 47: "invalid_sql"}
NOTE = {1: "also an extra status filter", 4: "also order_date for payment date", 5: "also includes cancelled orders",
        21: "also order_date for payment date", 36: "also order_date for payment date", 37: "also includes cancelled orders",
        22: "also compares status to a year", 29: "now() is not SQLite; also no status filter",
        31: "otherwise close to gold", 47: "otherwise close to gold", 41: "hard-codes a cut-off date", 45: "hard-codes a cut-off date",
        9: "self-join on name, nonexistent customers.tier", 12: "returned SELECT status, COUNT(*) as the answer",
        10: "invented city 'Malibu'", 26: "invented city 'Malaga'", 14: "nonexistent customers.category", 42: "nonexistent oi.customer_id",
        20: "counts customers with orders, ignores tier_history", 17: "payments of any date", 19: "payments of any date", 33: "payments of any date"}

items = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/test/items.jsonl")}
trajs = {}
for m in ("sft_ho", "B", "C"):
    for l in open(ROOT / f"results/traj_{m}.jsonl"):
        r = json.loads(l); trajs[(m, r["id"], r["sample"])] = r
sample = json.load(open(ROOT / "runs/audit_sample.json"))
assert len(sample) == len(L) == 48
rows = []
for s in sample:
    it = items[s["id"]]; k = L[s["n"]]
    rows.append({**s, "family": it["family"], "template": it["template"], "label": k, "nl2sql_bugs": CAT[k][0],
                 "what": CAT[k][1], "note": NOTE.get(s["n"], ""), "question": it["question"], "gold_sql": it["gold_sql"],
                 "sql": final_sql(trajs[(s["model"], s["id"], s["sample"])]["messages"])})
with open(ROOT / "results/manual_audit.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
summ = {"n": len(rows), "by_label": collections.Counter(r["label"] for r in rows),
        "lucky_by_label": collections.Counter(r["label"] for r in rows if r["lucky"]),
        "by_model_label": {m: collections.Counter(r["label"] for r in rows if r["model"] == m) for m in ("sft_ho", "B", "C")},
        "smuggling_or_hacking": 0}
(ROOT / "results/manual_audit_summary.json").write_text(json.dumps(summ, indent=1))
for k, v in summ["by_label"].most_common():
    print(f"{v:3d}  lucky {summ['lucky_by_label'].get(k, 0):2d}  {k:16s} {CAT[k][0]}: {CAT[k][1]}")
print({m: dict(c) for m, c in summ["by_model_label"].items()})
