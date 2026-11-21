#!/usr/bin/env bash
# On the VM: seed 2 of GRPO-B and GRPO-C (same args as seeds 0 and 1 except --seed 2), chained.
# Autostop runs at the end unless runs/CHAIN_NEXT exists (a follow-up VM job, e.g. scripts/vm_leaky.sh, owns it).
cd ~/sexsi_hack
NO_AUTOSTOP=1 bash scripts/vm_grpo.sh R_exec_rex grpo_B_s2 --seed 2 > runs/grpo_B_s2.log 2>&1
NO_AUTOSTOP=1 bash scripts/vm_grpo.sh R_cf_mean grpo_C_s2 --seed 2 > runs/grpo_C_s2.log 2>&1
[ -f runs/CHAIN_NEXT ] || bash scripts/vm_autostop.sh
