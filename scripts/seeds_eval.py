"""Seed replication of the main test-set comparison (GRPO-C vs GRPO-B, and each vs SFT), paper fixes 2/6/7.
Per seed: verified / silent-error rates (Wilson) and the paired, question-clustered bootstrap of each difference, exact
McNemar on sample 0, and the minimum detectable effect (80% power, two-sided 0.05: 2.8 x bootstrap SE, SE = CI width / 3.92).
Pooled: each question's verified rate averaged over the samples of every seed of an arm, then the same bootstrap.
Seed 0 = traj_B / traj_C (the hackathon runs), seed k = traj_B_s{k} / traj_C_s{k}; missing seeds are skipped.
SFT (traj_sft_ho, from runs/sft) is the shared GRPO initialisation, so it has one run.
  .venv/bin/python scripts/seeds_eval.py            # -> results/seeds_eval.json
"""
import json, statistics, sys
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


def compare(xs, ys, ids, k="verified"):
    """xs - ys (lists of runs, pooled per question): bootstrap, McNemar on the first run's sample 0, MDE."""
    d = paired_bootstrap(mean_by_q(xs, ids, k), mean_by_q(ys, ids, k))
    a, b = [xs[0][i][0][k] for i in ids], [ys[0][i][0][k] for i in ids]
    return {"diff_bootstrap95": d, "mde_80power": 2.8 * (d[2] - d[1]) / 3.92,
            "mcnemar_p_sample0": mcnemar_exact(sum(x and not y for x, y in zip(a, b)), sum(y and not x for x, y in zip(a, b)))}


sft = load("sft_ho")  # runs/sft = the held-out SFT, the GRPO initialisation (evaluated as sft_ho)
arms = {"B": [], "C": []}
out = {"seeds": {}}
for s, (b, c) in enumerate([("B", "C"), ("B_s1", "C_s1"), ("B_s2", "C_s2")]):
    pb, pc = load(b), load(c)
    if not (pb and pc):
        continue
    ids = sorted(set(pb) & set(pc) & set(sft))
    out["seeds"][s] = {
        "B": {"verified": rate(pb, "verified"), "silent_error": rate(pb, "silent_error")},
        "C": {"verified": rate(pc, "verified"), "silent_error": rate(pc, "silent_error")},
        "C_minus_B": compare([pc], [pb], ids), "C_minus_B_silent": compare([pc], [pb], ids, "silent_error"),
        "B_minus_SFT": compare([pb], [sft], ids), "C_minus_SFT": compare([pc], [sft], ids),
    }
    arms["B"].append(pb); arms["C"].append(pc)

ids = sorted(set.intersection(set(sft), *(set(p) for p in arms["B"] + arms["C"])))
def seed_level(ds):
    """Seeds as the unit (training variance included): mean, SD and Student-t 95% interval over per-seed differences."""
    if len(ds) < 2:
        return None
    m, sd = statistics.mean(ds), statistics.stdev(ds)
    h = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}[len(ds) - 1] * sd / len(ds) ** 0.5
    return {"per_seed": ds, "mean": m, "sd": sd, "t95": [m - h, m + h]}


spider = json.load(open("results/e13_spider_ours.json"))["comparisons"]
sp_keys = [k for k in ("C_vs_B", "C_s1_vs_B_s1", "C_s2_vs_B_s2") if k in spider][:len(arms["B"])]
diff = lambda k: [r[k]["diff_bootstrap95"][0] for r in out["seeds"].values()]
out["SFT_verified"] = rate(sft, "verified")
out["pooled"] = {"n_seeds": len(arms["B"]), "n_items": len(ids),
                 "B_verified": sum(mean_by_q(arms["B"], ids)) / len(ids), "C_verified": sum(mean_by_q(arms["C"], ids)) / len(ids),
                 "C_minus_B": compare(arms["C"], arms["B"], ids),
                 "B_minus_SFT": compare(arms["B"], [sft], ids), "C_minus_SFT": compare(arms["C"], [sft], ids)}
out["seed_level"] = {"C_minus_B": seed_level(diff("C_minus_B")), "B_minus_SFT": seed_level(diff("B_minus_SFT")),
                     "C_minus_SFT": seed_level(diff("C_minus_SFT")),
                     "spider_TS_C_minus_B": seed_level([spider[k]["TS_diff_bootstrap95"][0] for k in sp_keys])}
Path("results/seeds_eval.json").write_text(json.dumps(out, indent=1))

f = lambda r: f"{r['diff_bootstrap95'][0]:+.3f} [{r['diff_bootstrap95'][1]:+.3f}, {r['diff_bootstrap95'][2]:+.3f}] p={r['mcnemar_p_sample0']:.3f} mde={r['mde_80power']:.3f}"
print(f"SFT {out['SFT_verified'][0]:.3f}")
for s, r in out["seeds"].items():
    print(f"seed {s}: B {r['B']['verified'][0]:.3f}  C {r['C']['verified'][0]:.3f}\n  C-B {f(r['C_minus_B'])}\n  B-SFT {f(r['B_minus_SFT'])}\n  C-SFT {f(r['C_minus_SFT'])}")
p = out["pooled"]
print(f"pooled ({p['n_seeds']} seeds): B {p['B_verified']:.3f}  C {p['C_verified']:.3f}"
      f"\n  C-B {f(p['C_minus_B'])}\n  B-SFT {f(p['B_minus_SFT'])}\n  C-SFT {f(p['C_minus_SFT'])}")
for k, v in out["seed_level"].items():
    if v:
        print(f"seed-level {k}: per seed {[round(x, 3) for x in v['per_seed']]}  mean {v['mean']:+.3f}  sd {v['sd']:.3f}  t95 [{v['t95'][0]:+.3f}, {v['t95'][1]:+.3f}]")
