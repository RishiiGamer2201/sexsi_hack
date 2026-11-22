"""Seed replication of the main test-set comparison (GRPO-C vs GRPO-B), paper fixes 2/6/7.
Per seed: verified / silent-error rates (Wilson) and the paired, question-clustered C-B bootstrap.
Pooled: each question's verified rate averaged over the samples of every seed of an arm, then the same bootstrap.
Seed 0 = traj_B / traj_C (the hackathon runs), seed k = traj_B_s{k} / traj_C_s{k}; missing seeds are skipped.
  .venv/bin/python scripts/seeds_eval.py            # -> results/seeds_eval.json
"""
import json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluate import grade, paired_bootstrap, mcnemar_exact, wilson  # noqa: E402

items = {x["id"]: x for x in map(json.loads, open("data/test/items.jsonl"))}


def load(name):
    p = Path(f"results/traj_{name}.jsonl")
    if not p.exists():
        return None
    per = defaultdict(list)
    for r in map(json.loads, open(p)):
        per[r["id"]].append(grade(items[r["id"]], r["messages"]))
    return per


def rate(per, k):
    g = [x[k] for v in per.values() for x in v]
    return wilson(sum(g), len(g))


def mean_by_q(pers, ids, k="verified"):
    return [sum(x[k] for p in pers for x in p[i]) / sum(len(p[i]) for p in pers) for i in ids]


arms = {"B": [], "C": []}
out = {"seeds": {}}
for s, (b, c) in enumerate([("B", "C"), ("B_s1", "C_s1"), ("B_s2", "C_s2")]):
    pb, pc = load(b), load(c)
    if not (pb and pc):
        continue
    ids = sorted(set(pb) & set(pc))
    s0b, s0c = [pb[i][0]["verified"] for i in ids], [pc[i][0]["verified"] for i in ids]
    out["seeds"][s] = {
        "B": {"verified": rate(pb, "verified"), "silent_error": rate(pb, "silent_error")},
        "C": {"verified": rate(pc, "verified"), "silent_error": rate(pc, "silent_error")},
        "C_minus_B_verified_bootstrap95": paired_bootstrap(mean_by_q([pc], ids), mean_by_q([pb], ids)),
        "C_minus_B_silent_bootstrap95": paired_bootstrap(mean_by_q([pc], ids, "silent_error"), mean_by_q([pb], ids, "silent_error")),
        "mcnemar_p_sample0": mcnemar_exact(sum(x and not y for x, y in zip(s0c, s0b)), sum(y and not x for x, y in zip(s0c, s0b))),
    }
    arms["B"].append(pb); arms["C"].append(pc)

ids = sorted(set.intersection(*(set(p) for p in arms["B"] + arms["C"])))
out["pooled"] = {"n_seeds": len(arms["B"]), "n_items": len(ids),
                 "B_verified": sum(mean_by_q(arms["B"], ids)) / len(ids), "C_verified": sum(mean_by_q(arms["C"], ids)) / len(ids),
                 "C_minus_B_verified_bootstrap95": paired_bootstrap(mean_by_q(arms["C"], ids), mean_by_q(arms["B"], ids))}
Path("results/seeds_eval.json").write_text(json.dumps(out, indent=1))
for s, r in out["seeds"].items():
    d = r["C_minus_B_verified_bootstrap95"]
    print(f"seed {s}: B {r['B']['verified'][0]:.3f}  C {r['C']['verified'][0]:.3f}  C-B {d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}]  McNemar p={r['mcnemar_p_sample0']:.3f}")
p = out["pooled"]; d = p["C_minus_B_verified_bootstrap95"]
print(f"pooled ({p['n_seeds']} seeds): B {p['B_verified']:.3f}  C {p['C_verified']:.3f}  C-B {d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}]")
