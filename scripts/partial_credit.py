"""E11: intermediate (partial-credit) rewards instead of 0/1, audited like E0 and replayed on GRPO rollouts. CPU.

Per-DB credit c_k: 1 if the result matches gold (sqlcf.compare.match); else, for a single numeric cell, closeness
max(0, 1 - |pred - gold| / |gold|); else multiset F1 of rows (column order ignored). 0 on an SQL error or no SQL.
  P_single = c_0                 (partial credit on the original DB only)
  P_cf     = mean_k c_k          (partial credit averaged over the original and every copy)
Compared with the binary rewards R_exec_rex (single DB) and R_cf_mean / R_cf_strict (copies).

  (a) audit: E0 candidates (data/audit/items.jsonl, copies chosen blind to the mutants): mean pay to correct / mutant / hack queries, full-pay rate,
      and AUROC (does the reward rank every correct query above every wrong one?)
  (b) training signal: sft_ho's 2670 rollouts on the 445 GRPO prompts (G = 6): share of groups with any reward
      variance, and how lucky rollouts (right on the original, wrong on a copy) fare against their group's mean.

  python scripts/partial_credit.py      # -> results/e11_partial_credit.json
"""
import bisect
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.audit import hacks, wilson  # noqa: E402
from sqlcf.compare import _key, match  # noqa: E402
from sqlcf.rewards import _exec, final_sql  # noqa: E402


def credit(res, gold, ordered) -> float:
    if res is None:
        return 0.0
    gold = [tuple(r) for r in gold]
    if match(list(res), gold, ordered):
        return 1.0
    if len(res) == len(gold) == 1 and len(res[0]) == len(gold[0]) == 1:
        p, g = res[0][0], gold[0][0]
        if isinstance(p, (int, float)) and isinstance(g, (int, float)) and g != 0:
            return max(0.0, 1 - abs(p - g) / abs(g))
    a = Counter(tuple(sorted(r, key=_key)) for r in res)
    b = Counter(tuple(sorted(r, key=_key)) for r in gold)
    return 2 * sum((a & b).values()) / (sum(a.values()) + sum(b.values())) if a or b else 0.0


def credits(sql, it, dbs="dbs", gold="gold") -> list[float]:
    if not sql:
        return [0.0] * len(it[dbs])
    return [credit(_exec(d, sql), g, it["ordered"]) for d, g in zip(it[dbs], it[gold])]


REWARDS = {
    "R_exec_rex": lambda c: float(c[0] == 1),
    "R_cf_mean": lambda c: float(c[0] == 1) * sum(x == 1 for x in c[1:]) / len(c[1:]),
    "R_cf_strict": lambda c: float(all(x == 1 for x in c)),
    "P_single": lambda c: c[0],
    "P_cf": lambda c: sum(c) / len(c),
}


def auroc(pos, neg):
    """P(score(correct) > score(wrong)), ties count half."""
    neg = sorted(neg)
    tot = sum(bisect.bisect_left(neg, p) + 0.5 * (bisect.bisect_right(neg, p) - bisect.bisect_left(neg, p)) for p in pos)
    return tot / (len(pos) * len(neg))


def audit():
    scores = defaultdict(lambda: defaultdict(list))  # reward -> group -> [score]
    for it in map(json.loads, open(ROOT / "data/audit/items.jsonl")):
        cands = [("correct", it["gold_sql"])] + [("correct", q) for q in it["paraphrases"]]
        cands += [("mutant", q) for q in it["mutants"].values()]
        cands += [(f"hack:{h}", q) for h, q in hacks(it).items()]
        for group, sql in cands:
            c = credits(sql, it, "dbs_random", "gold_random")  # copies chosen blind to the mutants, as E0's headline
            for r, f in REWARDS.items():
                for g in {group, group.split(":")[0]}:
                    scores[r][g].append(f(c))
    out = {}
    for r, d in scores.items():
        out[r] = {g: {"n": len(v), "mean_pay": sum(v) / len(v), "full_pay": wilson(sum(x >= 1 for x in v), len(v))[0]}
                  for g, v in sorted(d.items())}
        out[r]["auroc_correct_vs_mutant"] = auroc(d["correct"], d["mutant"])
        out[r]["auroc_correct_vs_hack"] = auroc(d["correct"], d["hack"])
    return out


def signal():
    items = {it["id"]: it for it in map(json.loads, open(ROOT / "data/train/grpo_items.jsonl"))}
    groups = defaultdict(list)
    for t in map(json.loads, open(ROOT / "runs/traj_sft_ho_grpoprompts.jsonl")):
        groups[t["id"]].append(credits(final_sql(t["messages"]), items[t["id"]]))
    out = {"groups": len(groups), "rollouts": sum(map(len, groups.values()))}
    for r, f in REWARDS.items():
        mixed = above = lucky = wrong_paid = wrong = 0
        for cs in groups.values():
            s = [f(c) for c in cs]
            mean = sum(s) / len(s)
            mixed += max(s) > min(s)
            for c, x in zip(cs, s):
                if c[0] == 1 and any(y < 1 for y in c[1:]):  # lucky: right on the original, wrong on a copy
                    lucky += 1
                    above += x > mean
                if not all(y == 1 for y in c):
                    wrong += 1
                    wrong_paid += x > 0
        out[r] = {"groups_with_signal": mixed / len(groups), "lucky_above_group_mean": above / lucky,
                  "wrong_rollouts_paid_something": wrong_paid / wrong, "n_lucky": lucky, "n_wrong": wrong}
    return out


if __name__ == "__main__":
    assert credit(((5,),), [[5]], False) == 1 and credit(((4,),), [[5]], False) == 0.8
    assert credit(((1,), (2,)), [[1], [3]], False) == 0.5 and credit(None, [[1]], False) == 0
    res = {"what": "E11: partial-credit rewards (scripts/partial_credit.py)", "audit": audit(), "training_signal": signal()}
    (ROOT / "results/e11_partial_credit.json").write_text(json.dumps(res, indent=1))
    for r in REWARDS:
        a, s = res["audit"][r], res["training_signal"][r]
        print(f"{r:12} pay: correct {a['correct']['mean_pay']:.3f} mutant {a['mutant']['mean_pay']:.3f} "
              f"hack {a['hack']['mean_pay']:.3f} | AUROC mut {a['auroc_correct_vs_mutant']:.3f} hack {a['auroc_correct_vs_hack']:.3f}"
              f" | groups w/ signal {s['groups_with_signal']:.3f} lucky>mean {s['lucky_above_group_mean']:.3f}"
              f" wrong paid>0 {s['wrong_rollouts_paid_something']:.3f}")
