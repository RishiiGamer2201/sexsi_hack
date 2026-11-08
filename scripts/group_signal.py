"""GRPO signal check: per prompt group of G rollouts, does the reward vary (a gradient) or not?
  verified = all DBs pass (R_cf strict) | single = original DB passes (R_exec) | cf_frac = share of DBs passing (R_cf_mean)
"single_pass_cf_fail" rollouts are where R_exec and R_cf disagree: the only place B and C get different rewards.
  python scripts/group_signal.py runs/traj_sft_grpoprompts16.jsonl data/train/grpo_items.jsonl
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, ".")


def _mixed(v, key):
    return len({g[key] for g in v}) > 1


def summarize(per: dict[str, list[dict]]) -> dict:
    G = Counter(len(v) for v in per.values()).most_common(1)[0][0]
    n = sum(len(v) for v in per.values())
    rows = [g for v in per.values() for g in v]
    return {"prompts": len(per), "G": G, "rollouts": n,
            "verified_count_hist": dict(sorted(Counter(sum(g["verified"] for g in v) for v in per.values()).items())),
            "mixed_verified": sum(_mixed(v, "verified") for v in per.values()),
            "mixed_single": sum(_mixed(v, "single") for v in per.values()),
            "mixed_cf_frac": sum(_mixed(v, "cf_frac") for v in per.values()),
            "single_pass_cf_fail_rollouts": sum(g["single"] and not g["verified"] for g in rows),
            "verified_rate": sum(g["verified"] for g in rows) / n, "single_rate": sum(g["single"] for g in rows) / n}


if __name__ == "__main__":
    if len(sys.argv) == 1:  # self-check
        t, f, s = ({"verified": 1, "single": 1, "cf_frac": 1.0}, {"verified": 0, "single": 0, "cf_frac": 0.0},
                   {"verified": 0, "single": 1, "cf_frac": 0.5})
        r = summarize({"a": [t, t], "b": [t, f], "c": [f, s]})
        assert (r["mixed_verified"], r["mixed_single"], r["mixed_cf_frac"], r["single_pass_cf_fail_rollouts"]) == (1, 2, 2, 1), r
        print("ok"); sys.exit()
    from evaluate import grade
    items = {x["id"]: x for x in map(json.loads, open(sys.argv[2]))}
    per = defaultdict(list)
    for r in map(json.loads, open(sys.argv[1])):
        per[r["id"]].append(grade(items[r["id"]], r["messages"]))
    by_t = defaultdict(dict)
    for iid, v in per.items():
        by_t[items[iid]["template"]][iid] = v
    out = {"all": summarize(per)}
    for t, sub in sorted(by_t.items()):
        s = summarize(sub)
        out[t] = {k: (round(s[k], 3) if isinstance(s[k], float) else s[k]) for k in
                  ("prompts", "mixed_verified", "mixed_single", "mixed_cf_frac", "single_pass_cf_fail_rollouts", "verified_rate", "single_rate")}
    print(json.dumps(out, indent=1))
