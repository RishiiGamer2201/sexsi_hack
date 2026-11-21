#!/usr/bin/env bash
# On the VM: LeakySQL pilot, chained after scripts/vm_seed2.sh in the same VM session (L4 stockouts).
# B (R_exec_rex) vs C-min (R_cf_strict) from the hack-seeded SFT adapter, 60 steps, seed 0, otherwise the
# default config. runs/CHAIN_NEXT stops vm_seed2.sh from powering off; this script's C-min run ends in autostop.
cd ~/sexsi_hack
touch runs/CHAIN_NEXT
while pgrep -f "[v]m_seed2.sh" > /dev/null; do sleep 60; done
rm -f runs/CHAIN_NEXT
[ -d data_leaky ] || .venv-train/bin/python scripts/leaky_build.py > runs/leaky_build.log 2>&1
export SQLCF_DATA="$PWD/data_leaky" SQLCF_LEAKY=1
A="--init runs/sft_leaky/adapter --items data_leaky/train/items.jsonl"
NO_AUTOSTOP=1 bash scripts/vm_grpo.sh R_exec_rex grpo_B_leaky $A > runs/grpo_B_leaky.log 2>&1
bash scripts/vm_grpo.sh R_cf_strict grpo_Cmin_leaky $A > runs/grpo_Cmin_leaky.log 2>&1
