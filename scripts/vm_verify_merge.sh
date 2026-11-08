#!/usr/bin/env bash
# Check of the fp16 merge fix (sqlcf/precision.py): re-merge the SFT adapter in fp32 -> fp16, then greedy
# eval on 58 of SFT's own training items (runs/sft_own_items.jsonl, copied up from the laptop; the bf16
# merge got 26%). If verified >= 0.5, launch GRPO-B (which autostops); otherwise autostop now.
#   setsid nohup bash scripts/vm_verify_merge.sh > runs/verify.log 2>&1 < /dev/null &
set -uo pipefail
cd ~/sexsi_hack
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-train/bin:$PATH"
python train.py merge --init runs/sft/adapter --out runs/sft/merged &&
python evaluate.py gen --model runs/sft/merged --name sft_own16 --items runs/sft_own_items.jsonl \
  --n 1 --temperature 0 --out-dir runs &&
python evaluate.py score --items runs/sft_own_items.jsonl --traj runs/traj_sft_own16.jsonl --out-dir runs
v=$(python -c "import json; print(json.load(open('runs/e4_eval.json'))['sft_own16']['verified'][0])" 2>/dev/null || echo 0)
echo "== own-item verified: $v (bf16 merge: 0.26)"
if python -c "import sys; sys.exit(not float('$v') >= 0.5)"; then
  echo "== launching GRPO-B"; exec bash scripts/vm_grpo.sh R_exec_rex grpo_B > runs/grpo_B.log 2>&1
fi
bash scripts/vm_autostop.sh
