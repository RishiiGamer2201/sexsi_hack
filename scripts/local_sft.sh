#!/usr/bin/env bash
# SFT on the local 16 GB GPU (WSL), when the VM is unavailable: same run as the VM's, batch 1 x 16 accumulation.
#   setsid nohup bash scripts/local_sft.sh > runs/sft_local.log 2>&1 < /dev/null &
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PATH="$PWD/.venv-train/bin:$PATH"
/usr/bin/time -f "sft %e s" python train.py sft --out runs/sft --batch 1 "$@"
