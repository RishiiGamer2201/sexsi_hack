#!/usr/bin/env bash
# Local GPU, fp16 models: (1) GRPO signal check (scripts/local_grpo_signal.sh), (2) E4 test eval for SFT and
# base (8 samples, T=0.7), each retried through WSL CUDA crashes, then scoring. ~35 min on a 5070 Ti.
set -uo pipefail
cd "$(dirname "$0")/.."
try() { for i in 1 2 3; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }
bash scripts/local_grpo_signal.sh > runs/grpo_signal16.json && echo "== grpo signal done" && cat runs/grpo_signal16.json
try bash -c "bash scripts/local_eval.sh runs/sft/merged sft > runs/local_sft16.log 2>&1" && echo "== e4 sft done"
try bash -c "bash scripts/local_eval.sh CohereLabs/tiny-aya-global base > runs/local_base16.log 2>&1" && echo "== e4 base done"
.venv-train/bin/python evaluate.py score --traj results/traj_base.jsonl results/traj_sft.jsonl > /dev/null && echo "== scored"
