"""E14 curriculum: keep GRPO prompts where the SFT init is unsure AND often lucky, so B and C-min see different rewards.
Keep an item if some but not all of its G SFT rollouts pass the original DB, and >= 20% of those passes fail a copy.
Uses the existing SFT (held-out) rollouts on the GRPO prompts (G = 6, T = 1.0); no new sampling.
  .venv/bin/python scripts/curriculum.py runs/traj_sft_ho_grpoprompts.jsonl data/train/grpo_items.jsonl data/train/curriculum_items.jsonl
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, ".")


def keep(grades: list[dict], min_lucky: float = 0.2) -> bool:
    single = sum(g["single"] for g in grades)
    lucky = sum(g["single"] and not g["verified"] for g in grades)
    return 0 < single < len(grades) and lucky / single >= min_lucky


if __name__ == "__main__":
    if len(sys.argv) == 1:  # self-check
        v, l, f = {"single": 1, "verified": 1}, {"single": 1, "verified": 0}, {"single": 0, "verified": 0}
        assert keep([v, l, f]) and not keep([v, v, f]) and not keep([l, l]) and not keep([f, f]) and keep([v, v, v, v, l, f])
        print("ok"); sys.exit()
    from evaluate import grade
    traj, items_path, out = sys.argv[1:4]
    items = {x["id"]: x for x in map(json.loads, open(items_path))}
    per = defaultdict(list)
    for r in map(json.loads, open(traj)):
        per[r["id"]].append(grade(items[r["id"]], r["messages"]))
    kept = [iid for iid, g in per.items() if keep(g)]
    with open(out, "w") as f:
        for iid in kept:
            f.write(json.dumps(items[iid]) + "\n")
    rows = [g for iid in kept for g in per[iid]]
    stats = {"prompts_in": len(per), "kept": len(kept),
             "by_template": dict(Counter(items[i]["template"] for i in kept).most_common()),
             "kept_single_rate": round(sum(g["single"] for g in rows) / len(rows), 3),
             "kept_lucky_share_of_single": round(sum(g["single"] and not g["verified"] for g in rows)
                                                 / max(1, sum(g["single"] for g in rows)), 3),
             "all_lucky_rollouts": sum(g["single"] and not g["verified"] for v in per.values() for g in v)}
    print(json.dumps(stats, indent=1))
