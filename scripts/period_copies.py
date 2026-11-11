"""E12: period-edge copies, for questions filtered by a time period. CPU.

Aksh's question: "revenue from completed orders in March - can we make separate instances for each month to test on?"
Our templates filter by year (the finest period they use), so the analogue is one extra copy per item that puts the
asked period's edges into the data. For the slice of the item (city x year Y), half of its orders in Y move to Y-01-01 and
Y-12-31 (alternating; Dec 31 if the customer signed up after Jan 1), and half of its orders in the other year move to the
day just outside Y (2025-01-01 or 2024-12-31). Payments,
refunds and invoice adjustments move with their order (same offset, clipped to the generator's END date); a moved
payment lands 0, 1 or its own offset (>= 1) days after the order, so payments also sit on the edges and a December
order's payment can land in January of the next year. Every copy is re-checked against the business rules (db.write).

Date bugs are generated from each year-filtered gold query by rewriting its substr(x.<date>, 1, 4) = 'Y' clause:
  excl_end     x.d >= 'Y-01-01' AND x.d < 'Y-12-31'          (drops Dec 31)
  excl_start   x.d >  'Y-01-01' AND x.d <= 'Y-12-31'         (drops Jan 1)
  incl_next    x.d BETWEEN 'Y-01-01' AND 'Y+1-01-01'          (takes Jan 1 of the next year)
  col_swap     order date <-> payment date (only when both orders o and payments pay are in the query)
  no_filter    the year condition removed (a control: any DB with two years should catch it)

  (a) audit: on the E0 audit items with a year, how often each date bug is paid by the original DB alone, by the
      original + its mutant-blind copies (dbs_random, E0's headline setting), by the original + its greedy copies (dbs),
      and with the period-edge copy added; and whether any correct query (gold, paraphrases) fails the new copy
  (b) real answers: sft_ho's GRPO rollouts and every model's E4 test answers on year items: how many answers our
      verifier counts as verified fail the period-edge copy

  python scripts/period_copies.py      # -> results/e12_period_copies.json; copies in data/<split>/dbs/<base>/period/
"""
import json
import random
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluate import grade  # noqa: E402
from sqlcf import db  # noqa: E402
from sqlcf.audit import wilson  # noqa: E402
from sqlcf.cf import FOCUS_KEYS, TEST_N, _closure, _copy, _f_orders, _pick  # noqa: E402
from sqlcf.rewards import DATA, _exec, checks, final_sql  # noqa: E402

YEAR = re.compile(r"substr\((\w+)\.(\w+), 1, 4\) = '(\d{4})'")


def e_period_edges(rows, rng, f):
    y = f["year"]
    edge_out = date(y + 1, 1, 1) if y == min(db.YEARS) else date(y - 1, 12, 31)  # just outside Y, still in the data
    signup = {c[0]: date.fromisoformat(c[3]) for c in rows["customers"]}
    start = rng.randrange(2)  # alternate the two edges, so a slice with 2+ orders in Y gets both
    moves = {o[0]: [date(y, 12, 31), date(y, 1, 1)][(i + start) % 2] for i, o in enumerate(_pick(rng, _f_orders(rows, f), 0.5))}
    other = [o for o in _f_orders(rows, {**f, "year": None}) if o[2][:4] != str(y)]
    moves.update({o[0]: edge_out for o in _pick(rng, other, 0.5)})
    old = {}
    for i, o in enumerate(rows["orders"]):
        new = moves.get(o[0])
        if new and new < signup[o[1]] and new.year == y:
            new = date(y, 12, 31)  # signed up after Jan 1 of Y
        if new and new >= signup[o[1]]:
            old[o[0]] = (date.fromisoformat(o[2]), new)
            rows["orders"][i] = (o[0], o[1], new.isoformat(), o[3])

    def shift(d, oid, pay):  # offset from the order date (a payment: 0, 1 or its own offset days), clipped to END
        od, new = old[oid]
        off = (date.fromisoformat(d) - od).days
        return min(db.END, new + timedelta(days=rng.choice([0, 1, max(1, off)]) if pay else off)).isoformat()
    for t, col in (("payments", 3), ("refunds", 3), ("invoice_adjustments", 4)):
        rows[t] = [r[:col] + (shift(r[col], r[1], t == "payments"),) + r[col + 1:] if r[1] in old else r
                   for r in rows[t]]
    return rows


def mutants(sql: str) -> dict:
    m = YEAR.search(sql)
    if not m:
        return {}
    y = int(m.group(3))
    sub = lambda rep: YEAR.sub(lambda g: rep(f"{g.group(1)}.{g.group(2)}", g.group(1)), sql)
    out = {"excl_end": sub(lambda c, a: f"{c} >= '{y}-01-01' AND {c} < '{y}-12-31'"),
           "excl_start": sub(lambda c, a: f"{c} > '{y}-01-01' AND {c} <= '{y}-12-31'"),
           "incl_next": sub(lambda c, a: f"{c} BETWEEN '{y}-01-01' AND '{y + 1}-01-01'"),
           "no_filter": sub(lambda c, a: "1 = 1")}
    if re.search(r"\borders o\b", sql) and re.search(r"\bpayments pay\b", sql):
        swap = {"o.order_date": "pay.paid_date", "pay.paid_date": "o.order_date"}
        out["col_swap"] = sub(lambda c, a: f"substr({swap.get(c, c)}, 1, 4) = '{y}'")
    return out


_rows, _copies = {}, {}


def base_rows(base_rel: str) -> dict:
    """Rows of a generated base DB: data/<split>/dbs/<size>_s<seed>/base.db (test bases are E4 sub-DBs)."""
    if base_rel not in _rows:
        split, _, tag, _ = base_rel.split("/")
        size, seed = tag.split("_s")
        if split == "test":  # same construction as cf.EvalBase
            parent = db.generate("M", int(seed))
            rng = random.Random(f"test|{seed}")
            rows = _closure(parent, set(rng.sample(sorted(c[0] for c in parent["customers"]), TEST_N)))
        else:
            rows = db.generate(size, int(seed))
        n = _exec(base_rel, "SELECT COUNT(*), SUM(customer_id) FROM orders")
        assert n == ((len(rows["orders"]), sum(o[1] for o in rows["orders"])),), (base_rel, "rows differ from base.db")
        _rows[base_rel] = rows
    return _rows[base_rel]


def period_copy(it) -> str:
    """Relative path of the item's period-edge copy (one per base DB and focus)."""
    base, focus = it["dbs"][0], {k: it["params"][k] for k in FOCUS_KEYS if k in it["params"]}
    key = (base, tuple(focus.get(k) for k in FOCUS_KEYS))
    if key not in _copies:
        name = "_".join("x" if v is None else str(v) for v in key[1])
        p = DATA / Path(base).parent / "period" / f"{name}.db"
        db.write(e_period_edges(_copy(base_rows(base)), random.Random(f"period|{key}"), focus), p)
        _copies[key] = str(p.relative_to(DATA))
    return _copies[key]


def passes(sql, dbs, gold, ordered) -> bool:
    return all(checks(sql, dbs, gold, ordered))


def audit():
    pay = defaultdict(lambda: defaultdict(list))  # setting -> mutant kind -> [paid]
    correct_rejected, n_correct, items = 0, 0, 0
    for it in map(json.loads, open(ROOT / "data/audit/items.jsonl")):
        if "year" not in it["params"] or not YEAR.search(it["gold_sql"]):
            continue
        items += 1
        pc = period_copy(it)
        g_pc = list(_exec(pc, it["gold_sql"]))
        for q in [it["gold_sql"]] + it["paraphrases"]:
            n_correct += 1
            correct_rejected += not passes(q, [pc], [g_pc], it["ordered"])
        for kind, q in mutants(it["gold_sql"]).items():
            for setting, dbs, gold in (("single_db", it["dbs"][:1], it["gold"][:1]),
                                       ("copies_random", it["dbs_random"], it["gold_random"]),
                                       ("copies_greedy", it["dbs"], it["gold"]),
                                       ("copies_random+period", it["dbs_random"] + [pc], it["gold_random"] + [g_pc]),
                                       ("period_only", it["dbs"][:1] + [pc], it["gold"][:1] + [g_pc])):
                p = passes(q, dbs, gold, it["ordered"])
                pay[setting][kind].append(p)
                pay[setting]["all_date_bugs" if kind != "no_filter" else "control"].append(p)
    rate = lambda v: {"n": len(v), "paid": sum(v) / len(v), "ci95": wilson(sum(v), len(v))}
    return {"items_with_year": items, "correct_queries": n_correct, "correct_rejected_by_period_copy": correct_rejected,
            "pay_rate": {s: {k: rate(v) for k, v in sorted(d.items())} for s, d in pay.items()}}


def replay(items_path, traj_paths):
    """Answers on year items that the verifier counts as verified (original + copies): share failing the period copy."""
    items = {it["id"]: it for it in map(json.loads, open(items_path)) if "year" in it["params"] and YEAR.search(it["gold_sql"])}
    out = {}
    for tp in traj_paths:
        v = fail = single = single_fail = 0
        for t in map(json.loads, open(tp)):
            it = items.get(t["id"])
            if it is None:
                continue
            g = grade(it, t["messages"])
            if not g["single"]:
                continue
            pc = period_copy(it)
            bad = not passes(final_sql(t["messages"]), [pc], [list(_exec(pc, it["gold_sql"]))], it["ordered"])
            single += 1; single_fail += bad
            if g["verified"]:
                v += 1; fail += bad
        out[Path(tp).stem.removeprefix("traj_")] = {"single_db_pass": single, "single_pass_fail_period": single_fail,
                                                   "verified": v, "verified_fail_period": fail,
                                                   "verified_fail_share": fail / v if v else None}
    return out


if __name__ == "__main__":
    # self-check: the edit keeps the rules (db.write raises otherwise) and moves a December order's payment into January
    r = e_period_edges(_copy(db.generate("S", 1)), random.Random(0), {"year": 2024})
    o = {x[0]: x[2] for x in r["orders"]}
    assert any(o[p[1]] == "2024-12-31" and p[3] >= "2025-01-01" for p in r["payments"])
    assert mutants("SELECT 1 FROM orders o WHERE substr(o.order_date, 1, 4) = '2024'")["excl_end"].endswith("< '2024-12-31'")
    res = {"what": "E12: period-edge copies for year-filtered questions (scripts/period_copies.py)",
           "audit": audit(),
           "rollouts_sft_ho_grpo": replay(ROOT / "data/train/grpo_items.jsonl", [ROOT / "runs/traj_sft_ho_grpoprompts.jsonl"]),
           "test_answers": replay(ROOT / "data/test/items.jsonl", sorted((ROOT / "results").glob("traj_*.jsonl")))}
    (ROOT / "results/e12_period_copies.json").write_text(json.dumps(res, indent=1))
    a = res["audit"]
    print("items", a["items_with_year"], "correct rejected", a["correct_rejected_by_period_copy"], "/", a["correct_queries"])
    for s, d in a["pay_rate"].items():
        print(f"{s:22}", {k: round(v["paid"], 3) for k, v in d.items()})
    print(json.dumps({"grpo": res["rollouts_sft_ho_grpo"], "test": res["test_answers"]}, indent=1))
