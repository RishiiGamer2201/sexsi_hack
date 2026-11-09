"""Figure 3: what the training reward paid for during GRPO, B (R_exec_rex) vs C (R_cf_mean).
Reads runs/grpo_<X>_rewards.jsonl (one line per rollout, checks = [original, train CFs...], 24 rollouts per step)
and plots, per step (5-step rolling mean): original-DB pass rate, and the share of original-DB passes that
fail a counterfactual (the rollouts a single-DB reward pays by luck).

  python3 scripts/figure3.py [B C]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PER_STEP, WIN = 24, 5


def steps(run):
    rows = [json.loads(line)["checks"] for line in open(ROOT / f"runs/grpo_{run}_rewards.jsonl")]
    out = []
    for i in range(0, len(rows) - PER_STEP + 1, PER_STEP):
        g = rows[i:i + PER_STEP]
        single = sum(v[0] for v in g)
        lucky = sum(v[0] and not all(v) for v in g)
        out.append((single, lucky))
    return out


def roll(xs):
    return [sum(xs[max(0, i - WIN + 1):i + 1]) / len(xs[max(0, i - WIN + 1):i + 1]) for i in range(len(xs))]


def main(runs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    summary = {}
    for run in runs:
        s = steps(run)
        single = [x / PER_STEP for x, _ in s]
        lucky = [y / x if x else 0.0 for x, y in s]
        x = range(1, len(s) + 1)
        a1.plot(x, roll(single), label=run)
        a2.plot(x, roll(lucky), label=run)
        tot_single, tot_lucky = sum(x for x, _ in s), sum(y for _, y in s)
        half = len(s) // 2
        summary[run] = {"steps": len(s), "single_pass": tot_single / (PER_STEP * len(s)),
                        "lucky_share_of_passes": tot_lucky / tot_single if tot_single else None,
                        "lucky_share_first_half": sum(y for _, y in s[:half]) / max(1, sum(x for x, _ in s[:half])),
                        "lucky_share_second_half": sum(y for _, y in s[half:]) / max(1, sum(x for x, _ in s[half:]))}
    a1.set(xlabel="GRPO step", ylabel="rollouts passing the original DB", title="Single-DB pass rate")
    a2.set(xlabel="GRPO step", ylabel="share of those failing a counterfactual", title="Lucky passes (paid by R_exec_rex)")
    for a in (a1, a2):
        a.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "results/figure3_training_rewards.png", dpi=150)
    (ROOT / "results/figure3_training_rewards.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return summary


if __name__ == "__main__":
    r = main(sys.argv[1:] or ["B", "C"])
    assert all(0 <= v["single_pass"] <= 1 for v in r.values()), r
