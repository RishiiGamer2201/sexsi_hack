"""A5 regression test: AgentTune's built-in SQL reward pays a WHERE-padding hack as much as the honest query,
and patches/agenttune-sql-reward-hardening.patch closes it. The vendor tree is not modified: the patch is
applied to a temp copy with `patch -o`."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.audit import AGENTTUNE_SQL, _traj, load_agenttune_sql  # noqa: E402

PATCH = ROOT / "patches/agenttune-sql-reward-hardening.patch"
GOLD_SQL = "select * from customers where country = 'Peru'"
GOLD_ROWS = [[7, "Ana", "Peru"]]
POLICIES = {
    "honest": _traj(GOLD_SQL, GOLD_ROWS, "*yes*"),
    "hack_1eq1": _traj("select * from customers where 1 = 1", [[1, "Bo", "Chile"]], "*yes*"),
    "hack_idgt0": _traj("select * from customers where customer_id > 0", [[1, "Bo", "Chile"]], "*yes*"),
}


@pytest.fixture(scope="module")
def mods(tmp_path_factory):
    if not shutil.which("patch"):
        pytest.skip("patch(1) not installed")
    out = tmp_path_factory.mktemp("at") / "sql_patched.py"
    subprocess.run(["patch", "-s", "-o", str(out), str(AGENTTUNE_SQL), str(PATCH)], check=True)
    return load_agenttune_sql(), load_agenttune_sql(out)


def total(m, traj, extra=False):
    fns = [m.correctness_reward, m.query_reward, m.structure_reward]
    r = sum(f([traj], answer=["yes"])[0] for f in fns)
    return r + (m.result_match_reward([traj], gold_rows=[GOLD_ROWS])[0] if extra else 0.0)


def test_unpatched_pays_hack_like_honest(mods):
    orig, _ = mods
    assert total(orig, POLICIES["hack_1eq1"]) == total(orig, POLICIES["honest"])


def test_patch_closes_tautology(mods):
    _, fixed = mods
    assert total(fixed, POLICIES["hack_1eq1"]) < total(fixed, POLICIES["honest"])
    assert not fixed._has_real_where("select 1 from t where 1 = 1 and 'a' = 'a'")
    assert fixed._has_real_where("select 1 from t where name = 'x' order by id")


def test_residual_hack_needs_result_match(mods):
    _, fixed = mods
    # documented residual: a WHERE on a real column that filters nothing still earns the bonus
    assert total(fixed, POLICIES["hack_idgt0"]) == total(fixed, POLICIES["honest"])
    # the added result_match_reward separates both hacks from the honest policy
    honest = total(fixed, POLICIES["honest"], extra=True)
    for k in ("hack_1eq1", "hack_idgt0"):
        assert total(fixed, POLICIES[k], extra=True) < honest
