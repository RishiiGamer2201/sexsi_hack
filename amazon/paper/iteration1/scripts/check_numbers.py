"""Recompute every headline number in main.tex from results/*.json and check the text says the same.

Run from amazon/paper/iteration1:  python3 scripts/check_numbers.py   (exit 1 on any mismatch)
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

# test-set accuracy: three training seeds (results/seeds_eval.json); seed 0 is e4_eval.json
se = J("seeds_eval.json")
seeds = [se["seeds"][k] for k in sorted(se["seeds"])]
assert len(seeds) == 3 and abs(seeds[0]["C_minus_B"]["diff_bootstrap95"][0] - e4["comparisons"]["C_vs_B"]["verified_diff_bootstrap95"][0]) < 1e-9
add("verified sft_ho", p(e4["sft_ho"]["verified"][0]) + "\\%")
add("verified B seed 0 (appendix)", "verifies " + p(e4["B"]["verified"][0]) + "\\%")
add("pooled verified C vs B", f"verifies {p(se['pooled']['C_verified'])}\\% of test samples against {p(se['pooled']['B_verified'])}\\%")
add("abstract pooled", f"({p(se['pooled']['C_verified'])}\\% vs {p(se['pooled']['B_verified'])}\\%)")
v = diff3(se["pooled"]["C_minus_B"]["diff_bootstrap95"]); add("pooled C-B", f"(${v[0]}$ [${v[1]}$, ${v[2]}$])")
per = lambda k: ", ".join(f"${100 * s[k]['diff_bootstrap95'][0]:+.1f}$" for s in seeds[:2]) + f" and ${100 * seeds[2][k]['diff_bootstrap95'][0]:+.1f}$"
add("C-SFT per seed", "(" + ", ".join(f"${100 * s['C_minus_SFT']['diff_bootstrap95'][0]:+.1f}$" for s in seeds) + " points)")
add("B-SFT per seed", "(" + ", ".join(f"${100 * s['B_minus_SFT']['diff_bootstrap95'][0]:+.1f}$" for s in seeds) + " points over SFT)")
add("C-B per seed", "C$-$B is " + per("C_minus_B") + " by seed")
sl = se["seed_level"]
add("seed-level C-B", f"${100 * sl['C_minus_B']['mean']:+.1f}$ [${100 * sl['C_minus_B']['t95'][0]:+.1f}$, ${100 * sl['C_minus_B']['t95'][1]:+.1f}$]")
add("between-seed SD", f"standard deviation of {100 * sl['C_minus_B']['sd']:.1f} points")
mdes = [100 * s["C_minus_B"]["mde_80power"] for s in seeds]
add("MDE", f"{min(mdes):.1f}--{max(mdes):.1f} points and the three-seed pool {100 * se['pooled']['C_minus_B']['mde_80power']:.1f} points")
v = diff3(e14["comparisons"]["Cmin_cur_vs_B_cur"]["verified_diff_bootstrap95"]); add("Cmin-Bcur", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
f3s = [f3, J("figure3_training_rewards_s1.json"), J("figure3_training_rewards_s2.json")]
runs = [r for f in f3s for r in f.values() if isinstance(r, dict) and "single_pass" in r]
assert len(runs) == 6
sp_, ls_, dis = [r["single_pass"] for r in runs], [r["lucky_share_of_passes"] for r in runs], [r["single_pass"] * r["lucky_share_of_passes"] for r in runs]
add("single pass range", f"{100 * min(sp_):.0f}--{100 * max(sp_):.0f}\\% of rollouts passed")
add("lucky share range", f"only {100 * min(ls_):.0f}--{100 * max(ls_):.0f}\\% of passes")
add("disagreement range", f"disagreed on about {100 * min(dis):.0f}--{100 * max(dis):.0f}\\% of rollouts")
add("lucky first half", f"from {p(f3['B']['lucky_share_first_half'])}\\% to {p(f3['B']['lucky_share_second_half'])}\\%")

# Spider
sp = s13["models"]
sc = s13["comparisons"]
add("Spider pooled TS", f"reach {p(sp['C_pool']['TS'])}\\% test-suite accuracy against {p(sp['B_pool']['TS'])}\\%")
v = diff3(sc["C_pool_vs_B_pool"]["TS_diff_bootstrap95"]); add("Spider pooled C-B", f"(${v[0]}$ [${v[1]}$, ${v[2]}$])")
add("abstract Spider", f"gained {100 * sc['C_pool_vs_B_pool']['TS_diff_bootstrap95'][0]:.1f} points")
g = [100 * sc[k]["TS_diff_bootstrap95"][0] for k in ("C_vs_B", "C_s1_vs_B_s1", "C_s2_vs_B_s2")]
add("Spider per seed", f"${g[0]:+.1f}$, ${g[1]:+.1f}$ and ${g[2]:+.1f}$")
ss = sl["spider_TS_C_minus_B"]
add("Spider seed-level", f"seed-level ${100 * ss['mean']:+.1f}$ [${100 * ss['t95'][0]:+.1f}$, ${100 * ss['t95'][1]:+.1f}$]")
v = diff3(s14["comparisons"]["Cmin_cur_vs_B_cur"]["TS_diff_bootstrap95"]); add("Spider curriculum", f"${v[0]}$ [${v[1]}$, ${v[2]}$]")
add("Spider B vs SFT", f"SFT's {p(sp['sft_ho']['TS'][0])}\\% ({p(sp['B']['TS'][0])}\\%, {p(sp['B_s1']['TS'][0])}\\%, {p(sp['B_s2']['TS'][0])}\\%)")
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

# iteration 1: mechanism (A1) and baselines (A4)
a1, a4 = J("a1_mechanism.json"), J("a4_baselines.json")
ec = a1["effective_copies"]
add("prompts with two copies", f"{ec['copies_per_prompt']['2']} of {ec['grpo_prompts']} training prompts got two copies")
add("copies killing a mutant", f"only {ec['copies_killing_a_mutant']} of the {ec['copies']} copies")
mon = a1["monitor"]
add("monitor B_cur", f"{p(mon['B_cur']['first10'])}\\% to {p(mon['B_cur']['last10'])}\\% ($\\tilde R$)")
add("monitor main B", f"{p(mon['B']['first10'])}\\% to {p(mon['B']['last10'])}\\% ($\\tilde R$)")
add("monitor main C", f"{p(mon['C']['first10'])}\\% to {p(mon['C']['last10'])}\\% ($R_{{\\text{{mean}}}}$)")
add("monitor Cmin_cur", f"{p(mon['Cmin_cur']['first10'])}\\% to {p(mon['Cmin_cur']['last10'])}\\% ($R$)")
rp = a1["replay"]
add("replay main", f"{rp['C']['signal_groups_C_mean']} of the main CF run's {rp['C']['groups']} groups against {rp['C']['signal_groups_B']}")
add("replay curriculum", f"{rp['B_cur']['signal_groups_C_mean']} against {rp['B_cur']['signal_groups_B']}")
fb = a4["family_blind_testops"]["pay"]
add("family-blind mutants/hacks", f"pay {p(fb['ALL/mutant']['cf_strict@dbs']['rate'])}\\% of mutants and {p(fb['ALL/hack']['cf_strict@dbs']['rate'])}\\% of hacks")
assert fb["ALL/correct"]["cf_strict@dbs"]["rate"] == 0
add("family-blind correct n", f"0 of {fb['ALL/correct']['cf_strict@dbs']['n']:,} correct")
f4 = a4["heldout_f4"]["pay"]
add("held-out F4 hacks", f"from {p(f4['F4/hack']['single_db']['rate'])}\\% to {p(f4['F4/hack']['cf_strict@dbs_random']['rate'])}\\%")
add("held-out F4 mutants", f"{p(f4['F4/mutant']['single_db']['rate'])}\\% to {p(f4['F4/mutant']['cf_strict@dbs_random']['rate'])}\\%")
cm = a4["compute_matched_single_db"]["row"]
add("compute-matched single DB", f"({cm['customers']} customers) passes only {p(cm['rate_ci95'][0])}\\% of mutants")

# LeakySQL pilot (results/leaky_eval.json, scripts/leaky_eval.py)
lk = J("leaky_eval.json")
la, lt, ld = lk["arms"], lk["train"], lk["diffs"]
add("leaky SFT cache read", f"seeded SFT reads it in {p(la['sft_leaky']['cache_read'][0])}\\% of test samples")
add("leaky test cache read", f"fell to {p(la['B_leaky']['cache_read'][0])}\\% and {p(la['Cmin_leaky']['cache_read'][0])}\\% of test samples")
v = diff3(ld["Cmin_leaky_minus_B_leaky"]["cache_read"]); add("leaky cache C-B", f"(C$-$B ${v[0]}$ [${v[1]}$, ${v[2]}$])")
add("leaky train cache read", f"from {p(lt['B_leaky']['cache_read_steps_1_10'])}\\% to {p(lt['B_leaky']['cache_read_steps_51_60'])}\\% and from "
    f"{p(lt['Cmin_leaky']['cache_read_steps_1_10'])}\\% to {p(lt['Cmin_leaky']['cache_read_steps_51_60'])}\\% of rollouts")
add("leaky paid", f"paid {lt['B_leaky']['cache_reads_paid']} of {lt['B_leaky']['cache_reads']} training cache reads")
add("leaky mean reward", f"mean reward of {lt['B_leaky']['mean_reward_cache']:.2f} against {lt['B_leaky']['mean_reward_other']:.2f}")
add("leaky R paid", f"$R$ paid {lt['Cmin_leaky']['cache_reads_paid']} of {lt['Cmin_leaky']['cache_reads']}")
add("leaky verified", f"from {p(la['sft_leaky']['verified'][0])}\\% (seeded SFT) to {p(la['B_leaky']['verified'][0])}\\% under $\\tilde R$ and "
    f"{p(la['Cmin_leaky']['verified'][0])}\\% under $R$")
v = diff3(ld["Cmin_leaky_minus_B_leaky"]["verified"]); add("leaky verified C-B", f"(C$-$B ${v[0]}$ [${v[1]}$, ${v[2]}$])")

bad = [(d, s) for d, s in checks if s not in TEX_FLAT]
for d, s in checks:
    print(("OK   " if (d, s) not in bad else "MISS ") + d + ": " + s)
print(f"{len(checks) - len(bad)}/{len(checks)} numbers match")
sys.exit(1 if bad else 0)
