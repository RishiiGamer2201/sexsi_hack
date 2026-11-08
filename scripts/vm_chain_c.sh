#!/usr/bin/env bash
# On the VM: wait for the running GRPO-B train.py to exit, then run GRPO-C with identical args (vm_grpo.sh
# ends in autostop). Avoids a stop/start between B and C, which risks hours of L4 stockouts.
# Launch only after killing B's vm_grpo.sh wrapper, so its autostop cannot fire between the two runs.
cd ~/sexsi_hack
while pgrep -f "train.py grpo --reward R_exec_rex" > /dev/null; do sleep 30; done
echo "== B exited $(date -u +%H:%MZ); adapter: $(ls runs/grpo_B/adapter 2>/dev/null | wc -l) files"
bash scripts/vm_grpo.sh R_cf_mean grpo_C
