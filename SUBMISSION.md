# Lexsi submission pack

The form field by field, ready to paste. Submission deadline **Nov 15, 2026, 11:59 PM AoE = Nov 16, 17:29 IST** (extended by a day, team news Nov 11).

**Submit-page write-up checklist (Nov 16), required items → where in ARTICLE.md:** title + claim, tracks/problem statements (header) · abstract with before→after · problem and approach (§1–3) · kits used and how they connect (Appendix A) · base model + licence (§3.3, App. A) · data sources, splits, leak check, languages (§3.1) · metrics (§3.4) · setup and hyperparameters (§3.3, §8) · before-vs-after table (Table 2) · limitations (§9) · with more credits + expected before/after (§10) · artifacts and collections (App. A) · repo layout + run instructions (README) · declaration of outside work, teammates tagged with HF + GitHub links (last two sections). Resubmission is allowed and the latest one counts. The form says **every repo in the collections must be public by Nov 15, 11:59 PM AoE**, so the form can go in while the repos are still private. The HF Article field is required; the organisers accept an HTML page on HF (our project-page Space).


## Page 1: Your team

- **Registered email:** the exact address one of us registered with (Shreshth's, as team lead, unless someone else registered).
- **Abstract** (369 words, limit 500; plain-text copy of ABSTRACT.md). Paste the block below:

```text
Text-to-SQL agents trained with reinforcement learning usually get rewarded when their answer matches the gold answer on one database. A wrong query can match by luck, and then the reward teaches the luck. Our defence is to run the agent's final query on a few extra copies of the database as well, and to pay only if it is right on all of them. The agent never sees these copies, and code builds each one to expose a particular kind of bug.

We first checked the reward itself, without training anything. On a single database, almost a third of realistic buggy queries get paid. With the copies, about one in six do, and queries that try to game the reward almost never get through. No correct query was rejected. Two public SQL rewards, AgentTune's and SkyRL-SQL's, have the same holes, and we patched AgentTune's. The problem is not specific to our data: on Spider, between 8 and 15 percent of the answers that eight published systems get right fail on Zhong et al.'s test-suite databases.

We then trained Tiny Aya Global (3.35B) with GRPO, once with each reward. On our own test set the stricter reward did not help. Logging every rollout shows why: the two rewards disagreed on only about 7 percent of them, because our training questions were too easy for lucky answers to come up. The real-world benchmark tells a different story. On Spider, a public set of real databases that we did not build, the model trained with the copies beats the model trained on one database by about two points of test-suite accuracy, and it makes fewer lucky passes. A second pair of runs, trained only on hard questions where lucky answers are common, repeats that two-point gap on Spider; on our own test set it is again a null. Self-hosted, our model costs far less per query than Cohere Command A, but it is much less accurate and does not replace it.

We release the data generator, the databases, every rollout with its reward on each database, a browser demo, and a script that re-derives every number. The reward audit is the main result. The training results are reported as they came out.
```
- **Discord username:** the submitter's own Discord username.

## Page 2: Your artifacts

- **HF model collection:** https://huggingface.co/collections/sqlcf-lexsi/counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4 (3 LoRA adapters + the demo Space).
- **HF dataset collection:** https://huggingface.co/collections/sqlcf-lexsi/counterfactual-sql-data-rollouts-and-traces-6af479430243b7731f85d144 (`counterfactual-sql-data`: items, all DBs, SFT data, every GRPO rollout with per-DB rewards, eval trajectories, results).
- **HF article:** https://huggingface.co/spaces/sqlcf-lexsi/counterfactual-sql-article (project page built from ARTICLE.md by `scripts/make_site.py`; organisers said on Nov 12 that an HTML page on HF or Markdown on GitHub is accepted).
- **GitHub repo:** https://github.com/RishiiGamer2201/sexsi_hack

## Page 3: Repos, models, tracks

- **Repos used:** tick [x] AgentTune, [x] AuditKIT, [x] Other.
  - If Other asks for names: SkyRL-SQL reward (`NovaSky-AI/SkyRL` `d870046`, E7); ESM+ predictions (`bossben/ESMp` `91dd85b`) and the Zhong et al. 2020 test-suite DBs (E6).
- **Models used:** tick [x] Tiny Aya Global, [x] Other.
  - If Other asks for names: Cohere Command A `command-a-03-2025`, used for the ROI comparison.
- **Track:** tick [x] Track 3: Agentic Fine-tuning.
- **Problem statements (at most 2):** tick [x] Data and database agents, [x] Reward design and reward-hacking defences.

## Go-live order

1. **Refresh the article page:** `source .secrets.env && .venv-train/bin/python scripts/make_site.py` (Space `sqlcf-lexsi/counterfactual-sql-article`, private; `go_public.py` makes it public). Put its URL in the form.
2. Send the form.
3. Right after that, run `source .secrets.env && .venv-train/bin/python scripts/go_public.py` as a dry run, then again with `--go`. This makes the following public:
   - the 3 adapters (gated, automatic approval);
   - the dataset and the Space;
   - both collections;
   - the GitHub repo.
4. Open every link logged out, in a private window, before Nov 15, 11:59 PM AoE.

## Facts the write-up and judges look for

- **Title:** When Execution Success Lies: counterfactual-database rewards for a small SQL agent.
- **Team Teen_khapeetars:** Shreshth Rai (lead), Rishii Kumar Singh, Aksh Aggarwal.
- **Before/after (test set, 331 items × 8 samples; verified = right on the original DB and on all 4 copies):**
  - verified accuracy: SFT 9.4% → GRPO-B 12.7% (+3.2 pts, McNemar p = 0.006);
  - pass^2: 4.9% → 8.1%;
  - silent errors: 65.4% → 64.0%;
  - GRPO-C (counterfactual reward): 9.0%. This is a null result and is reported as one.
- **Reward before/after (the contribution):**
  - hacks paid: 54.1% → 1.9%;
  - buggy mutants paid: 29.5% → 16.8%;
  - correct queries rejected: 0 of 2847;
  - AgentTune `WHERE 1 = 1` exploit: 3.10 → 2.20 with our patch;
  - [AgentTune#11](https://github.com/Lexsi-Labs/AgentTune/issues/11) was fixed upstream in [PR #12](https://github.com/Lexsi-Labs/AgentTune/pull/12).
- **ROI:**
  - Command A reaches 81.0% verified at $4.24 per 1k queries. Tiny Aya B costs $0.061 per 1k on one L4 ($0.74/hr).
  - Tiny Aya is about 70× cheaper per query and about 11× cheaper per verified answer ($0.48 vs $5.24).
  - At 12.7% it is not a replacement for Command A.
- **Aksh's tasks (E10–E12):**
  - DPO from one checkpoint (E10), on the same rollouts with single-DB vs counterfactual labels: 9.7% vs 8.1% verified (start 9.4%). No gain, and lucky passes stay at 4.5% under both.
  - Partial credit (E11) pays mutants 0.66 on average, against 0.30 for the binary reward, and pays literal smuggling 0.86, against 0 for the strict reward. So it was not trained.
  - A period-edge copy (E12) cuts date bugs paid from 91% to 33%, with 0 of 1554 correct queries rejected. It rejects under 1% of the models' real verified answers.
- **Licences:**
  - adapters: CC-BY-NC-4.0 (the base model's licence), gated with automatic approval, per the organisers' Nov 9 ruling;
  - data: CC-BY-NC-4.0, synthetic, no personal data.

## Checklist

- [x] Every number reproduced by `verify_all.py` (Nov 14); tests pass; abstract rewritten Nov 15 (fewer numbers, plain wording)
- [x] Git history scanned: no tokens or keys in any commit
- [x] Two collections (models + demo; dataset), as the form asks
- [x] Article page Space refreshed (`make_site.py`), paper layout, Nov 15
- [ ] Form sent
- [x]  run Nov 16 ~14:10 IST; all 12 links return 200 logged out
