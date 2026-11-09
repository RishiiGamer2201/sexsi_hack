"""Manual audit sample (E4): 16 wrong test trajectories per model (sft_ho, B, C), seed 0, stratified:
6 lucky passes (original DB right, a counterfactual wrong) and 10 other wrong answers with SQL, spread over families.
Writes runs/audit_sample.md for reading; labels go in results/manual_audit.jsonl (NL2SQL-BUGs categories).

  .venv/bin/python scripts/audit_sample.py
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluate import grade  # noqa: E402
from sqlcf.rewards import final_sql  # noqa: E402

items = {json.loads(line)["id"]: json.loads(line) for line in open(ROOT / "data/test/items.jsonl")}
rng = random.Random(0)
picked = []
for m in ("sft_ho", "B", "C"):
    rows = [json.loads(line) for line in open(ROOT / f"results/traj_{m}.jsonl")]
    lucky, other = [], []
    for r in rows:
        g = grade(items[r["id"]], r["messages"])
        if g["verified"] or not g["has_sql"]:
            continue
        (lucky if g["single"] else other).append(r)
    for pool, k in ((lucky, 6), (other, 10)):
        by_fam = {}
        for r in pool:
            by_fam.setdefault(items[r["id"]]["family"], []).append(r)
        for f in by_fam.values():
            rng.shuffle(f)
        fams = sorted(by_fam)
        i = 0
        while sum(1 for p in picked if p[0] == m and p[2] == (pool is lucky)) < k and any(by_fam.values()):
            f = fams[i % len(fams)]
            if by_fam[f]:
                picked.append((m, by_fam[f].pop(), pool is lucky))
            i += 1
out = []
for n, (m, r, lucky) in enumerate(picked):
    it = items[r["id"]]
    sql = final_sql(r["messages"])
    out.append(f"## {n} · {m} · {'LUCKY' if lucky else 'wrong'} · {it['family']} {it['template']} · {r['id']} #{r['sample']}\n"
               f"Q: {it['question']}\nGOLD: {it['gold_sql']}\nSQL:  {sql}\nchecks: {grade(it, r['messages'])['cf_frac']:.2f}\n")
(ROOT / "runs/audit_sample.md").write_text("\n".join(out))
json.dump([{"n": n, "model": m, "id": r["id"], "sample": r["sample"], "lucky": lucky} for n, (m, r, lucky) in enumerate(picked)],
          open(ROOT / "runs/audit_sample.json", "w"))
print(len(picked), "sampled")
assert len(picked) == 48, len(picked)
