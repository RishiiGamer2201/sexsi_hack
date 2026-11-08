"""Rewards in AgentTune/TRL signature: fn(completions, **dataset_columns) -> list[float].

Dataset columns used: `dbs` (list of paths relative to SQLCF_DATA; [0] = original DB the
agent explored, rest = counterfactuals it never saw), `gold` (gold result per DB),
`ordered` (bool). The graded SQL is the last ```sql block of the final assistant message.

R_exec_set  single DB, BIRD-style set EX          (baseline, plan E0)
R_exec_rex  single DB, strict multiset comparator  (condition B)
R_cf_mean   C0 * mean(C1..CK)                       (condition C, default)
R_cf_strict C0 * all(C1..CK)
R_cf_soft   C0 * (1 - 0.2 * [any Ci fails])         (ReViSQL-style)
"""
import json
import os
import re
from functools import lru_cache
from pathlib import Path

from .compare import SQLError, match, normalize, run, set_match

DATA = Path(os.environ.get("SQLCF_DATA", Path(__file__).resolve().parent.parent / "data"))
_SQL_BLOCK = re.compile(r"```sql\s*(.*?)```", re.S | re.I)
_THINK = re.compile(r"<think>.*?(</think>|\Z)|<\|START_THINKING\|>.*?(<\|END_THINKING\|>|\Z)", re.S)


def final_text(completion) -> str:
    if isinstance(completion, list):
        for msg in reversed(completion):
            if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
                return str(msg["content"])
        return ""
    return str(completion or "")


def final_sql(completion) -> str | None:
    blocks = _SQL_BLOCK.findall(_THINK.sub("", final_text(completion)))
    sql = blocks[-1].strip().rstrip(";").strip() if blocks else ""
    return sql or None


@lru_cache(maxsize=200_000)
def _exec(db_rel: str, sql: str):
    try:
        return tuple(normalize(run(str(DATA / db_rel), sql)))
    except SQLError:
        return None


def checks(sql, dbs, gold, ordered) -> list[bool]:
    """Per-DB pass vector [C0, C1..CK]; all False if there is no SQL."""
    if not sql:
        return [False] * len(dbs)
    out = []
    for d, g in zip(dbs, gold):
        res = _exec(d, sql)
        out.append(res is not None and match(res, [tuple(r) for r in g], ordered))
    return out


def _log(name, sqls, scores, vecs):
    path = os.environ.get("SQLCF_REWARD_LOG")
    if path:
        with open(path, "a") as f:
            for s, r, v in zip(sqls, scores, vecs):
                f.write(json.dumps({"reward": name, "sql": s, "score": r, "checks": v}) + "\n")


def _need(dbs, gold, n):
    # AgentTune/TRL retry reward calls on TypeError; fail with a ValueError so a missing
    # column can never silently become an all-zero reward.
    if dbs is None or gold is None or len(dbs) != n or len(gold) != n:
        raise ValueError("SQL rewards need dataset columns `dbs`, `gold`, `ordered` aligned with completions "
                         "(set remove_unused_columns=False)")


def _make(name, combine):
    def reward(completions, dbs=None, gold=None, ordered=None, **_):
        _need(dbs, gold, len(completions))
        ordered = ordered if ordered is not None else [False] * len(completions)
        sqls = [final_sql(c) for c in completions]
        vecs = [checks(s, d, g, bool(o)) for s, d, g, o in zip(sqls, dbs, gold, ordered)]
        scores = [float(combine(v)) for v in vecs]
        _log(name, sqls, scores, vecs)
        return scores
    reward.__name__ = name
    return reward


R_exec_rex = _make("R_exec_rex", lambda v: v[0])
R_cf_mean = _make("R_cf_mean", lambda v: v[0] * (sum(v[1:]) / len(v[1:]) if v[1:] else 1.0))
R_cf_strict = _make("R_cf_strict", lambda v: v[0] and all(v[1:]))
R_cf_soft = _make("R_cf_soft", lambda v: v[0] * (1 - 0.2 * (not all(v[1:]))))


def R_exec_set(completions, dbs=None, gold=None, **_):
    _need(dbs, gold, len(completions))
    out = []
    for c, d, g in zip(completions, dbs, gold):
        sql = final_sql(c)
        res = _exec(d[0], sql) if sql else None
        out.append(float(res is not None and set_match(res, [tuple(r) for r in g[0]])))
    return out


REWARDS = {f.__name__: f for f in [R_exec_set, R_exec_rex, R_cf_mean, R_cf_strict, R_cf_soft]}
