#!/usr/bin/env bash
# One GRPO condition on the VM, then power off (scripts/vm_autostop.sh). Launch from the laptop (WSL gcloud):
#   gcloud compute ssh sqlcf-l4b --project project-54f35310-8b0b-478f-836 --zone asia-south1-b \
#     --command "cd ~/sexsi_hack && git pull -q; setsid nohup bash scripts/vm_grpo.sh R_exec_rex grpo_B > runs/grpo_B.log 2>&1 < /dev/null &"
# Extra args go to train.py (e.g. --steps 50 --prompts 3). B and C must get identical args (gate G2).
set -uo pipefail
cd ~/sexsi_hack
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-train/bin:$PATH"
reward=$1; name=$2; shift 2
echo "== grpo $name $reward $*"
# the reward log and trajectories are appended to; leftovers from an aborted run would corrupt gate G1
t=$(date +%s)
[ -f "runs/${name}_rewards.jsonl" ] && mv "runs/${name}_rewards.jsonl" "runs/stale_${name}_rewards_$t.jsonl"
[ -d "runs/$name" ] && mv "runs/$name" "runs/stale_${name}_$t"
SQLCF_REWARD_LOG=runs/${name}_rewards.jsonl /usr/bin/time -f "grpo %e s" .venv-train/bin/python train.py grpo \
  --reward "$reward" --init runs/sft/adapter --out "runs/$name" "$@" && echo "== GRPO OK"
[ -n "${NO_AUTOSTOP:-}" ] || bash scripts/vm_autostop.sh  # NO_AUTOSTOP=1 when another run is chained after this one
