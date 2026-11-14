#!/usr/bin/env bash
# Next experiments (E9 month instances, E10 intermediate reward, E11 standard vs counterfactual DPO) on the GPU VM.
# Guide: docs/NEXT_EXPERIMENTS.md. Run ON the VM from the repo root, one stage at a time, e.g.
#   setsid nohup bash scripts/vm_next.sh dpo-train > runs/next_dpo-train.log 2>&1 < /dev/null &
# Stages, in order:
#   check        GPU, env, data and checkpoints present?           (seconds)
#   setup        build missing data, fetch + merge sft_ho / B / C   (~15 min)
#   month        E9: build month DBs, audit, eval sft_ho B C         (~20 min)
#   partial      E10a: audit R_partial on CPU                       (~5 min)
#   grpo-P       E10b: GRPO with R_partial from sft_ho, as B and C  (~5-6 h on L4)
#   dpo-pool     E11a: 8 sft_ho rollouts per GRPO prompt            (~20-30 min)
#   dpo-pairs    E11b: build standard + cf pairs                    (~1 min)
#   dpo-train    E11c: DPO std, then DPO cf (same args)             (~1-2 h each)
#   eval         test set + month set for every new model, score    (~15 min per model)
#   smoke        tiny end-to-end run of dpo-train + eval (2 steps)  (~15 min)
#   logit-distil D4: logit distillation from the int4 teacher's top-20 log-probs (scripts/logit_distil.py):
#                alignment stats, kd_a0 (CE-only control) and kd_a1 (CE + KL), merge, test eval, score  (~5 h)
#   distil-int4  D3 student: SFT on the int4 teacher's verified answers (data/sft_distil_int4.jsonl from the RunPod
#                pod, docs/RUNPOD_INT4_TEACHER.md), same settings as sft_ho / sft_distil, then test eval + score (~2 h)
set -euo pipefail
cd "${REPO:-$HOME/sexsi_hack}"
export HF_HOME="$PWD/.cache/hf" TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-train/bin:$PATH"
[ -f .secrets.env ] && source .secrets.env  # HF_TOKEN (gated Tiny Aya); never commit this file
PY=.venv-train/bin/python
INIT=runs/sft_ho/adapter
mkdir -p runs results/next results/month
stage=${1:?stage: check|setup|month|partial|grpo-P|dpo-pool|dpo-pairs|dpo-train|eval|smoke|distil-int4|logit-distil}; shift || true
echo "== $stage $(date -u +%FT%TZ) $*"

fetch() {  # fetch <hf repo> <dir>: LoRA adapter from the team's HF org (gated: HF_TOKEN must have access)
  [ -f "$2/adapter_config.json" ] && return
  $PY -c "from huggingface_hub import snapshot_download as s; s('$1', local_dir='$2', allow_patterns=['adapter_*'])"
}
merged() {  # merged <adapter dir> <out dir>: fp32 merge, fp16 save (what evaluate.py gen loads)
  [ -f "$2/config.json" ] || $PY train.py merge --init "$1" --out "$2"
}
gen() {  # gen <name> <merged dir> <items> <out dir>
  $PY evaluate.py gen --model "$2" --name "$1" --items "$3" --out-dir "$4" "${@:5}"
}

case $stage in
check)
  nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv
  $PY -c "import torch, vllm, trl, peft; print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), 'vllm', vllm.__version__, 'trl', trl.__version__, 'peft', peft.__version__)"
  df -h . | tail -1
  for f in data/train/items.jsonl data/test/items.jsonl data/audit/items.jsonl data/month/items.jsonl \
           $INIT/adapter_config.json runs/sft_ho/merged/config.json runs/grpo_B/merged/config.json runs/grpo_C/merged/config.json; do
    [ -e "$f" ] && echo "ok      $f" || echo "MISSING $f"
  done
  [ -n "${HF_TOKEN:-}" ] && echo "HF_TOKEN set" || echo "HF_TOKEN not set (needed to download Tiny Aya / adapters)"
  ;;
setup)
  [ -f data/train/items.jsonl ] || $PY -m sqlcf.cf --name train --split train --seeds 101 102 103 104 105 106 --size S
  [ -f data/test/items.jsonl ]  || $PY -m sqlcf.cf --name test  --split test  --seeds 501 502 503 --size S --test
  [ -f data/audit/items.jsonl ] || $PY -m sqlcf.cf --name audit --split all   --seeds 301 302 303 304 305 --size S
  [ -f data/month/items.jsonl ] || $PY -m sqlcf.month build
  # the ONE checkpoint every new run starts from: sft_ho (B and C started from it too)
  [ -f $INIT/adapter_config.json ] || { [ -f runs/sft/adapter/adapter_config.json ] && echo "note: runs/sft/adapter exists; using the HF sft_ho adapter to be sure"; fetch sqlcf-lexsi/tiny-aya-global-sqlcf-sft $INIT; }
  merged $INIT runs/sft_ho/merged
  for m in B C; do
    [ -f runs/grpo_$m/merged/config.json ] && continue
    fetch sqlcf-lexsi/tiny-aya-global-sqlcf-grpo-$(echo $m | tr BC bc) runs/grpo_$m/adapter
    merged runs/grpo_$m/adapter runs/grpo_$m/merged
  done
  $PY -m pytest -q tests
  ;;
month)
  [ -f data/month/items.jsonl ] || $PY -m sqlcf.month build
  $PY -m sqlcf.month audit
  for m in sft_ho:runs/sft_ho/merged B:runs/grpo_B/merged C:runs/grpo_C/merged "$@"; do
    gen "${m%%:*}" "${m#*:}" data/month/items.jsonl results/month
  done
  $PY -m sqlcf.month score --traj results/month/traj_*.jsonl
  ;;
partial)
  $PY scripts/audit_partial.py --items data/audit/items.jsonl
  ;;
grpo-P)
  # identical to B and C except --reward (do not change steps / G / prompts unless you rerun B and C too)
  t=$(date +%s)
  [ -f runs/grpo_P_rewards.jsonl ] && mv runs/grpo_P_rewards.jsonl runs/stale_grpo_P_rewards_$t.jsonl
  [ -d runs/grpo_P ] && mv runs/grpo_P runs/stale_grpo_P_$t
  SQLCF_REWARD_LOG=runs/grpo_P_rewards.jsonl $PY train.py grpo --reward R_partial --init $INIT --out runs/grpo_P "$@"
  ;;
dpo-pool)
  $PY scripts/build_dpo_pairs.py prompts
  gen pool runs/sft_ho/merged data/dpo/prompts.jsonl runs/dpo --n 8 --temperature 1.0 "$@"
  $PY scripts/group_signal.py runs/dpo/traj_pool.jsonl data/dpo/prompts.jsonl || true
  ;;
dpo-pairs)
  $PY scripts/build_dpo_pairs.py pairs --traj runs/dpo/traj_pool.jsonl "$@"
  ;;
dpo-train)
  # std and cf differ ONLY in --pairs
  for c in std cf; do
    [ -d runs/dpo_$c ] && mv runs/dpo_$c runs/stale_dpo_${c}_$(date +%s)
    $PY train.py dpo --pairs data/dpo/pairs_$c.jsonl --init $INIT --out runs/dpo_$c "$@"
  done
  ;;
eval)
  names=${*:-dpo_std dpo_cf P}
  for n in $names; do
    dir=runs/dpo_${n#dpo_}/merged; [ "$n" = P ] && dir=runs/grpo_P/merged
    [ -f $dir/config.json ] || { echo "skip $n: no $dir"; continue; }
    gen $n $dir data/test/items.jsonl results/next
    gen $n $dir data/month/items.jsonl results/month
  done
  # existing test trajectories (base, sft_ho, B, C, command_a) are in results/; score everything together
  $PY evaluate.py score --traj results/traj_{sft_ho,B,C}.jsonl results/next/traj_*.jsonl --out-dir results/next
  $PY -m sqlcf.month score --traj results/month/traj_*.jsonl
  ;;
smoke)
  # does DPO run end to end at all? 32 pairs, 2 steps, then 10 test items
  [ -f data/dpo/pairs_cf.jsonl ] || { echo "run dpo-pool and dpo-pairs first"; exit 1; }
  head -32 data/dpo/pairs_cf.jsonl > runs/smoke_pairs.jsonl
  rm -rf runs/dpo_smoke
  $PY train.py dpo --pairs runs/smoke_pairs.jsonl --init $INIT --out runs/dpo_smoke --steps 2
  gen dpo_smoke runs/dpo_smoke/merged data/test/items.jsonl runs/smoke_eval --limit 10 --n 2
  echo "== SMOKE OK"
  ;;
distil-int4)
  [ -f data/sft_distil_int4.jsonl ] || { echo "copy data/sft_distil_int4.jsonl from the pod first"; exit 1; }
  [ -f data/sft.jsonl ] || $PY -m sqlcf.build_sft --items data/train/items.jsonl --out data/sft.jsonl
  # the int4 file must be built from the same 353 rows as data/sft.jsonl (distil.py asserts this on the pod)
  python3 -c "import json; a=[json.loads(l)['id'] for l in open('data/sft.jsonl')]; b=[json.loads(l)['id'] for l in open('data/sft_distil_int4.jsonl')]; assert a==b, 'row ids differ from data/sft.jsonl'; print(len(b), 'rows ok')"
  [ -d runs/sft_distil_int4 ] && mv runs/sft_distil_int4 runs/stale_sft_distil_int4_$(date +%s)
  $PY train.py sft --data data/sft_distil_int4.jsonl --out runs/sft_distil_int4 "$@"
  gen sft_distil_int4 runs/sft_distil_int4/merged data/test/items.jsonl results
  $PY evaluate.py score --traj results/traj_*.jsonl --out-dir results/next > /dev/null
  $PY -c "import json; r=json.load(open('results/next/e4_eval.json')); print({m: round(r[m]['verified'][0], 3) for m in ('sft_ho', 'sft_distil', 'sft_distil_int4', 'command_a', 'command_a_int4') if m in r})"
  ;;
logit-distil)
  for f in data/sft_distil_int4_raw.jsonl results/teacher_command_a_int4.logprobs.jsonl; do
    [ -f $f ] || { echo "copy $f from the pod first"; exit 1; }
  done
  $PY scripts/logit_distil.py stats --out runs/kd_stats  # aligned share and mapped mass: is there signal at all?
  for al in 0 1; do  # kd_a0 = same code and data, CE only: the control kd_a1 is compared with
    n=kd_a$al
    [ -d runs/$n ] && mv runs/$n runs/stale_${n}_$(date +%s)
    $PY scripts/logit_distil.py train --alpha $al --out runs/$n "$@"
    merged runs/$n/adapter runs/$n/merged
    gen $n runs/$n/merged data/test/items.jsonl results
  done
  $PY evaluate.py score --traj results/traj_*.jsonl --out-dir results/next > /dev/null
  $PY -c "import json; r=json.load(open('results/next/e4_eval.json')); print({m: round(r[m]['verified'][0], 3) for m in ('sft_ho', 'sft_distil', 'sft_distil_int4', 'kd_a0', 'kd_a1') if m in r}); print({k: v['verified_diff_bootstrap95'] for k, v in r['comparisons'].items() if 'kd_' in k})"
  ;;
*) echo "unknown stage $stage"; exit 2 ;;
esac
echo "== $stage done $(date -u +%FT%TZ)"
