#!/usr/bin/env bash
# Laptop (WSL), unattended. Symposium Horizon A, steps A2 and A3:
#   1. start sqlcf-l4b (retry through L4 stockouts until DEADLINE), check the SFT adapter md5;
#   2. copy the stranded seed-1 adapters (B_s1, C_s1) + logs off the VM;
#   3. launch scripts/vm_seed2.sh (GRPO-B then GRPO-C, --seed 2);
#   4. meanwhile, on the local GPU: merge + E4 (test) + E13 (Spider) generation for B_s1 and C_s1;
#   5. watch the VM chain, copy B_s2 / C_s2 back, release the autostop hold, then evaluate them locally.
#   setsid nohup bash scripts/laptop_seed2.sh > runs/laptop_seed2.log 2>&1 < /dev/null &
set -uo pipefail
cd "$(dirname "$0")/.."
P=project-54f35310-8b0b-478f-836; Z=asia-south1-b
DEADLINE=$(date -d "2026-11-24T12:00:00+05:30" +%s)  # zone move (scripts/vm_migrate.sh) relaunches this
ist() { TZ=Asia/Kolkata date "+%d %b %H:%M"; }
ssh_() { gcloud compute ssh sqlcf-l4b --project $P --zone $Z --command "$1" 2>/dev/null; }
try() { for i in 1 2 3; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }
stop_vm() { gcloud compute instances stop sqlcf-l4b --project $P --zone $Z --quiet; }
fetch() {  # fetch RUN: adapter, log and reward log of one VM run
  mkdir -p runs/grpo_$1
  try gcloud compute scp --recurse "sqlcf-l4b:~/sexsi_hack/runs/grpo_$1/adapter" runs/grpo_$1/ --project $P --zone $Z
  try gcloud compute scp "sqlcf-l4b:~/sexsi_hack/runs/grpo_$1.log" "sqlcf-l4b:~/sexsi_hack/runs/grpo_$1_rewards.jsonl" runs/ --project $P --zone $Z
}
evaluate() {  # evaluate RUN on the local GPU
  export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1
  [ -f runs/grpo_$1/adapter/adapter_model.safetensors ] || { echo "== no adapter for $1"; return; }
  .venv-train/bin/python train.py merge --init runs/grpo_$1/adapter --out runs/grpo_$1/merged && echo "== merged $1 $(ist) IST"
  try bash -c "bash scripts/local_eval.sh runs/grpo_$1/merged $1 > runs/local_e4_$1.log 2>&1" && echo "== e4 $1 $(ist) IST"
  try bash -c "PATH=$PWD/.venv-train/bin:\$PATH python scripts/spider_eval.py gen --model runs/grpo_$1/merged --name $1 > runs/local_spider_$1.log 2>&1" && echo "== spider $1 $(ist) IST"
}

n=0
until gcloud compute instances start sqlcf-l4b --project $P --zone $Z --quiet >/dev/null 2>&1; do
  n=$((n + 1))
  [ "$(date +%s)" -gt "$DEADLINE" ] && { echo "== gave up $(ist) IST after $n stockouts"; exit 1; }
  [ $((n % 15)) -eq 0 ] && echo "stockout x$n, $(ist) IST"
  sleep 120
done
echo "== VM started $(ist) IST after $n stockouts"
for _ in $(seq 20); do ssh_ true && break; sleep 15; done
want=$(md5sum runs/sft/adapter/adapter_model.safetensors | cut -c1-32)
got=$(ssh_ "cd ~/sexsi_hack && md5sum runs/sft/adapter/adapter_model.safetensors | cut -c1-32")
[ "$want" = "$got" ] || { echo "== SFT adapter mismatch (VM: '$got'), stopping VM"; stop_vm; exit 1; }
ssh_ "cd ~/sexsi_hack && touch runs/HOLD_AUTOSTOP && ls runs/grpo_B_s1/adapter runs/grpo_C_s1/adapter && grep -h '^== \|^grpo ' runs/grpo_B_s1.log runs/grpo_C_s1.log"
for r in B_s1 C_s1; do fetch $r; done
echo "== seed 1 copied $(ist) IST: $(ls runs/grpo_B_s1/adapter runs/grpo_C_s1/adapter 2>&1 | tr '\n' ' ')"

# the VM cannot git pull (no GitHub credentials), so copy the code over
for f in scripts/vm_seed2.sh scripts/vm_grpo.sh scripts/vm_autostop.sh train.py; do
  try gcloud compute scp $f "sqlcf-l4b:~/sexsi_hack/$f" --project $P --zone $Z || { echo "== scp $f failed, stopping VM"; stop_vm; exit 1; }
done
ssh_ "cd ~/sexsi_hack && (setsid nohup bash scripts/vm_seed2.sh > /dev/null 2>&1 < /dev/null &) && sleep 5 && pgrep -fc vm_seed2.sh"
echo "== launched vm_seed2.sh $(ist) IST"

for r in B_s1 C_s1; do evaluate $r; done

# watch every 5 min until the chain is gone (empty answer = ssh hiccup, keep waiting)
while :; do
  sleep 300
  c=$(ssh_ "pgrep -fc '[v]m_seed2.sh'")
  s=$(ssh_ "cd ~/sexsi_hack && for r in B_s2 C_s2; do [ -f runs/grpo_\$r.log ] && echo \$r \$(tr '\r' '\n' < runs/grpo_\$r.log | grep -aoE '[0-9]+/60 \[' | tail -1) \$(grep -ac Traceback runs/grpo_\$r.log) tb; done")
  echo "$(ist) IST: $(echo $s | tr '\n' ' ') [chain procs: ${c:-?}]"
  [ "$c" = "0" ] && break
done
ssh_ "cd ~/sexsi_hack && grep -h '^== \|^grpo ' runs/grpo_B_s2.log runs/grpo_C_s2.log"
for r in B_s2 C_s2; do fetch $r; done
ssh_ "rm -f ~/sexsi_hack/runs/HOLD_AUTOSTOP"
echo "== seed 2 copied, hold released $(ist) IST: $(ls runs/grpo_B_s2/adapter runs/grpo_C_s2/adapter 2>&1 | tr '\n' ' ')"
for r in B_s2 C_s2; do evaluate $r; done
echo "== VM: $(gcloud compute instances describe sqlcf-l4b --project $P --zone $Z --format='value(status)')"
echo "== all done $(ist) IST"
