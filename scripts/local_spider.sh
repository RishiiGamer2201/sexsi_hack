#!/usr/bin/env bash
# E13 on the local 16 GB card (WSL): Spider-dev generation for base, sft_ho, B, C, then CPU scoring.
#   bash scripts/local_spider.sh [extra spider_eval.py gen args, e.g. --limit 8 --n 2 --out-dir runs]
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 VLLM_USE_FLASHINFER_SAMPLER=0 HF_HUB_OFFLINE=1
export PATH="$PWD/.venv-train/bin:$PATH"
declare -A M=([base]=CohereLabs/tiny-aya-global [sft_ho]=runs/sft/merged [B]=runs/grpo_B/merged [C]=runs/grpo_C/merged)
for name in base sft_ho B C; do
  m=${M[$name]}
  # same tokenizer fix as local_eval.sh (VM-saved tokenizer class unknown to the local transformers)
  if [ -d "$m" ] && grep -q TokenizersBackend "$m/tokenizer_config.json" 2>/dev/null; then
    cp .cache/hf/hub/models--CohereLabs--tiny-aya-global/snapshots/*/{tokenizer.json,tokenizer_config.json} "$m/"
  fi
  echo "== gen $name $(TZ=Asia/Kolkata date +%H:%M) IST"
  /usr/bin/time -f "gen $name %e s" python scripts/spider_eval.py gen --model "$m" --name "$name" "$@"
done
echo "== score $(TZ=Asia/Kolkata date +%H:%M) IST"
python scripts/spider_eval.py score "$@"
echo "== done $(TZ=Asia/Kolkata date +%H:%M) IST"
