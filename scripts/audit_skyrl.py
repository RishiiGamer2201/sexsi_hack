"""A3: audit a second open RL reward (SkyRL-SQL) with the E0 gold-mutants and hacks.

SkyRL's `compute_score_single` (NovaSky-AI/SkyRL @ d870046, skyrl-gym/skyrl_gym/envs/sql/utils.py, Apache-2.0)
executes the predicted and the reference SQL once on ONE database and pays 1.0 if the two `frozenset`s of
rows are equal (order- and duplicate-blind). We score every E0 candidate four ways:

  skyrl_single   SkyRL as shipped (original DB)
  skyrl_cf_min   SkyRL's comparator, but required to pass on the original + the blind-chosen counterfactual copies
  rex_single     our strict comparator (multiset; ordered if gold is ordered), original DB only   (= R_exec_rex)
  rex_cf_min     strict comparator on original + copies                                            (= R_cf_strict@random)

skyrl_single - skyrl_cf_min is the database hole (closed by copies); skyrl_cf_min - rex_cf_min is the comparator
hole (wrong answers that set comparison pays on every database).

  .venv/bin/python scripts/audit_skyrl.py  ->  results/a3_skyrl_audit.json   (CPU, no SkyRL install needed)
"""
import json
import sqlite3
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.audit import hacks, wilson  # noqa: E402
from sqlcf.rewards import DATA, R_cf_strict, R_exec_rex  # noqa: E402


# Transcribed from SkyRL @ d870046 skyrl-gym/skyrl_gym/envs/sql/utils.py (Apache-2.0, NovaSky-AI): the outcome part
# of calculate_reward_single. Execute pred and reference on the same DB, rows -> frozenset, pay 1.0 iff equal and
# both ran. (Their format check and thread timeout are left out: our candidates are well-formed and fast.)
@lru_cache(maxsize=None)
def _sky_rows(db_file, sql):
    try:
        con = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
        try:
            return frozenset(con.execute(sql).fetchall())
        finally:
            con.close()
    except Exception:
        return None


class sky:  # noqa: N801  (same call shape as SkyRL's module)
    @staticmethod
    def compute_score_single(sql, reference, db_file):
        p, g = _sky_rows(db_file, sql), _sky_rows(db_file, reference)
        return 1.0 if p is not None and g is not None and p == g else 0.0


def sky_text(sql):
    return sql


def ours(sql):
    return [{"role": "assistant", "content": f"```sql\n{sql}\n```"}]


items = [json.loads(line) for line in open(ROOT / "data/audit/items.jsonl")]
stats = defaultdict(lambda: [0, 0])        # (reward, group) -> [paid, n]
hole = defaultdict(lambda: [0, 0, 0])      # mutant -> [paid by skyrl_cf_min, ... and rejected by rex_cf_min, n]
examples = {}
for it in items:
    cands = [("correct", q) for q in [it["gold_sql"], *it["paraphrases"]]]
    cands += [(f"mutant:{m}", q) for m, q in it["mutants"].items()]
    cands += [(f"hack:{h}", q) for h, q in hacks(it).items()]
    n = len(cands)
    rex1 = R_exec_rex([ours(q) for _, q in cands], dbs=[it["dbs"]] * n, gold=[it["gold"]] * n, ordered=[it["ordered"]] * n)
    rexcf = R_cf_strict([ours(q) for _, q in cands], dbs=[it["dbs_random"]] * n, gold=[it["gold_random"]] * n,
                        ordered=[it["ordered"]] * n)
    for (kind, q), r1, rc in zip(cands, rex1, rexcf):
        s1 = sky.compute_score_single(sky_text(q), it["gold_sql"], str(DATA / it["dbs"][0]))
        scf = min([s1] + [sky.compute_score_single(sky_text(q), it["gold_sql"], str(DATA / d)) for d in it["dbs_random"][1:]])
        group = kind.split(":")[0]
        for rname, v in (("skyrl_single", s1), ("skyrl_cf_min", scf), ("rex_single", r1), ("rex_cf_min", rc)):
            for key in {(rname, group), (rname, kind)}:
                stats[key][0] += v >= 1.0
                stats[key][1] += 1
        if group == "mutant":
            m = kind.split(":")[1]
            hole[m][2] += 1
            if scf >= 1.0:
                hole[m][0] += 1
                if rc < 1.0:
                    hole[m][1] += 1
                    examples.setdefault(m, {"item": it["id"], "gold": it["gold_sql"], "mutant": q})

rows = []
for (r, g), (k, n) in sorted(stats.items()):
    wrong = g not in ("correct",)
    p, lo, hi = wilson(k if wrong else n - k, n)
    rows.append({"reward": r, "candidates": g, "n": n, "metric": "FP (wrong SQL paid)" if wrong else "FN (correct SQL not paid)",
                 "rate": p, "ci95": [lo, hi]})
out = {"skyrl_commit": "d870046", "n_items": len(items), "rows": rows,
       "comparator_hole_by_mutant": {m: {"paid_on_every_db_by_set_compare": a, "of_which_rejected_by_strict": b, "n": c}
                                     for m, (a, b, c) in sorted(hole.items())},
       "comparator_hole_examples": examples}
(ROOT / "results/a3_skyrl_audit.json").write_text(json.dumps(out, indent=1))
for row in rows:
    if row["candidates"] in ("correct", "mutant", "hack"):
        print(f"{row['reward']:13} {row['candidates']:8} {row['metric'][:2]} {row['rate']:.3f} "
              f"[{row['ci95'][0]:.3f}, {row['ci95'][1]:.3f}] n={row['n']}")
print("comparator hole (paid by set compare on every DB, rejected by strict):")
for m, v in out["comparator_hole_by_mutant"].items():
    if v["of_which_rejected_by_strict"]:
        print(f"  {m:20} {v['of_which_rejected_by_strict']}/{v['n']}")
