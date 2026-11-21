#!/usr/bin/env bash
# LeakySQL pilot, laptop GPU: hack-seeded SFT (scripts/leaky_sft.py data), same config as the held-out SFT
# (batch 1 x 16 accumulation, 2 epochs), then the cache-read probe on 60 GRPO leak prompts x 6 (T = 1.0).
#   setsid nohup bash scripts/local_leaky_sft.sh > runs/leaky/sft.log 2>&1 < /dev/null &
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export SQLCF_DATA="$PWD/data_leaky" SQLCF_LEAKY=1
mkdir -p runs/leaky
/usr/bin/time -f "sft %e s" .venv-train/bin/python train.py sft --data data_leaky/sft_seeded.jsonl --out runs/sft_leaky --batch 1 --save-every 20
bash scripts/local_eval.sh runs/sft_leaky/merged sft_leaky_probe --items data_leaky/train/grpo_leak.jsonl --n 6 --temperature 1.0 --out-dir runs/leaky
.venv-train/bin/python scripts/leaky_score.py runs/leaky/traj_sft_leaky_probe.jsonl data_leaky/train/grpo_leak.jsonl
