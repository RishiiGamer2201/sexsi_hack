"""gold=1, paraphrase=1, caught mutant=0 under CF, literal smuggling=0 under CF,
malformed / missing SQL = 0, writes impossible."""
import json
import shutil

import pytest

from sqlcf import cf
from sqlcf.audit import literal_sql
from sqlcf.compare import SQLError, run
from sqlcf.rewards import DATA, REWARDS, R_cf_mean, R_cf_strict, R_exec_rex, final_sql


@pytest.fixture(scope="module")
def items():
    path = cf.build_items("_pytest", "all", [4242], "S")
    yield [json.loads(l) for l in open(path)]
    shutil.rmtree(DATA / "_pytest")


def comp(sql):
    return [{"role": "user", "content": "q"},
            {"role": "assistant", "content": "<think>```sql\nSELECT 1\n```</think>Answer:\n```sql\n" + sql + "\n```"}]


def cols(it, n):
    return {k: [it[k]] * n for k in ("dbs", "gold", "ordered")}


def test_items_exist_for_every_family(items):
    assert {it["family"] for it in items} == {"F1", "F2", "F3", "F4"}
    assert all("preserving" in it["cf_kinds"] and "changing" in it["cf_kinds"] for it in items)


def test_gold_and_paraphrases_fully_paid(items):
    for it in items:
        qs = [it["gold_sql"]] + it["paraphrases"]
        for name, f in REWARDS.items():
            assert f([comp(q) for q in qs], **cols(it, len(qs))) == [1.0] * len(qs), (name, it["id"])


def test_caught_blind_mutants_pass_single_db_but_fail_cf(items):
    n = 0
    for it in items:
        for m, q in it["mutants"].items():
            if it["mutant_blind"][m] and it["mutant_caught"][m]:
                n += 1
                assert R_exec_rex([comp(q)], **cols(it, 1)) == [1.0]
                assert R_cf_strict([comp(q)], **cols(it, 1)) == [0.0]
                assert R_cf_mean([comp(q)], **cols(it, 1))[0] < 1.0
    assert n > 0, "no blind mutant at size S: E0 would be vacuous"


def test_literal_smuggling_rejected_by_cf(items):
    for it in items:
        q = literal_sql(it["gold"][0])
        assert R_cf_strict([comp(q)], **cols(it, 1)) == [0.0], it["id"]


def test_malformed_and_missing_sql_score_zero(items):
    it = items[0]
    bad = ["Answer: 42",                                          # no sql block
           [{"role": "assistant", "content": ""}],               # empty
           comp("SELEC broken"), comp("DELETE FROM customers"),  # error / write
           comp("SELECT 1; DROP TABLE customers")]               # two statements
    bad = [b if isinstance(b, list) else ([{"role": "assistant", "content": b}] if isinstance(b, str) else b) for b in bad]
    for name, f in REWARDS.items():
        assert f(bad, **cols(it, len(bad))) == [0.0] * len(bad), name
    assert run(str(DATA / it["dbs"][0]), "SELECT COUNT(*) FROM customers")[0][0] > 0


def test_sandbox():
    assert final_sql("x <think>```sql\nSELECT 2\n```</think>") is None
    with pytest.raises(SQLError):
        run(":memory:", "ATTACH DATABASE 'x.db' AS x")
