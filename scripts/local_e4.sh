#!/usr/bin/env bash
# Local GPU, fp16 models: (1) SFT rollouts on the GRPO prompts (G=6, T=1.0) = GRPO signal check,
# (2) E4 test eval for SFT and base (8 samples, T=0.7), then scoring. ~35 min on a 5070 Ti.
set -uo pipefail
cd "$(dirname "$0")/.."
bash scripts/local_eval.sh runs/sft/merged sft_grpoprompts16 --items data/train/grpo_items.jsonl --n 6 --temperature 1.0 --out-dir runs > runs/local_sft_grpoprompts16.log 2>&1 && echo "== grpoprompts done"
bash scripts/local_eval.sh runs/sft/merged sft > runs/local_sft16.log 2>&1 && echo "== e4 sft done"
bash scripts/local_eval.sh CohereLabs/tiny-aya-global base > runs/local_base16.log 2>&1 && echo "== e4 base done"
.venv-train/bin/python evaluate.py score --traj results/traj_base.jsonl results/traj_sft.jsonl > /dev/null && echo "== scored"
