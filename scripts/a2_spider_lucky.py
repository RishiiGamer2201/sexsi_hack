"""A2: lucky-pass rates of real text-to-SQL systems on a real benchmark (Spider dev, 1034 questions). CPU only.

Copies: the distilled test-suite databases of Zhong, Yu & Klein (EMNLP 2020; taoyds/test-suite-sql-eval, Apache-2.0,
Google Drive file 1mkCx2GOFIqNesD4y8TDAO1yX1QZORP5w), unzipped to external/testsuite_db/database/<db>/:
<db>.sqlite is the original Spider DB, every other .sqlite in the folder is a test-suite DB.
Predictions: public Spider-dev prediction files of 8 systems from the ESM+ repo (bossben/ESMp @ 91dd85b,
spider_dev/*.txt; one SQL per line, aligned with spider_dev/gold.txt "SQL<TAB>db_id").

Scoring uses our comparator (sqlcf.compare.match: multiset rows, column permutation allowed, ordered when the gold
has ORDER BY; read-only, 5 s timeout). Note the official script strips DISTINCT by default; we keep it, so our EX is
slightly stricter than published EX.
  EX     pred matches gold on the original DB
  TS     pred matches gold on the original DB and on every test-suite DB
  lucky  EX pass but TS fail;  lucky share = lucky / EX passes

  .venv/bin/python scripts/a2_spider_lucky.py  ->  results/a2_spider_lucky.json
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.audit import wilson  # noqa: E402
from sqlcf.compare import SQLError, match, run  # noqa: E402

DBROOT = ROOT / "external/testsuite_db/database"
PRED = ROOT / "external/ESMp/spider_dev"
SYSTEMS = ["C3", "Claude", "DAIL", "DIN", "GPT4Turbo", "Graphix", "RASAT+PICARD", "RESDSQL"]


def _rows(db, sql):
    try:
        return run(str(db), sql)
    except SQLError:
        return None


def score(task):
    pred, gold, db_id = task
    folder = DBROOT / db_id
    orig = folder / f"{db_id}.sqlite"
    ordered = "order by" in gold.lower()
    g = _rows(orig, gold)
    p = _rows(orig, pred) if pred.strip() else None
    ex = g is not None and p is not None and match(p, g, ordered)
    if not ex:
        return ex, False, None
    for db in sorted(folder.glob("*.sqlite")):
        if db == orig:
            continue
        g2, p2 = _rows(db, gold), _rows(db, pred)
        if g2 is None:          # gold itself fails on this suite DB: skip it, as the official script would error
            continue
        if p2 is None or not match(p2, g2, ordered):
            return True, False, db.name
    return True, True, None


if __name__ == "__main__":
    gold = [line.rstrip("\n").split("\t") for line in open(PRED / "gold.txt")]
    out = {"n_questions": len(gold), "suite_dbs_per_db": {}, "systems": {}}
    for d in sorted({db for _, db in gold}):
        out["suite_dbs_per_db"][d] = len(list((DBROOT / d).glob("*.sqlite"))) - 1
    with Pool(16) as pool:
        for s in SYSTEMS:
            preds = [line.rstrip("\n") for line in open(PRED / f"{s}.txt")]
            assert len(preds) == len(gold), s
            res = pool.map(score, [(p, g, d) for p, (g, d) in zip(preds, gold)], chunksize=8)
            n = len(res)
            ex = sum(r[0] for r in res)
            ts = sum(r[1] for r in res)
            lucky = ex - ts
            out["systems"][s] = {"EX": ex / n, "TS": ts / n, "lucky": lucky, "EX_pass": ex,
                                 "lucky_share_of_EX_ci95": wilson(lucky, ex),
                                 # indices only: ESMp ships no licence, so its SQL text is not redistributed here
                                 "lucky_cases": [{"q": i, "db": gold[i][1], "failed_on": r[2]}
                                                 for i, r in enumerate(res) if r[0] and not r[1]]}
            v = out["systems"][s]
            print(f"{s:13} EX {v['EX']:.3f}  TS {v['TS']:.3f}  lucky {lucky}/{ex} = "
                  f"{v['lucky_share_of_EX_ci95'][0]:.3f} [{v['lucky_share_of_EX_ci95'][1]:.3f}, {v['lucky_share_of_EX_ci95'][2]:.3f}]", flush=True)
    (ROOT / "results/a2_spider_lucky.json").write_text(json.dumps(out, indent=1))
