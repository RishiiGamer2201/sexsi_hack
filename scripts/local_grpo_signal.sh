#!/usr/bin/env bash
# Local GPU: SFT rollouts on the GRPO prompts (G=6, T=1.0), retried through WSL CUDA crashes, then group_signal.py.
set -uo pipefail
cd "$(dirname "$0")/.."
m=${1:-runs/sft/merged}; name=${2:-sft_grpoprompts16}
for i in 1 2 3; do
  bash scripts/local_eval.sh "$m" "$name" --items data/train/grpo_items.jsonl --n 6 --temperature 1.0 --out-dir runs \
    > "runs/local_$name.log" 2>&1 && break
  echo "crash $i"; sleep 15
done
.venv-train/bin/python scripts/group_signal.py "runs/traj_$name.jsonl" data/train/grpo_items.jsonl
