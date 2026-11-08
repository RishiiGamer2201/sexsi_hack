#!/usr/bin/env bash
# Eval part of the smoke test only (after vm_smoke.sh produced runs/smoke_sft and runs/smoke_grpo).
set -euo pipefail
cd ~/sexsi_hack
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-train/bin:$PATH"
PY=.venv-train/bin/python
echo "== eval"
for m in smoke_sft smoke_grpo; do
  /usr/bin/time -f "gen $m %e s" $PY evaluate.py gen --model runs/$m/merged --name $m --n 1 --limit 4 --out-dir runs
done
$PY evaluate.py score --traj runs/traj_smoke_sft.jsonl runs/traj_smoke_grpo.jsonl --out-dir runs | head -40
echo "== SMOKE OK"
