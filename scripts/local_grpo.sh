#!/usr/bin/env bash
# One GRPO condition on the local GPU (E14 curriculum pilot). Same as vm_grpo.sh minus the VM autostop.
#   bash scripts/local_grpo.sh R_cf_strict grpo_Cmin_cur --items data/train/curriculum_items.jsonl
set -uo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-train/bin:$PATH"
reward=$1; name=$2; shift 2
echo "== grpo $name $reward $* ($(TZ=Asia/Kolkata date '+%d %b %H:%M IST'))"
t=$(date +%s)
[ -f "runs/${name}_rewards.jsonl" ] && mv "runs/${name}_rewards.jsonl" "runs/stale_${name}_rewards_$t.jsonl"
[ -d "runs/$name" ] && mv "runs/$name" "runs/stale_${name}_$t"
SQLCF_REWARD_LOG=runs/${name}_rewards.jsonl /usr/bin/time -f "grpo %e s" .venv-train/bin/python train.py grpo \
  --reward "$reward" --init runs/sft/adapter --out "runs/$name" "$@" && echo "== GRPO OK"
