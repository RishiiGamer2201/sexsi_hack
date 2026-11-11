# Lexsi submission pack

Everything the form asks for, ready to paste. Deadline **Nov 14, 2026, end of day AoE**; resubmission allowed, latest counts. Judging first checks validity: **artifacts public**, write-up and checklist submitted.

## Go-live order (team rule: public only right after the form is sent)

1. Send the form with the links below (the write-up field can be the GitHub `ARTICLE.md` link).
2. Right after: `source .secrets.env && .venv-train/bin/python scripts/go_public.py` (dry run, check), then `--go`. Flips 3 adapters (gated, automatic approval), dataset, Space, collection and the GitHub repo to public.
3. Publish the HF Article: `python scripts/make_hf_article.py`, paste `runs/hf_article.md` into huggingface.co › New Article (org `sqlcf-lexsi`), tag @hi-phi-r25i @LogicPalette @AkshAgg.
4. Resubmit the form with the Article URL. Open every link logged out (private window) to confirm.

## Form fields

- **Team:** Teen_khapeetars: Shreshth Rai (lead), Rishii Kumar Singh, Aksh Aggarwal.
- **Registered email:** the team lead's registered address.
- **Track / problem statements:** Track 3; #6 Data and database agents, #9 Reward design and reward-hacking defences.
- **Title:** When Execution Success Lies: counterfactual-database rewards for a small SQL agent.
- **Abstract (<500 words):** `ABSTRACT.md` (491 words).
- **Model collection:** https://huggingface.co/collections/sqlcf-lexsi/counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4
  - https://huggingface.co/sqlcf-lexsi/tiny-aya-global-sqlcf-sft
  - https://huggingface.co/sqlcf-lexsi/tiny-aya-global-sqlcf-grpo-b
  - https://huggingface.co/sqlcf-lexsi/tiny-aya-global-sqlcf-grpo-c
- **Dataset:** https://huggingface.co/datasets/sqlcf-lexsi/counterfactual-sql-data (items, DBs, SFT trajectories, every GRPO rollout, eval trajectories, results).
- **Public deployment (demo):** https://huggingface.co/spaces/sqlcf-lexsi/counterfactual-sql-demo (runs in the browser).
- **GitHub (reproducibility):** https://github.com/RishiiGamer2201/sexsi_hack (`python verify_all.py` re-derives every number).
- **Write-up:** HF Article URL (step 3); fallback https://github.com/RishiiGamer2201/sexsi_hack/blob/main/ARTICLE.md
- **Lexsi repos used:** AgentTune `d4db4c1` (multi-turn GRPO with tools, render/parse/fold, provenance; we patched its multi-turn token stream, and our SQL-reward report [AgentTune#11](https://github.com/Lexsi-Labs/AgentTune/issues/11) was fixed upstream in [PR #12](https://github.com/Lexsi-Labs/AgentTune/pull/12)); AuditKIT `9da5838` (silent-error framing, pass^k).
- **Models used:** CohereLabs/tiny-aya-global 3.35B (trained policy, LoRA); Cohere Command A `command-a-03-2025` (ROI comparison only).
- **Other data used:** Zhong et al. 2020 Spider test-suite DBs and the ESM+ prediction files (`bossben/ESMp` `91dd85b`) for E6; SkyRL-SQL's reward for E7. Not redistributed.
- **Before/after (test, 331 items × 8, verified = right on original + all 4 copies):** SFT 9.4% → GRPO-B 12.7% verified (+3.2 pts, McNemar p = 0.006); pass^2 4.9% → 8.1%; silent error 65.4% → 64.0%. GRPO-C (counterfactual reward) 9.0%: null, reported as one.
- **Reward before/after (the contribution):** hacks paid 54.1% → 1.9%; buggy mutants paid 29.5% → 16.8%; 0/2847 correct queries rejected; AgentTune `WHERE 1 = 1` exploit 3.10 → 2.20 with our patch.
- **ROI:** Command A 81.0% verified at $4.24 per 1k queries vs Tiny Aya B $0.061 on one L4 ($0.74/hr): ~70× cheaper per query, ~11× per verified answer ($0.48 vs $5.24), not a replacement at 12.7%.
- **Licences:** adapters CC-BY-NC-4.0 (base model's), gated with automatic approval per the organisers' Nov 9 ruling; data CC-BY-NC-4.0, synthetic, no personal data.

## Checklist

- [x] Every number reproduced by `verify_all.py` (Nov 11), tests pass, abstract 491 words
- [x] Git history scanned: no tokens or keys in any commit
- [x] Article has all 9 sections the slides ask for (problem, repos, models, datasets, model and data collections, experiments, "with more credits", team tags)
- [ ] Form sent
- [ ] `go_public.py --go` run; every link opens logged out
- [ ] HF Article published; form resubmitted with its URL
