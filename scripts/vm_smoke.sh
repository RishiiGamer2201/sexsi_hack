#!/usr/bin/env bash
# Smoke test on the VM (run inside ~/sexsi_hack, under nohup): tests, real-tokenizer render,
# tiny SFT, 2 GRPO steps with colocated vLLM (timed: gate G2), 4-trajectory eval + scoring.
set -euo pipefail
cd ~/sexsi_hack
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
PY=.venv-train/bin/python
mkdir -p runs results
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo "== tests";  $PY -m pytest -q tests 2>&1 | tail -1
echo "== render"; $PY -W ignore train.py render | tail -3
echo "== sft";    /usr/bin/time -f "sft %e s" $PY train.py sft --out runs/smoke_sft --epochs 0.05
rm -f runs/smoke_rewards.jsonl
echo "== grpo";   SQLCF_REWARD_LOG=runs/smoke_rewards.jsonl /usr/bin/time -f "grpo %e s" $PY train.py grpo \
                    --reward R_cf_mean --init runs/smoke_sft/merged --out runs/smoke_grpo --steps 2 --G 2 --prompts 1
echo "== rewards"; head -c 2000 runs/smoke_rewards.jsonl; echo
echo "== eval";   $PY evaluate.py gen --model runs/smoke_sft/merged --name smoke_sft --n 1 --limit 4 --out-dir runs
$PY evaluate.py gen --model runs/smoke_grpo/merged --name smoke_C --n 1 --limit 4 --out-dir runs
$PY evaluate.py score --traj runs/traj_smoke_sft.jsonl runs/traj_smoke_C.jsonl --out-dir runs | head -40
echo "== SMOKE OK"
