#!/usr/bin/env bash
# From WSL on the laptop: start the VM (retrying L4 stockouts), copy the local verified SFT adapter up as
# runs/sft/adapter (the VM's own is kept as runs/sft/adapter_vm), then launch GRPO-B (it autostops the VM).
#   bash scripts/laptop_kick_grpo.sh [tries]
set -uo pipefail
cd ~/developer/comps/sexsi_hack
P=project-54f35310-8b0b-478f-836; Z=asia-south1-a
ssh_() { gcloud compute ssh sqlcf-l4 --project $P --zone $Z --command "$1"; }
bash scripts/vm_start.sh "${1:-90}" || exit 1
for i in $(seq 10); do ssh_ "cd ~/sexsi_hack && git pull -q && rm -rf runs/sft/adapter_up && mkdir -p runs/sft/adapter_up" && break; sleep 20; done
gcloud compute scp --recurse runs/sft/adapter/* sqlcf-l4:~/sexsi_hack/runs/sft/adapter_up/ --project $P --zone $Z || exit 1
ssh_ "cd ~/sexsi_hack/runs/sft && { [ -d adapter_vm ] || mv adapter adapter_vm; } && rm -rf adapter && mv adapter_up adapter && ls adapter && cd ~/sexsi_hack && (setsid nohup bash scripts/vm_grpo.sh R_exec_rex grpo_B > runs/grpo_B.log 2>&1 < /dev/null &) && sleep 2 && echo launched"
