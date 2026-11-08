#!/usr/bin/env bash
# Container entrypoint: run.sh <stage>. Outputs go to the Cloud Storage FUSE mount /gcs/$BUCKET.
# Needs env BUCKET and HF_TOKEN (Tiny Aya is gated; the token's account must accept the licence).
set -euo pipefail
cd /app
STAGE=${1:?stage: smoke|sft|grpo_B|grpo_C|eval}
OUT=/gcs/${BUCKET:?}/runs
mkdir -p "$OUT"
export SQLCF_REWARD_LOG=$OUT/${STAGE}_rewards.jsonl
nvidia-smi

case $STAGE in
  smoke)   # ~20-30 min: real tokenizer render, 2 SFT steps, 2 GRPO steps (G=2), 4-trajectory eval
    python train.py render | tail -40
    python train.py sft --out /tmp/sft --epochs 0.02
    python train.py grpo --reward R_cf_mean --init /tmp/sft/merged --out /tmp/grpo --steps 2 --G 2 --prompts 1
    python evaluate.py gen --model /tmp/sft/merged --name smoke --n 1 --limit 4 --out-dir "$OUT"
    python evaluate.py gen --model /tmp/grpo/merged --name C --n 1 --limit 4 --out-dir "$OUT"
    python evaluate.py score --traj "$OUT"/traj_smoke.jsonl "$OUT"/traj_C.jsonl --out-dir "$OUT"
    ;;
  sft)     python train.py sft --out "$OUT/sft" ;;
  grpo_B)  python train.py grpo --reward R_exec_rex --init "$OUT/sft/merged" --out "$OUT/grpo_B" ;;
  grpo_C)  python train.py grpo --reward R_cf_mean  --init "$OUT/sft/merged" --out "$OUT/grpo_C" ;;
  eval)
    python evaluate.py gen --model CohereLabs/tiny-aya-global --name base --n "${N:-4}" --out-dir "$OUT"
    for m in sft grpo_B grpo_C; do python evaluate.py gen --model "$OUT/$m/merged" --name "${m#grpo_}" --n "${N:-4}" --out-dir "$OUT"; done
    python evaluate.py score --traj "$OUT"/traj_base.jsonl "$OUT"/traj_sft.jsonl "$OUT"/traj_B.jsonl "$OUT"/traj_C.jsonl --out-dir "$OUT"
    ;;
  *) echo "unknown stage $STAGE"; exit 2 ;;
esac
