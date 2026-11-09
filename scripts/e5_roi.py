"""E5 ROI table: Command A (API, single-turn) vs self-hosted Tiny Aya + LoRA (multi-turn agent).
Accuracy from results/e4_eval.json; Command A cost from billed tokens x list price; Tiny Aya cost = GPU $/hr x
measured generation time (runs/local_<model>.log, "gen <model> <s> s") / trajectories.

  python3 scripts/e5_roi.py [--gpu-usd-hr 0.74] [--models sft_ho B C]
Prices: Command A $2.50 / 1M input, $10.00 / 1M output (Cohere list price for command-a-03-2025, checked Nov 9 2026).
GPU default: our g2-standard-4 + L4 VM on-demand rate. Tiny Aya is priced at L4 throughput: B was timed on the L4
(runs/time_l4.log); the other models' laptop times are scaled by B's L4 / laptop ratio.
"""
import argparse
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_USD, OUT_USD = 2.50 / 1e6, 10.00 / 1e6

ap = argparse.ArgumentParser()
ap.add_argument("--gpu-usd-hr", type=float, default=0.74)
ap.add_argument("--models", nargs="+", default=["sft_ho", "B", "C"])
a = ap.parse_args()

e4 = json.loads((ROOT / "results/e4_eval.json").read_text())
rows = [json.loads(line) for line in open(ROOT / "results/traj_command_a.jsonl")]
tin = sum(r["billed"].get("input_tokens", 0) for r in rows)
tout = sum(r["billed"].get("output_tokens", 0) for r in rows)
lat = sorted(r["latency_s"] for r in rows)
out = {"command_a": {"n": len(rows), "verified": e4.get("command_a", {}).get("verified"),
                     "single": e4.get("command_a", {}).get("single"),
                     "usd_per_1k": 1000 * (tin * IN_USD + tout * OUT_USD) / len(rows),
                     "tokens_per_query": [tin / len(rows), tout / len(rows)],
                     "latency_s_median": statistics.median(lat), "latency_s_p90": lat[int(0.9 * len(lat)) - 1]}}
def gen_s(log, name):
    hit = re.findall(rf"^gen {re.escape(name)} ([0-9.]+) s", log.read_text(), re.M) if log.exists() else []
    return float(hit[-1]) if hit else None


# L4 timing (scripts/vm_time_l4.sh) exists for B only; other models are scaled by B's L4 / laptop time ratio.
l4_b, lap_b = gen_s(ROOT / "runs/time_l4.log", "B_l4"), gen_s(ROOT / "runs/local_B.log", "B")
ratio = l4_b / lap_b if l4_b and lap_b else None
for m in a.models:
    lap = gen_s(ROOT / f"runs/local_{m}.log", m)
    n = sum(1 for _ in open(ROOT / f"results/traj_{m}.jsonl"))
    if not lap or m not in e4:
        print(f"skip {m}: no timing or no score")
        continue
    l4, how = (l4_b, "measured on L4") if m == "B" and l4_b else ((lap * ratio, "laptop time x B's L4/laptop ratio") if ratio else (lap, "laptop time"))
    out[m] = {"n": n, "verified": e4[m]["verified"], "single": e4[m]["single"], "gen_s_laptop": lap, "gen_s_l4": l4, "l4_time": how,
              "trajectories_per_s": n / l4, "usd_per_1k": 1000 * a.gpu_usd_hr * l4 / 3600 / n}
out["assumptions"] = {"command_a_usd_per_1M": [2.50, 10.00], "gpu_usd_hr": a.gpu_usd_hr, "l4_over_laptop_ratio": ratio,
                      "throughput": "vLLM batched, 331 items x 8 samples, T=0.7; B timed on the L4 (785 s) and on an RTX 5070 Ti "
                                    "laptop; per-query latency not measured for Tiny Aya"}
(ROOT / "results/e5_roi.json").write_text(json.dumps(out, indent=1))
print("| Model | Verified | Single-DB | $ / 1k queries | Latency / throughput |\n|---|---|---|---|---|")
for m, v in out.items():
    if m == "assumptions":
        continue
    pct = lambda x: f"{100 * x[0]:.1f}% [{100 * x[1]:.1f}, {100 * x[2]:.1f}]" if x else "n/a"
    speed = (f"median {v['latency_s_median']:.1f} s, p90 {v['latency_s_p90']:.1f} s" if m == "command_a"
             else f"{v['trajectories_per_s']:.1f} trajectories/s batched on L4 ({v['l4_time']})")
    print(f"| {m} | {pct(v['verified'])} | {pct(v['single'])} | ${v['usd_per_1k']:.3f} | {speed} |")
assert out["command_a"]["usd_per_1k"] > 0
