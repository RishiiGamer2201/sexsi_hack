#!/usr/bin/env bash
# On the VM: a second seed of GRPO-B and GRPO-C, the same args as seed 0 (defaults) except --seed 1, chained so
# the VM is not stopped between the runs (L4 stockouts). C's vm_grpo.sh ends in autostop.
# --seed changes the prompt order (our shuffle and TRL's sampler) and the torch RNG; TRL fixes the colocated
# vLLM engine seed to the process index, so seed 0 and seed 1 differ through the prompt order.
cd ~/sexsi_hack
NO_AUTOSTOP=1 bash scripts/vm_grpo.sh R_exec_rex grpo_B_s1 --seed 1 > runs/grpo_B_s1.log 2>&1
bash scripts/vm_grpo.sh R_cf_mean grpo_C_s1 --seed 1 > runs/grpo_C_s1.log 2>&1
