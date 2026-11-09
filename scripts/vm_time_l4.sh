#!/usr/bin/env bash
# E5 ROI: time GRPO-B's test generation on the L4 (same settings as the laptop eval: 331 items x 8, T=0.7),
# so the Tiny Aya $/1k figure uses L4 throughput at the L4 price. Output: runs/traj_B_l4.jsonl, runs/time_l4.log.
#   gcloud compute ssh sqlcf-l4 ... --command "cd ~/sexsi_hack; setsid nohup bash scripts/vm_time_l4.sh > runs/time_l4.log 2>&1 < /dev/null &"
set -uo pipefail
cd ~/sexsi_hack
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 VLLM_USE_FLASHINFER_SAMPLER=0 PATH="$PWD/.venv-train/bin:$PATH"
m=runs/grpo_B/merged
[ -f $m/config.json ] || /usr/bin/time -f "merge %e s" python train.py merge --init runs/grpo_B/adapter --out $m
grep -q TokenizersBackend $m/tokenizer_config.json 2>/dev/null && cp .cache/hf/hub/models--CohereLabs--tiny-aya-global/snapshots/*/{tokenizer.json,tokenizer_config.json} $m/
nvidia-smi --query-gpu=name --format=csv,noheader
/usr/bin/time -f "gen B_l4 %e s" python evaluate.py gen --model $m --name B_l4 --out-dir runs && echo "== L4 TIMING DONE"
bash scripts/vm_autostop.sh
