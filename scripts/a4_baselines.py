"""A4 (symposium plan): CPU baselines a reviewer will ask for. Writes results/a4_baselines.json.

  (1) compute-matched single DB: the E1 blind rate (share of bug mutants a single DB cannot tell from gold) at
      150 customers = the rows of the 50-customer original plus its 2 training copies, next to E1's 50/500/5,000.
      Hacks need no run: literal answers and hard-coded IDs are read off the DB the agent explores, so a single
      visible DB pays them at any size (E0: 1,302/1,302 literals, 235/235 ID lists), while hidden copies do not.
  (2) held-out F4: F4 audit items rebuilt on the audit seeds with the F4-targeted edits (later_tier,
      superseded_tier, adjustments) removed from the copy pool, so no copy was designed for this family.
  (3) family-blind copies: audit items whose copies are only the generic TEST_OPS mutations (resample, clone,
      status flip, tier relabel; the test-set generator), all grading every item: "do your copies encode your bugs?"

  .venv-train/bin/python scripts/a4_baselines.py      # minutes of CPU; builds data/a4_* (gitignored)
"""
import json
import random
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf import cf, db  # noqa: E402
from sqlcf.audit import hacks, wilson  # noqa: E402
from sqlcf.compare import SQLError, match, run  # noqa: E402
from sqlcf.rewards import checks  # noqa: E402
from sqlcf.templates import TEMPLATES  # noqa: E402

AUDIT_SEEDS, E1_SEEDS = [301, 302, 303, 304, 305], [900, 901, 902]
F4_EDITS = ("later_tier", "superseded_tier", "adjustments")


def blind_rate(customers: int):
    """E1's blind-rate count at an arbitrary DB size (same seeds and templates as sqlcf.audit.e1)."""
    db.SIZES[f"n{customers}"] = customers
    tmp = Path(tempfile.mkdtemp(dir=ROOT / "data"))
    k = n = 0
    try:
        for seed in E1_SEEDS:
            p = db.write(db.generate(f"n{customers}", seed), tmp / f"{seed}.db")
            for t in TEMPLATES:
                for prm in t.grid():
                    g = run(p, t.sql.format(**prm))
                    if cf.degenerate(g):
                        continue
                    for q in t.mutants.values():
                        try:
                            k += match(run(p, q.format(**prm)), g, t.ordered)
                        except SQLError:
                            pass
                        n += 1
    finally:
        shutil.rmtree(tmp)
    return {"customers": customers, "blind": k, "n": n, "rate_ci95": [round(x, 4) for x in wilson(k, n)]}


def score(items_path: Path, selections=("dbs", "dbs_random")):
    """Full-pay rates per candidate group under single-DB and strict-CF grading of each copy selection."""
    stats = defaultdict(lambda: [0, 0])
    for it in (json.loads(l) for l in open(items_path)):
        cands = [("correct", it["gold_sql"])] + [("correct", q) for q in it["paraphrases"]]
        cands += [("mutant", q) for q in it["mutants"].values()] + [("hack", q) for q in hacks(it).values()]
        for sel in selections:
            gold = it["gold" if sel == "dbs" else "gold_random"]
            for group, sql in cands:
                v = checks(sql, it[sel], gold, it["ordered"])
                for fam in (it["family"], "ALL"):
                    for rew, paid in (("single_db", v[0]), (f"cf_strict@{sel}", all(v))):
                        if rew == "single_db" and sel != selections[0]:
                            continue
                        st = stats[(fam, group, rew)]
                        st[0] += paid
                        st[1] += 1
    out = defaultdict(dict)
    for (fam, group, rew), (k, n) in sorted(stats.items()):
        if group == "correct":  # report the false-negative side for correct SQL
            k = n - k
        out[f"{fam}/{group}"][rew] = {"rate": round(k / n, 4), "ci95": [round(x, 4) for x in wilson(k, n)[1:]], "n": n}
    return dict(out)


def heldout_f4():
    edits, tmpls = dict(cf.EDITS), list(cf.TEMPLATES)
    try:
        cf.EDITS = {k: v for k, v in edits.items() if k not in F4_EDITS}
        cf.TEMPLATES = [t for t in tmpls if t.family == "F4"]
        shutil.rmtree(cf.DATA / "a4_heldout_f4", ignore_errors=True)
        path = cf.build_items("a4_heldout_f4", "all", AUDIT_SEEDS, "S")
    finally:
        cf.EDITS, cf.TEMPLATES = edits, tmpls
    rep = json.load(open(path.parent / "build_report.json"))
    return {"pool_edits": sorted(set(edits) - set(F4_EDITS)), "build": {"items": rep["items"], "drops": rep["drops"]},
            "pay": score(path)}


def family_blind():
    shutil.rmtree(cf.DATA / "a4_testops", ignore_errors=True)
    path = cf.build_items("a4_testops", "all", AUDIT_SEEDS, "S", test=True)
    rep = json.load(open(path.parent / "build_report.json"))
    return {"copies": sorted(cf.TEST_OPS), "build": {"items": rep["items"], "drops": rep["drops"]},
            "pay": score(path, selections=("dbs",))}


def main():
    out = {"compute_matched_single_db": {
        "note": "150 customers = 50-customer original + 2 copies; E1 rows for 50/500/5,000 are in e1_blind_rate.json",
        "row": blind_rate(150)}}
    print("compute-matched:", out["compute_matched_single_db"]["row"])
    out["heldout_f4"] = heldout_f4()
    print("held-out F4:", json.dumps(out["heldout_f4"]["pay"].get("F4/mutant")), json.dumps(out["heldout_f4"]["pay"].get("F4/hack")))
    out["family_blind_testops"] = family_blind()
    for k in ("ALL/mutant", "ALL/hack", "ALL/correct"):
        print("TEST_OPS", k, json.dumps(out["family_blind_testops"]["pay"].get(k)))
    (ROOT / "results/a4_baselines.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    random.seed(0)
    main()
