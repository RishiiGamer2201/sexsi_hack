#!/usr/bin/env bash
# SFT on the local 16 GB GPU (WSL), when the VM is unavailable: same run as the VM's, batch 1 x 16 accumulation.
# WSL throws sporadic "CUDA error: unknown error" mid-run, so: checkpoint every 10 steps and resume, up to 8 tries.
#   bash scripts/local_sft.sh > runs/sft_local_train.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PATH="$PWD/.venv-train/bin:$PATH"
for i in $(seq 8); do
  echo "== attempt $i"
  /usr/bin/time -f "sft %e s" python train.py sft --out runs/sft --batch 1 --save-every 10 "$@" && { echo "== SFT OK"; exit 0; }
  sleep 15
done
exit 1
