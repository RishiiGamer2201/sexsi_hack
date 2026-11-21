"""A1 (symposium plan): four CPU re-analyses of stored data that explain the GRPO null. No GPU, no new samples.

  (a) per-family reward audit, read from results/e0_reward_audit.json (blind CF, informed CF, single-DB);
  (b) advantage replay over the GRPO reward logs: groups of G = 6 consecutive rollouts (TRL's RepeatSampler
      repeats each prompt G times in a row and rewards are logged in completion order), how many groups carry
      any reward variance under each reward, and on how many rollouts each CF reward flips B's advantage sign;
  (c) the monitor curve: per-step share of rollouts that pass the original DB but fail a copy (single-DB minus
      CF reward), for the main and the curriculum pairs; saved as results/figure_monitor_gap.png;
  (d) effective training copies: of the copies attached to the 445 GRPO prompts, how many catch at least one
      base-blind mutant (exact comparator, sqlcf.rewards.checks).

  .venv-train/bin/python scripts/a1_mechanism.py      # -> results/a1_mechanism.json (+ figure)
"""
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.rewards import checks  # noqa: E402
from train import SFT_BASES  # noqa: E402

G, PER_STEP = 6, 24
RUNS = {"B": "grpo_B", "C": "grpo_C", "B_cur": "grpo_B_cur", "Cmin_cur": "grpo_Cmin_cur"}
REPLAY = {  # reward of one rollout from its pass vector [C0, C1..CK]
    "B": lambda v: float(v[0]),
    "C_mean": lambda v: v[0] * (sum(v[1:]) / len(v[1:]) if v[1:] else 1.0),
    "C_strict": lambda v: float(v[0] and all(v[1:])),
    "C_pen": lambda v: v[0] - 0.5 * (v[0] and not all(v[1:])),
}


def per_family():
    rows = json.load(open(ROOT / "results/e0_reward_audit.json"))["rows"]
    out = defaultdict(dict)
    names = {"R_cf_strict@random": "cf_blind", "R_cf_strict": "cf_informed", "R_exec_rex": "single_db"}
    for r in rows:
        if r["family"] != "ALL" and r["reward"] in names and r["candidates"] in ("mutant", "hack"):
            out[r["family"]][f'{r["candidates"]}_{names[r["reward"]]}'] = {
                "rate": round(r["rate"], 4), "ci95": [round(x, 4) for x in r["ci95"]], "n": r["n"]}
    return dict(sorted(out.items()))


def sign(x, eps=1e-9):
    return 0 if abs(x) < eps else (1 if x > 0 else -1)


def advantages(rs):
    m, sd = statistics.fmean(rs), statistics.pstdev(rs)
    return [0.0 if sd < 1e-9 else (r - m) / sd for r in rs]


def replay(vecs):
    groups = [vecs[i:i + G] for i in range(0, len(vecs) - len(vecs) % G, G)]
    res = {"groups": len(groups), "rollouts": len(groups) * G,
           "lucky_rollouts": sum(v[0] and not all(v[1:]) for v in vecs)}
    adv = {k: [a for g in groups for a in advantages([f(v) for v in g])] for k, f in REPLAY.items()}
    for k, f in REPLAY.items():
        res[f"signal_groups_{k}"] = sum(statistics.pstdev([f(v) for v in g]) > 1e-9 for g in groups)
        if k != "B":
            res[f"sign_flips_vs_B_{k}"] = sum(sign(a) != sign(b) for a, b in zip(adv[k], adv["B"]))
    return res


def monitor(vecs):
    steps = [vecs[i:i + PER_STEP] for i in range(0, len(vecs), PER_STEP)]
    gap = [sum(v[0] and not all(v[1:]) for v in s) / len(s) for s in steps]
    return gap, {"first10": round(statistics.fmean(gap[:10]), 3), "last10": round(statistics.fmean(gap[-10:]), 3)}


def effective_copies():
    items = [json.loads(l) for l in open(ROOT / "data/train/items.jsonl")]
    items = [it for it in items if it["dbs"][0].split("/")[-2] not in SFT_BASES]
    n_copies, by_edit, kills = Counter(), Counter(), Counter()
    with_blind = 0
    for it in items:
        n_copies[len(it["dbs"]) - 1] += 1
        vecs = [checks(sql, it["dbs"], it["gold"], it["ordered"]) for sql in it["mutants"].values()]
        blind = [v for v in vecs if v[0]]
        with_blind += bool(blind)
        for k, edit in enumerate(it["cf_edits"], start=1):
            by_edit[edit] += 1
            kills[edit] += any(not v[k] for v in blind)
    return {"grpo_prompts": len(items), "copies_per_prompt": dict(sorted(n_copies.items())),
            "copies": sum(by_edit.values()), "copies_killing_a_mutant": sum(kills.values()),
            "prompts_with_base_blind_mutant": with_blind,
            "by_edit": {e: {"chosen": by_edit[e], "kill": kills[e]} for e in sorted(by_edit, key=lambda e: -by_edit[e])}}


def figure(curves):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def smooth(x, w=5):
        return [statistics.fmean(x[max(0, i - w + 1):i + 1]) for i in range(len(x))]

    fig, axes = plt.subplots(1, 2, figsize=(7, 2.6), sharey=True)
    for ax, pair, title in ((axes[0], ("B", "C"), "Main pair"), (axes[1], ("B_cur", "Cmin_cur"), "Curriculum pair")):
        for name, style in zip(pair, ("-", "--")):
            ax.plot(range(1, len(curves[name]) + 1), smooth(curves[name]), style, label=name)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("GRPO step", fontsize=8)
        ax.legend(fontsize=7, frameon=False)
        ax.tick_params(labelsize=7)
    axes[0].set_ylabel("lucky share of rollouts\n(pass $D_0$, fail a copy)", fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figure_monitor_gap.png", dpi=200)


def main():
    out = {"per_family_audit": per_family(), "replay": {}, "monitor": {}}
    curves = {}
    for name, run in RUNS.items():
        vecs = [json.loads(l)["checks"] for l in open(ROOT / f"runs/{run}_rewards.jsonl")]
        assert all(len({len(v) for v in vecs[i:i + G]}) == 1 for i in range(0, len(vecs), G)), run  # one prompt per group
        out["replay"][name] = replay(vecs)
        curves[name], out["monitor"][name] = monitor(vecs)
    out["effective_copies"] = effective_copies()
    (ROOT / "results/a1_mechanism.json").write_text(json.dumps(out, indent=1) + "\n")
    figure(curves)
    print(json.dumps({k: out[k] for k in ("replay", "monitor")}, indent=1))
    e = out["effective_copies"]
    print(f"effective copies: {e['copies_killing_a_mutant']}/{e['copies']} kill a base-blind mutant; "
          f"copies per prompt {e['copies_per_prompt']}; {e['prompts_with_base_blind_mutant']} prompts have one")


if __name__ == "__main__":
    main()
