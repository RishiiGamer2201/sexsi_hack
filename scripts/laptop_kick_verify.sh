#!/usr/bin/env bash
# From WSL on the laptop: start the VM (retrying stockouts), copy up the own-item file, start vm_verify_merge.sh.
set -uo pipefail
cd ~/developer/comps/sexsi_hack
P=project-54f35310-8b0b-478f-836; Z=asia-south1-a
bash scripts/vm_start.sh "${1:-60}" || exit 1
for i in $(seq 10); do
  gcloud compute scp runs/sft_own_items.jsonl sqlcf-l4:~/sexsi_hack/runs/ --project $P --zone $Z >/dev/null 2>&1 && break
  sleep 20
done
gcloud compute ssh sqlcf-l4 --project $P --zone $Z --command \
  "cd ~/sexsi_hack && git pull -q && ls runs/sft/adapter runs/sft_own_items.jsonl && (setsid nohup bash scripts/vm_verify_merge.sh > runs/verify.log 2>&1 < /dev/null &) && sleep 2 && echo launched"
