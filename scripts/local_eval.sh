#!/usr/bin/env bash
# E4 generation on the local 16 GB card (WSL): bash scripts/local_eval.sh MODEL NAME [extra evaluate.py args]
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 VLLM_USE_FLASHINFER_SAMPLER=0 HF_HUB_OFFLINE=1
export PATH="$PWD/.venv-train/bin:$PATH"
m=$1; name=$2; shift 2
# VM models are saved by a newer transformers (tokenizer class TokenizersBackend, unknown to the
# local 4.57); fine-tuning never changes the tokenizer, so use the base model's files
if [ -d "$m" ] && grep -q TokenizersBackend "$m/tokenizer_config.json" 2>/dev/null; then
  cp .cache/hf/hub/models--CohereLabs--tiny-aya-global/snapshots/*/{tokenizer.json,tokenizer_config.json} "$m/"
fi
/usr/bin/time -f "gen $name %e s" python evaluate.py gen --model "$m" --name "$name" --gpu-mem 0.75 "$@"
