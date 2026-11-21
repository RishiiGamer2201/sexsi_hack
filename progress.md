# Progress log

> **Rule: update this file after each and every step** (a run launched or finished, a bug found or fixed, a decision made, access changed). Add a dated entry at the top of the log, and keep "Current state" and "Next" accurate. Commit and push it with the work it describes.

## Current state (Nov 19)

- **Final result (Nov 19): Top 10% of 369 submissions**, Track 3 Agentic Fine-tuning, Lexsi AI Safety & Alignment Hackathon 2026 (Lexsi Labs with Cohere Labs and Hugging Face). Not selected for Stage 2. Certificate ID `LX26-SG3KM-YBE7G`, issued 19 Nov 2026, verify at hackathon.lexsi.ai/results. Project listed as "Counterfactual-DB SQL Rewards". Submitted 16 Nov ~14:15 IST; all artifacts public. The notes below are the Nov 9 state, kept for history.

- **All experiments done** (E0, E1, E2, E3 B + C, E4, E5, manual audit, plus zero-GPU E6 Spider, E7 SkyRL, E8 self-consistency, AgentTune patch). Training comparison is a null: B 12.7% verified, C 9.0%, SFT 9.4%.
- **Nov 14: D3 + D4 distillation from int4 Command A done (RunPod A100).** No student beats sft_ho: D3 3.7%, kd_a0 6.9%, kd_a1x (fixed logit distillation) 6.9%. B stays best. See the Nov 14 log entry.
- **VM `sqlcf-l4`: TERMINATED**, no job queued. Start with `bash scripts/vm_start.sh` only if a new run is approved.
- **Write-up:** ARTICLE.md revised per plan §9C (TL;DR leads with the audit, before/after table, hack catalogue, E6–E8, null paragraph, prior art, threats box, pre-registered §10). README judge's view updated. ABSTRACT.md not yet updated with E6–E8.
- **Report to user:** `reports/Strengthening results Nov 9.md`.
- **Hugging Face, org `sqlcf-lexsi`, ALL PRIVATE** (user: nothing public until approved):
  - Space `counterfactual-sql-demo`, dataset `counterfactual-sql-data`.
  - Models `tiny-aya-global-sqlcf-sft`, `-grpo-b`, `-grpo-c` (LoRA adapters + LICENSE + NOTICE + card).
  - Collection `counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4` with all five.
- **Licence ruling (organisers, Discord, Nov 9):** adapters of the gated base may be published with its licence included. During judging every artifact must be public, or gated with automatic approval; private or manual-approval repos count as missing.

## Next

Nothing pending. Round 1 is over and we did not reach Stage 2. The organisers offered feedback and technical help if we keep working on the idea. Possible follow-ups: evaluate the seed-1 B/C adapters stranded on the `sqlcf-l4` disk, or ask the organisers for feedback. The items below are the old pre-submission list.

1. **Submission pack ready (Nov 11): follow [SUBMISSION.md](SUBMISSION.md)**, which is laid out like the real form's pages. The form's HF Article URL is the project-page Space (`scripts/make_site.py`). Then `scripts/go_public.py --go` (adapters, dataset, Space, both collections, GitHub). The form says every repo must be public by Nov 15, 11:59 PM AoE.
2. Null decision made: **accept and polish** (user, Nov 9). No GPU runs; VM stays off.
3. (Done Nov 10) AgentTune#11 fixed upstream by PR #12.
4. Optional polish: demo "shaky answer" flag (D5).

## Log

### Nov 21

- **Amazon Trusted AI Symposium 2027 started (user's request).** Rules:
  - deadline Nov 30, 2026; submit by email to trusted-ai-symposium@amazon.com;
  - official NeurIPS 2025 LaTeX style (zip in `amazon/paper/`);
  - 4 pages, with references and appendices on extra pages;
  - the abstract in intro/methods/results/conclusions form;
  - author names, affiliations and emails;
  - non-archival; double submission OK.

  This replaces the Nov 11 "no Amazon" rule, which was only for the Lexsi deadline. Everything goes in `amazon/`. Downloaded third-party PDFs (`amazon/research_notes/pdfs/`) and the style zip are gitignored.
  - Step 1: full project report, `amazon/PROJECT_REPORT.md`.
  - Steps 2–3: NeurIPS 2020–2026 paper study, a study of the template and 4-page workshop papers, and past Amazon symposium papers. Notes go in `amazon/research_notes/` and are then merged into `amazon/NEURIPS_PAPER_RULES.md`.
  - Step 4: rules from `C:\developer\research_ai\paper-writing` that are missing from the rules file get added to it.
  - Diagrams in TikZ (user preference).
  - **Steps 1–4 done (Nov 21):**
    - `amazon/PROJECT_REPORT.md` (~17k words): every experiment, number and source, plus 22 inconsistencies between sources.
    - `amazon/research_notes/`: NeurIPS 2020–22 (13 papers), 2023–24 (12), 2025–26 (14); the template plus 8 four-page workshop papers; the past Amazon symposium (one earlier edition, Jan 2026 in New York, with 7 works found).
    - `amazon/NEURIPS_PAPER_RULES.md`: Part I has 274 rules with era conflicts resolved; Part II has 139 rules from the user's paper-writing guides, plus a conflicts list.
    - Template builds in WSL after `sudo apt install texlive-latex-extra cm-super`, with the `[preprint]` option, on US Letter and with 0 Type 3 fonts.

### Nov 19

- **Result: Top 10% of 369 submissions (not in Stage 2).** From the results page and the team certificate (ID `LX26-SG3KM-YBE7G`, 19 Nov 2026). The page says Stage 2 places were very limited and the organisers will give feedback or technical help if we continue. The certificate image is not committed: it stays with the team. Organiser on Discord (Nov 19): result tiers are top 5% / top 10% / top 25% / participation; only top 5% (~20 teams) go to the final stage. Judge feedback is available on request via a ticket in Discord #report_issues (the bot was timing out that evening). Mentorship is offered to any team that extends the work or aims for a publication.

### Nov 15

- **Aksh's checks (13:10–13:28 IST).** `devChaudhari7/rl-sql` returns 404 on GitHub (repo and user), so it is dropped from related work and references. It came from the Nov 9 research notes and was never verified. AgentTune issue #11 is now named in Appendix A, the AgentTune reference and the README (with PR #12). README brought in line with the paper: title, no arrows, a Spider GRPO-C vs GRPO-B row, and a link to the project page.
- **E14 curriculum pilot (Rishii's go, 15 Nov ~13:10 IST). This runs the §8 "next experiment", scaled down to fit the deadline.**
  - **Curriculum** (`scripts/curriculum.py`, no new sampling): from SFT-ho's existing 6 rollouts per GRPO prompt (T = 1.0), keep items where some but not all pass the original DB and at least 20% of those passes fail a copy. That leaves 36 of 445 items (F3 net revenue 14, F1 paying customers 11, F2 refunded category 11). On them, 89% of original-DB passes are lucky, against about 8% in the original GRPO runs.
  - **Runs:** B (`R_exec_rex`) against C-min (`R_cf_strict`), 1 seed, 60 steps, same config as the original runs. C-penalty and seeds 2–3 are dropped for time.
  - **Local GPU does not fit GRPO:** at `--vllm-mem 0.5` the vLLM KV cache needs 0.56 GiB and only 0.46 GiB is left, and two model copies alone take about 13.4 GB of the 16 GB.
  - **Temp VM:** `scripts/laptop_e14.sh` snapshots sqlcf-l4's disk, boots `sqlcf-e14` in the first zone with a free L4 (zone move approved by Rishii), runs both conditions, copies results back, and deletes the temp VM and snapshot. Then it merges and runs E4 + E13 generation locally. About 8.5 VM-hours (~$6.3).
  - **After the run:** §8 comes out of the article and a short results section replaces it (Rishii's call).
- **Shreshth's second round on the paper (15 Nov, ~13:00 IST).**
  - **Abstract** (ABSTRACT.md and the article): the Spider result now leads the training paragraph. C beats B by about 2 points of test-suite accuracy with fewer lucky passes, one seed, second seed under way. 353 words.
  - **Distillation removed** from the abstract, the introduction, §6 (now "Cost against Command A") and Appendix B (old B9 dropped, B10–B13 renumbered B9–B12). Also removed from README and SUBMISSION. The raw results (E9, D2–D4) stay in `results/` and git history.
  - **References** expanded: 36 entries with authors, full titles, venues and arXiv IDs. Added Spider, BIRD, GRPO, LoRA, DPO, VeriEQL, Command A, Tiny Aya, AuditKIT, ESM+ and SkyRL. In-text citations are now author-year.
  - **Project page** (`make_site.py`): paper layout. One 740px serif column (Times New Roman, or Tinos as its web fallback), justified text, left-aligned section headings, a small-caps abstract block, booktabs tables, figures with captions, small outlined link buttons. Bulma dropped.
- **Aksh + Shreshth follow-up (12:41–12:44 IST): links and the "synthetic" wording.**
  - **References are links.** Each arXiv ID and GitHub repo in the list is a link. On the project page every in-text citation (45 of them) jumps to its entry; checked in the rendered DOM, with no broken anchors. AuditKIT and SkyRL are now cited in the text.
  - **"Synthetic" fixed.** §3.1 no longer says "all our data is synthetic". It now names both kinds: synthetic for training, the audit and our test set, and real Spider data (Sections 4.4 and 5.4). The limitation now reads "Synthetic training data". The dataset card's "synthetic" stays, because the released data is synthetic; we do not redistribute Spider.
- **Limitations section removed (Shreshth, 12:56 IST).** §8 is now "The next experiment". The caveats tied to specific results stay where the result is stated: one seed (abstract, §5.3, §5.4), Spider as a transfer test rather than a leaderboard score (§5.4), and the scorer note (B4).
- **Second seed:** VM still in L4 stockout (375 tries by 12:14 IST). The driver keeps retrying until 16 Nov 06:00 IST.

### Nov 14

- **ARTICLE.md restructured as a paper (15 Nov, Shreshth's request).**
  - **Structure:** Abstract, Introduction with four contributions, Related work, Method, Reward audit, Training (with Spider transfer), Cost and distillation, Other things we tried, Limitations and the next experiment, Conclusion, References.
  - **Appendices:** A holds artifacts, licences and Lexsi tools; B holds every detailed table; C holds implementation notes.
  - **Style:** the main text has few numbers, no arrows or em dashes, and plain wording. Every number and table from the old version is kept, in the main text or the appendix.
  - **Project page:** `make_site.py` now takes the author line from the article subtitle.
  - **Abstract:** ABSTRACT.md rewritten in the same style earlier the same day.
- **Second training seed for B and C (team go, 14 Nov ~20:15 IST).** E13's C-vs-B gap uses only one training run each, so we are adding a second.
  - **Runs:** `scripts/vm_seed1.sh` runs GRPO-B, then GRPO-C. Both use the default config plus `--seed 1`. The flag changes the prompt order and the torch RNG; the vLLM engine seed is fixed by TRL.
  - **Driver:** `scripts/laptop_seed1.sh` runs unattended:
    1. retries the VM start until 16 Nov 06:00 IST;
    2. checks that the VM's SFT adapter md5 matches the local one;
    3. launches the runs and watches them;
    4. copies the adapters back and releases the autostop hold;
    5. runs the local merge, then E4 and E13 generation for B_s1 and C_s1.
  - **Status:** asia-south1-a has been in L4 stockout since 20:27 IST. Per the team rule we keep retrying and do not move zones.
  - **Cost:** about 7.5 VM-hours (~$5.5).
- **E13 done (19:23 IST, 36 min on the local 5070 Ti, $0).** Results in `results/e13_spider_ours.json`; trajectories in `results/spider_{base,sft_ho,B,C}.jsonl`. These were renamed from `traj_spider_*` so the `traj_*` globs in verify_all, evaluate.py and demo.py don't pick them up. Re-scoring is byte-identical.

  | Model | EX | TS | Lucky share of EX passes |
  |---|---|---|---|
  | base | 15.4 | 12.6 | 18.3 |
  | SFT | 38.5 | 29.1 | 24.4 |
  | B | 38.0 | 27.9 | 26.4 |
  | C | 39.1 | 29.9 | 23.6 |

  - **C vs B, TS:** +1.9 [+0.6, +3.3] (paired bootstrap over questions). EX +1.1 [−0.3, +2.5]. Lucky rate −0.8 [−1.8, +0.2]. McNemar on sample 0: p = 0.14.
  - **B vs SFT, TS:** −1.2 [−2.5, +0.1].
  - **C vs SFT, TS:** +0.7 [−0.5, +2.1].
  - **The order flips relative to our own test set (C −3.7 there).** One seed each and not pre-registered, so suggestive only.
  - **ARTICLE changes:** new section E13 (§8), plus E13 in the TL;DR, the audit table, licences (§5) and limitations.
- **E13: our models on a real benchmark (Spider dev + Zhong test-suite DBs), started on the local GPU at 18:47 IST.** Team asked for a real-world test without building data. New `scripts/spider_eval.py` (+ `scripts/local_spider.sh`): base, sft_ho, B, C each answer the 1034 Spider-dev questions (4 samples, T = 0.7, same agent loop and prompt as E4 except the schema), graded EX (original DB) vs TS (original + every test-suite DB) with E6's scorer. Questions from HF `xlangai/spider` (CC BY-SA 4.0) in `external/spider_hf/`, checked 1034/1034 against ESM+ gold. Smoke (sft_ho, 8 questions × 2) passed: 6/16 TS. Out of distribution for the trained models (they saw one retail schema), so a transfer test. Result: `results/e13_spider_ours.json`.
- **D3 + D4: Command A int4 as a local teacher, text and logit distillation. Done; negative result. B (12.7%) is still the best model.**
  - **Teacher:** `gghfez/command-a-03-2025-AWQ` (int4 AWQ W4A16, 68.2 GB, downloaded pre-quantised, no quantisation by us), vLLM 0.22.1 on one RunPod A100 SXM 80 GB (`--gpu-mem 0.95 --max-model-len 3072 --eager`; 57.8 GiB weights, 60k-token KV cache). About 2 h of pod time for teacher, training and eval. Runbook: `docs/RUNPOD_INT4_TEACHER.md`, `scripts/runpod_teacher.sh`.
  - **int4 vs API on the test set** (`results/e5_int4_accuracy.json`): 77.0% verified [72.2, 81.2] vs 81.0%, −3.9 pts, McNemar p = 0.047; most of the gap is F1 (100% → 83.3%). `has_sql` 100%, lucky 6 vs 6.
  - **D3 filter on the 353 train items** (`results/d1_teacher_filter_int4.json`): 208 verified (API 211), 47 lucky (API 47); `cancelled` filter in 308 answers (API 324). The teacher also saved top-20 log-probs plus token ids per step (`results/teacher_command_a_int4.logprobs.jsonl`, 353/353 rows, tokens rebuild the text in 353/353).
  - **Students** (Tiny Aya, LoRA r=16, 2 epochs, lr 1e-4, trained on the pod's A100; verified on 331 × 8, in `results/e4_eval.json`):

    | Model | Data / loss | Verified |
    |---|---|---|
    | `sft_distil_int4` (D3) | int4 teacher's verified answers, reformatted (TRL SFT) | 3.7% [3.0, 4.5] |
    | `kd_a0` | teacher's exact text, CE only (`scripts/logit_distil.py --alpha 0`) | 6.9% [6.0, 7.9] |
    | `kd_a1` | + KL to teacher top-20, `--align start` | 1.2% [0.9, 1.7] |
    | `kd_a1x` | + KL, `--align exact` | 6.9% [6.0, 8.0] |

    D3 vs D2 +0.4 [−1.0, +1.8] (quantisation is not the cause). kd_a1x vs kd_a0 +0.1 [−1.0, +1.2]; kd_a1x vs sft_ho −2.5 [−4.1, −0.9].
  - **Bug found and fixed in `logit_distil.align`:** it kept a position when the teacher and student tokens started at the same character, without checking that they were the same token (teacher `.` vs student `.custom`). On 22% of kd_a1's 34,205 KD positions the target's top token was not the text's token (17.7%: absent from the target). kd_a1 learned those targets: 35% of answers without SQL, 60.5% of final SQL fails to run, 517 `--` comments, 343 `'canceled'` filters. Fix: `--align exact` (default) keeps a position only if the teacher's sampled token is the student's token; 72% of positions kept, mapped mass 99.7%, target ≠ text on 0.9%. Regression test in `tests/test_logit_distil.py` (4 pass).
  - **Why text distillation fails:** the teacher's habits transfer. Final SQL with a `cancelled` filter: sft_ho 17%, kd_a0 67%, kd_a1x 51%, D3 65%. Final answers are about 2.4× longer than gold. The counterfactual filter keeps these answers because the filter changes no result on the train DBs. A fix would be data selection (drop teacher answers whose filters differ from gold), not a different loss.
  - Write-up for the team: https://claude.ai/artifact/MA5jpqHm7FtoRNaLbLUEox. ARTICLE.md not changed. Adapters are not pushed to HF (negative results; local in `runs/{sft_distil_int4,kd_a0,kd_a1,kd_a1x}`).
  - **Merged into main (Rishii).** ARTICLE.md: D3 + D4 subsection under E9 plus one sentence in the 60-second view; project page Space rebuilt. `verify_all.py` on Python 3.14 regenerates `e4_eval.json` with identical values (key order only), and `d1_teacher_filter.json` / `e12_period_copies.json` now include the new field and models; regenerated files committed so verify_all passes.
  - `results/e4_eval.json` rescored with the new trajectories (Python 3.12: all earlier models and comparisons unchanged); `verify_all.py` now also reproduces the D3 filter and the int4 accuracy file.

### Nov 12

- **Article as a project page (Shreshth, team chat Nov 12: "html with tex compilation", Nerfies-style).** New `scripts/make_site.py`: ARTICLE.md becomes a Bulma hero with Code/Demo/Dataset/Models buttons, the article body (marked.js), KaTeX math (cut out before Markdown parsing so `_` survives; prices like $0.57 are left alone), the figures copied in, and BibTeX. Pushed to the static Space `sqlcf-lexsi/counterfactual-sql-article` (private); added to `go_public.py`. Checked in headless Edge at 1280 px and 500 px (9 formulas, 3 figures, no KaTeX errors). SUBMISSION's HF Article field now points at this Space (organisers: an HTML page on HF or MD on GitHub is accepted).
- **D1 done** (`results/d1_teacher_filter.json`, teacher answers in `results/teacher_command_a.jsonl`): 353/353 calls, no quota stop.
  - Single-DB filter keeps 258 teacher answers (73.1%); the counterfactual filter keeps 211 (59.8%).
  - **47 lucky answers (18.2% of what a single-DB filter keeps) are wrong on the copies** and would have gone into distillation data.
  - By family (n / single / verified): F1 152 / 111 / 88, F2 81 / 27 / 3, F3 120 / 120 / 120. No smuggled answers.
- **D2 data fixed before training:** the first `build` dropped rejected items (211 rows), which confounds data size with the teacher and leaves F2 with 3 rows. Now the 142 rejected items keep sft_ho's gold trajectory: 353 rows, all prefixes identical to `data/sft.jsonl`, 211 endings replaced by the teacher's plan + SQL.
- **D2 done (local RTX 5070 Ti):** SFT 1205 s. The merge crashed the WSL VM once (the VM restarted; a retry worked). The eval ran out of GPU memory at `--gpu-mem 0.75` because another project's Windows process (`voxsplit`) holds part of the card; it was left alone, and the eval ran at 0.6 (649 s).
  - **sft_distil 3.3% verified [2.7, 4.0] vs sft_ho 9.4%: −6.2 pts [−8.3, −4.1], McNemar p < 0.001.** Silent errors 76.2% vs 65.4%. F1 falls from 30.9% to 4.2%.
  - Cause: Command A adds `status != 'cancelled'` in 325 of 353 answers (gold: 71). 186 of the 211 verified teacher endings have it, because on those items it never changed a result on any DB. The student writes it in 56% of its test answers (sft_ho 14%). All F1 sample-0 losses are `F1_category_buyers` ("count orders of any status").
  - Written up as ARTICLE E9, the 60-second view, the README table, an ABSTRACT sentence and SUBMISSION facts. The distilled adapter is not pushed to HF (a negative result; local in `runs/sft_distil`).
  - verify_all OK (every results/*.json reproduced), 10 tests pass, abstract.txt 482 words. HF dataset (still private) re-pushed with the teacher answers, D1 result, `sft_distil.jsonl` and `traj_sft_distil.jsonl`; card updated.
- **Aksh's three items (from the team PDF), started on the user's "Do all 3":**
  - **E10, DPO from one checkpoint (std vs counterfactual labels):** pairs come from sft_ho's 2670 GRPO-prompt rollouts (`scripts/dpo.py pairs`). Std has 420 pairs and cf has 351; none were dropped for length.
    - TRL's DPOTrainer ran out of memory at step 0 every time. WSL reported it as "CUDA driver error: device not ready": the 262k-vocab logits over a ~1600-token sequence (prompt ~1270 tokens) are about 10 GB.
    - Replaced with a short DPO loop in `scripts/dpo.py`. It keeps logits only after the prefix that chosen and rejected share, which is the same loss, and computes reference log-probs once with the sft_ho adapter. Training now runs (loss 0.69 to 0.26 by step 13). Running on the local GPU: `scripts/local_dpo.sh`, which trains, merges and evals both runs.
  - **E11, partial credit (`scripts/partial_credit.py`, CPU), done.** Partial credit gives 6–8 pts more GRPO groups a signal, but pays mutants 0.66 against 0.30 for the binary reward, and pays literal smuggling 0.86 under P_cf against 0 under strict. AUROC is unchanged. Side finding: C's `R_cf_mean` put lucky rollouts above the group mean 59% of the time; strict never does. No GPU run, because the audit already rules it out.
  - **E12, period-edge copies (`scripts/period_copies.py`, CPU, 19 s), done.** Date bugs generated from 777 year-filtered audit queries were paid 92.1% by one DB and 91.4% by the existing copies; with one period-edge copy, 32.9%. 0/1554 correct queries rejected. On real answers it rejects only 2/305 (B), 2/218 (C) and 1/223 (sft_ho) verified test answers, and 4/998 GRPO rollouts. All are order date used instead of payment date.
  - E11 and E12 are in ARTICLE and verify_all, and on the dataset card.
  - **E10 done (local GPU; training 741 s std, 660 s cf).** Verified: sft_ho 9.4%, dpo_std 9.7%, dpo_cf 8.1%. cf vs std −1.6 pts [−2.6, −0.6], McNemar on sample 0 p = 0.40. Lucky passes 4.5% for both.
    - cf's lower silent-error rate (55.1% vs 62.4%) comes from more invalid tool calls (27.4% vs 20.0%), not from fewer wrong answers.
    - Only 30 cf pairs reject a lucky answer. F1 falls in both runs.
    - Written up as ARTICLE E10, a README row and SUBMISSION facts. The adapters are not pushed (local in `runs/dpo_{std,cf}`).

### Nov 11

- **Rishii's task from the team notes (Sexsi Researchers PDF): distil Command A?** Checked on the Hub (hackathon token):
  - Neither model fits our hardware (1 L4, 24 GB; the 2-GPU request was denied), so the "quantised model" route is out:
    - `CohereLabs/c4ai-command-a-03-2025` is 111B parameters, 222 GB in bf16, about 60 GB even at 4-bit;
    - `CohereLabs/command-a-plus-05-2026-w4a4` is 219B parameters, 132 GB already quantised.
  - The only route is the Cohere API (`scripts/e5_command_a.py` takes `--items`).
  - Our train items already have gold SQL, so distilling Command A's SQL alone adds nothing over SFT on gold.
  - What could add something:
    - D1 (API only, no GPU): Command A writes a plan + SQL on the 907 train items, and we measure how many teacher answers a single-DB filter would keep that the copies reject.
    - D2 (L4): SFT Tiny Aya on the verified teacher traces and compare with `sft_ho` (9.4%).
  - Not started: waiting for the user's go (trial-key quota; GPU spend). The PDF's "$4.25" is now $4.24.
- **D1 + D2 approved (user); deadline extended to Nov 15 AoE.**
  - D2 runs on the local RTX 5070 Ti (free), not the VM. The VM stays TERMINATED.
  - New `scripts/distil.py` (`items` / `score` / `build`): the teacher answers the same 353 items as `sft_ho`; D2 data rebuilds `data/sft.jsonl` with the same seed and check queries, swapping in the teacher's verified SQL with its plan in the final turn.
  - `e5_command_a.py --plan`; `scripts/local_distil.sh` (SFT, eval, scoring).
  - `evaluate.PAIRS` adds sft_distil vs sft_ho and B vs sft_distil. `verify_all.py` reruns D1.
  - Pilot of 3 calls: plans sensible, all 3 verified. Full teacher run started: 353 calls at T=0.3.
- **Form matched (user sent screenshots of the real form).** The form asks for a separate HF model collection and HF dataset collection, a required HF Article URL, a Discord username, and checkboxes. Changes:
  - New private collection `counterfactual-sql-data-rollouts-and-traces-6af479430243b7731f85d144` holds the dataset.
  - The model collection now holds the 3 adapters + the Space; the dataset was removed from it.
  - Both collections are set by `push_models.py --collections-only`.
  - `hf_links.py` (all cards), `go_public.py` (both collections), ARTICLE header + §6/§7 and README updated.
  - `make_hf_article.py` also writes `runs/abstract.txt` (plain text for the form).
  - SUBMISSION.md rewritten page by page.
- **Lexsi only (user): no Amazon symposium, no NeurIPS-style paper.** Removed `paper/` and its links (ARTICLE, README, SUBMISSION); ARTICLE §2 keeps the KaTeX reward math (Markdown + KaTeX, per Shreshth). HF readiness: new `scripts/hf_links.py` gives every HF card (3 adapters, dataset, Space) the same block of track, team handles and cross-links; model cards gain a "Use" snippet (base + PeftModel), dataset card a load snippet, Space card `short_description` + tags; `push_space.py` default now ships all 5 deployed runs. Only the README.md files were re-uploaded, repos stay private. `make_hf_article.py` now loads figures from the HF dataset (`resolve/main/results/...`). All 5 cards read back identical; Space RUNNING. `verify_all.py` OK; 9 CPU tests pass, `tests/test_precision.py` needs torch so runs in `.venv-train` (passes).
- **LaTeX write-up** (superseded, removed same day, see above).
- **Submission prep (Shreshth: get everything ready now).**
  - Added `SUBMISSION.md` (every form field + go-live order + checklist), `scripts/go_public.py` (dry run shows all 6 HF items and GitHub still private), and `scripts/make_hf_article.py` (ARTICLE → `runs/hf_article.md` with absolute links).
  - ARTICLE: DRAFT banner replaced by links, all HF/GitHub links clickable, figures 1–3 embedded, §4 licence line updated to the organisers' ruling, §12 HF handles (Rishii = @LogicPalette).
  - Rounding fix: Command A is $4.2445 per 1k queries, so $4.24 (was $4.25) and $5.24 per 1k verified (was $5.25), in ARTICLE, README and ABSTRACT.
  - Git history scanned (61 commits): no tokens or keys. Commit author email will be visible once the repo is public. Removed a stray empty file `0`.
  - `verify_all.py` OK, 9 tests pass, abstract 491 words.

### Nov 10

- **Team lead is Shreshth** (per Rishii; name spelling fixed from "Rishi"). ARTICLE §12 said "Rishii (lead)"; fixed. "Lead's OK" notes in plan/progress were Rishii's rules, now say so. GCP quota: Vertex serving L4 case #77369396 approved 1→2 (unused); CE 2-GPU request denied (unneeded); credit left ₹2,972.81; VM TERMINATED.
- **AgentTune#11 closed as fixed.** Maintainer aryapratinavseth merged PR #12 (`e56a109`, 07:13 UTC) with `_has_real_where`, opt-in `result_match_reward`, `tests/test_sql_reward_hacking.py`, and a CHANGELOG entry citing #11. No comments on the issue. Their PR also fixed a second bug we had not seen: real rollouts store tool output as `str(result)`, so `query_reward` read every result as "no rows". Our training never used AgentTune's SQL reward, so our runs are unaffected. ARTICLE §3 updated.

### Nov 9

- **User decisions + follow-ups.**
  - AgentTune issue **posted** from RishiiGamer2201: https://github.com/Lexsi-Labs/AgentTune/issues/11 (self-contained repro, checked against the installed package: 3.1 / 3.1; patch inlined). Patch comment no longer points at our private doc; test and repro rerun, same numbers.
  - **Command A price confirmed** from the user's Cohere dashboard screenshots: trial key, real charge $0.00; run-day usage 222,578 input / 85,815 output tokens vs our logged 220,580 / 85,348 (within 1%; the extra is probe calls). List price $2.50 / $10.00 per 1M confirmed, so $4.27 vs our $4.24 per 1k queries. Note added to ARTICLE E5.
  - E6 results file now stores question indices only (ESMp has no licence, so its SQL text is not redistributed); same numbers, 292K → 72K.
  - **HF dataset re-pushed, still private** (45 files, includes a2/a3/a4 results; card lists them).
  - Null: accept and polish. Go-public: right after submission.

- **Plan §9 A2–A5 and C1–C6 done (zero GPU).** Commit has scripts, results and write-up.
  - **A2 / E6 Spider dev** (`scripts/a2_spider_lucky.py`, `results/a2_spider_lucky.json`): 8 published systems' predictions (ESM+ repo) scored on the original DB vs Zhong et al.'s test-suite DBs. Lucky share of EX passes 8.1% (Graphix) to 14.9% (Claude). A hand check of 40: 27 row-count, 13 value differences; mostly real bugs, some ties or ambiguous gold. Our strict comparator keeps DISTINCT, so absolute EX/TS sit below the official script.
  - **A3 / E7 SkyRL-SQL** (`scripts/audit_skyrl.py`; comparison transcribed from SkyRL @ d870046, not executed): pays 37.5% of mutants and 53.2% of hacks; with copies 27.2% / 1.9%; with copies + strict 16.8% / 1.9%. Comparator hole = dropped DISTINCT (188/203).
  - **A4 / E8 self-consistency** (`scripts/a4_selfconsistency.py`): majority vote over 8 samples lifts B 13.9→16.9%, C 6.3→13.6%, SFT 8.5→11.8%; voting on 5 DBs adds nothing over 1 DB (±1 pt). Shaky flag (share < 0.5) recall 53–59%, precision 94–98%, no gain from extra DBs. Reported as a null.
  - **A5 AgentTune** : `patches/agenttune-sql-reward-hardening.patch` (WHERE must name a column; opt-in `result_match_reward`), `scripts/agenttune_repro.py` (hack 3.10 → 2.20 patched; residual `customer_id > 0` hack 3.10, caught by result match), `tests/test_agenttune_reward.py` (patches a temp copy; vendor untouched). Issue draft in `docs/`, not posted. `load_agenttune_sql` takes a path now. Tests: 9 passed (test_precision.py needs torch, skipped in `.venv`).
  - `verify_all.py` now also reruns E7 and E8.

- **Deep research done** (4 parallel tracks: literature, training techniques, cheap extensions, framing/judging). Report: `reports/Stronger counterfactual SQL entry.md`; notes in `research_notes/`. Summaries added to research.md §9 (prior art, why the null, real-benchmark routes) and plan.md §9 (A–D action plan).
  - Judging is official: validity check, then double-blind scoring on write-up clarity, practical usefulness, code quality and overall review. Before/after metrics and "meaningfully better for usage" are required. Shortlisted teams get Nov 16–21 and $200 HF credits.
  - Closest work: ReViSQL (33% of positive SQL rewards are false positives, at 235B) and DualSQL (stricter matcher: +0.4 EX, the same near-null pattern). Must cite Zhong 2020 test suites.
  - **Replay of the training logs (A1):** lucky rollouts 7.1% (B) / 7.2% (C); rollouts that fail the original but pass a copy 0.1% / 0.3%. So the report's "C was partly lenient" hypothesis is refuted, and C was truly stricter. Training prompts passed the original DB about 86% of the time, so most groups had no gradient and few lucky passes. That is why the stricter reward had little to act on.
- **HF org members:** AkshAgg and hi-phi-r25i joined `sqlcf-lexsi` (API member list: AkshAgg, LogicPalette, hi-phi-r25i). Space, dataset and models still private.
- **Model repos pushed, private:** `scripts/push_models.py` uploads the three LoRA adapters (sft_ho, B, C; no `ref/`, no `training_args.bin`) with the base model's CC-BY-NC-4.0 text as `LICENSE` (`docs/LICENSE-CC-BY-NC-4.0.txt`), a `NOTICE` naming Cohere's licence addendum and Acceptable Use Policy, and a card (base_model, G3 label, verified / single / silent error / F4 with 95% CIs), plus B and C's provenance, config and training stats. It also builds one private collection with Space, dataset and the 3 models. Verified via the API: all 6 private, models not gated. `--public --gated` will make the models public with automatic-approval gating, per the organisers' ruling.
- **L4 re-timing done (ROI item 1):** GRPO-B's 331 x 8 test generation took 785 s on the L4 vs 524 s on the laptop (ratio 1.50), same accuracy (12.5% vs 12.7% verified; `results/e5_l4_check.json`). VM TERMINATED after copy. ROI now priced at L4 speed: Tiny Aya B $0.061 per 1k (SFT $0.054, C $0.052, scaled by the ratio) vs Command A $4.25: about 70x cheaper per query, 11x per verified answer. Article, README and abstract updated.
- **README "judge's 60-second view" and ABSTRACT.md (about 430 words) written.** Correction: Command A's F2 failure is mostly caught by the single-DB check too (32/36); the counterfactual copies catch the other 4 lucky passes. Article and abstract say so.
- **Manual audit done:** 48 wrong test trajectories (16 each from sft_ho, B, C; 6 lucky passes + 10 other per model; seed 0, stratified by family), labelled with NL2SQL-BUGs categories (`results/manual_audit.jsonl`). Top errors: `order_date` for payment date 11, value linking 7, extra status filter 6. All 18 lucky passes are real semantic bugs; none is smuggling or hacking.
- **L4 re-timing started** for the ROI table (`scripts/vm_time_l4.sh`: merge B on the VM, same 331 x 8 eval, autostop with hold). Per-query latency for Tiny Aya is left as future work (ARTICLE §10).
- **GRPO-C done and evaluated: the training comparison is null.** VM TERMINATED by autostop after the watcher copied C's adapter, logs and reward log (hold file released).
  - Test verified: SFT 9.4%, B 12.7%, **C 9.0%**. C vs SFT −0.5 pts (p=0.21); C vs B −3.7 pts [−5.3, −2.3] (p<0.001).
  - H4 not met: silent error C 61.2% vs B 64.0%, McNemar p=0.61 (bootstrap −2.9 pts [−5.3, −0.5]); C's drop comes with lower accuracy.
  - H5: no held-out-family gain (F4: SFT 9.2%, B 9.9%, C 8.8%). H6: no literal smuggling by any model (0/2648).
  - Lucky passes on test 5.1% for SFT, B and C. Figure 3: B and C rewards differed on only about 7% of training rollouts (lucky share 8.2% vs 8.3%; both fell over training), so the two runs saw almost the same signal.
  - G3: B released as improved, C labelled null. One seed per condition, so the B-C gap may be run variance.
  - ARTICLE.md updated with all C and E5 numbers; `verify_all.py` passes with every model.
- **E5 done: Command A on all 331 test items** (single-turn, schema in the prompt, 1 sample per item, T=0.7):
  - verified **81.0%** [76.4, 84.8], single-DB 82.8%, lucky passes 1.8%. By family: F1 100%, F2 0%, F3 64%, F4 95%. Silent error is 0 by definition (no tool calls), so it is not comparable.
  - ROI (`results/e5_roi.json`): Command A $4.25 per 1k queries (median 9.7 s, p90 42 s); Tiny Aya B $0.04 per 1k. Per 1k *verified-correct* answers: Command A about $5.2, B about $0.32, but B's 12.7% accuracy is far from usable.
- **While GRPO-C trains (step 46/60 at 05:17 UTC):**
  - `scripts/figure3.py`: per-step share of training rollouts paid by the single-DB check but failing a counterfactual. B: 86% of rollouts pass the original DB; 8.2% of those are lucky (10.7% in the first half, 5.9% in the second).
  - `scripts/push_dataset.py`: **private** HF dataset `sqlcf-lexsi/counterfactual-sql-data` (items, DBs as one tar.gz per split, SFT data, results, B's rollout log). Re-run after C and E5.
  - `evaluate.py`: comparisons now also test silent error (McNemar + bootstrap), since H4 was pre-registered on it. B vs sft_ho silent error −1.4 pts [−3.6, +0.9], p=0.06.
  - `ARTICLE.md`: HF Article / README draft (12 sections, C and E5 cells marked TBD).
  - `vm_autostop.sh` waits (max 30 min) while `runs/HOLD_AUTOSTOP` exists, so the laptop watcher can copy C's adapter and logs off before the VM powers down.
  - E5 at 170/331. Command A calls take median 10 s, p90 38 s, so the run is slow from model latency, not only rate limits.
  - `scripts/e5_roi.py`: ROI table from billed tokens ($2.50 / $10.00 per 1M) and measured local generation time x GPU $/hr. Partial: Command A $3.94 per 1k queries; Tiny Aya B $0.04 per 1k (5070 Ti throughput priced at the L4 VM rate, $0.74/hr).
- **E4 for GRPO-B done** (local merge 129 s, generation 524 s; 331 test items x 4 samples):
  - verified (passes original + all counterfactual DBs): base 0.9%, sft_ho 9.4%, **B 12.7%** (B vs sft_ho +3.2 pts, 95% CI [1.8, 4.8], McNemar p=0.006).
  - inflation (single-DB pass minus verified): sft_ho 5.1%, B 5.1%, so GRPO with the single-DB reward raised accuracy but not the lucky-pass rate. C (R_cf_mean) is the test of whether that drops.
  - silent error (tools all ran, SQL given, still wrong): sft_ho 65.4%, B 64.0%.
- **GRPO-B done:** 60/60 steps in 3.5 h (12,561 s), adapter saved; the VM chain started GRPO-C at 02:36 UTC (step 36/60 at 05:00 UTC). B's adapter was copied to the laptop for a local fp16 merge and E4.
- **Demo rebuilt without Gradio.** Gradio-Lite failed in the browser (its gradio pins `huggingface-hub<1.0`, the runtime has 2.4.0; Gradio-Lite's last release is Sep 2025).
  - Now `demo/index.html` loads pinned Pyodide 0.27.7 and runs `sqlcf/demo.py` (plain Python: scoring core plus a JSON API). The UI is hand-written HTML. `app.py` was removed.
  - Checked headless in Node with Pyodide 0.27.7 (`runs/pyodide_test/test.mjs`): the same showcase checks and rewards as desktop Python.

- **Credentials set by the user** in `.secrets.env` (gitignored): `CO_API_KEY` (Cohere trial) and `HF_TOKEN_HACK` (account LogicPalette, write only on org `sqlcf-lexsi`; plus "repos created by this token" in the personal namespace). The CVPR token is never used.
- **HF org `sqlcf-lexsi`** created by the user. Members to invite: AkshAgg, hi-phi-r25i (in the web UI; the token has no member permissions).
- **Licence question posted** in Discord #hackathon-lexsi to @_1024_m (adapters un-gated or gated?). Waiting for the reply.
- **Demo Space: `sqlcf-lexsi/counterfactual-sql-demo`, private, static.** HF now bills Gradio and Docker Spaces (402 for free orgs and for free personal accounts), so the same `app.py` runs in the visitor's browser via Gradio-Lite 5.45.0 (Pyodide; SQLite in WebAssembly). `scripts/push_space.py` builds and uploads it.
- **E5 started:** Command A (`command-a-03-2025`) on the 331 test items, single-turn, T=0.7 (`scripts/e5_command_a.py`). A 3-item trial was 3/3 verified, at about 10 s and about 670 input / 155 output tokens per call.

- **Gradio demo: `app.py`** (CPU only; needs `data/test`, 1.2 MB, and `results/traj_*.jsonl`).
  - Pick a test question and a recorded run, or type your own SQL. It shows the per-DB checks (original plus each counterfactual) and the score each reward function gives.
  - Questions with a run that the single-DB reward accepts but a counterfactual rejects are listed first: 72 of 331.
  - Example: on `F1_category_buyers|electronics|2024|S_s501`, `sft #7` filters `o.status` although the question says "any status". It passes the original DB, so R_exec_rex = 1; the `flip_status` counterfactual catches it, so R_cf_mean = 0.75 and R_cf_strict = 0.
  - Not deployed yet: a Space needs the hackathon HF token (not the CVPR one).
- **`verify_all.py`:** reruns E0, E1, the AgentTune audit and the E4 scoring, then checks `git diff` on `results/*.json`. It passes; every committed number reproduces exactly (17 s, CPU).
- **Blocked on user credentials:** E5 ROI needs a Cohere trial key; HF Space and collections need the hackathon HF token.

- **Gate G1 passed: reward form for C frozen as R_cf_mean.** From 240 GRPO-B rollouts (40 groups of 6, first 10 steps), counting groups with non-zero reward variance:
  - R_cf_mean 8/40, R_cf_soft 8/40, R_cf_strict 5/40 (R_exec_rex 8/40). FN on gold is 0 for every form (E0), so the count decides.
  - Mean and soft tie; mean stays, since GRPO-C was already set up for it and it is the simpler form.
- **GRPO-C chained after B on the VM** (`scripts/vm_chain_c.sh`), with no stop/start in between, because a restart risks hours of L4 stockouts.
  - B's `vm_grpo.sh` wrapper was killed so its autostop cannot fire between the runs. B's train.py keeps running.
  - C uses identical args and the same SFT adapter. The VM autostops after C, about 6.5 h from now.

- **GRPO-B smoke test passed.** The first 96 rollouts average 0.80 R_exec_rex, so vLLM is serving the trained weights; base weights would give about 0.01.
  - Logged step rewards 0.92 / 1.0 / 0.5. Steps take 200-215 s, so 60 steps is about 3.4 h.
  - Policy entropy is low (0.01-0.02 at T=1.0); 3 of 16 early groups have non-zero reward variance.
- **G1, first pass (96 rollouts, 16 groups):** every form ties at 3/16 non-zero-variance groups (mean, strict, soft, and R_exec_rex). Too few to decide; rerunning at 240 rollouts. If they still tie, R_cf_mean stays, as GRPO-C already uses it.

- **VM started** after 4 more stockouts; the held-out SFT adapter was uploaded, and **GRPO-B launched** at 23:06 UTC (Nov 8).
- **Stale-log bug, caught before G1.** The aborted 15:01 GRPO-B run had left `runs/grpo_B_rewards.jsonl` (24 rollouts) and `runs/grpo_B/trajectories.jsonl`, and the reward log is opened in append mode.
  - Both were moved aside on the VM (`runs/stale_grpo_B_*_1501.jsonl`) before the new run's first reward write.
  - Fix: `vm_grpo.sh` now moves any leftover reward log and output dir aside at start, so GRPO-C cannot hit the same thing.

- **E4, held-out SFT (`sft_ho`)** (331 test items x 8, T=0.7). B and C start from this model, so it is now the SFT baseline.

  | Metric | Base | SFT (all templates) | SFT held out |
  |---|---|---|---|
  | Verified | 0.009 | 0.117 | **0.094** [0.084, 0.106] |
  | Single-DB | 0.014 | 0.151 | 0.145 |
  | Silent errors | 0.045 | 0.632 | 0.654 |
  | Inflation (single - verified) | 0.005 | 0.033 | **0.051** |
  | Invalid tool calls | 0.64 | 0.16 | 0.17 |
  | Verified, F1 / F2 / F3 / F4 | 0.05 / 0 / 0 / 0.006 | 0.76 / 0.003 / 0.014 / 0.05 | 0.31 / 0.01 / 0 / 0.09 |

  - sft_ho vs base: p=8.4e-06, diff +8.5 pp [6.3, 10.7]. sft vs sft_ho: p=1.9e-01, diff +2.3 pp [0.1, 4.6].
  - The drop is all F1: test F1 templates resemble the held-out `F1_paying_customers`. F4 went up.
  - Inflation rose, so there is more for C to fix on test than with the all-templates SFT.
  - `evaluate.PAIRS` now compares B and C against `sft_ho`.

- **Held-out SFT trained** (353 trajectories, local GPU, 72 min, no crash). Saved to `runs/sft` (local).
- **Signal check, held-out SFT** (445 GRPO prompts, G=6, T=1.0; `results/grpo_signal_sft_ho.json`):
  - **170 rollouts pass the original DB but fail a counterfactual (was 8).** These are where R_exec and R_cf differ, so B and C now train on different rewards.
  - Groups: 140 mixed on single-DB pass, 147 mixed on cf_frac, 117 mixed on verified.

  | Template | Verified | Single-DB | Pass orig, fail CF |
  |---|---|---|---|
  | F1_paying_customers (held out) | 0.10 | 0.17 | 19 |
  | F2_refunded_category (held out) | 0.15 | 0.42 | 26 |
  | F3_net_revenue (held out) | 0.00 | 0.47 | 123 |
  | 8 seen templates | 0.44 to 0.97 | same | 2 |

  - On F3_net_revenue, B rewards about half the rollouts for SQL that is wrong on every counterfactual; only C's partial credit (16 mixed groups) points away from it. This is the shortcut the project is about.
  - Every seen template still has mixed groups.
- **E4 for held-out SFT** running locally (`sft_ho`). **VM retry restarted** (`laptop_kick_grpo.sh 90`): it uploads the new adapter and launches GRPO-B.

- **Design change: 3 GRPO-only train templates**, kept out of SFT: `F1_paying_customers`, `F2_refunded_category`, `F3_net_revenue` (`build_sft.GRPO_ONLY`; see plan.md).
  - Why: with SFT on all 11 templates, only 8 of 2670 GRPO rollouts had R_exec != R_cf, so B and C would train almost identically. On unseen compositions SFT makes silent errors, and at size S about 30% of those pass the original DB (E1).
  - SFT data drops from 462 to 353 trajectories. Retraining on the local GPU, then the signal check per template (`group_signal.py` now breaks results down by template and adds `cf_frac`, the partial-credit reward C sees).
  - The all-templates SFT is kept as `runs/sft_alltpl` (local).
- **User decision: keep the VM in asia-south1-a and keep retrying** (no zone move). The retry is paused while SFT retrains, so it cannot upload a half-written adapter.
- **Eval sampling bug (fixed in 90e8fae).** `SamplingParams(seed=...)` set a per-request seed, so every copy of a prompt sampled identically. 331 of 331 E4 groups and 444 of 445 GRPO-prompt groups were clones.
  - That made pass^k flat and the CIs effectively n=1, and it hid every mixed GRPO group.
  - The greedy own-items check (0.26 to 1.00) is not affected. GRPO training samples through TRL, so it is not affected either.
- **E4, fp16 models, real samples** (331 test items x 8, T=0.7, local GPU). Replaces all earlier E4 numbers.

  | Metric | Base | SFT |
  |---|---|---|
  | Verified | 0.009 | **0.117** [0.106, 0.130] |
  | Single-DB | 0.014 | 0.151 |
  | Silent errors | 0.045 | 0.632 |
  | Has final SQL | 0.46 | 0.985 |
  | Invalid tool calls | 0.64 | 0.16 |
  | pass^1 / pass^2 / pass^4 | 0.009 / 0.001 / 0 | 0.117 / 0.075 / 0.046 |
  | Verified, F1 / F2 / F3 / F4 | 0.05 / 0 / 0 / 0.006 | **0.76** / 0.003 / 0.014 / 0.05 |

  SFT beats base on verified: McNemar p=3.6e-8, paired bootstrap +10.8 pp [8.3, 13.5].
  - Test templates are new compositions. On them SFT pattern-matches the closest training template and returns plausible but wrong SQL, hence 63% silent errors.
    - F2_units_paid filters on `order_date` instead of payment date.
    - F3_avg_order averages per item instead of per order.
- **GRPO signal check** (SFT, fp16, 445 GRPO prompts, G=6, T=1.0): **125 mixed groups (28%)**, mean verified 0.94, and every train template has mixed groups. So GRPO-B can use the current prompt set.
  - **Caveat for B vs C:** only 8 of 2670 rollouts pass the original DB but fail a counterfactual, and those are the only rollouts where R_exec and R_cf differ.
  - So on these prompts B and C get nearly the same reward. Any difference has to come from rollouts that drift into such shortcuts during GRPO, or show up on test.
  - A prompt mix weighted toward templates with a high blind rate (E1) would sharpen the contrast. That is a design decision; see "Next".
- **SFT retrained on the local RTX 5070 Ti** (batch 1 x 16 accumulation, otherwise the same config as on the VM).
  - WSL threw `CUDA error: unknown error` mid-run 3 times, at steps 21, 84 and 34. The Windows log shows no driver reset, and CUDA works again right after.
  - Fix: `--save-every 10` with auto-resume in `scripts/local_sft.sh`. The successful run took 2 attempts and 1629 s.
- **Fix verified:** the fp32-to-fp16 merge verifies 1.00 on SFT's own 58 items (bf16: 0.26). It also has 0 silent errors and 0 invalid tool calls.
- `scripts/group_signal.py` counts, per GRPO group, how many rollouts verify. On the old bf16 rollouts: 370 of 445 prompts all-fail, 66 all-pass, 9 mixed.

### Nov 8

- **The VM couldn't be started:** 15 L4 stockouts in a row, so the adapter was not fetched; the VM is TERMINATED.
  - The local GPU is taken by another project, so the merge check moved to the VM (`vm_verify_merge.sh`). It is chained to GRPO-B so the VM does not have to be restarted through stockouts again.
  - Local venv: pinned `datasets<5`; 5.1.0 needs a newer `huggingface_hub` than transformers 4.57 allows.
- **Root cause of the weak SFT results: the LoRA merge in bf16 (fixed in 2ae4f3e).**
  - A LoRA update is about 0.4% of a weight, roughly one bf16 rounding step. Adding it in bf16 rounds most of it away: 38-61% of the weights in `runs/sft/merged` are bit-identical to base.
  - The merged model got only 26% of its own SFT training items right under greedy decoding. Key tokens there have a teacher-forced loss of 4-8.5 nats, against a training loss of 0.007.
  - Ruled out: HF and vLLM give the same loss, and the SFT and eval prompt renderings match (`scripts/check_render_match.py`).
  - TRL's vLLM weight sync has the same flaw: it merges and unmerges in place in bf16 every step. Rollouts lose the update, and the base weights drift.
  - **Fix (`sqlcf/precision.py`):**
    - Merges are computed in fp32 and saved in fp16. fp16 matches fp32 on Tiny Aya (loss 1.3558 vs 1.3557; bf16 gives 1.3636).
    - GRPO continues the SFT adapter on the original bf16 base; TRL keeps a frozen copy as the KL reference.
    - vLLM runs in fp16 and gets fp16(W + dW), computed out of place.
    - `evaluate.py` serves in fp16. Test: `tests/test_precision.py`.
  - **Correction to the GRPO-B entry below:** the prompts were not memorized. Over all 445 GRPO prompts (G=6), 354 failed every rollout and only 12 had mixed outcomes. The 0.96 reward at step 1 was a small sample. All E4 SFT numbers below come from the broken bf16 model and will be redone.
- **E4 SFT result** (local GPU, 331 items × 8 samples, 13.5 min):

  | Metric | SFT | Base |
  |---|---|---|
  | Verified accuracy | 0.019 | 0.004 |
  | Single-DB accuracy | 0.025 | |
  | Has final SQL | 0.51 | |
  | Silent errors | 0.41 | |
  | Invalid tool calls | 0.37 | |

  SFT beats base on verified accuracy: McNemar p=0.031, paired bootstrap +1.5 pp [0.1, 3.1]. Only 7 of 331 test items get mixed outcomes across their 8 samples.

  VM models fail to load locally, because the VM's newer transformers saves the tokenizer as class `TokenizersBackend`. `local_eval.sh` now copies in the base tokenizer files; fine-tuning does not change the tokenizer.
- **GRPO-B aborted after step 1** (190 s per step, so G2 itself would pass with 60 steps ≈ 3.2 h).
  - Reward on the train prompts was 0.96, and 75% of groups had zero reward variance. Every check vector was all-True or all-False.
  - **Cause:** SFT and GRPO prompts come from the same 11 templates. `SFT_BASES` splits them by base DB only, so after 2 epochs of SFT the GRPO prompts are memorized. Test templates are disjoint and almost always failed.
  - So GRPO had no signal on the train prompts, and none on unseen templates either. B and C would also see identical rewards.
  - Stopped to save about 3 h of GPU. This is the "overfitting to templates" case in plan.md.
- **GRPO-B launched** at about 20:25 IST, with the default config.
- **SFT done.** 174 steps in 64 min; final train loss 0.042. The VM powered itself off at 14:48Z, and an L4 stockout cost 2 retries when restarting it.
- **SFT format check** on 32 test items, 1 sample each:

  | Metric | Value |
  |---|---|
  | Has final SQL | 1.00 |
  | Tool calls per trajectory | 2.0 |
  | Invalid tool calls | 0.19 |
  | Correct on the test DB | 0/32 |
  | Verified | 0/32 |

  The model follows the oracle pattern rigidly: one probe query, the answer query, then the final answer. When the answer query returns `ERROR`, it submits the same SQL anyway, because the oracle trajectories never show a repair. Its mistakes are near misses, such as `oi.customer_id` where `o.customer_id` is right. GRPO should fix this if sampled groups contain some correct rollouts.
- **SFT at epoch 1.09:** loss 0.007, token accuracy 0.997, entropy 0.01. The model is memorizing the templated oracle trajectories. **Risk:** GRPO groups whose rollouts all get the same reward give no learning signal. **Check:** run `gate_g1.py` on GRPO-B's first steps. If few groups have reward variance, rerun SFT for 1 epoch (about 32 min).
- **E4 base result** (2648 trajectories, Wilson 95% CIs):

  | Metric | Value |
  |---|---|
  | Verified accuracy | 0.004 [0.002, 0.007] |
  | Single-DB accuracy | 0.010 |
  | Has final SQL | 0.62 |
  | Silent errors | 0.012 |
  | Smuggled | 0.000 |
  | Invalid tool calls | 0.75 |
  | Tool calls per trajectory | 1.77 |

  The untrained model almost never answers correctly, and 3 in 4 of its tool calls fail.
- **Gate G1 tooling.** `scripts/gate_g1.py` rescores the check vectors in the reward log under the mean, strict and soft forms. G1 can then be decided from GRPO-B's first steps, with no extra GPU run.
- **Prepared GRPO launch.** `scripts/vm_grpo.sh REWARD NAME [train.py args]` runs one condition and then powers the VM off.
- **SFT is learning.** Loss fell from 0.49 to 0.16 by epoch 0.17, and token accuracy reached 0.96.
- **Base eval moved to the local GPU.**
  - Installed vLLM 0.22.1 in the local `.venv-train`.
  - Added `evaluate.py --gpu-mem`; the local card uses 0.75 because the desktop holds about 2 GB.
  - A 4-item test ran in 317 s, most of it model load and compile.
- **Full SFT launched** on the VM at about 19:00 IST (`scripts/vm_sft.sh`).
- **Smoke test passed** on the VM. Timings:
  - SFT: 22 s/step (16 examples per step).
  - GRPO: 9.6 s and 18.4 s per step (G=2, 1 prompt).
  - Eval: about 2 min per model for 4 items.

  Rewards are still 0: after 0.05 SFT epochs the model writes wrong or missing final SQL, and it often puts a tool call and its final SQL in one turn.
- **Fixed: eval crashes.**
  - vLLM's LoRA support fails on Tiny Aya's tied embeddings. GRPO adapters are now merged (`runs/<run>/merged`), and eval serves merged models.
  - FlashInfer's sampler fails to compile on the VM, so eval disables it.
  - The venv's `ninja` was not on PATH.
- **Fixed: GRPO trained on the wrong tokens.** AgentTune's multi-turn token stream dropped the chat-template tokens between turns, so the trainer scored tokens in a context vLLM never saw (importance ratio ~1e-5). vLLM prompts also had a double BOS.
  - Fix: `patches/agenttune-multiturn-ids.patch` re-renders the finished conversation and puts the loss only on assistant turns. `scripts/vm_setup.sh` applies it.
  - Check: `scripts/check_token_gap.py`, on CPU.
  - Side effect: vLLM's importance-sampling correction is off, so GRPO is purely on-policy.
- **Fixed: GRPO memory.**
  - TRL loads the policy in fp32 by default; it is now loaded in bf16.
  - A 4 GiB logits allocation ran out of memory; GRPO now uses batch 1 with gradient accumulation of G×prompts.
  - vLLM sleep mode segfaults on wake-up, so it is off.
- **VM:**
  - asia-south1-a had an L4 stockout for about 1.5 h; `scripts/vm_start.sh` retries the start.
  - Moving the VM to another zone needs Rishii's OK.
  - `~/.ssh/config` must be mode 600, or SSH rejects it once teammates share the group.
- **Access:**
  - Aksh: VM user `aksh` with sudo, in Rishii's `admin_wsl` user group, able to read the HF token, plus IAM `compute.instanceAdmin.v1` on the VM.
  - A grant mistakenly made to a placeholder email was revoked within minutes; the audit log shows no activity from it.
- **VM setup:** created `sqlcf-l4`, pinned the vendor repos, installed torch 2.11, vLLM 0.22.1 and TRL 1.7.1, and copied the data and the hackathon HF read token to the VM.
- **Earlier (CPU):**
  - Built the datasets: audit 1302 items, train 907, test 331, SFT 462 trajectories.
  - E0 reward audit: H2 not met; the false-positive cut is 43% against the pre-registered 50%.
  - E1 blind rate: S size 0.292.

  See `plan.md`, "Status".
- E14 attempt 1 (temp VM sqlcf-e14, asia-southeast1-c, 13:54 to 14:30 IST): both arms hit CUDA OOM at step 3/60
  (22 GiB L4; the hard curriculum prompts produce long trajectories; 279 s/step). The driver stopped the VM.
  Attempt 2, same settings for both arms: `--max-completion 1536` (new train.py flag, default stays 2048),
  `--vllm-mem 0.40`, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; laptop_e14.sh now restarts the stopped VM.
  GPU quota is 1 L4 across all regions, so the seed-1 retry on sqlcf-l4 cannot start while E14 runs.
- E14 attempt 2 (16:33 IST) never trained: the temp VM's `git pull` fails silently, so it ran the old train.py, which
  rejected `--max-completion`; both arms exited in seconds and the driver stopped the VM (~25 min billed).
  The driver now copies train.py to the VM. Attempt 3 (19:2x IST) relaunched by hand on the same VM after a
  first try at the scp edit did not apply; B_cur training with the new flags from 19:27 IST.
- E14 attempt 3 OOMed again at step 4/60 with a 1536-token cap (tried to allocate 1.60 GiB, 1.19 GiB free; the
  completion logits over Tiny Aya's 262k vocabulary). SFT-model trajectories on the 36 curriculum items are short
  (p50 269 tokens, p99 500, max 1100; a 768 cap truncates 0.9%, the same as 1024), so attempt 4 (19:45 IST) uses
  `--max-completion 768 --vllm-mem 0.40` for both arms.
- E14 B_cur trained (60/60, 19:45 to 23:08 IST); evaluated locally while Cmin_cur trains (17 min for merge + E4 + Spider).
  Training log: original-DB pass 0.70 to 0.93, all-copies pass 0.11 to ~0.20-0.28, lucky share of passes flat ~0.7-0.8.
  Test set (results/e14/e4_eval.json): B_cur verified 7.1% vs SFT-ho 9.4% (-2.3 [-3.7, -1.0]) and vs B 12.7%.
  Spider (results/e14_spider.json): B_cur TS 27.6% vs SFT-ho 29.1% (-1.6 [-2.8, -0.3]); lucky share of EX 28.3%,
  the highest of our models (+1.5 pts lucky rate vs SFT-ho [+0.6, +2.5]). Waiting on Cmin_cur (~02:40 IST).

### Nov 16
- E14 Cmin_cur trained (60/60, to 02:40 IST). The laptop driver died at the copy step (laptop_e14.sh was edited while
  running); adapters copied by hand, temp VM sqlcf-e14 and snapshot sqlcf-l4-e14 deleted 02:54 IST. Cmin_cur
  evaluated locally (17 min).
- E14 results (results/e14/e4_eval.json, results/e14_spider.json), C-min minus B, one run each:
  test set verified 6.3% vs 7.1%, -0.8 [-1.8, +0.2] (pre-registered >= +2 failed: second null; both below SFT 9.4%);
  Spider TS 29.7% vs 27.6%, +2.1 [+0.9, +3.4], lucky rate -0.9 [-1.9, +0.1] (main pair: +1.9 [+0.6, +3.3]).
  Training steps 11-60: all-DB pass 31.8% vs 23.6%, lucky share of original-DB passes 59.1% vs 73.0%.
- ARTICLE §8 is now "A curriculum of hard questions" (results, Table 4), replacing the plan. Abstract ("second seed
  under way" replaced by the E14 replication), intro contribution 3, §5.3 pointer, conclusion and README updated.
  Site re-uploaded.
- Seed 1: with E14's VM deleted, the 1-L4 quota freed and sqlcf-l4 started at 03:18 IST (after 768 stockouts), but the
  driver's adapter check chained `git pull &&` (the VM cannot pull) and stopped it. Fixed (68aae4e: scp the code,
  check the md5 without pulling); relaunched 03:22 IST. GRPO-B seed 1 training at ~207 s/step: B_s1 ~06:50,
  C_s1 ~10:25 IST, then local merge + E4 + Spider (~40 min).
- Seed 1: GRPO-B seed 1 finished 60/60 at 06:57 IST, no tracebacks (~206 s/step). GRPO-C seed 1 now training on the
  same VM; ETA ~10:30 IST, then VM autostop and local evals.
- **Submit-page checklist pass (16 Nov, 12:40 IST, user approved).** The submit page lists required write-up items. Added to
  ARTICLE.md: languages + leak check (§3.1; new scripts/leak_check.py: 0 question overlap train/test, 0 exact gold-SQL
  overlap, 36 near-duplicate gold SQL from a sibling template), trajectory metrics table (§5.2: tool calls, invalid tool
  calls, throughput/latency), §9 Limitations (re-added, short), §10 With more compute (plan + forecast), Team: author
  contributions, declaration of outside work (none; first commit Nov 8), LLM usage (~80% first drafts via Claude Code).
  SUBMISSION.md maps each required item to its section. Seed-1 recovery: VM autostopped before the driver copied the
  adapters (30-min hold vs 15-min poll); driver killed 12:37, recover_s1 restarting the VM to copy, then local evals.
- **Team section per submit page (user, 13:00 IST).** Removed author contributions and LLM usage. Headings now match the
  site: "Declaration of work done outside the hackathon" and "Teammates tagged" (HF + GitHub for each: hi-phi-r25i /
  shreshth3000, LogicPalette / RishiiGamer2201, AkshAgg / Aksh2906).
- **Repo paths out of the article (Shreshth, 12:52 IST: "justification yeh deke hatado").** Removed the page-header note
  ("Every number comes from stored runs in results/; python verify_all.py ...") from make_site.py and the same sentence
  from ARTICLE.md, plus 17 inline script/result/patch paths. README gets a "Where each article result lives" table
  (section -> code -> output, every path checked to exist) with the verify_all line.
- **Aksh edited the article page directly on HF (16 Nov 13:15-13:34 IST, 4 Space commits, not in git).** Merged into ARTICLE.md
  by extracting the page markdown and patching (claim + tracks, At a glance, Why it matters, related work + Mirage/
  RewardShield/SynSQL/Zhang 2026c, hyperparameters, environment, 3.5 kits, 3.6 metrics, 3.7 threat model, H1/H7, by-family
  table, sample trajectory, compute table, Appendix D prompts, Reproduction, Acknowledgements). Rebuilt page == Aksh page
  except two fixes: seed-1 line (trained, not evaluated: VM had no L4 13:40, user skipped) and Limitations run count.
- **Submitting (16 Nov ~14:00 IST).** SUBMISSION.md now carries the 369-word plain abstract inline (runs/abstract.txt is not in git).
- **Public (16 Nov ~14:10 IST, user: "go public").** go_public.py --go: 3 adapters (gated auto), dataset, both Spaces, both
  collections, GitHub repo all public. gh here lacks --accept-visibility-change-consequences, so the script now falls back
  to plain --visibility public. Pre-check: 0 token patterns in git history, no chat exports tracked. All 12 submission links
  return 200 anonymously.
- **Submitted (16 Nov ~14:15 IST).** Lexsi form: "Submission received"; confirmation email on its way. Latest submission counts,
  so a resubmit before 17:29 IST replaces it. sqlcf-l4 stays TERMINATED; seed-1 adapters (B_s1, C_s1) remain on its disk, unevaluated.
