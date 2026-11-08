"""GRPO signal check: per prompt, how many of its G rollouts verify (all DBs) vs pass only the original DB.
Mixed groups (0 < verified < G) give GRPO a gradient; all-pass / all-fail groups give none.
  python scripts/group_signal.py runs/traj_sft_grpoprompts16.jsonl data/train/grpo_items.jsonl
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, ".")
from evaluate import grade  # noqa: E402


def summarize(per: dict[str, list[dict]]) -> dict:
    G = Counter(len(v) for v in per.values()).most_common(1)[0][0]
    ver = Counter(sum(g["verified"] for g in v) for v in per.values())
    mixed_v = sum(n for k, n in ver.items() if 0 < k < G)
    # groups where the single-DB (original) reward is mixed: R_exec-style signal
    single_mixed = sum(1 for v in per.values() if 0 < sum(g["single"] for g in v) < G)
    fp = sum(g["single"] and not g["verified"] for v in per.values() for g in v)
    n = sum(len(v) for v in per.values())
    return {"prompts": len(per), "G": G, "verified_count_hist": dict(sorted(ver.items())),
            "mixed_verified": mixed_v, "mixed_single": single_mixed,
            "single_pass_cf_fail_rollouts": fp, "rollouts": n,
            "verified_rate": sum(g["verified"] for v in per.values() for g in v) / n}


if __name__ == "__main__":
    if len(sys.argv) == 1:  # self-check
        t, f = {"verified": 1, "single": 1}, {"verified": 0, "single": 0}
        s = summarize({"a": [t, t], "b": [t, f], "c": [f, {"verified": 0, "single": 1}]})
        assert s["mixed_verified"] == 1 and s["mixed_single"] == 2 and s["single_pass_cf_fail_rollouts"] == 1, s
        print("ok"); sys.exit()
    items = {x["id"]: x for x in map(json.loads, open(sys.argv[2]))}
    per = defaultdict(list)
    for r in map(json.loads, open(sys.argv[1])):
        per[r["id"]].append(grade(items[r["id"]], r["messages"]))
    print(json.dumps(summarize(per), indent=1))
