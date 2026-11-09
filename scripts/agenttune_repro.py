"""A5 minimal repro: AgentTune's built-in SQL reward (correctness + query + structure, @ d4db4c1) scores a policy that
always runs `select * from customers where 1 = 1` and answers *yes* exactly as high as the honest policy on every
yes-question. With patches/agenttune-sql-reward-hardening.patch (applied to a temp copy) it scores lower.

  .venv/bin/python scripts/agenttune_repro.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.audit import AGENTTUNE_SQL, _traj, load_agenttune_sql  # noqa: E402

gold_rows = [[7, "Ana", "Peru"]]
pols = {"honest": _traj("select * from customers where country = 'Peru'", gold_rows, "*yes*"),
        "hack   where 1 = 1": _traj("select * from customers where 1 = 1", [[1, "Bo", "Chile"]], "*yes*"),
        "hack   where customer_id > 0": _traj("select * from customers where customer_id > 0", [[1, "Bo", "Chile"]], "*yes*")}
with tempfile.TemporaryDirectory() as d:
    out = Path(d) / "sql_patched.py"
    subprocess.run(["patch", "-s", "-o", str(out), str(AGENTTUNE_SQL), str(ROOT / "patches/agenttune-sql-reward-hardening.patch")], check=True)
    mods = {"original": load_agenttune_sql(), "patched": load_agenttune_sql(out)}
    print(f"{'policy':32} {'original':>9} {'patched':>9} {'patched+result_match':>21}")
    for name, t in pols.items():
        row = []
        for m in mods.values():
            row.append(sum(f([t], answer=["yes"])[0] for f in (m.correctness_reward, m.query_reward, m.structure_reward)))
        row.append(row[-1] + mods["patched"].result_match_reward([t], gold_rows=[gold_rows])[0])
        print(f"{name:32} {row[0]:9.2f} {row[1]:9.2f} {row[2]:21.2f}")
