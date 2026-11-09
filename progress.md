# Progress log

> **Rule: update this file after each and every step** (a run launched or finished, a bug found or fixed, a decision made, access changed). Add a dated entry at the top of the log, and keep "Current state" and "Next" accurate. Commit and push it with the work it describes.

## Current state (Nov 9)

- **All experiments done** (E0, E1, E2, E3 B + C, E4, E5, manual audit). Training comparison is a null: B 12.7% verified, C 9.0%, SFT 9.4%. `verify_all.py` passes.
- **VM `sqlcf-l4`: TERMINATED**, no job queued. Start with `bash scripts/vm_start.sh` only if a new run is approved.
- **Write-up:** ARTICLE.md (12 sections, all numbers), ABSTRACT.md, README judge's view.
- **Hugging Face, org `sqlcf-lexsi`, ALL PRIVATE** (user: nothing public until approved):
  - Space `counterfactual-sql-demo`, dataset `counterfactual-sql-data`.
  - Models `tiny-aya-global-sqlcf-sft`, `-grpo-b`, `-grpo-c` (LoRA adapters + LICENSE + NOTICE + card).
  - Collection `counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4` with all five.
- **Licence ruling (organisers, Discord, Nov 9):** adapters of the gated base may be published with its licence included. During judging every artifact must be public, or gated with automatic approval; private or manual-approval repos count as missing.

## Next

1. **User approval to go public** before submission (deadline Nov 14 AoE). Then: `scripts/push_models.py --public --gated` (models gated, auto-approve), and make the Space, dataset and collection public.
2. User: confirm Command A price at docs.cohere.com. (Done: AkshAgg and hi-phi-r25i are `sqlcf-lexsi` members, checked via the API on Nov 9.)
3. User decision on the null: accept and polish (recommended) / second seed (about 7 h VM) / redesigned C.
4. Publish the HF Article from ARTICLE.md; final submission form.
5. Zero-GPU strengtheners from plan.md §9A (A2 Spider lucky-pass rates, A3 SkyRL reward audit, A4 gold-free multi-DB voting, A5 AgentTune repro and patch), then the write-up changes in §9C. GPU items in §9B need the user's go.

## Log

### Nov 9

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
  - Moving the VM to another zone needs the lead's OK.
  - `~/.ssh/config` must be mode 600, or SSH rejects it once teammates share the group.
- **Access:**
  - Aksh: VM user `aksh` with sudo, in the lead's user group, able to read the HF token, plus IAM `compute.instanceAdmin.v1` on the VM.
  - A grant mistakenly made to a placeholder email was revoked within minutes; the audit log shows no activity from it.
- **VM setup:** created `sqlcf-l4`, pinned the vendor repos, installed torch 2.11, vLLM 0.22.1 and TRL 1.7.1, and copied the data and the hackathon HF read token to the VM.
- **Earlier (CPU):**
  - Built the datasets: audit 1302 items, train 907, test 331, SFT 462 trajectories.
  - E0 reward audit: H2 not met; the false-positive cut is 43% against the pre-registered 50%.
  - E1 blind rate: S size 0.292.

  See `plan.md`, "Status".
