"""Sandboxed SQL execution and result comparison.

run(): read-only, single statement, no ATTACH, 5 s timeout.
match(): multiset by default; ordered when the gold is ordered; column permutation
allowed; floats rounded to 4 dp (and 3.0 == 3). set_match(): BIRD-style set EX.
"""
import itertools
import sqlite3
import time
from collections import Counter

TIMEOUT_S = 5.0
MAX_ROWS = 100_000


class SQLError(Exception):
    pass


def _deny_attach(action, *_):
    return sqlite3.SQLITE_DENY if action in (sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH) else sqlite3.SQLITE_OK


def run(db_path: str, sql: str, timeout: float = TIMEOUT_S) -> list[tuple]:
    """Execute one read-only query; raise SQLError on any failure."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
    try:
        con.execute("PRAGMA query_only = ON")
        con.set_authorizer(_deny_attach)
        deadline = time.monotonic() + timeout
        con.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)
        cur = con.execute(sql)  # sqlite3 refuses multiple statements here
        rows = cur.fetchmany(MAX_ROWS + 1)
        if len(rows) > MAX_ROWS:
            raise SQLError("too many rows")
        return rows
    except sqlite3.Error as e:
        raise SQLError(str(e)) from e
    finally:
        con.close()


def _norm(v):
    if isinstance(v, float):
        v = round(v, 4)
        return int(v) if v.is_integer() else v
    if isinstance(v, bytes):
        return v.hex()
    return v


def normalize(rows) -> list[tuple]:
    return [tuple(_norm(v) for v in r) for r in rows]


def _key(v):
    return (v is None, type(v).__name__, v if v is not None else 0)


def match(pred, gold, ordered: bool = False) -> bool:
    """True if pred equals gold up to column permutation (multiset, or list if ordered)."""
    pred, gold = normalize(pred), normalize(gold)
    if len(pred) != len(gold):
        return False
    if not gold:
        return True
    ncol = len(gold[0])
    if any(len(r) != ncol for r in pred):
        return False
    gcols = [sorted((r[j] for r in gold), key=_key) for j in range(ncol)]
    pcols = [sorted((r[j] for r in pred), key=_key) for j in range(ncol)]
    # candidate pred columns for each gold column = same sorted values
    cands = [[i for i in range(ncol) if pcols[i] == gcols[j]] for j in range(ncol)]
    if any(not c for c in cands):
        return False
    target = gold if ordered else Counter(gold)
    for perm in itertools.product(*cands):
        if len(set(perm)) != ncol:
            continue
        mapped = [tuple(r[i] for i in perm) for r in pred]
        if (mapped if ordered else Counter(mapped)) == target:
            return True
    return False


def set_match(pred, gold) -> bool:
    """BIRD/Spider-style execution accuracy: set of rows, column order as written."""
    return set(normalize(pred)) == set(normalize(gold))


if __name__ == "__main__":
    assert match([(1, "a"), (1, "a")], [(1, "a"), (1, "a")])
    assert not match([(1, "a")], [(1, "a"), (1, "a")])           # duplicates matter
    assert set_match([(1, "a")], [(1, "a"), (1, "a")])           # ...but not for set EX
    assert match([("a", 1)], [(1, "a")])                         # column permutation
    assert match([(2.00000001,)], [(2,)])                        # float rounding
    assert not match([(1,), (2,)], [(2,), (1,)], ordered=True)
    assert match([(1,), (2,)], [(2,), (1,)])
    assert not match([(1, 2)], [(1, 2, 3)])
    print("compare.py self-check ok")
