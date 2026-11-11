#!/usr/bin/env bash
# D2 on the local 16 GB GPU: SFT Tiny Aya on Command A's verified answers (data/sft_distil.jsonl, same items,
# epochs and settings as sft_ho), then E4 test eval (331 x 8, T=0.7) and rescoring. Retries WSL CUDA crashes.
#   bash scripts/local_distil.sh > runs/distil/d2.log 2>&1
set -uo pipefail
cd "$(dirname "$0")/.."
try() { for i in 1 2 3; do "$@" && return 0; echo "crash $i: $*"; sleep 15; done; return 1; }
.venv/bin/python scripts/distil.py build || exit 1
# local_sft.sh passes "$@" after its own --out, and argparse keeps the last value
bash scripts/local_sft.sh --data data/sft_distil.jsonl --out runs/sft_distil && echo "== D2 SFT OK" || exit 1
try bash scripts/local_eval.sh runs/sft_distil/merged sft_distil && echo "== D2 eval OK" || exit 1
.venv/bin/python evaluate.py score --traj results/traj_*.jsonl > /dev/null && echo "== scored"
.venv/bin/python -c "import json; r=json.load(open('results/e4_eval.json')); print({m: round(r[m]['verified'][0],3) for m in ('sft_ho','sft_distil','B','command_a')}); print(json.dumps({k: v for k, v in r['comparisons'].items() if 'distil' in k}, indent=1))"
