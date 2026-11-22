# Seed rewrite: apply after seed 2 (fixes 2, 6, 7)

Numbers come from `results/seeds_eval.json` and `results/e13_spider_ours.json` (`*_s1`, `*_s2`, `*_pool`). The `[S2 ...]` slots wait for seed 2. Seeds 0 and 1 are known (Nov 22).

## The likely story (if seed 2 does not overturn it)

- Both rewards have deterministic audit results. These don't depend on training seeds.
- Training:
  - Neither reward reliably beats SFT in 60 GRPO steps.
  - C stays at the SFT level (9.0, 8.8, [S2]).
  - B swings widely (12.7, 7.6, [S2]).
- Methods lesson:
  - The between-seed SD of C−B (3.5 points over 2 seeds) is about twice the half-width of a one-seed question-bootstrap CI.
  - So a one-seed CI that excludes 0 is not evidence about a reward.
  - This fits a trusted-AI venue: it is about how RL reward comparisons are reported.

## Edits by line (main.tex as of 853790a)

- **l.41 abstract:**
  - Replace "(9.0\% vs 12.7\%) ... on Spider it suggests a small transfer gain of 1.9 points."
  - New text: "did not improve accuracy over three training seeds (C−B pooled [S2 pooled]); a single seed's interval excluded zero in both directions, so seed variance, not the reward, set the sign."
- **l.99:** change "Arms share initialization, data, seed and hyperparameters" to "Arms share initialization, data and hyperparameters; each arm is trained with three seeds (0–2), which change prompt order (dataset shuffle) and the trainer RNG (TRL `seed`)."
- **l.102:**
  - Replace "Each arm has one seed."
  - New text: "The primary test is the paired, question-clustered bootstrap of C−B, pooled over seeds; per-seed intervals understate uncertainty because they ignore training variance. At 80% power a single seed detects about 2 points and the pool about 1.5 [S2 update]."
- **l.138:**
  - Rewrite as a per-seed list or a small table: B−SFT and C−SFT per seed.
  - Seed 0: +3.2 / −0.5. Seed 1: −1.9 / −0.6. [S2]
  - Keep the "rewards disagreed on about 7% of rollouts" explanation; it is seed 0's training log. Seed 1 agrees: 84% single-DB pass, 8.3% (B_s1) / 8.1% (C_s1) of passes lucky, i.e. about 7% of rollouts (`scripts/figure3.py B_s1 C_s1`; it overwrites results/figure3_*, so restore them with git checkout after). Rerun for s2.
  - Keep the curriculum sentence (one seed, so flag it as such).
- **l.142, Spider:**
  - Seed 0: +1.9 [+0.6, +3.3]. Seed 1: −0.5 [−1.8, +0.7]. Pooled over seeds 0+1: +0.7 [−0.2, +1.6]. [S2 pooled]
  - Drop "suggests a transfer gain" unless the three-seed pool excludes 0.
- **l.152, Limitations:** change "one seed per arm" to "three seeds per arm (one for the curriculum pair)".
- **l.246, table:** the hyperparameters table row "Seed & 0 & 0" becomes "Seeds & 0–2 & 0–2".
- **l.299–300, appendix "Second seed":** replace the paragraph with "Seeds", giving the per-seed table (verified B, C, C−B, B−SFT, C−SFT; Spider TS C−B) and the between-seed SD.

## Checks to add to scripts/check_numbers.py

- The per-seed C−B, B−SFT and C−SFT values from `seeds_eval.json`.
- Pooled C−B, and the pooled Spider C_pool_vs_B_pool.
- The between-seed SD.

## Space

- 4-page limit: the l.138 rewrite must not grow.
- Move the per-seed table to the appendix and keep only pooled numbers in the main text.
