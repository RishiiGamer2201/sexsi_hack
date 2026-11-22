#!/usr/bin/env bash
# Full SFT on the VM, then a format check of the SFT model (32 test items, 1 sample each),
# then power the VM off unless a teammate is logged in. Launch from the laptop:
#   gcloud compute ssh sqlcf-l4b --project project-54f35310-8b0b-478f-836 --zone asia-south1-b \
#     --command "cd ~/sexsi_hack && git pull -q; setsid nohup bash scripts/vm_sft.sh > runs/sft.log 2>&1 < /dev/null &"
set -uo pipefail
cd ~/sexsi_hack
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-train/bin:$PATH"
PY=.venv-train/bin/python
mkdir -p runs results
echo "== sft";  /usr/bin/time -f "sft %e s" $PY train.py sft --out runs/sft &&
echo "== eval" && /usr/bin/time -f "gen sft %e s" $PY evaluate.py gen --model runs/sft/merged --name sft_fmt --n 1 --limit 32 --out-dir runs &&
$PY evaluate.py score --traj runs/traj_sft_fmt.jsonl --out-dir runs | head -40 &&
echo "== SFT OK"
bash scripts/vm_autostop.sh
