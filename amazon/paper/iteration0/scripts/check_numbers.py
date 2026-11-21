"""Recompute every headline number in main.tex from results/*.json and check the text says the same.

Run from amazon/paper/iteration0:  python3 scripts/check_numbers.py   (exit 1 on any mismatch)
Numbers that come from logs not in results/ (A1 replay 102/1440, manual audit, AgentTune patch 2.20,
54/103 test-copy catch rate) are listed in notes/claim_source_map.md and checked by hand.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
RES = HERE.parents[2] / "results"
TEX = (HERE / "main.tex").read_text()
TEX_FLAT = re.sub(r"\s+", " ", TEX)
J = lambda n: json.loads((RES / n).read_text())

e0 = {(r["reward"], r["candidates"]): r for r in J("e0_reward_audit.json")["rows"] if r["family"] == "ALL"}
a3 = {(r["reward"], r["candidates"]): r for r in J("a3_skyrl_audit.json")["rows"]}
e1 = J("e1_blind_rate.json")
e4 = J("e4_eval.json")
e14 = J("e14/e4_eval.json")
s13 = J("e13_spider_ours.json")
s14 = J("e14_spider.json")
f3 = J("figure3_training_rewards.json")
a2 = J("a2_spider_lucky.json")["systems"]
roi = J("e5_roi.json")
at = J("e0_agenttune.json")
p = lambda x: f"{100 * x:.1f}"


def diff3(v):  # bootstrap triple -> "+1.9 [+0.6, +3.3]" in the tex's $..$ style
    return [f"{100 * t:+.1f}" for t in v]


checks = []  # (description, expected string that must appear in main.tex)
add = lambda d, s: checks.append((d, s))

add("mutants paid, single-DB", p(e0[("R_exec_rex", "mutant")]["rate"]) + "\\%")
add("mutants paid, CF blind", p(e0[("R_cf_strict@random", "mutant")]["rate"]) + "\\%")
add("hacks paid, single-DB", p(e0[("R_exec_rex", "hack")]["rate"]) + "\\%")
add("hacks paid, CF blind", p(e0[("R_cf_strict@random", "hack")]["rate"]) + "\\%")
assert e0[("R_cf_strict@random", "correct")]["rate"] == 0 and e0[("R_cf_strict@random", "correct")]["n"] == 2847
add("correct n", "0 of 2,847")
add("mutant pay, informed copies", p(e0[("R_cf_strict", "mutant")]["rate"]) + "\\%")
add("set match mutants", p(e0[("R_exec_set", "mutant")]["rate"]) + "\\%")
add("set+copies mutants", p(a3[("skyrl_cf_min", "mutant")]["rate"]) + "\\%")
assert e0[("R_exec_set", "mutant:no_distinct")]["rate"] == 1.0 and e0[("R_exec_set", "mutant:no_distinct")]["n"] == 203
add("all_customers survive", p(e0[("R_cf_strict@random", "mutant:all_customers")]["rate"]) + "\\% of \\texttt{all\\_customers}")
add("missing_refunds survive", p(e0[("R_cf_strict@random", "mutant:missing_refunds")]["rate"]) + "\\% of \\texttt{missing\\_refunds}")
hc = a3[("rex_cf_min", "hack:hardcoded_ids")]
add("hard-coded IDs kept", f"({round(hc['rate'] * hc['n'])} of {hc['n']})")
rel = 1 - e0[("R_cf_strict@random", "mutant")]["rate"] / e0[("R_exec_rex", "mutant")]["rate"]
add("relative cut", f"{100 * rel:.0f}\\% relative cut")
db_hole = e0[("R_exec_set", "mutant")]["rate"] - a3[("skyrl_cf_min", "mutant")]["rate"]
cmp_hole = a3[("skyrl_cf_min", "mutant")]["rate"] - e0[("R_cf_strict@random", "mutant")]["rate"]
add("database hole", f"removes {p(db_hole)} points")
add("comparator hole", f"removes {p(cmp_hole)} more")

# E1 blind rate vs size
e1r = {r["size"]: r["rate_ci95"][0] for r in e1["rows"] if r["family"] == "ALL"}
add("E1 blind rate S", f"{p(e1r['S'])}\\% of realistic buggy queries")
add("E1 blind rate M", f"against {p(e1r['M'])}\\% at 500")
add("E1 blind rate L (appendix)", f"{100 * e1r['L']:.2f}\\% at 5,000")

# test-set accuracy
for m in ("sft_ho", "B", "C"):
    add(f"verified {m}", p(e4[m]["verified"][0]) + "\\%")
c = e4["comparisons"]
v = diff3(c["B_vs_sft_ho"]["verified_diff_bootstrap95"]); add("B-SFT", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
add("B-SFT McNemar", f"$p = {c['B_vs_sft_ho']['mcnemar_p_sample0']:.3f}$")
v = diff3(c["C_vs_B"]["verified_diff_bootstrap95"]); add("C-B", f"${v[0]}$ [${v[1]}$, ${v[2]}$]".replace("$-", "$-"))
v = diff3(e14["comparisons"]["Cmin_cur_vs_B_cur"]["verified_diff_bootstrap95"]); add("Cmin-Bcur", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
add("single pass share", f"{100 * f3['B']['single_pass']:.0f}\\% of rollouts passed")
add("lucky share of passes", f"only {100 * f3['B']['lucky_share_of_passes']:.0f}\\% of passes")
add("lucky first half", f"from {p(f3['B']['lucky_share_first_half'])}\\% to {p(f3['B']['lucky_share_second_half'])}\\%")

# Spider
sp = s13["models"]
add("TS C", p(sp["C"]["TS"][0]) + "\\% test-suite")
add("TS B", p(sp["B"]["TS"][0]) + "\\% for the single-DB")
v = diff3(s13["comparisons"]["C_vs_B"]["TS_diff_bootstrap95"]); add("Spider C-B", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
v = diff3(s14["comparisons"]["Cmin_cur_vs_B_cur"]["TS_diff_bootstrap95"]); add("Spider curriculum", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
add("McNemar main", f"$p = {s13['comparisons']['C_vs_B']['TS_mcnemar_p_sample0']:.2f}$")
add("McNemar curriculum", f"$p = {s14['comparisons']['Cmin_cur_vs_B_cur']['TS_mcnemar_p_sample0']:.2f}$")
add("lucky share C vs B", f"{p(sp['C']['lucky_share_of_EX'][0])}\\% vs {p(sp['B']['lucky_share_of_EX'][0])}\\%")
v = diff3(s13["comparisons"]["B_vs_sft_ho"]["TS_diff_bootstrap95"]); add("Spider B-SFT", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
ls = [m["lucky_share_of_EX"][0] for m in s14["models"].values()]
add("small-model lucky range", f"{100 * min(ls):.0f}--{100 * max(ls):.0f}\\%")
pub = [s["lucky_share_of_EX_ci95"][0] for s in a2.values()]
add("published lucky range", f"{p(min(pub))}--{p(max(pub))}\\%")

# cost
add("Command A verified", p(roi["command_a"]["verified"][0]) + "\\%")
add("Command A $/1k", f"\\${roi['command_a']['usd_per_1k']:.2f}")
add("Tiny Aya B $/1k", f"\\${roi['B']['usd_per_1k']:.3f}")
ratio = (roi["command_a"]["usd_per_1k"] / roi["command_a"]["verified"][0]) / (roi["B"]["usd_per_1k"] / roi["B"]["verified"][0])
add("per-verified ratio", f"about {ratio:.0f}$\\times$")

bad = [(d, s) for d, s in checks if s not in TEX_FLAT]
for d, s in checks:
    print(("OK   " if (d, s) not in bad else "MISS ") + d + ": " + s)
print(f"{len(checks) - len(bad)}/{len(checks)} numbers match")
sys.exit(1 if bad else 0)
