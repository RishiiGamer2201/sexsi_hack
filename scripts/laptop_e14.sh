#!/usr/bin/env bash
# BILLABLE (~$0.74/hr). E14 curriculum pilot, unattended from the laptop (WSL):
#  1. snapshot sqlcf-l4's disk (its zone has an L4 stockout) and boot a temp VM from it in the first zone with a free L4;
#  2. check the SFT adapter, run GRPO-B (R_exec_rex) then GRPO-Cmin (R_cf_strict) on data/train/curriculum_items.jsonl;
#  3. copy adapters + logs + rewards back, DELETE the temp VM and the snapshot;
#  4. locally: fp16 merge, E4 (test set) and E13 (Spider) generation for B_cur and Cmin_cur.
#   setsid nohup bash scripts/laptop_e14.sh > runs/laptop_e14.log 2>&1 < /dev/null &
set -uo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
P=project-54f35310-8b0b-478f-836; SRC_Z=asia-south1-a; VM=sqlcf-e14; SNAP=sqlcf-l4-e14
DEADLINE=$(date -d "2026-11-16T02:00:00+05:30" +%s)  # a later start cannot finish + be written up
ZONES="asia-south1-b asia-south1-c asia-southeast1-a asia-southeast1-b asia-southeast1-c asia-east1-a asia-east1-b
 asia-east1-c asia-northeast1-a asia-northeast1-b asia-northeast1-c europe-west4-a europe-west4-b europe-west4-c
 us-central1-a us-central1-b us-central1-c us-east1-b us-east1-c us-east1-d us-west1-a us-west1-b us-west1-c"
ITEMS=data/train/curriculum_items.jsonl
# attempt 1 (Nov 15 13:55) OOMed at step 3/60 on both arms (22 GiB L4; the hard prompts run long).
# Same settings for both arms: shorter completions, a smaller vLLM share, no allocator fragmentation.
ARGS="--items $ITEMS --max-completion 1536 --vllm-mem 0.40"; ENV="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
ist() { TZ=Asia/Kolkata date "+%d %b %H:%M"; }
try() { for i in 1 2 3; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }

disk=$(gcloud compute instances describe sqlcf-l4 --project $P --zone $SRC_Z --format='value(disks[0].source)' | sed 's#.*/##')
gcloud compute snapshots describe $SNAP --project $P >/dev/null 2>&1 ||
  gcloud compute disks snapshot "$disk" --project $P --zone $SRC_Z --snapshot-names $SNAP --quiet || { echo "== snapshot failed"; exit 1; }
echo "== snapshot $SNAP of $disk ready $(ist) IST"

# reuse the temp VM if attempt 1 left it stopped
Z=$(gcloud compute instances list --project $P --filter="name=$VM" --format="value(zone.basename())")
n=0
while [ -n "$Z" ] && ! gcloud compute instances start $VM --project $P --zone $Z --quiet >/dev/null 2>&1; do
  n=$((n + 1)); [ "$(date +%s)" -gt "$DEADLINE" ] && { echo "== gave up restarting $VM $(ist) IST"; exit 1; }
  echo "restart of $VM in $Z failed x$n, $(ist) IST"; sleep 120
done
while [ -z "$Z" ]; do
  for z in $ZONES; do
    gcloud compute instances create $VM --project $P --zone "$z" --machine-type g2-standard-4 \
      --accelerator type=nvidia-l4,count=1 --maintenance-policy TERMINATE \
      --source-snapshot $SNAP --boot-disk-size 150GB --boot-disk-type pd-balanced --quiet >/dev/null 2>&1 && { Z=$z; break; }
  done
  n=$((n + 1))
  [ -n "$Z" ] && break
  [ "$(date +%s)" -gt "$DEADLINE" ] && { echo "== gave up $(ist) IST after $n rounds"; gcloud compute snapshots delete $SNAP --project $P --quiet; exit 1; }
  echo "no L4 in any zone, round $n, $(ist) IST"; sleep 300
done
echo "== $VM up in $Z $(ist) IST"
ssh_() { gcloud compute ssh $VM --project $P --zone $Z --command "$1" 2>/dev/null; }
cleanup() {
  gcloud compute instances delete $VM --project $P --zone $Z --quiet && echo "== deleted $VM $(ist) IST"
  gcloud compute snapshots delete $SNAP --project $P --quiet && echo "== deleted $SNAP"
}
for _ in $(seq 40); do ssh_ true && break; sleep 15; done
want=$(md5sum runs/sft/adapter/adapter_model.safetensors | cut -c1-32)
got=$(ssh_ "cd ~/sexsi_hack && git pull -q; md5sum runs/sft/adapter/adapter_model.safetensors | cut -c1-32")
[ "$want" = "$got" ] || { echo "== SFT adapter mismatch (VM: '$got')"; cleanup; exit 1; }
gcloud compute scp $ITEMS "$VM:~/sexsi_hack/$ITEMS" --project $P --zone $Z &&
  gcloud compute scp scripts/vm_grpo.sh scripts/vm_autostop.sh "$VM:~/sexsi_hack/scripts/" --project $P --zone $Z ||
  { echo "== scp failed"; cleanup; exit 1; }
# the second run autostops (after the HOLD is released or 30 min), so a dead laptop cannot leave the VM billing
ssh_ "cd ~/sexsi_hack && touch runs/HOLD_AUTOSTOP && (setsid nohup bash -c 'export $ENV; NO_AUTOSTOP=1 bash scripts/vm_grpo.sh R_exec_rex grpo_B_cur $ARGS > runs/grpo_B_cur.log 2>&1; bash scripts/vm_grpo.sh R_cf_strict grpo_Cmin_cur $ARGS > runs/grpo_Cmin_cur.log 2>&1' > /dev/null 2>&1 < /dev/null &) && sleep 5 && pgrep -fc '[v]m_grpo.sh'"
echo "== launched B_cur then Cmin_cur $(ist) IST"

while :; do
  sleep 900
  # done = /usr/bin/time's "grpo N s" line in the second log (vm_grpo.sh then idles in autostop, waiting on the HOLD)
  d=$(ssh_ "grep -ac '^grpo [0-9.]* s' ~/sexsi_hack/runs/grpo_Cmin_cur.log 2>/dev/null")
  s=$(ssh_ "cd ~/sexsi_hack && for r in B_cur Cmin_cur; do [ -f runs/grpo_\$r.log ] && echo \$r \$(tr '\r' '\n' < runs/grpo_\$r.log | grep -aoE '[0-9]+/60 \[' | tail -1) \$(grep -ac Traceback runs/grpo_\$r.log) tb; done")
  echo "$(ist) IST: $(echo $s | tr '\n' ' ') [done: ${d:-?}]"
  [ "${d:-0}" -ge 1 ] 2>/dev/null && break
done
ssh_ "cd ~/sexsi_hack && grep -h '^== \|^grpo ' runs/grpo_B_cur.log runs/grpo_Cmin_cur.log"
for r in B_cur Cmin_cur; do
  mkdir -p runs/grpo_$r
  try gcloud compute scp --recurse "$VM:~/sexsi_hack/runs/grpo_$r/adapter" runs/grpo_$r/ --project $P --zone $Z
  try gcloud compute scp "$VM:~/sexsi_hack/runs/grpo_${r}.log" "$VM:~/sexsi_hack/runs/grpo_${r}_rewards.jsonl" runs/ --project $P --zone $Z
done
if [ -f runs/grpo_B_cur/adapter/adapter_model.safetensors ] && [ -f runs/grpo_Cmin_cur/adapter/adapter_model.safetensors ]; then
  cleanup
else
  echo "== adapters missing, temp VM kept for a manual look; stopping it"; gcloud compute instances stop $VM --project $P --zone $Z --quiet; exit 1
fi

# local GPU: wait while the seed-1 driver (or anything else) is using it
for r in B_cur Cmin_cur; do
  while pgrep -f "[e]valuate.py gen|[s]pider_eval.py gen|[t]rain.py " >/dev/null; do sleep 120; done
  .venv-train/bin/python train.py merge --init runs/grpo_$r/adapter --out runs/grpo_$r/merged && echo "== merged $r $(ist) IST"
  try bash -c "bash scripts/local_eval.sh runs/grpo_$r/merged $r > runs/local_e4_$r.log 2>&1" && echo "== e4 $r $(ist) IST"
  try bash -c "PATH=$PWD/.venv-train/bin:\$PATH python scripts/spider_eval.py gen --model runs/grpo_$r/merged --name $r > runs/local_spider_$r.log 2>&1" && echo "== spider $r $(ist) IST"
done
echo "== E14 done $(ist) IST"
