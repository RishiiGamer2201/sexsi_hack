# Training techniques that would make a stricter (counterfactual-DB) verifier change GRPO/RLVR outcomes for text-to-SQL

Context assumed (from the team, not re-researched): Tiny Aya Global 3.35B, LoRA r=16, GRPO via AgentTune (TRL + vLLM), 1x L4, 60 steps ~3.2 h, group 8, 24 rollouts/step (so 3 prompts/step, ~180 prompt-groups and 1,440 rollouts in total). B = strict exec match on 1 DB (12.7%), C = mean pass over original + 4 CF DBs (9.0%), SFT 9.4%. Rewards disagreed on ~7% of rollouts. L4 = $0.74/h.

Labels used below: **[Fact]** = taken from a cited source. **[Derived]** = arithmetic or algebra anyone can check from the stated setup. **[Inference]** = my judgement.

---

## Ranked recommendations (synthesis across all questions)

### Takeaway
The current null result is close to built in. Three things mute the CF signal: (a) the reward differs on only ~100 rollouts; (b) under GRPO's default per-group std normalisation, a group whose only "pass" is lucky gets *exactly the same advantages* under C-mean as under B; (c) under C-mean a lucky pass (0.2–0.8) still scores above a failure (0), so it is still reinforced. Run the zero-GPU analyses first. Then make one small retrain pair: small-slice / lucky-prone curriculum plus a min or penalty reward. Total budget is about 9–10 L4-hours (~$7).

### Cited Findings
- TRL GRPOConfig defaults: `scale_rewards="group"`, i.e. advantage = (r − mean)/std per group. `scale_rewards=False` disables std scaling. The docs cite Dr. GRPO: "scaling by std(r) may cause a question-level difficulty bias". Default `loss_type="dapo"`, `beta=0.0`, `epsilon_high` is optional (DAPO recommends 0.28), and `reward_weights` combines several reward functions. The docs I could read show no built-in zero-std-group filter, only a logged metric `frac_reward_zero_std` — [TRL GRPO Trainer docs](https://huggingface.co/docs/trl/main/en/grpo_trainer)
- Everything else is cited per question below.

### Inferences
- **[Derived] Why C-mean ≈ B under GRPO.** Group of 8 under C with one lucky pass, r = [0.2, 0×7]: mean 0.025, std 0.066, so the lucky rollout's advantage is +2.65. Under B the same group is [1, 0×7]: mean 0.125, std 0.331, advantage +2.65. They are identical, because std normalisation is scale-invariant within a group. Under C-mean the CF signal only matters in groups that contain *both* a genuine pass and a lucky pass. Even there the lucky pass keeps a positive advantage: [1, 0.2, 0×6] gives mean 0.15, so 0.2 > mean. The policy is still pushed toward lucky over failing.
- **[Derived] How the alternatives behave.** Under **min** (all-or-nothing), a lucky pass = 0, the same as a failure. A group with only lucky passes then becomes zero-variance (no gradient) instead of a positive update. Under a **penalty** (e.g. r = −1 when original passes but any CF fails), the lucky pass gets a negative advantage in every group.

**Ranked experiment list** (GPU hours on one L4 at $0.74/h):

| # | What to change | Expected outcome | L4 h / $ | Informative either way because |
|---|---|---|---|---|
| 1 | **Zero-GPU re-analysis of stored 331×8 samples (SFT, B, C).** (a) Paired item-level bootstrap or clustered SE for B−C and B−SFT. (b) pass@1 vs pass@8 per model. (c) Lucky-pass rate on test: original-pass ∧ CF-fail. | Likely shows B−C (3.7 pts) is not clearly significant once items are clustered (see power section). It also tells whether B is "sharpening" (pass@1 up, pass@8 flat). | 0 GPU, ~2 h CPU/work | If B−C *is* significant with item-clustered SE, the gap needs explaining (the C reward actively hurts). If not, the honest headline is "no detectable difference at n=1 seed". |
| 2 | **Zero-GPU advantage replay from training logs.** Recompute per-rollout GRPO advantages under B, C-mean, C-min and C-penalty(−1 and −0.5), with `scale_rewards` group vs False. Count rollouts whose advantage *sign* differs from B. | Predicts that C-mean flips the sign for ≈0 rollouts and that min/penalty flip it for all lucky ones. This is the "effective disagreement", which is smaller than the 7% raw disagreement. | 0 GPU, ~1 h | It shows whether any retrain could matter before spending GPU time. It is also a clean mechanistic figure for the write-up. |
| 3 | **Zero-GPU (or ~0.5 h) test-time multi-DB self-consistency.** For each test item, run all 8 candidate SQLs on the original + 4 CF DBs. Cluster candidates by the tuple of results across all 5 DBs, pick the largest cluster, and compare with original-DB-only majority voting and with pass@1. | Arctic reports +0.5–0.9 pts from 8-way majority voting on one DB at 7B–32B. Multi-DB signatures should split "lucky" clusters, so expect a similar or slightly larger gain, capped by pass@8. | ~0 GPU (CPU SQL execution); 0.5 h only if regenerating | Positive: a "strict verifier helps at inference" result with no training. Null: the CF DBs add no discrimination beyond one DB at this accuracy level. **Caveat:** if the CF DBs are built from the *gold* query (bug-targeted), using them at test time is not a deployable setting. Report it as an analysis, or rebuild CF DBs from schema only. |
| 4 | **Lucky-prone curriculum calibration.** Sample the SFT model (8/item) on train items with *small-slice* originals (e.g. 50 customers, where 29% of bugs are invisible). Measure the lucky-pass fraction among original-passes and the fraction of groups with 0 < pass-rate < 1. Keep items/templates with high lucky rates and nonzero variance. | Target ≥25–30% of original-passes being lucky (vs ~8% now). That raises raw disagreement 3–4x, concentrated in prompts that give gradients. | ~1 h generation (estimate) ≈ $0.75 | If even small slices give few lucky passes for this model, the CF verifier cannot matter for this model/task, which is itself a finding. |
| 5 | **Main retrain pair on that curriculum:** B (original-only, small slice) vs C′ (**min** or **penalty −1** for lucky). Same seed, same prompts, prompts prefiltered to nonzero-variance, optionally `scale_rewards=False`. Evaluate on the same 331 items. | If the single-DB verifier is now genuinely noisy (29% invisible bugs), B learns lucky patterns and C′ should beat B on CF-verified accuracy. A plausible effect is a few points, but it is uncertain. | 2 × 3.2 h = 6.4 h ≈ $4.7 | A C′ > B result gives the direct "stricter verifier matters when the single DB is a weak verifier" claim. A null even here means verifier strictness is not the bottleneck at 60 steps and 3B. Either way it is far more informative than the current pair. |
| 6 | **CF-filtered rejection-sampling fine-tune (RFT/RAFT)** using the step-4 samples: SFT on CF-all-pass trajectories vs SFT on original-pass trajectories. | RAFT is "competitive with GRPO" in math. The difference between the two arms scales with the lucky fraction (with ~8% lucky now it would be tiny; with ~30% it may be visible). | ~2 × 0.5–1 h ≈ $1–1.5 (estimate) | It is a cheap second route to the same claim, and it does not rely on GRPO advantage quirks. |
| 7 | **Seed replication** (only if budget remains): one more seed of the winning arm in #5 (or of B). | Gives a crude σ_seed estimate. | 3.2 h ≈ $2.4 | It anchors whether any observed gap exceeds run-to-run noise. |
| 8 | (Optional) **Spurious/format-only reward control**: reward = 1 for any executable SQL. | Tests whether B's +3.3 over SFT comes from correctness signal or from format/tool-use learning. | 3.2 h ≈ $2.4 | If the control matches B, then reward strictness *cannot* show up at this scale. |

Steps 1–6 come to ≈8.4 L4-h ≈ $6.2, plus eval passes (eval time not given; the team knows it). This fits <$10 and about one working day.

### Gaps
- Exact AgentTune hooks (custom reward function, group filtering, `scale_rewards` pass-through) were not checked. TRL supports `scale_rewards` and `reward_weights`, but whether AgentTune exposes them is unknown.
- No literature run measures CF/test-suite rewards inside RL for SQL specifically. All transfer is by analogy (code unit tests, math).

---

## How to raise the fraction of rollouts where rewards disagree (hard-prompt mining, curriculum, adversarial DB sizing, zero-variance filtering)

### Takeaway
There is solid evidence that filtering out zero-variance prompts and keeping "learnable" ones changes RLVR efficiency and outcomes. For this project the stronger lever is to choose the DB slice size and items so the single DB is a *weak* verifier: the current design picked a size where the two verifiers agree by construction.

### Cited Findings
- **DAPO.** Dynamic sampling drops groups that are all-correct or all-wrong, so every batch has nonzero advantages. With clip-higher (ε_high=0.28), token-level loss and overlong shaping, DAPO reaches 50 on AIME 2024 with Qwen2.5-32B, vs 47 for DeepSeek-R1-Zero-Qwen-32B, in half the steps — [DAPO project page](https://dapo-sia.github.io), [arXiv 2503.14476](https://arxiv.org/html/2503.14476v1). verl's reproduction reports 52% with dynamic sampling vs 50% without — [verl DAPO recipe](https://verl.readthedocs.io/en/v0.5.x/algo/dapo.html). A community-reported cumulative ablation (GRPO 30 → … → +dynamic sampling 50) could not be verified against the paper — [rl-llm-wiki discussion](https://huggingface.co/datasets/rl-llm-wiki/knowledge-base/discussions/94).
- **GRESO** ("Act Only When It Pays", arXiv 2506.02177) predicts zero-variance prompts *before* rollout from their reward history. A prompt that is zero-variance in the current epoch was zero-variance in a previous epoch with >90% probability. About 20% of previously zero-variance prompts become useful again, so some exploration is kept. Post-hoc dynamic sampling can need up to ~5x more rollouts when 80% of prompts are uninformative — [GRESO project page](https://infini-ai-lab.github.io/GRESO), [arXiv 2506.02177](https://arxiv.org/html/2506.02177v1).
- **Reinforce-Rej** (from "A Minimalist Approach to LLM Reasoning", arXiv 2504.11343) filters out prompts whose responses are all correct or all incorrect. It matches GRPO's final performance with better KL efficiency and stability. The paper argues GRPO's advantage over RAFT comes largely from how it handles all-wrong/negative samples — [arXiv 2504.11343](https://arxiv.org/pdf/2504.11343), [alphaxiv overview](https://alphaxiv.org/overview/2504.11343v2).
- **Arctic-Text2SQL-R1** (SQL-specific data filtering). Dropping training items whose gold SQL returns empty results or runs >5 s removed ~1,400 BIRD and ~1,700 SPIDER items. Model-based filtering of synthetic data (keep an item if ≥1 of 10 temperature-1.0 samples is correct) gave 66.5 BIRD-dev / 88.3 SPIDER-test for 14B, vs 64.6 / 86.4 for unfiltered augmentation and 64.9 / 86.8 without augmentation — [arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2).
- **Test-suite evaluation.** Single-DB denotation checking has false positives. Zhong et al. found that one database fails to distinguish 5% of "neighbor" (minimally mutated) queries, while 1,000 random DBs distinguish >99%. Distilled suites are released for 11 datasets — [Semantic Evaluation for Text-to-SQL with Distilled Test Suites, arXiv 2010.02840](https://arxiv.org/pdf/2010.02840) (2020; the closest prior work to the CF-DB idea).
- TRL logs `frac_reward_zero_std` but the docs show no built-in filter for zero-std groups — [TRL docs](https://huggingface.co/docs/trl/main/en/grpo_trainer).

### Inferences
- **[Derived]** With 3 prompts/step and an SFT pass rate of ~10%, many groups of 8 are likely all-fail (an item with p=0.1 is all-fail with probability 0.9^8 ≈ 0.43, and items with p≈0 are always all-fail). These contribute no gradient under either reward. `frac_reward_zero_std` in the existing logs gives the real number. If it is ≥0.5, half the 3.2 h was spent on dead groups.
- **[Inference]** Cheapest way to approximate dynamic sampling without touching AgentTune internals: offline prefiltering. Sample SFT 8x on the train pool and keep items with 1–7 passes out of 8 (Arctic/Reinforce-Rej style). Rank items by lucky-pass count.
- **[Inference] Adversarial DB sizing is the key design fix.** The team's own measurement says 29% of bugs are invisible at 50 customers vs <1% at 500. Training B on 50-customer originals makes B's reward a weak verifier, which is the regime where the Zhong et al. 5%-false-positive argument (and its RL analogue) predicts a stricter verifier should matter. The current run used the regime where B is already near-strict.
- **[Inference]** Mix in templates with high lucky rates (e.g. those where the bug is a missing DISTINCT, a wrong join type, NULL handling, or tie-breaking in ORDER BY/LIMIT). The CF generator is bug-targeted, so its bug taxonomy can be the curriculum axis directly.

### Gaps
- No paper found that sizes the verification DB adversarially *during RL*. This would be a novel contribution, not a replication.
- I did not verify DAPO's per-component ablation numbers in the paper itself.

---

## Reward shaping: lucky-pass penalty vs mean vs min; partial credit; binary vs graded for small models

### Takeaway
SQL-specific evidence is split. Reasoning-SQL reports small gains from partial rewards (+~1.8 EX at 7B with all rewards vs execution only). Arctic reports that simple execution plus a small syntax term works as well or better, and that finer-grained rewards caused "lazy" behaviour. Code-RL evidence (DeepCoder) favours all-or-nothing over pass fraction to avoid hacking. For CF rewards, "mean" is the weakest choice under GRPO normalisation. Use **min** or an **explicit penalty**.

### Cited Findings
- **Reasoning-SQL** (arXiv 2503.23157), Qwen2.5-Coder-7B on BIRD dev (Table 1). Execution-only EX 68.90. +syntax 68.97. +schema-linking 69.23. +n-gram 69.94. LLM-judge only 69.16. All rewards 70.66. Caveat: the table columns were garbled in extraction, and the SFT row differs between Table 1 and Table 2. Table 2 (with schema linking): 3B SFT 55.9 → GRPO all-rewards 58.67; 7B 61.53 → 64.01; 14B 63.75 → 65.31. Training used lr 1e-6, effective batch 32, 3 epochs over 8,026 BIRD items, group 6, reward weights exec 3 / judge 2 / others 1, and 8x H100. The LLM judge is applied only to queries with zero execution accuracy — [arXiv 2503.23157v2](https://arxiv.org/html/2503.23157v2).
- **Arctic-Text2SQL-R1** (arXiv 2505.20315). Reward = 1 for an execution match, 0.1 for valid executable SQL, 0 otherwise. The authors say finer-grained rewards produced "lazy" behaviour (no numbers given). Head-to-head at 14B: Arctic 66.49 BIRD-dev / 87.20 SPIDER-test vs Reasoning-SQL 64.21 / 81.43. The comparison is confounded by data filtering. 7B Arctic reaches 68.9 dev / 68.5 test on BIRD, and the 32B model was #1 on the BIRD single-model leaderboard (70.5 dev / 71.8 test) — [arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2), [HF paper page](https://huggingface.co/papers/2505.20315).
- **DeepCoder** (Agentica/Together) uses a sparse outcome reward. It deliberately avoided K/N partial credit for passing tests because partial credit could teach the model to hardcode public-test answers. It also required ≥5 unit tests per problem to limit hacking — [Together AI DeepCoder blog](https://together.ai/blog/deepcoder).
- **VeRPO** (arXiv 2601.03525) argues that a naive pass-fraction reward ignores test difficulty and risks overfitting to easy tests. It proposes difficulty-weighted dense rewards — [arXiv 2601.03525](https://arxiv.org/html/2601.03525v1).
- **Negative reinforcement.** Training only on negative samples (NSR) improves pass@k across k ≤ 256 over the base model and often matches PPO/GRPO. Positive-only reinforcement raises pass@1 but hurts high-k and collapses entropy. W-REINFORCE (upweighting the negative term) is proposed. Models: Qwen2.5-Math-7B, Qwen3-4B, Llama-3.1-8B-Instruct — [arXiv 2506.01347](https://arxiv.org/html/2506.01347v2), [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b8026fe01f5f8f7a80a1a9bf01d08cad-Abstract-Conference.html).
- **Dr. GRPO** std-normalisation bias, as documented in TRL: per-group std scaling "may cause a question-level difficulty bias". Fix: `scale_rewards=False`, which makes update size depend on the raw reward scale — [TRL docs](https://huggingface.co/docs/trl/main/en/grpo_trainer) citing "Understanding R1-Zero-Like Training" (arXiv 2503.20783; the paper itself was not re-fetched this session).

### Inferences
- **[Derived]** Under default group std scaling, C-mean gives the same advantages as B in every group whose passes are all lucky, and a lucky pass still has a positive advantage in mixed groups (see Ranked section). C-mean is therefore expected to behave like B. The observed 3.7-pt gap is more plausibly noise than reward effect, given that 93% of rollout rewards were identical.
- **[Inference] Ranking for this setup:**
  1. **Penalty**: r = 1 if all 5 DBs pass, −1 (or −0.5) if the original passes and any CF fails, 0 otherwise. This is the only option that makes lucky < fail. NSR evidence suggests negative signal is efficient and preserves entropy.
  2. **Min / all-or-nothing**, which matches the DeepCoder logic: lucky = fail.
  3. Mean, which is effectively ≈ B under std scaling.

  Pair 1 or 2 with `scale_rewards=False` only if the reward scale is kept fixed (it is here: −1…1).
- **[Inference]** Partial credit such as schema-linking Jaccard or n-gram similarity is unlikely to be the best use of one day. Reasoning-SQL's gain (~1.8 pts at 7B over 3 epochs × 8k items) sits within plausible seed noise for a single 60-step run. Arctic reports hacking/laziness. The 0.1 syntax-valid bonus is a cheap, low-risk densifier for a 10%-accuracy model, but it dilutes the CF contrast. Keep it fixed across arms if used.
- **[Inference] Asymmetric magnitude:** a −0.5 penalty is a safer first try than −1. A small model at ~10% accuracy may otherwise learn to avoid answering, or to produce empty or erroring SQL, if failure (0) beats a lucky attempt by a large margin. Monitor the fraction of executable outputs.

### Gaps
- No ablation found of min vs mean vs penalty for *multi-DB* SQL rewards.
- I could not confirm whether Reasoning-SQL's gains were averaged over seeds (seeds are not reported in the extracted sections).

---

## Using the CF verifier outside RL: RFT / STaR / expert iteration; best-of-n and self-consistency at inference

### Takeaway
Rejection-sampling fine-tuning on positively verified samples is competitive with GRPO in math, so CF-filtered RFT is a cheap, clean test of verifier strictness. Execution-based majority voting gives SQL models about +0.5–2 pts. A multi-DB result signature is a natural stricter version and needs no GPU, given the stored 331×8 samples.

### Cited Findings
- **RAFT** (training only on positively rewarded samples) is "competitive" with GRPO/PPO. RAFT++ (adding importance sampling and clipping) is reported near GRPO: 52.5 vs 53.9 average on Qwen2.5-Math-7B (exact figures differ across summaries). RAFT++ converges faster early and is overtaken later. Models: Qwen2.5-Math-7B and LLaMA-3.2-3B-Instruct — [arXiv 2504.11343](https://arxiv.org/pdf/2504.11343), [alphaxiv overview](https://alphaxiv.org/overview/2504.11343v2).
- **Arctic voting** on BIRD-dev with 8 generations. 14B: baseline 70.1 → voting 70.6 → voting + value retrieval 70.8. 32B: 70.5 → 71.2 → 71.5. 7B: 63.9 → 64.8 BIRD-dev and 85.0 → 87.1 SPIDER-test — [arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2).
- **Test suites.** Multiple databases discriminate semantically different queries that coincide on one DB: one DB misses 5% of neighbours, a distilled suite misses <1% — [arXiv 2010.02840](https://arxiv.org/pdf/2010.02840).
- **PSR vs NSR.** Positive-only reinforcement (which is what RFT effectively does) raises pass@1 but lowers high-k pass@k and entropy — [arXiv 2506.01347](https://arxiv.org/html/2506.01347v2).

### Inferences
- **[Inference] Zero-GPU measurements on the stored samples:**
  - (i) **Oracle CF reranking.** Fraction of items where any of the 8 samples passes all 5 DBs. This is CF-verified pass@8, the ceiling for any reranker/RFT.
  - (ii) **Original-only oracle** (pass@8 on 1 DB) minus (i) = the number of items where best-of-8 would be fooled by a lucky pass.
  - (iii) **Non-oracle multi-DB self-consistency**: majority vote over result signatures across 5 DBs vs over 1 DB.
  - (iv) **pass@1 for SFT, B and C.**

  All four only need SQL re-execution on CPU. (iii) is the only deployable one, and only if the CF DBs can be generated without the gold query.
- **[Inference] RFT design.**
  1. Sample the SFT model 8x on train items, preferably on small-slice originals to increase lucky passes.
  2. Build set A = original-pass trajectories and set B′ = CF-all-pass trajectories. Dedupe up to ~2 per item.
  3. Train two LoRA SFTs from the SFT checkpoint with the same steps.
  4. Evaluate on the 331 items.

  The expected gap is roughly proportional to the share of lucky trajectories in A. At ~8% lucky it will be undetectable. At ~30% (small slices) it has a chance.
- **[Inference]** RFT drops negative signal, which NSR suggests carries much of RLVR's benefit. Expect RFT to raise pass@1 but not pass@8.

### Gaps
- No SQL paper found that compares RFT filtered on multi-DB vs single-DB verification.
- Generation throughput of 3.35B on an L4 for multi-turn rollouts was not measured; the 0.5–1 h estimates are extrapolated from the team's own 24 rollouts/step at ~3.2 min/step. Measure before committing.

---

## Statistical power: run-to-run GRPO variance and how many seeds are needed for ~3 points

### Takeaway
With one seed per arm, a 3–4-point gap at ~10% accuracy is not distinguishable from run-to-run noise. Published small-model RLVR runs show seed SDs of ~0.5–3 pts. That implies roughly 3 seeds per arm at the optimistic end and 10+ at a 2-pt SD for 80% power at Δ=3. The <$10 budget cannot buy that. Report paired item-level CIs and frame claims as "no detectable difference / mechanism-level evidence".

### Cited Findings
- **"A Sober Look at Progress in LM Reasoning"** (arXiv 2504.07086, COLM 2025): many reported RL gains for 1.5B models fall within the seed/decoding variance of the DeepSeek-R1-1.5B baseline. On small benchmarks, seed changes give "double-digit" swings. The authors recommend ≥10 seeds on small benchmarks and reporting mean ± SD — [arXiv 2504.07086](https://arxiv.org/abs/2504.07086). (These numbers concern evaluation-seed variance on AIME/AMC-size sets, which are much smaller than 331 items.)
- **Training-seed variance examples:**
  - 2B GUI-grounding GRPO, 3 seeds: range 0.4–0.9 pts — [arXiv 2606.25964](https://arxiv.org/pdf/2606.25964).
  - Qwen3-4B code RLVR, 5 runs: baseline SDs around 1–3 pts, "noticeable variance across runs" — [arXiv 2605.28022](https://arxiv.org/pdf/2605.28022).
  - Qwen2.5-Math-7B: method-vs-GRPO margins of +2.3 to +4.4 pts across 3 seeds — [arXiv 2608.03467](https://arxiv.org/pdf/2608.03467).

  These come from search-result summaries and were not fully read.
- **"Adding Error Bars to Evals"** (Miller, arXiv 2411.00640): use question-level *paired* differences when comparing models. Use clustered SEs when items are grouped; clustered SEs can be >3x naive SEs on popular evals — [arXiv 2411.00640](https://arxiv.org/pdf/2411.00640), [Anthropic post](https://www.anthropic.com/research/statistical-approach-to-model-evals).
- Classic deep-RL power analysis: [How Many Random Seeds?, arXiv 1806.08295](https://arxiv.org/pdf/1806.08295) (2018; methodology only).

### Inferences
- **[Derived] Eval noise for one model** at p≈0.11 with 331 items × 8 samples:
  - Worst case (all 8 samples per item identical): SE = √(0.098/331) ≈ 1.7 pts.
  - Best case (independent samples): √(0.098/2648) ≈ 0.6 pts.

  The truth lies between, and the stored data gives it exactly via an item-clustered bootstrap. For B−C unpaired worst case, SE ≈ 2.4 pts, so z ≈ 1.5 for Δ=3.7 (not significant). The paired best case gives z > 4. Compute it.
- **[Derived] Seeds per arm** for 80% power, two-sided α=0.05, Δ=3 pts: n ≈ 2·(1.96+0.84)²·σ²/Δ² = 1.74·σ², where σ² = σ_seed² + SE_eval². Taking SE_eval ≈ 1.2:

  | σ_seed (pts) | Seeds per arm |
  |---|---|
  | 0.5 | ~3 |
  | 1 | ~5 |
  | 2 | ~10 |
  | 3 | ~19 |

  At 3.2 h × $0.74 ≈ $2.4 per run, even 3 seeds/arm (4 extra runs ≈ $9.5) exhausts the budget.
- **[Inference]** It is more useful to spend at most 1 extra run on a repeat seed to get a crude σ_seed, and to evaluate intermediate checkpoints (e.g. steps 30/45/60) as a cheap noise proxy. Put the remaining budget into making the effect larger (curriculum + penalty) rather than measuring a near-zero effect more precisely.
- **[Inference]** B vs SFT (+3.3) carries the same caveat. Do not claim "GRPO helped" without the paired CI.

### Gaps
- No study found that reports training-seed variance specifically for ~3B LoRA GRPO on text-to-SQL.

---

## Is 60 steps too short? KL, learning rate, LoRA and when reward design starts to matter

### Takeaway
Yes, very likely. 60 steps × 3 prompts ≈ 180 prompt-groups is under 1% of the prompt exposure in published SQL-GRPO runs. LoRA evidence says RL needs little capacity but many episodes. Under these conditions only gross reward differences, not a 7%-of-rollouts difference, can show up.

### Cited Findings
- **Reasoning-SQL** trains 3 epochs over 8,026 BIRD items: ~24k prompt-visits, effective batch 32, group 6, lr 1e-6. Its figures show 200+ steps, and a 3B checkpoint is cited at step 849 — [arXiv 2503.23157v2](https://arxiv.org/html/2503.23157v2).
- **Arctic-Text2SQL-R1**: batch 256 with 16 rollouts per prompt, KL β=0.001, clip 0.2, temperature 0.8. 16/24/32 rollouts gave no significant difference. Compute was 64 H100s, from a few hours (7B) to 2.5 days (32B). Online RL beat batch RL (66.6 vs 64.9 BIRD-dev at 32B) — [arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2).
- **"LoRA Without Regret"** (Thinking Machines, Sep 2025): LoRA matches full fine-tuning for RL even at very low ranks, which the authors relate to policy gradients extracting ~O(1) bits per episode. The best LoRA learning rate is ~10x the full-FT rate, and LoRA is less tolerant of large batches — [Thinking Machines blog](https://thinkingmachines.ai/blog/lora/), [TRL "LoRA without regret" docs](https://huggingface.co/docs/trl/main/en/lora_without_regret).
- **Spurious rewards**: on Qwen2.5-Math-7B, random rewards give +21.4 and ground-truth +29.1 MATH-500 points, but Llama-3.1-8B and OLMo2-7B do not benefit from spurious rewards. Part of the effect is attributed to GRPO clipping bias — [Spurious Rewards, arXiv 2506.10947](https://par.nsf.gov//servlets/purl/10631836), [ICML 2026 poster](https://icml.cc/virtual/2026/poster/61082).

### Inferences
- **[Derived]** Differential signal in the current run ≈ 7% × 1,440 ≈ 100 rollouts. Under C-mean with std scaling, almost none of those received a different-sign advantage. At ~1 bit/episode (LoRA-without-regret heuristic), that is on the order of tens of bits of "CF-specific" information: not enough to move a 3B policy measurably.
- **[Inference]** Early RL gains in short runs are often format/tool-use and sharpening effects, which both B and C share. The spurious-reward results show that early gains can be reward-content-independent for some model families, and Aya's behaviour here is unknown. Hence the optional format-only control (#8 in the ranked list).
- **[Inference] Practical levers within budget:**
  - Raise prompts/step at fixed rollouts by reducing the group to 4–6 if group 8 is mostly zero-variance. Arctic found rollout count insensitive between 16 and 32; no evidence found for groups below 8.
  - Check that the LoRA LR is in the ~1e-5–5e-5 range (10x full-FT, by the LoRA-without-regret rule) rather than a full-FT value like 1e-6.
  - Keep β small (0.0–0.001; the TRL default is 0.0).

  Doubling steps to 120 for one arm costs 6.4 h. That is only worth it after the curriculum change raises the disagreement rate.

### Gaps
- No paper found that directly measures "number of GRPO steps before reward-design differences become detectable" for small models.
- The team's actual LoRA learning rate and β were not given here.

---

## Process rewards / multiple verifiers / verifier ensembles relevant to SQL

### Takeaway
The CF-DB reward is itself a verifier ensemble (a test suite). SQL-RL literature mostly combines execution with weaker auxiliary signals (syntax, schema linking, LLM judge). Arctic's results suggest the extra verifiers add little at scale. For this budget, a multi-DB execution ensemble with a penalty is the right "multi-verifier"; LLM-judge or process rewards are not worth the cost.

### Cited Findings
- Reasoning-SQL combines execution, an LLM judge (only on failed executions), syntax, schema-linking Jaccard and n-gram rewards, weighted 3/2/1/1/1. All rewards together gave +~1.8 EX over execution-only at 7B — [arXiv 2503.23157v2](https://arxiv.org/html/2503.23157v2).
- Arctic uses execution + syntax only, outperforms Reasoning-SQL at 14B (confounded by data), and reports "lazy" behaviour with finer-grained rewards — [arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2).
- Multi-DB test suites cut single-DB false positives from 5% of neighbour queries to <1% — [arXiv 2010.02840](https://arxiv.org/pdf/2010.02840).
- DeepCoder: all-or-nothing over many tests, and a minimum test count as an anti-hacking measure — [Together AI DeepCoder blog](https://together.ai/blog/deepcoder).

### Inferences
- **[Inference]** By analogy with DeepCoder's "≥5 tests" rule, 4 CF DBs is a reasonable ensemble size. Item-level diversity of bug targets matters more than adding DBs.
- **[Inference]** An LLM-judge reward would need a second model on a single L4 alongside vLLM rollouts. It does not fit the budget, and it confounds the strict-verifier question.

### Gaps
- Not covered this session: process reward models for SQL, verifier-pitfall papers (e.g. false negatives from rule-based verifiers), and Weaver-style weak-verifier aggregation. I did not search them because of the tool-call budget.
- SQL-R1 (arXiv 2504.08600) and "Does RL Really Incentivize Reasoning" (arXiv 2504.13837, Yue et al., which finds that base models match or beat RL models at large-k pass@k) were not re-verified this session. The second is relevant to the pass@8-vs-pass@1 check in the ranked list but should be verified before citing numbers.
