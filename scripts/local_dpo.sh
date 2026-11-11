#!/usr/bin/env bash
# E10 on the local 16 GB GPU: DPO from sft_ho with single-DB (std) vs counterfactual (cf) preference labels,
# then merge (own process), E4 test eval (331 x 8) and rescoring. Pairs: scripts/dpo.py pairs.
#   bash scripts/local_dpo.sh > runs/dpo.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# WSL throws sporadic "CUDA driver error: device not ready" / "unknown error": retry (a DPO run restarts from scratch)
try() { for i in 1 2 3 4 5; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }
for k in std cf; do
  [ -f runs/dpo_$k/adapter/adapter_model.safetensors ] || \
    try /usr/bin/time -f "dpo $k %e s" .venv-train/bin/python scripts/dpo.py train --kind $k --out runs/dpo_$k || exit 1
  [ -f runs/dpo_$k/merged/config.json ] || try .venv-train/bin/python train.py merge --init runs/dpo_$k/adapter --out runs/dpo_$k/merged || exit 1
  # 0.6: another process holds part of the card (see progress.md, D2)
  [ -f results/traj_dpo_$k.jsonl ] || try bash scripts/local_eval.sh runs/dpo_$k/merged dpo_$k --gpu-mem 0.6 || exit 1
  echo "== dpo_$k done"
done
.venv/bin/python evaluate.py score --traj results/traj_*.jsonl > /dev/null && echo "== scored"
.venv/bin/python -c "import json; r=json.load(open('results/e4_eval.json')); print({m: [round(x, 3) for x in r[m]['verified']] for m in ('sft_ho','dpo_std','dpo_cf','B','C')}); print({m: round(r[m]['silent_error'][0], 3) for m in ('sft_ho','dpo_std','dpo_cf')}); print(json.dumps({k: v for k, v in r['comparisons'].items() if 'dpo' in k}, indent=1))"
