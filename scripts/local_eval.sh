#!/usr/bin/env bash
# E4 generation on the local 16 GB card (WSL): bash scripts/local_eval.sh MODEL NAME [extra evaluate.py args]
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 VLLM_USE_FLASHINFER_SAMPLER=0 HF_HUB_OFFLINE=1
export PATH="$PWD/.venv-train/bin:$PATH"
m=$1; name=$2; shift 2
/usr/bin/time -f "gen $name %e s" python evaluate.py gen --model "$m" --name "$name" --gpu-mem 0.75 "$@"
