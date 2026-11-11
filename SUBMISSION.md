# Lexsi submission pack

The form field by field, ready to paste. Submission deadline **Nov 14, 2026, end of day AoE**. Resubmission is allowed and the latest one counts. The form says **every repo in the collections must be public by Nov 15, 11:59 PM AoE**, so the form can go in while the repos are still private. The HF Article field is required, and there is no GitHub fallback for it.

Generate the paste files first: `python scripts/make_hf_article.py` writes `runs/abstract.txt` and `runs/hf_article.md`.

## Page 1: Your team

- **Registered email:** the exact address one of us registered with (Shreshth's, as team lead, unless someone else registered).
- **Abstract:** paste `runs/abstract.txt`. This is ABSTRACT.md as plain text, under 500 words; the script asserts the count.
- **Discord username:** the submitter's own Discord username.

## Page 2: Your artifacts

- **HF model collection:** https://huggingface.co/collections/sqlcf-lexsi/counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4 (3 LoRA adapters + the demo Space).
- **HF dataset collection:** https://huggingface.co/collections/sqlcf-lexsi/counterfactual-sql-data-rollouts-and-traces-6af479430243b7731f85d144 (`counterfactual-sql-data`: items, all DBs, SFT data, every GRPO rollout with per-DB rewards, eval trajectories, results).
- **HF article:** the URL of the published Article (see go-live step 1).
- **GitHub repo:** https://github.com/RishiiGamer2201/sexsi_hack

## Page 3: Repos, models, tracks

- **Repos used:** tick [x] AgentTune, [x] AuditKIT, [x] Other.
  - If Other asks for names: SkyRL-SQL reward (`NovaSky-AI/SkyRL` `d870046`, E7); ESM+ predictions (`bossben/ESMp` `91dd85b`) and the Zhong et al. 2020 test-suite DBs (E6).
- **Models used:** tick [x] Tiny Aya Global, [x] Other.
  - If Other asks for names: Cohere Command A `command-a-03-2025`, used for the ROI comparison only.
- **Track:** tick [x] Track 3: Agentic Fine-tuning.
- **Problem statements (at most 2):** tick [x] Data and database agents, [x] Reward design and reward-hacking defences.

## Go-live order

1. **Publish the HF Article** at huggingface.co › New Article, under org `sqlcf-lexsi`:
   - paste `runs/hf_article.md`;
   - tag @hi-phi-r25i, @LogicPalette and @AkshAgg;
   - copy its URL into the form.
   - Its figures load from the dataset, so they show only once the dataset is public (step 3).
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
- **Licences:**
  - adapters: CC-BY-NC-4.0 (the base model's licence), gated with automatic approval, per the organisers' Nov 9 ruling;
  - data: CC-BY-NC-4.0, synthetic, no personal data.

## Checklist

- [x] Every number reproduced by `verify_all.py` (Nov 11); tests pass; abstract 491 words
- [x] Git history scanned: no tokens or keys in any commit
- [x] Two collections (models + demo; dataset), as the form asks
- [ ] HF Article published
- [ ] Form sent
- [ ] `go_public.py --go` run; every link opens logged out (by Nov 15, 11:59 PM AoE)
