# Plan — When Execution Success Lies

Team **Teen_khapeetars** · Track 3 · Problem statements **#6 (data and database agents) + #9 (reward design and reward-hacking defences)** · Build closes **Nov 14, end of day AoE**. Background and sources are in [research.md](research.md).

---

## 0. What changed from the original research direction

| Original plan | Change | Why |
|---|---|---|
| The headline is GRPO B vs C accuracy | **The headline is a reward audit**: FP/FN rates of 5 rewards, needing no GPU. GRPO B vs C is the second result. | GRPO on Tiny Aya gave +5 pp (Kataa) or 0 (PRINCE2) for other teams. The audit is a result even if training is null, and no competitor reports FP-reward rates. |
| Rewards compared: B vs C only | Add **AgentTune's built-in SQL reward** and a **strict single-DB comparator (multiset/REX)** to the audit | AgentTune's flagship example is a SQL agent and its reward can be gamed. That is direct, useful feedback to the organisers. The REX baseline answers "isn't a stricter comparator enough?" (DualSQL). |
| Counterfactual copies just need the gold answer to change on ≥2 DBs | Every item needs **≥1 answer-preserving** variant (gold result unchanged, wrong SQL diverges) **and ≥1 answer-changing** variant | Answer-changing variants defeat literal smuggling. Answer-preserving variants isolate fan-out and duplicate bugs (Ai 2026, SQLoom). |
| Reward C = `C0 × mean(C1..CK)` | Keep it, plus **pre-registered ablations**: strict all-pass, and a ReViSQL-style soft `C0·(1−0.2·[any Ci fails])`. Freeze one choice for training on Nov 10, from audit FN rates. | The mean form reduces zero-variance GRPO groups. The soft form is the closest prior-art baseline. |
| Comparator not specified | **Multiset** comparison; order-sensitive only if the gold has `ORDER BY`; column permutation allowed; floats rounded to 4 decimals; 5 s timeout; read-only DB | Set-based EX (the BIRD default) hides exactly our DISTINCT/duplicate family. |
| Citations as listed | Fix ReViSQL's title and the context of the 32.8%; add **Ai 2026, DualSQL, Progress-SQL, CodeContests+, RobustTests (2608.24135)** | See research.md §5. Drop any "first to use counterfactual DBs" wording. |
| Compute not planned | **No HF credits. Compute = GCP Vertex AI custom training, 1× L4 24GB, asia-south1** (quota approved 2026-11-08, case #77369774), paid from ~₹3,845 GCP credit. One GPU, so runs are sequential. One shared SFT run for B and C. | See §5 compute budget. |
| Deliverables not listed | Map everything to the official checklist (§7). Add an **ROI table vs Cohere Command A** and a **Gradio demo** that needs no GPU. | Both are required or preferred by the rules, and both appear in the strongest entries. |

**Novelty sentence (use verbatim; don't strengthen it):**
> To our knowledge, this is the first study to use execution on code-generated, bug-family-targeted counterfactual databases as the online RL reward for a small (~3B) text-to-SQL agent, and to measure that reward's per-family false-positive and false-negative rates, its generalization to a held-out bug family, and answer smuggling. Prior work applied multi-database checks to evaluation (Zhong et al. 2020; Ai 2026) or supervised fine-tuning (SQLoom), or used symbolic verification on a single database (ReViSQL).

### Status — Nov 8, end of day (W1 done on CPU; W2/W3 code written, not yet run on GPU)

**Built and checked** (`tests/` pass; every builder checks gold == pandas and paraphrase == gold on every DB, 0 errors):

| Set | Command | Items | Notes |
|---|---|---|---|
| audit | `python -m sqlcf.cf --name audit --split all --seeds 301..305 --size S` | 1302 | all 18 templates, F1–F4 |
| train | `--name train --split train --seeds 101..106 --size S` | 907 | F1 393 / F2 192 / F3 322; 401/420 base-blind mutants caught by the chosen CFs |
| test (E4) | `--name test --split test --seeds 501 502 503 --size S --test` | 331 | different generator, see below; F4 (held out) = 214 |
| SFT | `python -m sqlcf.build_sft` | 353 traj | bases S_s101–103 only; 3 GRPO-only templates excluded (Nov 9, below) |
| GRPO prompts | `train.grpo_rows` | 445 | bases S_s104–106; 0 overlap with SFT; 103 of them on the GRPO-only templates |

**Deviations from the plan below (decided on evidence):**
- **DB size S (50 customers), not M, for train/audit.** E1: the blind rate is ~0.2–0.36 at S, ~0.01 at M, and 0 at L. At M, almost no mutant passes the original DB, so there is nothing for the reward to catch. What drives blindness is the size of the question's slice (city × year × category), more than the DB size.
- **CF edits are focused on the item's slice** (its city/year/category). With unfocused edits, most blind mutants were uncatchable and 334 items were dropped; with focused edits, 54 items were dropped and 508/535 blind mutants became catchable.
- **Two CF selections per item:** greedy (≤3 CFs that kill the most mutants; used for training) and **random** (1 changing + 1 preserving, chosen blind to the mutants). E0 reports both. FP on mutants under greedy is optimistic by construction.
- **Test generator (E4)**: an FK-closed 50-customer sub-DB of a size-M parent, plus 4 family-blind mutations (resample half the customers, clone 25% of subgraphs, flip placed↔cancelled, relabel tiers), all used. It catches only 54 of 103 base-blind mutants, so test "verified" is *less* strict than the training reward. Report that next to E4.
- **GRPO-only train templates (Nov 9):** `F1_paying_customers`, `F2_refunded_category` and `F3_net_revenue` are kept out of SFT (`build_sft.GRPO_ONLY`).
  - With all 11 templates in SFT, the SFT model solved the GRPO prompts deterministically. Only 8 of 2670 rollouts passed the original DB but failed a counterfactual, so R_exec and R_cf would have given B and C almost the same reward.
  - On compositions it has not seen, SFT makes silent errors (63% on test), and at size S about 30% of those pass the original DB. That is where B and C diverge.
  - Test templates stay untouched.
- **18 templates, not 10–12 per family:** 11 train and 7 test (4 of them F4). The parameter grids still give 907 train and 331 test items. Add templates only if the SFT/GRPO rollouts show overfitting to templates.
- **Tiny Aya's chat template ignores tools.** AgentTune then appends its fallback tool prompt to the system turn, and the model calls tools as a JSON list `[{"tool_name":…,"parameters":…}]`. Tool results are folded into user turns. `train.py` builds the SFT text with AgentTune's own constants and fold function, so SFT matches the GRPO rollouts; `evaluate.py gen` uses AgentTune's render, parser and fold too.
- **Reward-call safety:** AgentTune/TRL retry a reward call on `TypeError`. Our rewards raise `ValueError` if the `dbs`/`gold` columns are missing (GRPO must keep `remove_unused_columns=False`), so a silent all-zero reward can't happen.

**Headline numbers so far** (audit set, 1302 items, 5 base DBs; Wilson 95% CIs; `results/e0_reward_audit.json`, `results/e1_blind_rate.json`, `results/e0_agenttune.json`):

| Reward | FP on gold mutants (n=1814) | FP on hacks (n=2839) | FN on gold + paraphrases (n=2847) |
|---|---|---|---|
| R_exec_set (BIRD set EX) | 0.375 [0.353, 0.397] | 0.541 [0.523, 0.560] | 0.000 |
| R_exec_rex (strict multiset, 1 DB) | 0.295 [0.274, 0.316] | 0.541 | 0.000 |
| R_cf, **random** CFs (1 changing + 1 preserving, chosen blind to mutants) | **0.168 [0.152, 0.186]** | **0.019 [0.015, 0.025]** | 0.000 |
| R_cf, greedy CFs (≤3, chosen to kill these same mutants: optimistic) | 0.015 [0.010, 0.022] | 0.020 | 0.000 |

- **H2 is not met on the honest (random) row:** a 43% relative cut in mutant FP vs R_exec_rex, against the pre-registered ≥50%. Hack FP falls 96%. We report this as it is; the greedy row is the CF-selection upper bound, not the H2 test.
- **Mean rewards** (what GRPO actually sees): R_cf_mean pays mutants 0.148 (greedy) / 0.228 (random) on average, vs 0.295 for R_exec_rex.
- **AgentTune built-in SQL reward (H3)** (n=360 yes/no items: 314 yes, 46 no):

  | Policy | Reward on yes items | Reward on no items | Overall |
  |---|---|---|---|
  | Honest gold SQL | +3.10 | +3.10 | +3.10 |
  | Trivial WHERE padding, always "yes" | +3.10 | −2.0 | +2.45 |
  | Same padding, always "no" | −2.0 | +3.10 | −1.35 |
  | No SQL, always "yes" | −0.90 | −2.5 | −1.10 |

  Padding the WHERE clause and always answering "yes" gets the honest score on every yes item.
- **E1 blind rate (H1):** S 0.292 [0.266, 0.319] · M 0.008 · L 0.002. By family at S: F1 0.21, F2 0.34, F3 0.36, F4 0.31.

**Compute update (Nov 8, 15:00):** Compute Engine GPU quota approved too (GPUS_ALL_REGIONS = 1). **Team VM `sqlcf-l4`**:
- Machine: g2-standard-4 + 1× L4 23 GB, zone asia-south1-a.
- Image: Deep Learning VM (driver 580), 150 GB disk, 15 GB RAM.
- Cost: ~$0.74/hr while RUNNING. **Stop it whenever nobody is using it**; a stopped VM only bills for its disk.
- Created by `scripts/make_vm.sh`.
- The VM replaces the Vertex batch jobs as the main path (interactive SSH, no image build). `vertex/` stays as a fallback.

**Access (resolved):** hackathon HF read token on the VM (`.cache/hf/token`); Aksh has a sudo account on the VM and IAM to start/stop it. Shreshth: still needs an SSH key.

**VM smoke test passed (Nov 8, evening):** tests → render → tiny SFT → 2 GRPO steps (vLLM colocate) → merge → eval on 4 items → scoring, end to end on the L4 (`scripts/vm_smoke.sh`, `vm_smoke_eval.sh`). Fixes needed on the way:
- TRL loads a model path in fp32 by default (no room for vLLM): `model_init_kwargs={"dtype": "bfloat16"}`.
- AgentTune's multi-turn stream dropped the chat-template tokens between turns, so the trainer scored tokens in a context vLLM never saw (importance ratio ~1e-5), and vLLM got a double BOS. Fixed by `patches/agenttune-multiturn-ids.patch` (re-render the finished conversation; loss on assistant spans; CPU check `scripts/check_token_gap.py`). Consequence: vLLM importance-sampling correction is off (on-policy GRPO).
- 4 GiB logits OOM: batch 1 + gradient accumulation G×prompts. vLLM sleep mode segfaults on wake-up in vLLM 0.22.1, so it is off.
- vLLM LoRA crashes on Tiny Aya's tied embeddings: GRPO adapters are merged; eval serves merged models. FlashInfer sampler JIT fails on the VM: disabled for eval.

Smoke numbers (G=2, 1 prompt): SFT 22 s/step (16 examples); GRPO step 9.6 s and 18.4 s; eval gen ~2 min per model for 4 items. Rewards were 0 (wrong or missing final SQL after 0.05 SFT epochs), so no GRPO gradient yet; the model also writes a tool call and a final ```sql block in one turn. Both should change after full SFT. **G2 still open:** time real-config steps (G=6, 4 prompts) at the start of GRPO-B.

**Compute risk:** asia-south1-a had an L4 stockout for ~1.5 h on Nov 8 (`scripts/vm_start.sh` retries). Moving the VM to asia-south1-b/c needs the lead's OK.

---

## 1. Pre-registered hypotheses and gates

Commit this section to the repo **before** any training run. The commit timestamp is our pre-registration.

| ID | Hypothesis | Test | Pass criterion |
|---|---|---|---|
| H1 | The single-DB exec reward pays buggy gold-mutants at a material rate, and the rate depends on DB size | E1 blind rate at S/M/L sizes | Descriptive. Report with Wilson CIs. |
| H2 | The counterfactual reward cuts the false-positive rate vs single-DB exec without inflating false negatives | E0 audit on mutants + gold + hacking policies | FP down ≥50% relative; FN ≤5% on gold and paraphrased-gold queries |
| H3 | AgentTune's built-in SQL reward pays hacking policies | E0 on the yes/no subset | Descriptive. Mean reward of each hack vs gold. |
| H4 | GRPO-C has a lower silent-error rate than GRPO-B on fresh test DBs | E4, McNemar on paired tasks | p < 0.05. **A null result is reported as a null.** |
| H5 | The gain carries over to the held-out family | E4 on held-out-family items only | Direction-consistent with H4; CI reported |
| H6 | GRPO-B smuggles literals more than GRPO-C | E4 literal-only SQL rate | Descriptive with CIs |

**Gates set in advance:**
- **G1 (Nov 10, midday):** freeze the reward form for C, choosing among mean, strict and soft. Pick the form with the lowest FN on gold queries; break ties by most non-zero-variance groups on SFT rollouts.
- **G2 (Nov 10, evening):** if a measured GRPO step means fewer than 60 steps per condition fit the budget, shrink to G=6 and 3 prompts per step, or a 50-step equal budget. B and C always get **identical** budgets.
- **G3 (Nov 12):** an adapter is released as "improved" only if it beats SFT on verified accuracy on fresh test DBs. Otherwise we release it labelled as a null.

---

## 2. Experiments

### E0 — Reward audit (headline, CPU only)
Score a fixed pool of candidate queries per item under every reward and measure how often each one is fooled.

- **Rewards:**
  1. `R_agenttune`: built-in `correctness_reward` + `query_reward` + `structure_reward`, on a yes/no subset of items.
  2. `R_exec_set`: single DB, set comparison (BIRD-style).
  3. `R_exec_rex`: single DB, strict multiset comparator.
  4. `R_cf`: ours (mean, strict and soft variants).
- **Candidate pool:**
  - **Gold** and **2 paraphrased gold** queries per item (equivalent SQL written differently). These measure FN.
  - **Gold mutants** per family: `COUNT(*)`↔`COUNT(DISTINCT)`, joins that fan out, a dropped status filter, an `INNER`/`LEFT` swap, an old-row read, a missing refund. These measure FP.
  - **Hacking policies:**
    - literal smuggling (`SELECT <gold value from the original DB>`)
    - hard-coded IDs
    - trivial `WHERE` padding
    - yes/no guessing (for `R_agenttune`)
    - empty or `LIMIT` tricks
- **Output:** FP and FN rate per reward × per family, with Wilson CIs. This is **figure 1**.
- Optional external oracle: run VeriEQL on passes so our FP numbers are comparable with ReViSQL's 32.8%.

### E1 — Blind rate vs DB size (CPU only)
How often each gold mutant passes on the original DB at sizes **S / M / L** (≈50 / 500 / 5,000 customers), realistic and never hand-built to be blind. This is **figure 2**.

### E2 — SFT warm start (shared by B and C)
- **Data:** scripted oracle trajectories built from gold SQL (`list_tables` → `describe` → exploratory query → final SQL), on train templates only. An optional teacher (Command A) adds variety.
- **Training:** 1–2 epochs of LoRA r=16 via AgentTune `create_distill_trainer` or SFT.
- **Evaluate:** base vs SFT with n=8 samples.
- **Filter:** keep train prompts whose SFT pass rate is in (0,1). These are the GRPO prompts.

### E3 — GRPO B vs C (same everything except the reward)
- Same model, SFT adapter, data, seed, steps, G and lr. Only `reward_funcs` differs.
- **Starting config:**
  - G=8, about 4 prompts per step
  - `max_completion_length` about 3072, at most 5 turns
  - β about 0.01–0.04, lr about 1e-5 (Kataa used 5e-5)
  - colocated vLLM
  - tool output truncated to 20 rows / 1.5K chars
- **Logging (log our own rewards; AgentTune's `trajectories.jsonl` leaves `reward` null):**
  - every rollout's C0 and each Ci
  - which reward paid it
  - a literal-only flag
  - **FP/FN reward rate during training** for both runs, scored against a stricter offline oracle (more counterfactual DBs + pandas). This is **figure 3**.
- **Optional:** R0 (executes-only reward), if compute allows.

### E4 — Evaluation
- **Test DBs** are built with a **different generator** from the training counterfactuals: SQLoom-style FK-closed sub-DB + mutation, vs our rule-based training copies.
- **Test sets:** test templates of the 3 train families, plus **all items of the held-out family**.
- **Models:** base, SFT, GRPO-B, GRPO-C; n=8, temperature 0.7.
- **Metrics:**

| Metric | How |
|---|---|
| Verified accuracy | Correct on original **and** all test counterfactual DBs (AuditKIT `CustomPredicate` oracle) |
| Silent-error rate | Every tool call executed, final answer wrong (AuditKIT "claims success, verified failed") |
| Single-DB accuracy | Shows the inflation gap vs verified accuracy |
| Held-out-family verified accuracy | Same as verified, held-out family only |
| Literal smuggling rate | Final SQL has no table reference, or hard-codes IDs/values seen in tool output |
| pass^k (k=1,2,4) | τ-bench formula |
| Trajectory metrics | AgentTune ARR, LCF, TAC; invalid-tool-call rate |

- **Statistics:** exact McNemar on discordant pairs; paired bootstrap (10K) on the accuracy difference; Wilson CIs. Use our own implementations; use AuditKIT `compare_models` only from main after Nov 7.
- **Manual audit:** about 50 trajectories by hand, labelled with NL2SQL-BUGs categories.

### E5 — ROI (preferred by the rules)
Run Cohere Command A (partner model; trial key) on the same test set, single-turn with the schema in the prompt. Compare accuracy, $/1k queries, and latency vs self-hosted Tiny Aya + LoRA (GPU $/hr ÷ throughput).

### E6 — Stress test of public SQL benchmarks (optional, only if ahead)
Run SafeQuery's public retail tasks through our counterfactual generator and report how much single-DB accuracy holds up. Frame it respectfully, as a benchmark stress test, not a takedown. Check the dataset licence first.

---

## 3. Data design

- **Schema:** customers, orders (with status: placed/shipped/cancelled), order_items, payments, refunds, tier_history (valid_from), invoice_adjustments. Faker values, fixed seeds, sizes S/M/L. The business rules are written as code assertions so every counterfactual stays valid.
- **Families:**

| Family | Split |
|---|---|
| F1 duplicate-sensitive counts | Train + test templates |
| F2 join fan-out | Train + test templates |
| F3 missing business filters | Train + test templates |
| F4 superseded/corrected records | **Held out**; test only |

  F4 is the most "business-semantic" family, so holding it out tests general care rather than patching known traps. **Swap it on Nov 9 if the team prefers; freeze it before training.**
- **Size:** about 10–12 templates per family, split by **template**. Parameterised to about 600 train and 200 test items.
- **Each template carries:**
  - NL question variants
  - gold SQL
  - a pandas function
  - a list of bug mutants
  - grading mode (set/list/subset)
  - a yes/no variant where natural (for the `R_agenttune` audit)
- **Validity filters, per item and per DB:**
  - gold SQL == pandas answer
  - gold result non-empty
  - the result is deterministic under shuffled insert order (catches ties)
  - ≥1 answer-preserving and ≥1 answer-changing variant
  - otherwise drop the item
- **Counterfactual copies:** `VACUUM INTO` + seeded family-targeted edits:
  - second order for a customer
  - zero-order customers
  - cancelled orders
  - later tier row
  - refund
  - extra 1:N children

  Optionally distil to the minimal K (2–3) that kills all mutants of the item. Precompute gold results so the reward is a CPU lookup + one SQLite execution per DB.

---

## 4. Code layout (minimum)

```
sqlcf/
  db.py          # schema + seeded generator (S/M/L) + business-rule assertions
  templates.py   # families: question variants, gold SQL, pandas fn, mutants, grading mode
  cf.py          # train counterfactuals (rule edits) + test generator (FK-closed sub-DB + mutation)
  compare.py     # multiset comparator, ORDER BY sensitivity, column permutation, float rounding, timeout
  rewards.py     # R_exec_set, R_exec_rex, R_cf{mean,strict,soft} in AgentTune reward signature
  audit.py       # E0 + E1 -> results/*.json + figures
  build_sft.py   # oracle trajectories
  agent.py       # system prompt, run_sql tool (original DB only), dataset rows
train.py         # SFT (TRL, prompt/completion per assistant turn) + GRPO (AgentTune, --reward)
evaluate.py      # E4: gen (vLLM multi-LoRA, AgentTune render/parse) + score (stats) + selfcheck
vertex/          # Dockerfile (vllm 0.22.1 base, py3.12), run.sh stages, submit.sh (billable)
tests/test_rewards.py   # gold=1, mutant=0 on CF, literal=0, malformed/missing tool call=0
demo/index.html  # static demo: sqlcf/demo.py in the browser via Pyodide (free static Space; no GPU)
verify_all.py    # regenerate every number in the write-up from stored runs
```

---

## 5. Schedule and owners

Three workstreams. Owners are suggestions; swap them freely.
- **W1 Data and rewards:** generator, families, counterfactuals, comparator, audit.
- **W2 Training:** install, SFT, GRPO, compute.
- **W3 Evaluation and packaging:** AuditKIT, stats, demo, HF collections, write-up, ROI.

| Date | W1 Data and rewards | W2 Training | W3 Eval and packaging | Done when |
|---|---|---|---|---|
| **Nov 8 (today)** | Schema + generator skeleton; F1 templates | Every teammate accepts the Tiny Aya licence. Lead redeems the $20 coupon (check spam). **Secure a second GPU source.** Start the AgentTune + vLLM install on Linux GPU. | Join Discord #hackathon-lexsi. **Open a ticket: can a gated-model LoRA adapter be published un-gated?** Create the GitHub repo + HF org/collections. | Tokens work; install started; ticket open |
| **Nov 9** | F1–F4 templates, pandas checker, train counterfactuals, comparator, `rewards.py` + unit tests. Run **E0 + E1**. | Run the README Tiny Aya GRPO example end to end. Verify the reward signature with a print-reward. Confirm vLLM loads `cohere2`; else switch to the TRL fallback. | Write `audit.py` figures. Commit the **pre-registration (§1)**. Start the article skeleton (9 sections). | Figures 1–2 exist; one GRPO step ran |
| **Nov 10** | Test generator (different method). Freeze the held-out family. Build SFT oracle trajectories. | SFT run (~1.5 h L4, Vertex). Base vs SFT eval. Filter GRPO prompts. **Time one GRPO step: gate G2.** | AuditKIT `CustomPredicate` oracle + stats module. **Gate G1: freeze the reward form.** | SFT adapter; budget fixed |
| **Nov 11** | Support: fix data bugs found in SFT rollouts | **GRPO-B** then **GRPO-C** (same budget; sequential, quota is 1 GPU; ~5–6 h each on L4, so start B early) | Live FP/FN logging dashboard from rollout logs (figure 3) | Both adapters saved |
| **Nov 12** | Manual audit of about 50 trajectories | Re-run only if a crash happened (no tuning of C alone) | **E4 eval** for base/SFT/B/C; McNemar, bootstrap, pass^k; **gate G3**. E5 ROI. | Results table final |
| **Nov 13** | E6 (optional). Clean the dataset cards. | Push adapters to the HF model collection | Gradio Space demo; HF Article; README with a "judge's 60-second view" table; `verify_all.py`. **Submit v1.** | v1 submitted |
| **Nov 14** | Buffer | Buffer | Fix issues found in a read-through; resubmit before the AoE deadline | Final submitted |

**Compute budget.** No HF credits. Paid compute = **GCP Vertex AI custom training jobs, `g2-standard-8` + 1× NVIDIA L4 24GB, region asia-south1** (quota `CustomModelTrainingL4GPUsPerProjectPerRegion` = 1, approved 2026-11-08, case #77369774), billed to the ~₹3,845 credit on project `project-54f35310-8b0b-478f-836`. Compute Engine L4 ≈ ₹71/hr; Vertex adds a small premium, so assume **~₹85/hr** until the first bill confirms. No other paid GPU source is approved.

| Job | Machine | Time | Cost |
|---|---|---|---|
| Data, counterfactual DBs, E0/E1 audit, reward unit tests | Laptop CPU | — | ₹0 |
| Pipeline debug (model loads, 2 GRPO steps, G=2, no vLLM, fp16) | Free Kaggle/Colab T4 | ~1 h | ₹0 |
| Vertex smoke (nvidia-smi, vLLM loads `cohere2`, 5 GRPO steps real config) → gate G2 | L4 | ~0.5 h | ~₹45 |
| SFT (~600 trajectories × 2 epochs) | L4 | ~1.5 h | ~₹130 |
| GRPO-B (60 steps × 8 prompts × G=4–6) | L4 | ~5–6 h | ~₹500 |
| GRPO-C (identical budget) | L4 | ~5–6 h | ~₹500 |
| Eval (base/SFT/B/C × 200 items × n=4, vLLM multi-LoRA) | L4 | ~1.5–2 h | ~₹170 |
| **Total** | | **~14–16 h** | **~₹1,350** (budget **~₹2,500** for job start-up overhead and one rerun; credit ₹3,845) |

**Notes:**
- L4 times are L40S estimates (Kataa: SFT + 90 GRPO steps + eval on one L40S) scaled ~2.5× for L4's lower bf16 throughput. Replace them with the gate-G2 timing.
- **24 GB config is tight:** vLLM colocate `gpu_memory_utilization` ~0.3, G=4–6, completions capped at 2K tokens, gradient checkpointing on. If it OOMs, drop G before dropping steps; B and C must keep identical settings.
- Vertex jobs are batch containers: ~5–10 min start-up each, no SSH (use `--enable-web-access` for a shell while running). Chain SFT→GRPO→eval inside one script where possible. Write outputs to a GCS bucket in asia-south1 (`/gcs/<bucket>/`) and push adapters to the HF Hub. Pass `HF_TOKEN` as an env var.
- Quota is 1 GPU, so B and C run sequentially (~11–12 h total). Start GRPO-B on the morning of Nov 11 at the latest.
- The free HF account and access token are still needed: to download gated Tiny Aya, and to publish the submission collections.
- **Never run GRPO on a T4** (no bf16; 381 s per step measured by another team).

**If behind, cut in this order:** E6 → R0 → the optional VeriEQL oracle → strict/soft training ablations (keep them in the audit only) → GRPO steps (equal for both) → the teacher-model SFT variety.
**Never cut:** E0/E1 audit, verified accuracy, McNemar, held-out family, the honest-null policy, the required deliverables.

---

## 6. Write-up outline (HF Article; README mirrors it)

1. **Judge's 60-second view:** one table of the main FP/FN and verified-accuracy numbers with CIs, and links to the demo, models, data and `verify_all.py`.
2. Problem and approach. Open with the silent-error example and the AgentTune reward finding.
3. Repos and features used:
   - **AgentTune:** GRPO, tools, distill.
   - **AuditKIT:** `agent_eval` oracle, pass^k.
   - CuratorKIT, only if we actually use it (e.g., provenance on the generated data).
4. Models and licences: Tiny Aya Global CC-BY-NC; LSAL; Command A used only as teacher/ROI.
5. Datasets and licences.
6. Model collection.
7. Data collection.
8. Experiments:
   - E0 audit (figure 1)
   - blind rate (figure 2)
   - FP/FN during training (figure 3)
   - E4 table
   - held-out family
   - smuggling
   - ROI
   - **nulls and what else we tried**
9. Related work and novelty, using the exact sentence above and every must-cite.
10. With more credits: Aya Expanse 8B, more steps, VeriEQL oracle, adversarial counterfactuals seeded from the model's own near-misses (the prove-your-thesis plan for Nov 16–21).
11. Limitations, and the guardrail wording: family 4 is described only as "superseded and corrected records" in SQL terms; no RAG framing.
12. Teammates tagged.

---

## 7. Submission checklist (mapped to the rules)

- [ ] Registered email; abstract under 500 words
- [ ] **Public un-gated HF model collection:** SFT, GRPO-B and GRPO-C adapters (resolve the licence question first)
- [ ] **Public HF dataset collection:** DB generator outputs (S/M/L), templates, train counterfactual DBs and test DBs, E0/E1 results, rollout logs with per-DB rewards, `trajectories.jsonl`, `lexsi_provenance.json`, AuditKIT sidecar JSONL
- [ ] HF Article (or README) with the 9 requested sections
- [ ] GitHub repo with reproducibility notes + `verify_all.py`
- [ ] Repos/models used listed; Track 3; PS #6 and #9
- [ ] Before/after on **more than one** metric: verified accuracy, silent-error rate, FP reward rate, pass^k, smuggling rate
- [ ] Public demo: Gradio Space showing one query scored on original + counterfactual DBs, with the reward each function gives
- [ ] ROI table vs Command A
- [ ] Every number traceable to a stored run

---

## 8. First actions (today)

1. **Lead:** redeem the HF coupon; every teammate accepts the `CohereLabs/tiny-aya-global` licence and creates an HF token.
2. **Someone:** list available GPUs (university cluster, personal, Kaggle, Colab Pro) and post them in the team chat.
3. **Someone:** open the Discord ticket on publishing un-gated LoRA adapters of a gated CC-BY-NC base.
4. **W1:** start `db.py` + F1 templates. The E0/E1 audit needs no GPU and should be running by tomorrow night.
5. **W2:** start the AgentTune install and run the README Tiny Aya example.
