# Claim → source map (iteration 0)

All paths are relative to the repo root. `results/` is the Lexsi results folder.

## Checked automatically

`python3 scripts/check_numbers.py` (run from `amazon/paper/iteration1`; `build.sh` runs it too) recomputes 41 numbers from `results/*.json` and checks that `main.tex` contains each exact string. Last run: **41/41 match**.

These cover:
- the audit rates in Table 1 and the abstract;
- the 43% relative cut;
- the database hole (10.3) and comparator hole (10.4);
- hard-coded IDs, 54 of 235;
- the E1 blind rates (29.2 / 0.8 / 0.24);
- verified accuracy (9.4 / 12.7 / 9.0);
- every bootstrap difference and McNemar p value;
- the training-reward shares (86%, 8%, 10.7%→5.9%);
- the Spider TS and lucky-share figures and both lucky ranges;
- the Command A ROI numbers.

Tables 1, 2 and the two appendix tables come straight from `scripts/make_tables.py`. Nothing in them is typed by hand.

## Checked by hand (not in results/*.json)

| Claim in paper | Value | Source |
|---|---|---|
| Rewards disagreed on ~7% of rollouts | 102 of 1,440 (B run; 104 in C run) | A1 replay, `amazon/PROJECT_REPORT.md` line ~513, quoting `progress.md` Nov 9 |
| Hand audit | 48 wrong trajectories, 18 lucky, 0 hacks | `results/manual_audit_summary.json` |
| AgentTune exploit | 3.10 = honest SQL on 314 yes items; patch 2.20; fixed next day | `results/e0_agenttune.json`, `docs/agenttune_sql_reward_issue.md`, AgentTune issue #11 / PR #12 |
| Test copies catch 54 of 103 base-blind mutants | 54/103 | `amazon/PROJECT_REPORT.md` (grep "54 of 103") |
| Period-edge copy (Appendix D) | 92.1% → 32.9%, 0 of 1,554 correct rejected | `results/e12_period_copies.json` |
| Curriculum: 89% of SFT single-DB passes are lucky on 36 prompts | 89%, 36 of 445 | `progress.md` (Nov 15 E14 entry) |
| Literal answers paid by single-DB | 1,302 of 1,302 | `results/a3_skyrl_audit.json` rex_single hack:literal |
| Set match pays every dropped DISTINCT | 203 of 203 | `results/e0_reward_audit.json` R_exec_set mutant:no_distinct (asserted in check script) |
| Training cost | about $11 L4 | Appendix C compute paragraph; `progress.md` cost lines |
| Split sizes | 1,302 / 907 / 331; 214 F4 test items | `PROJECT_REPORT.md` data section |

Each paragraph in `main.tex` has a `% src:` comment naming its files.
