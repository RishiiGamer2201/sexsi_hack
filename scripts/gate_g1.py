"""Gate G1 tie-break: share of GRPO groups with non-zero reward variance per R_cf form.

Rescores the per-rollout check vectors [C0, C1..CK] logged by SQLCF_REWARD_LOG (early GRPO-B
steps = rollouts of the SFT policy). TRL logs a generation batch as consecutive groups of G.
  python scripts/gate_g1.py runs/grpo_B_rewards.jsonl --G 6 [--first 96]
FN on gold is 0 for every form (E0), so this count decides G1.
"""
import argparse
import json
import statistics

FORMS = {
    "R_cf_mean": lambda v: v[0] * (sum(v[1:]) / len(v[1:]) if v[1:] else 1.0),
    "R_cf_strict": lambda v: float(v[0] and all(v[1:])),
    "R_cf_soft": lambda v: v[0] * (1 - 0.2 * (not all(v[1:]))),
    "R_exec_rex": lambda v: float(v[0]),
}


def nonzero_var(vecs, G):
    groups = [vecs[i:i + G] for i in range(0, len(vecs) - G + 1, G)]
    return len(groups), {k: sum(statistics.pvariance([f(v) for v in g]) > 0 for g in groups) for k, f in FORMS.items()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--G", type=int, default=6)
    ap.add_argument("--first", type=int, default=0, help="only the first N rollouts")
    a = ap.parse_args()
    vecs = [r["checks"] for r in map(json.loads, open(a.log))][: a.first or None]
    n, counts = nonzero_var(vecs, a.G)
    print(f"{len(vecs)} rollouts, {n} groups of {a.G}")
    for k, c in counts.items():
        print(f"{k:12s} non-zero-variance groups {c}/{n} = {c / max(n, 1):.3f}")
    # check: group 1 spreads under every form; group 2 ([0,..] vs [1,0,0]) only under soft and rex
    t = [[1, 1, 0], [1, 1, 1], [0, 1, 1], [0, 0, 0], [1, 0, 0], [0, 0, 0]]
    assert nonzero_var(t, 3)[1] == {"R_cf_mean": 1, "R_cf_strict": 1, "R_cf_soft": 2, "R_exec_rex": 2}
