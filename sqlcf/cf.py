"""Counterfactual databases and item building.

Train/audit counterfactuals = one family-targeted rule edit per DB, *focused* on the
item's slice (its city / year / category params), so the edit actually touches the rows
the question reads. Pools are built lazily per (base DB, focus) and cached. Every edit
keeps the business rules (db.write re-checks them). Per item we classify each pool DB as
answer-preserving / answer-changing for the gold SQL and greedily pick <= k_max that
(a) include one of each kind and (b) kill as many bug mutants as possible.

Test DBs (plan E4, --test) use a different generator: FK-closed sub-DB of a size-M parent plus
generic, family-blind mutations (TEST_OPS); all of them grade every item.

Usage: python -m sqlcf.cf --name audit --split all --seeds 301 302 --size S
       python -m sqlcf.cf --name test --split test --seeds 501 502 --size S --test
"""
import argparse
import json
import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from . import db
from .compare import SQLError, match, normalize, run
from .templates import TEMPLATES

DATA = Path(__file__).resolve().parent.parent / "data"
FOCUS_KEYS = ("city", "year", "category")


def _copy(rows):
    return {t: list(v) for t, v in rows.items()}


def _pick(rng, xs, frac):
    xs = list(xs)
    return rng.sample(xs, max(1, round(len(xs) * frac))) if xs else []


def _f_customers(rows, f):
    return [c for c in rows["customers"] if f.get("city") in (None, c[2])]


def _f_orders(rows, f, status=None):
    cust = {c[0] for c in _f_customers(rows, f)}
    y = f.get("year")
    return [o for o in rows["orders"] if o[1] in cust and (y is None or o[2][:4] == str(y))
            and status in (None, o[3])]


def _f_ordering_customers(rows, f):
    have = {o[1] for o in rows["orders"]}
    return [c for c in _f_customers(rows, f) if c[0] in have]


def _must(rows, rng, f):
    cat = f.get("category")
    return rng.choice([p for p in rows["products"] if p[2] == cat]) if cat else None


# ---------------- edits: (rows, rng, focus) -> rows; all keep business rules ----------------
def e_dup_order(rows, rng, f):
    """Extra active order for customers who already ordered (count-distinct customers unchanged)."""
    ids = db.next_ids(rows)
    for c in _pick(rng, _f_ordering_customers(rows, f), 0.5):
        db.add_order(rows, rng, c[0], c[3], rng.choice(["shipped", "placed"]), rows["products"], ids, f.get("year"), _must(rows, rng, f))
    return rows


def e_new_customers(rows, rng, f):
    """Brand-new customers in the slice, with orders (changes most aggregates)."""
    ids = db.next_ids(rows)
    for _ in range(max(2, len(_f_customers(rows, f)) // 3)):
        c = db.add_customer(rows, rng, ids, city=f.get("city"))
        for _ in range(rng.randint(1, 3)):
            db.add_order(rows, rng, c[0], c[3], rng.choice(["shipped", "shipped", "placed", "cancelled"]),
                         rows["products"], ids, f.get("year"), _must(rows, rng, f))
    return rows


def e_zero_order_customers(rows, rng, f):
    ids = db.next_ids(rows)
    for _ in range(max(2, len(_f_customers(rows, f)) // 3)):
        db.add_customer(rows, rng, ids, city=f.get("city"))
    return rows


def e_cancelled_orders(rows, rng, f):
    """Cancelled orders for customers who already ordered (active-only answers unchanged)."""
    ids = db.next_ids(rows)
    for c in _pick(rng, _f_ordering_customers(rows, f), 0.5):
        db.add_order(rows, rng, c[0], c[3], "cancelled", rows["products"], ids, f.get("year"), _must(rows, rng, f))
    return rows


def _tiers_by_customer(rows, f):
    keep = {c[0] for c in _f_customers(rows, f)}
    out = {}
    for r in rows["tier_history"]:
        if r[1] in keep:
            out.setdefault(r[1], []).append(r)
    return sorted((k, sorted(v, key=lambda r: r[3])) for k, v in out.items())


def e_later_tier(rows, rng, f):
    """New, later tier row (changes current tier)."""
    tid = db.next_ids(rows)["tier_history"]
    for cid, hist in _pick(rng, _tiers_by_customer(rows, f), 0.5):
        last = date.fromisoformat(hist[-1][3])
        if last >= db.END - timedelta(days=2):
            continue
        tid += 1
        when = db._rand_date(rng, last + timedelta(days=1), db.END)
        rows["tier_history"].append((tid, cid, rng.choice([t for t in db.TIERS if t != hist[-1][2]]), when.isoformat()))
    return rows


def e_superseded_tier(rows, rng, f):
    """Extra historical tier row strictly between the first two rows (current tier unchanged)."""
    tid = db.next_ids(rows)["tier_history"]
    for cid, hist in _pick(rng, [(c, h) for c, h in _tiers_by_customer(rows, f) if len(h) >= 2], 0.7):
        a, b = date.fromisoformat(hist[0][3]), date.fromisoformat(hist[1][3])
        if (b - a).days < 2:
            continue
        tid += 1
        rows["tier_history"].append((tid, cid, rng.choice(db.TIERS), db._rand_date(rng, a + timedelta(days=1), b - timedelta(days=1)).isoformat()))
    return rows


def _balance(rows):
    out = {}
    for p in rows["payments"]:
        out[p[1]] = out.get(p[1], 0) + p[2]
    for r in rows["refunds"]:
        out[r[1]] = out.get(r[1], 0) - r[2]
    return out


def e_refunds(rows, rng, f):
    """Refunds on shipped orders with refundable balance (gross unchanged)."""
    rid = db.next_ids(rows)["refunds"]
    left = _balance(rows)
    for o in _pick(rng, [o for o in _f_orders(rows, f, "shipped") if left.get(o[0], 0) >= 1], 0.4):
        rid += 1
        rows["refunds"].append((rid, o[0], rng.randint(1, left[o[0]]), db._rand_date(rng, date.fromisoformat(o[2]), db.END).isoformat()))
    return rows


def e_split_payments(rows, rng, f):
    """Split payments into two installments (all totals unchanged; join fan-out changes)."""
    target = {o[0] for o in _f_orders(rows, f, "shipped")}
    pid = db.next_ids(rows)["payments"]
    out = []
    for p in rows["payments"]:
        if p[1] in target and p[2] >= 2 and rng.random() < 0.6:
            a = rng.randint(1, p[2] - 1)
            pid += 1
            out += [(p[0], p[1], a, p[3]), (pid, p[1], p[2] - a, p[3])]
        else:
            out.append(p)
    rows["payments"] = out
    return rows


def e_split_items(rows, rng, f):
    """Split item lines (qty >= 2) into two lines; value/units unchanged, line counts change."""
    target = {o[0] for o in _f_orders(rows, f)}
    cat = f.get("category")
    pcat = {p[0]: p[2] for p in rows["products"]}
    iid = db.next_ids(rows)["order_items"]
    out = []
    for i in rows["order_items"]:
        if i[1] in target and i[3] >= 2 and cat in (None, pcat[i[2]]) and rng.random() < 0.7:
            iid += 1
            out += [(i[0], i[1], i[2], 1, i[4]), (iid, i[1], i[2], i[3] - 1, i[4])]
        else:
            out.append(i)
    rows["order_items"] = out
    return rows


def e_adjustments(rows, rng, f):
    """Positive invoice correction + matching payment on shipped orders (gross unchanged)."""
    ids = db.next_ids(rows)
    for o in _pick(rng, _f_orders(rows, f, "shipped"), 0.4):
        amt = rng.randint(10, 300)
        ids["invoice_adjustments"] += 1
        ids["payments"] += 1
        rows["invoice_adjustments"].append((ids["invoice_adjustments"], o[0], amt, "correction", o[2]))
        rows["payments"].append((ids["payments"], o[0], amt, o[2]))
    return rows


def e_drop_customers(rows, rng, f):
    """Delete 30% of the slice's customers with their FK closure (changes most aggregates)."""
    gone = {c[0] for c in _pick(rng, _f_customers(rows, f), 0.3)}
    return _closure(rows, {c[0] for c in rows["customers"]} - gone)


def _closure(rows, keep):
    """FK-closed sub-DB: customers in `keep` and everything that hangs off them (all products)."""
    out = {"products": list(rows["products"])}
    out["customers"] = [c for c in rows["customers"] if c[0] in keep]
    out["tier_history"] = [t for t in rows["tier_history"] if t[1] in keep]
    out["orders"] = [o for o in rows["orders"] if o[1] in keep]
    keep_o = {o[0] for o in out["orders"]}
    for t in ("order_items", "payments", "refunds", "invoice_adjustments"):
        out[t] = [r for r in rows[t] if r[1] in keep_o]
    return out


EDITS = {f.__name__[2:]: f for f in [
    e_dup_order, e_new_customers, e_zero_order_customers, e_cancelled_orders, e_later_tier,
    e_superseded_tier, e_refunds, e_split_payments, e_split_items, e_adjustments, e_drop_customers]}


# ---------------- item building ----------------
def load_tables(path) -> dict:
    con = sqlite3.connect(path)
    try:
        return {t: pd.read_sql(f"SELECT * FROM {t}", con) for t in db.TABLES}
    finally:
        con.close()


def degenerate(res) -> bool:
    """Empty, all-NULL, or a single 0/NULL scalar: too weak to grade."""
    res = normalize(res)
    return (not res or all(v is None for r in res for v in r)
            or (len(res) == 1 and len(res[0]) == 1 and res[0][0] in (0, None)))


def _safe_run(path, sql):
    try:
        return run(path, sql)
    except SQLError as e:
        return {"error": str(e)}


def _passes(res, gold, ordered):
    return not isinstance(res, dict) and match(res, gold, ordered)


class Base:
    """One generated base DB + lazily built focused CF pools (cached on disk and in memory)."""

    def __init__(self, root: Path, size: str, seed: int):
        self.dir, self.seed = root / "dbs" / f"{size}_s{seed}", seed
        self.rows = db.generate(size, seed)
        self.base = db.write(self.rows, self.dir / "base.db")
        self.shuf = db.write(self.rows, self.dir / "shuf.db", insert_seed=seed + 1)
        self.pools, self.frames = {}, {self.base: load_tables(self.base)}

    def pool(self, focus: dict) -> dict:
        key = tuple(focus.get(k) for k in FOCUS_KEYS)
        if key not in self.pools:
            sub = self.dir / ("f_" + "_".join(str(k) if k is not None else "x" for k in key))
            paths = {}
            for j, (name, f) in enumerate(EDITS.items()):
                rng = random.Random(f"{self.seed}|{key}|{j}")
                paths[name] = p = db.write(f(_copy(self.rows), rng, focus), sub / f"cf_{name}.db")
                self.frames[p] = load_tables(p)
            self.pools[key] = paths
        return self.pools[key]


# ---------------- test DBs (plan E4): a different generator from the training edits ----------------
# Base = FK-closed random sub-DB (TEST_N customers) of a size-M parent; CFs = generic mutations that
# know nothing about the bug families or the item's slice. Every test CF is used (no selection).
TEST_N = 50


def t_resample(rows, parent, rng):
    """Another sub-DB of the same parent sharing half the customers."""
    mine = sorted(c[0] for c in rows["customers"])
    rest = sorted({c[0] for c in parent["customers"]} - set(mine))
    return _closure(parent, set(rng.sample(mine, len(mine) // 2)) | set(rng.sample(rest, len(mine) - len(mine) // 2)))


def t_clone(rows, parent, rng):
    """Copy 25% of customers with their whole subgraph under new ids."""
    ids = db.next_ids(rows)

    def nid(t):
        ids[t] += 1
        return ids[t]
    for c in _pick(rng, rows["customers"], 0.25):
        cid = nid("customers")
        rows["customers"].append((cid,) + c[1:])
        rows["tier_history"] += [(nid("tier_history"), cid) + t[2:] for t in rows["tier_history"] if t[1] == c[0]]
        for o in [o for o in rows["orders"] if o[1] == c[0]]:
            oid = nid("orders")
            rows["orders"].append((oid, cid) + o[2:])
            for t in ("order_items", "payments", "refunds", "invoice_adjustments"):
                rows[t] += [(nid(t), oid) + r[2:] for r in rows[t] if r[1] == o[0]]
    return rows


def t_flip_status(rows, parent, rng):
    """Swap placed <-> cancelled on 40% of unpaid orders (neither has payments)."""
    flip = {o[0] for o in _pick(rng, [o for o in rows["orders"] if o[3] != "shipped"], 0.4)}
    rows["orders"] = [o[:3] + ({"placed": "cancelled", "cancelled": "placed"}[o[3]],) if o[0] in flip else o
                      for o in rows["orders"]]
    return rows


def t_relabel_tier(rows, parent, rng):
    """Change the tier label of 30% of tier rows (dates untouched)."""
    pick = {t[0] for t in _pick(rng, rows["tier_history"], 0.3)}
    rows["tier_history"] = [t[:2] + (rng.choice([x for x in db.TIERS if x != t[2]]),) + t[3:] if t[0] in pick else t
                            for t in rows["tier_history"]]
    return rows


TEST_OPS = {f.__name__[2:]: f for f in [t_resample, t_clone, t_flip_status, t_relabel_tier]}


class EvalBase(Base):
    def __init__(self, root: Path, size: str, seed: int):
        self.dir, self.seed = root / "dbs" / f"{size}_s{seed}", seed
        parent = db.generate("M", seed)
        rng = random.Random(f"test|{seed}")
        self.rows = _closure(parent, set(rng.sample(sorted(c[0] for c in parent["customers"]), TEST_N)))
        self.base = db.write(self.rows, self.dir / "base.db")
        self.shuf = db.write(self.rows, self.dir / "shuf.db", insert_seed=seed + 1)
        self.frames = {self.base: load_tables(self.base)}
        self.pools = {}
        for name, op in TEST_OPS.items():
            p = db.write(op(_copy(self.rows), parent, random.Random(f"test|{seed}|{name}")), self.dir / f"t_{name}.db")
            self.frames[p] = load_tables(p)
            self.pools[name] = p

    def pool(self, focus: dict) -> dict:
        return self.pools


def build_items(name: str, split: str, seeds: list[int], size: str, k_max: int = 3, test: bool = False) -> Path:
    root = DATA / name
    items, drops, errors = [], {}, []
    tmpls = [t for t in TEMPLATES if split == "all" or t.split == split]

    def drop(why):
        drops[why] = drops.get(why, 0) + 1

    for seed in seeds:
        B = (EvalBase if test else Base)(root, size, seed)
        for t in tmpls:
            for prm in t.grid():
                iid = f"{t.id}|{'|'.join(map(str, prm.values()))}|{size}_s{seed}"
                f = lambda s: s.format(**prm)
                gold_sql = f(t.sql)
                gold0 = run(B.base, gold_sql)
                if degenerate(gold0):
                    drop("degenerate")
                    continue
                pool = B.pool({k: prm[k] for k in FOCUS_KEYS if k in prm})
                paths = {"base": B.base, **pool}
                res = {k: run(p, gold_sql) for k, p in paths.items()}
                # gold == pandas and paraphrases == gold on every DB
                for k, p in paths.items():
                    if not match(t.pandas(B.frames[p], prm), res[k], t.ordered):
                        errors.append({"item": iid, "db": k, "what": "pandas!=gold",
                                       "pandas": normalize(t.pandas(B.frames[p], prm))[:5], "gold": normalize(res[k])[:5]})
                    for q in t.paraphrases:
                        if not _passes(_safe_run(p, f(q)), res[k], t.ordered):
                            errors.append({"item": iid, "db": k, "what": "paraphrase!=gold", "sql": f(q)})
                # determinism under shuffled insert order (ties, unordered LIMIT)
                if any(not _passes(_safe_run(B.shuf, f(q)), gold0, t.ordered)
                       for q in [t.sql] + t.paraphrases + t.nondeterministic_paraphrases):
                    drop("nondeterministic")
                    continue
                kind = {k: "preserving" if match(res[k], gold0, t.ordered) else "changing" for k in pool}
                if not test and len(set(kind.values())) < 2:
                    drop("no_preserving_or_changing_cf")
                    continue
                mut = {m: {k: _passes(_safe_run(p, f(q)), res[k], t.ordered) for k, p in paths.items()}
                       for m, q in t.mutants.items()}
                if test:  # every test CF, chosen blind to the mutants
                    chosen = rand = list(pool)
                else:
                    chosen = _select(list(pool), kind, mut, k_max, random.Random(iid))
                    # mutant-blind selection (one random CF of each kind): unbiased audit of FP on mutants
                    rr = random.Random(iid + "|random")
                    rand = [rr.choice(sorted(k for k in pool if kind[k] == want)) for want in ("changing", "preserving")]
                items.append({
                    "id": iid, "template": t.id, "family": t.family, "split": t.split, "params": prm,
                    "question": f(random.Random(iid).choice(t.questions)), "gold_sql": gold_sql, "ordered": t.ordered,
                    "dbs": [str(paths[k].relative_to(DATA)) for k in ["base"] + chosen],
                    "cf_edits": chosen, "cf_kinds": [kind[k] for k in chosen],
                    "gold": [normalize(res[k]) for k in ["base"] + chosen],
                    "dbs_random": [str(paths[k].relative_to(DATA)) for k in ["base"] + rand],
                    "gold_random": [normalize(res[k]) for k in ["base"] + rand],
                    "paraphrases": [f(q) for q in t.paraphrases],
                    "mutants": {m: f(q) for m, q in t.mutants.items()},
                    "mutant_blind": {m: v["base"] for m, v in mut.items()},
                    "mutant_caught": {m: (not v["base"]) or any(not v[k] for k in chosen) for m, v in mut.items()},
                    "mutant_catchable": {m: any(not x for x in v.values()) for m, v in mut.items()},
                })
    keep = {DATA / d for x in items for d in x["dbs"] + x["dbs_random"]}
    for p in (root / "dbs").rglob("cf_*.db"):  # unreferenced pool DBs: not needed by rewards
        if p not in keep:
            p.unlink()
    out = root / "items.jsonl"
    out.write_text("".join(json.dumps(x) + "\n" for x in items))
    (root / "build_report.json").write_text(json.dumps({"items": len(items), "drops": drops, "errors": errors[:200], "n_errors": len(errors)}, indent=1))
    print(f"{name}: {len(items)} items, drops={drops}, errors={len(errors)}", file=sys.stderr)
    return out


def _select(pool, kind, mut, k_max, rng):
    """Greedy: best changing CF, best preserving CF, then add CFs while they kill more mutants."""
    def kills(k):
        return {m for m, v in mut.items() if v["base"] and not v[k]}
    chosen, killed = [], set()
    for need in ("changing", "preserving", None, None, None):
        if len(chosen) >= k_max:
            break
        cands = [k for k in pool if k not in chosen and (need is None or kind[k] == need)]
        rng.shuffle(cands)
        best = max(cands, key=lambda k: len(kills(k) - killed), default=None)
        if best is None or (need is None and not kills(best) - killed):
            continue
        chosen.append(best)
        killed |= kills(best)
    return chosen


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--split", default="all", choices=["train", "test", "all"])
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--size", default="M", choices=list(db.SIZES))
    ap.add_argument("--k-max", type=int, default=3)
    ap.add_argument("--test", action="store_true", help="E4 test generator (sub-DB + generic mutations)")
    a = ap.parse_args()
    build_items(a.name, a.split, a.seeds, a.size, a.k_max, a.test)
