# Self-review of iteration 0 (written as a skeptical reviewer)

## Summary a reviewer would write

The paper adds hidden counterfactual databases to the execution-match reward for text-to-SQL RL. It audits the new reward on fixed candidate queries: full pay on buggy queries falls from 29.5% to 16.8%, full pay on hacks falls from 54.1% to 1.9%, and 0 correct queries are rejected. It finds an exploit in AgentTune's reward, now fixed upstream. In GRPO training on a 3.35B model, the CF reward does not improve in-domain accuracy, and it shows a small (+1.9 point), weakly significant gain on Spider.

## Top 3 weaknesses

1. **The training result is a null, and the positive signal is thin.**
   - In domain, the CF arm is worse than the single-DB arm (9.0% vs 12.7%).
   - The Spider gain has McNemar p = 0.14 and 0.94. Its bootstrap treats the 4 samples per question as independent. The main-pair comparison was not pre-registered.
   - Each arm has one seed and 60 steps.
   - A reviewer may read "it suggests a transfer gain" as overclaiming. **Fix for the next iteration:** evaluate the stranded seed-1 adapters, and run more seeds or longer training on prompts where the rewards disagree (the curriculum idea).
2. **Synthetic, single-schema evaluation.**
   - The audit, training and test all use one generated retail schema. The bug families were written by us, the same people who wrote the copies.
   - The test copies are weaker than the training reward (they catch 54 of 103 base-blind mutants).
   - Spider transfer is the only real-data evidence.
   - **Fix:** run the audit on BIRD or Spider with automatically generated counterfactual copies, or on a second schema.
3. **The headline audit partly uses copies informed by the bugs, and the bug families are ours.**
   - Training used the informed copies (1.5% mutant pay, an optimistic bound). The blind number (16.8%) misses the pre-registered 50% cut.
   - A reviewer will ask how the method does on bugs nobody thought of.
   - **Fix:** a held-out family (F4 is already held out at test time; report its audit separately), plus a red-team attempt by someone outside the team.

## Smaller issues

- Several 2025–26 citations are incomplete (see `citations_to_verify.md`).
- The family names (F1–F4) follow the code. Check that they read well to outsiders.
- Figure 1 uses colour to tell the rewards apart. It also labels them in text, so it can be read in grayscale.
- The body uses the full 4 pages, so adding content means cutting something.
