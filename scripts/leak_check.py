"""Train/test leak check: exact and near-duplicate overlap of questions and gold SQL between splits.

Near-duplicate = MinHash-free Jaccard over word 3-shingles >= 0.8 (exhaustive, splits are small).
  python scripts/leak_check.py  ->  results/leak_check.json
"""
import json
import re
from itertools import product

SPLITS = {s: [json.loads(l) for l in open(f"data/{s}/items.jsonl")] for s in ("train", "test", "audit")}


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"\d+(\.\d+)?", "#", s.lower())).strip()


def shingles(s, n=3):
    w = norm(s).split()
    return {tuple(w[i:i + n]) for i in range(max(1, len(w) - n + 1))}


def field(it, *keys):
    return next(it[k] for k in keys if k in it)


out = {}
for a, b in (("train", "test"), ("train", "audit"), ("audit", "test")):
    r = {}
    for name, keys in (("question", ("question", "nl", "q")), ("gold_sql", ("gold_sql", "gold", "sql"))):
        A = [field(x, *keys) for x in SPLITS[a]]
        B = [field(x, *keys) for x in SPLITS[b]]
        exact = len({x.strip().lower() for x in A} & {x.strip().lower() for x in B})
        templ = len({norm(x) for x in A} & {norm(x) for x in B})  # same text up to numbers
        SA, SB = [shingles(x) for x in A], [shingles(x) for x in B]
        near = sum(any(len(sb & sa) / len(sb | sa) >= 0.8 for sa in SA) for sb in SB)
        r[name] = {"exact": exact, "same_up_to_numbers": templ, f"{b}_items_near_dup_of_{a}": near, "n_" + b: len(B)}
    out[f"{a}_vs_{b}"] = r
json.dump(out, open("results/leak_check.json", "w"), indent=1)
print(json.dumps(out, indent=1))
