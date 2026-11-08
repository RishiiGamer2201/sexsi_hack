# When Execution Success Lies — counterfactual-DB rewards for a small SQL agent

Lexsi hackathon, Track 3 (PS #6 + #9), team Teen_khapeetars. Plan and status: [plan.md](plan.md). Background: [research.md](research.md).

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
```

## Layout

`sqlcf/` data generator, templates, counterfactual DBs, comparator, rewards, audit, agent tool ·
`train.py` SFT + GRPO · `evaluate.py` E4 · `vertex/` Vertex AI job files · `tests/` reward tests.
