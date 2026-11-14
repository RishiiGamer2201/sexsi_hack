#!/usr/bin/env bash
# Laptop (WSL), unattended: retry the VM start through L4 stockouts until DEADLINE, check the SFT adapter matches,
# launch scripts/vm_seed1.sh (GRPO-B then GRPO-C, --seed 1), watch it, copy adapters + logs back, release the
# autostop hold, then local fp16 merge, E4 (test set) and E13 (Spider) generation for B_s1 and C_s1.
#   setsid nohup bash scripts/laptop_seed1.sh > runs/laptop_seed1.log 2>&1 < /dev/null &
set -uo pipefail
cd "$(dirname "$0")/.."
P=project-54f35310-8b0b-478f-836; Z=asia-south1-a
DEADLINE=$(date -d "2026-11-16T06:00:00+05:30" +%s)
ist() { TZ=Asia/Kolkata date "+%d %b %H:%M"; }
ssh_() { gcloud compute ssh sqlcf-l4 --project $P --zone $Z --command "$1" 2>/dev/null; }
try() { for i in 1 2 3; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }

n=0
until gcloud compute instances start sqlcf-l4 --project $P --zone $Z --quiet >/dev/null 2>&1; do
  n=$((n + 1))
  [ "$(date +%s)" -gt "$DEADLINE" ] && { echo "== gave up $(ist) IST after $n stockouts"; exit 1; }
  [ $((n % 15)) -eq 0 ] && echo "stockout x$n, $(ist) IST"
  sleep 120
done
echo "== VM started $(ist) IST after $n stockouts"
for _ in $(seq 20); do ssh_ true && break; sleep 15; done
want=$(md5sum runs/sft/adapter/adapter_model.safetensors | cut -c1-32)
got=$(ssh_ "cd ~/sexsi_hack && git pull -q && md5sum runs/sft/adapter/adapter_model.safetensors | cut -c1-32")
if [ "$want" != "$got" ]; then
  echo "== SFT adapter mismatch (VM: '$got'), stopping VM"
  gcloud compute instances stop sqlcf-l4 --project $P --zone $Z --quiet; exit 1
fi
ssh_ "cd ~/sexsi_hack && touch runs/HOLD_AUTOSTOP && (setsid nohup bash scripts/vm_seed1.sh > /dev/null 2>&1 < /dev/null &) && sleep 5 && pgrep -fc vm_seed1.sh"
echo "== launched vm_seed1.sh $(ist) IST"

# watch every 15 min until vm_seed1.sh is gone (an empty answer = ssh hiccup, keep waiting)
while :; do
  sleep 900
  c=$(ssh_ "pgrep -fc '[v]m_seed1.sh'")  # [v]: do not count this ssh command itself
  s=$(ssh_ "cd ~/sexsi_hack && for r in B_s1 C_s1; do [ -f runs/grpo_\$r.log ] && echo \$r \$(tr '\r' '\n' < runs/grpo_\$r.log | grep -aoE '[0-9]+/60 \[' | tail -1) \$(grep -ac Traceback runs/grpo_\$r.log) tb; done")
  echo "$(ist) IST: $(echo $s | tr '\n' ' ') [chain procs: ${c:-?}]"
  [ "$c" = "0" ] && break
done
ssh_ "cd ~/sexsi_hack && grep -h '^== \|^grpo ' runs/grpo_B_s1.log runs/grpo_C_s1.log"
for r in B_s1 C_s1; do
  mkdir -p runs/grpo_$r
  gcloud compute scp --recurse "sqlcf-l4:~/sexsi_hack/runs/grpo_$r/adapter" runs/grpo_$r/ --project $P --zone $Z
  gcloud compute scp "sqlcf-l4:~/sexsi_hack/runs/grpo_${r}.log" "sqlcf-l4:~/sexsi_hack/runs/grpo_${r}_rewards.jsonl" runs/ --project $P --zone $Z
done
ssh_ "rm -f ~/sexsi_hack/runs/HOLD_AUTOSTOP"
echo "== copied, hold released $(ist) IST: $(ls runs/grpo_B_s1/adapter runs/grpo_C_s1/adapter 2>&1 | tr '\n' ' ')"
sleep 300
echo "== VM: $(gcloud compute instances describe sqlcf-l4 --project $P --zone $Z --format='value(status)')"

export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1
for r in B_s1 C_s1; do
  [ -f runs/grpo_$r/adapter/adapter_model.safetensors ] || { echo "== no adapter for $r"; continue; }
  .venv-train/bin/python train.py merge --init runs/grpo_$r/adapter --out runs/grpo_$r/merged && echo "== merged $r $(ist) IST"
  try bash -c "bash scripts/local_eval.sh runs/grpo_$r/merged $r > runs/local_e4_$r.log 2>&1" && echo "== e4 $r $(ist) IST"
  try bash -c "PATH=$PWD/.venv-train/bin:\$PATH python scripts/spider_eval.py gen --model runs/grpo_$r/merged --name $r > runs/local_spider_$r.log 2>&1" && echo "== spider $r $(ist) IST"
done
echo "== all done $(ist) IST"
