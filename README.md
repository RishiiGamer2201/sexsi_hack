# When Execution Success Lies — counterfactual-DB rewards for a small SQL agent

Lexsi hackathon, Track 3 (PS #6 + #9), team Teen_khapeetars. Full write-up: [ARTICLE.md](ARTICLE.md). Submission pack: [SUBMISSION.md](SUBMISSION.md). Plan: [plan.md](plan.md). Log: [progress.md](progress.md). Background: [research.md](research.md).

## Judge's 60-second view

A text-to-SQL agent is usually rewarded for matching the gold answer on **one** database, and a wrong query can match by luck. We also check it on code-generated **counterfactual copies** of the database that the agent never sees.

| Result | Number (95% CI) |
|---|---|
| Buggy gold-mutants paid by the single-DB reward | 29.5% [27.4, 31.6] |
| Same mutants paid by the counterfactual reward (CFs chosen blind to the mutants) | 16.8% [15.2, 18.6]: a 43% cut; pre-registered target 50%, not met |
| Reward hacks (literal smuggling, hard-coded IDs, ...) paid: single-DB → counterfactual | 54.1% → 1.9% |
| Correct queries rejected by the counterfactual reward | 0 / 2847 |
| AgentTune's built-in SQL reward: `WHERE 1 = 1` + always "yes" | 3.10, same as honest SQL on yes-questions; 2.20 with our patch |
| SkyRL-SQL's reward (set compare, one DB): mutants / hacks paid | 37.5% / 53.2%; with copies + strict compare 16.8% / 1.9% |
| Spider dev, 8 published systems: share of correct-looking answers that fail a test-suite DB | 8.1% – 14.9% |
| Test verified accuracy (Tiny Aya 3.35B): base / SFT / GRPO-B single-DB reward / GRPO-C counterfactual reward | 0.9% / 9.4% / **12.7%** / 9.0% |
| GRPO-C vs GRPO-B (pre-registered H4) | **null**: C is not better (−3.7 pts verified, p < 0.001; silent error p = 0.61) |
| Why: rollouts on which B's and C's rewards differed during training | about 7% |
| Command A (single-turn) | 81.0% verified, $4.24 per 1k queries vs $0.06 for Tiny Aya B on an L4 |
| DPO from sft_ho, same rollouts, single-DB vs counterfactual labels (E10) | 9.7% vs 8.1% verified (start 9.4%): no gain; lucky passes 4.5% under both |
| Partial credit instead of 0/1 (E11): mutants paid on average / literal smuggling paid | 0.66 vs 0.30 binary / 0.86 vs 0 strict: more signal, all of it towards wrong answers |
| Period-edge copy for year questions (E12): date bugs paid / real verified answers it rejects | 91% → **33%**, 0 of 1554 correct rejected / under 1% (B 2 of 305, C 2 of 218) |

Every number is re-derived from stored runs by `python verify_all.py`. On Hugging Face: [model collection](https://huggingface.co/collections/sqlcf-lexsi/counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4) (adapters + demo) and [data collection](https://huggingface.co/collections/sqlcf-lexsi/counterfactual-sql-data-rollouts-and-traces-6af479430243b7731f85d144): [demo](https://huggingface.co/spaces/sqlcf-lexsi/counterfactual-sql-demo), [data](https://huggingface.co/datasets/sqlcf-lexsi/counterfactual-sql-data), adapters [SFT](https://huggingface.co/sqlcf-lexsi/tiny-aya-global-sqlcf-sft) / [GRPO-B](https://huggingface.co/sqlcf-lexsi/tiny-aya-global-sqlcf-grpo-b) / [GRPO-C](https://huggingface.co/sqlcf-lexsi/tiny-aya-global-sqlcf-grpo-c). The adapters carry the base model's CC-BY-NC-4.0 licence and are gated with automatic approval.

## Setup (Linux / WSL)

```bash
# third-party repos (not committed)
mkdir -p vendor && cd vendor
git clone https://github.com/Lexsi-Labs/AgentTune.git && git -C AgentTune checkout d4db4c1 && git -C AgentTune apply ../../patches/agenttune-multiturn-ids.patch
git clone https://github.com/Lexsi-Labs/AuditKIT.git  && git -C AuditKIT checkout 9da5838
git clone https://github.com/UEddy/Kataa.git          && git -C Kataa checkout c0c65a1
cd ..
# CPU env (data, rewards, audit, scoring)
uv venv .venv && uv pip install --python .venv/bin/python pandas numpy scipy matplotlib pytest
# training env (GPU box): python>=3.12, AgentTune + TRL + vLLM 0.22.1
uv venv --python 3.12 .venv-train && uv pip install --python .venv-train/bin/python -e vendor/AgentTune trl peft datasets vllm==0.22.1
```

Tiny Aya (`CohereLabs/tiny-aya-global`) is gated: accept the licence and use an HF read token with
"read access to public gated repos you can access".

## Rebuild data (CPU, deterministic)

```bash
.venv/bin/python -m sqlcf.cf --name audit --split all   --seeds 301 302 303 304 305 --size S
.venv/bin/python -m sqlcf.cf --name train --split train --seeds 101 102 103 104 105 106 --size S
.venv/bin/python -m sqlcf.cf --name test  --split test  --seeds 501 502 503 --size S --test
.venv/bin/python -m sqlcf.build_sft --items data/train/items.jsonl --out data/sft.jsonl
.venv/bin/python -m pytest -q tests
```

## Experiments

```bash
.venv/bin/python -m sqlcf.audit e0                                         # E0 -> results/
.venv/bin/python -m sqlcf.audit agenttune                                  # E0, AgentTune reward
.venv/bin/python -m sqlcf.audit e1 --seeds 900 901 902                     # E1
.venv-train/bin/python train.py sft  --out runs/sft                        # E2
.venv-train/bin/python train.py grpo --reward R_exec_rex --out runs/grpo_B # E3 condition B
.venv-train/bin/python train.py grpo --reward R_cf_mean  --out runs/grpo_C # E3 condition C
for m in sft grpo_B grpo_C; do .venv-train/bin/python evaluate.py gen --model runs/$m/merged --name ${m#grpo_}; done
.venv/bin/python evaluate.py score --traj results/traj_*.jsonl             # E4
.venv/bin/python scripts/figure3.py B C                                    # training-reward audit (needs runs/grpo_*_rewards.jsonl)
source .secrets.env && .venv/bin/python scripts/e5_command_a.py            # E5: Command A on the test set (CO_API_KEY)
.venv/bin/python scripts/e5_roi.py                                         # E5 ROI table
.venv/bin/python scripts/audit_sample.py && .venv/bin/python scripts/audit_labels.py  # manual audit
.venv/bin/python scripts/audit_skyrl.py                                    # E7: SkyRL-SQL reward audit
.venv/bin/python scripts/a4_selfconsistency.py                             # E8: gold-free voting + shaky-answer flag
.venv/bin/python scripts/agenttune_repro.py                                # AgentTune reward exploit: before / after patch
.venv/bin/python scripts/partial_credit.py                                 # E11: partial-credit rewards
.venv/bin/python scripts/period_copies.py                                  # E12: period-edge copies vs date bugs
bash scripts/local_dpo.sh                                                  # E10: DPO std vs cf labels (16 GB GPU)
# E6 needs external/testsuite_db/database (Zhong et al. test-suite DBs, Google Drive 1mkCx2GOFIqNesD4y8TDAO1yX1QZORP5w)
# and external/ESMp (git clone https://github.com/bossben/ESMp, checkout 91dd85b)
.venv/bin/python scripts/a2_spider_lucky.py                                # E6: Spider-dev lucky passes
.venv/bin/python verify_all.py                                             # re-derive every results/*.json
source .secrets.env && .venv/bin/python scripts/push_models.py             # adapters + licence + collection (private; --public --gated later)
```

## Layout

`sqlcf/` data generator, templates, counterfactual DBs, comparator, rewards, audit, agent tool ·
`train.py` SFT + GRPO · `evaluate.py` E4 · `vertex/` Vertex AI job files · `tests/` reward tests.
