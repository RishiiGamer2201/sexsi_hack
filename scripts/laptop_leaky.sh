#!/usr/bin/env bash
# Laptop (WSL), unattended: LeakySQL pilot on the VM, chained after seed 2 (scripts/laptop_seed2.sh starts the VM).
#   1. wait for runs/leaky/GO (set by hand after the seeded-SFT probe looks sane) and for sqlcf-l4 to be RUNNING;
#   2. copy the seeded SFT adapter and the leaky code over, launch scripts/vm_leaky.sh;
#   3. keep runs/HOLD_AUTOSTOP alive while it runs (laptop_seed2.sh removes it after copying seed 2);
#   4. copy B_leaky / Cmin_leaky back, release the hold (the VM then powers itself off), evaluate locally.
#   setsid nohup bash scripts/laptop_leaky.sh > runs/leaky/laptop.log 2>&1 < /dev/null &
set -uo pipefail
cd "$(dirname "$0")/.."
P=project-54f35310-8b0b-478f-836; Z=asia-south1-a
DEADLINE=$(date -d "2026-11-23T12:00:00+05:30" +%s)
ist() { TZ=Asia/Kolkata date "+%d %b %H:%M"; }
ssh_() { gcloud compute ssh sqlcf-l4 --project $P --zone $Z --command "$1" 2>/dev/null; }
try() { for i in 1 2 3; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }
status() { gcloud compute instances describe sqlcf-l4 --project $P --zone $Z --format='value(status)' 2>/dev/null; }

until [ -f runs/leaky/GO ] && [ "$(status)" = RUNNING ] && ssh_ "pgrep -f '[v]m_seed2.sh' > /dev/null"; do
  [ "$(date +%s)" -gt "$DEADLINE" ] && { echo "== gave up waiting $(ist) IST"; exit 1; }
  sleep 300
done
echo "== VM running seed 2, GO set: $(ist) IST"
ssh_ "mkdir -p ~/sexsi_hack/runs/sft_leaky ~/sexsi_hack/scripts ~/sexsi_hack/sqlcf"
try gcloud compute scp --recurse runs/sft_leaky/adapter "sqlcf-l4:~/sexsi_hack/runs/sft_leaky/" --project $P --zone $Z || exit 1
for f in scripts/vm_leaky.sh scripts/vm_grpo.sh scripts/vm_autostop.sh scripts/leaky_build.py sqlcf/agent.py train.py; do
  try gcloud compute scp $f "sqlcf-l4:~/sexsi_hack/$f" --project $P --zone $Z || { echo "== scp $f failed"; exit 1; }
done
want=$(md5sum runs/sft_leaky/adapter/adapter_model.safetensors | cut -c1-32)
got=$(ssh_ "md5sum ~/sexsi_hack/runs/sft_leaky/adapter/adapter_model.safetensors | cut -c1-32")
[ "$want" = "$got" ] || { echo "== seeded SFT adapter mismatch on VM"; exit 1; }
ssh_ "cd ~/sexsi_hack && (setsid nohup bash scripts/vm_leaky.sh > runs/vm_leaky.log 2>&1 < /dev/null &) && sleep 5 && pgrep -fc vm_leaky.sh"
echo "== launched vm_leaky.sh $(ist) IST (waits for seed 2)"

while :; do
  sleep 300
  c=$(ssh_ "touch ~/sexsi_hack/runs/HOLD_AUTOSTOP; pgrep -fc '[v]m_leaky.sh'")
  s=$(ssh_ "cd ~/sexsi_hack && for r in B_leaky Cmin_leaky; do [ -f runs/grpo_\$r.log ] && echo \$r \$(tr '\r' '\n' < runs/grpo_\$r.log | grep -aoE '[0-9]+/60 \[' | tail -1) \$(grep -ac Traceback runs/grpo_\$r.log) tb; done")
  echo "$(ist) IST: $(echo $s | tr '\n' ' ') [chain procs: ${c:-?}]"
  [ "$c" = "0" ] && break
done
ssh_ "cd ~/sexsi_hack && grep -h '^== \|^grpo ' runs/grpo_B_leaky.log runs/grpo_Cmin_leaky.log"
for r in B_leaky Cmin_leaky; do
  mkdir -p runs/grpo_$r
  try gcloud compute scp --recurse "sqlcf-l4:~/sexsi_hack/runs/grpo_$r/adapter" runs/grpo_$r/ --project $P --zone $Z
  try gcloud compute scp "sqlcf-l4:~/sexsi_hack/runs/grpo_$r.log" "sqlcf-l4:~/sexsi_hack/runs/grpo_${r}_rewards.jsonl" runs/ --project $P --zone $Z
done
ssh_ "rm -f ~/sexsi_hack/runs/HOLD_AUTOSTOP"
echo "== copied, hold released $(ist) IST"

export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 SQLCF_DATA="$PWD/data_leaky" SQLCF_LEAKY=1
for r in B_leaky Cmin_leaky; do
  .venv-train/bin/python scripts/leaky_score.py --rewards runs/grpo_${r}_rewards.jsonl
  [ -f runs/grpo_$r/adapter/adapter_model.safetensors ] || { echo "== no adapter for $r"; continue; }
  .venv-train/bin/python train.py merge --init runs/grpo_$r/adapter --out runs/grpo_$r/merged
done
for r in sft_leaky B_leaky Cmin_leaky; do
  m=runs/$r/merged; [ $r = sft_leaky ] || m=runs/grpo_$r/merged
  try bash -c "bash scripts/local_eval.sh $m $r --items data_leaky/test/items.jsonl --out-dir runs/leaky > runs/leaky/e4_$r.log 2>&1" &&
    .venv-train/bin/python scripts/leaky_score.py runs/leaky/traj_$r.jsonl data_leaky/test/items.jsonl
done
sleep 120
echo "== VM: $(status)"
echo "== all done $(ist) IST"
