#!/usr/bin/env bash
# D3 on a RunPod GPU pod: int4 Command A (gghfez/command-a-03-2025-AWQ, 68.2 GB) as a local distillation teacher.
# Guide: docs/RUNPOD_INT4_TEACHER.md. Run ON the pod from the repo root, one stage at a time, e.g.
#   setsid nohup bash scripts/runpod_teacher.sh teacher > runs/pod_teacher.log 2>&1 < /dev/null &
# Two phases: first check the int4 model's accuracy, decide, then (only if it is good) make the distillation data.
#   setup         venv (vLLM 0.22.1, same as the VM), train/test data, start the 68 GB download   (~10 min)
#   smoke         1B W4A16 model, same int4 kernel path, 8 items each prompt, then scoring    (~3 min)
#   wait          block until the Command A download is complete
# Phase 1, accuracy:
#   accuracy      test + accuracy-score                                                         (~15-20 min)
#   test          the 331 test items, T=0.7 (as the API run)  -> results/traj_command_a_int4.jsonl
#   accuracy-score  CPU: int4 vs API, per item and per family  -> results/e5_int4_accuracy.json
# Phase 2, distillation teacher (run only if phase 1 looks good):
#   distil        teacher + distil-score                                                        (~10-15 min)
#   teacher       plan + SQL, T=0.3, the 353 sft_ho items, + top-20 log-probs per token (logit distillation)
#                 -> results/teacher_command_a_int4.jsonl, results/teacher_command_a_int4.logprobs.jsonl
#   distil-score  CPU: D1-int4 filter + student data: data/sft_distil_int4.jsonl (text, D3),
#                 data/sft_distil_int4_raw.jsonl (teacher's exact text, for the log-probs, D4)
# Then copy the files to the GCP VM for the student SFT + eval (guide, step 5).
set -euo pipefail  # one command per line: under set -e, a failure on the left of && does not stop the script
cd "${REPO:-/workspace/sexsi_hack}"
export HF_HOME=/workspace/hf TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1 PATH="$PWD/.venv-pod/bin:$PATH"
[ -f .secrets.env ] && source .secrets.env  # HF_TOKEN only if a repo turns out gated; never commit this file
PY=.venv-pod/bin/python
TEACHER=${TEACHER:-gghfez/command-a-03-2025-AWQ}
SMOKE=RedHatAI/gemma-3-1b-it-quantized.w4a16  # same format: compressed-tensors int4, group 128
TP=${TP:-1}  # 2 on 2 x 80 GB cards
mkdir -p runs results
stage=${1:?stage: setup|smoke|wait|accuracy|test|accuracy-score|distil|teacher|distil-score}; shift || true
echo "== $stage $(date -u +%FT%TZ) $*"

case $stage in
setup)
  nvidia-smi --query-gpu=name,memory.total --format=csv
  df -h /workspace | tail -1
  command -v uv > /dev/null || pip install -q uv
  [ -x $PY ] || { uv venv -q --python 3.12 .venv-pod && uv pip install -q --python $PY vllm==0.22.1 hf_xet pandas numpy scipy pytest; }
  $PY -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
  # same data as the VM (deterministic generators): the D1 assert in distil.py checks the 353 ids match
  [ -f data/train/items.jsonl ] || $PY -m sqlcf.cf --name train --split train --seeds 101 102 103 104 105 106 --size S
  [ -f data/test/items.jsonl ]  || $PY -m sqlcf.cf --name test  --split test  --seeds 501 502 503 --size S --test
  [ -f data/sft.jsonl ]         || $PY -m sqlcf.build_sft --items data/train/items.jsonl --out data/sft.jsonl
  [ -f runs/distil/items.jsonl ] || $PY scripts/distil.py items
  # the big download runs in the background while smoke runs; the repo is Xet-backed: hf_xet, high-performance mode
  HF_XET_HIGH_PERFORMANCE=1 setsid nohup $PY -c "from huggingface_hub import snapshot_download as s; s('$TEACHER', max_workers=16); print('DOWNLOAD OK')" \
    > runs/download.log 2>&1 < /dev/null &
  echo "download started: tail -f runs/download.log; du -sh $HF_HOME"
  ;;
smoke)
  rm -f runs/smoke_*.jsonl
  $PY scripts/teacher_local.py --model $SMOKE --name smoke --items runs/distil/items.jsonl --out runs/smoke_plan.jsonl \
    --plan --temperature 0.3 --limit 8 --gpu-mem 0.3 --logprobs 20
  # log-probs: one row per answer, the sampled tokens must spell the answer text (alignment relies on it)
  $PY - <<'PYEOF'
import json
t = {r["id"]: r["messages"][-1]["content"] for r in map(json.loads, open("runs/smoke_plan.jsonl"))}
lp = [json.loads(l) for l in open("runs/smoke_plan.logprobs.jsonl")]
assert len(lp) == len(t), (len(lp), len(t))
for r in lp:
    assert len(r["tokens"]) == len(r["top"]) and all(len(x) == 20 for x in r["top"]), r["id"]
# the tokens end with the end-of-turn token, which the text leaves out (logit_distil.py's alignment stops there)
ok = sum("".join(r["tokens"]).startswith(t[r["id"]]) for r in lp)
print(f"logprobs: {len(lp)} rows, top-20 at every step, tokens spell the text (+ end token) in {ok}/{len(lp)}")
print("first step:", lp[0]["top"][0][:3])
PYEOF
  $PY scripts/teacher_local.py --model $SMOKE --name smoke --items data/test/items.jsonl --out runs/smoke_test.jsonl \
    --temperature 0.7 --limit 8 --gpu-mem 0.3
  $PY -c "import json; r=[json.loads(l) for l in open('runs/smoke_plan.jsonl')]; print(len(r), 'rows; first answer:'); print(r[0]['messages'][-1]['content'][:600])"
  $PY scripts/distil.py score --teacher runs/smoke_plan.jsonl --tag smoke | head -12  # scoring runs on any answers
  echo "== SMOKE OK (a 1B model is mostly wrong: this checks the plumbing, not the accuracy)"
  ;;
wait)
  until grep -q "DOWNLOAD OK" runs/download.log; do
    pgrep -f snapshot_download > /dev/null || { echo "download process died:"; tail -5 runs/download.log; exit 1; }
    du -sh $HF_HOME 2>/dev/null | cut -f1; sleep 30
  done
  echo "download complete"
  ;;
teacher)
  $PY scripts/teacher_local.py --model $TEACHER --tp $TP --items runs/distil/items.jsonl \
    --out results/teacher_command_a_int4.jsonl --plan --temperature 0.3 --logprobs 20 "$@"
  ;;
test)
  $PY scripts/teacher_local.py --model $TEACHER --tp $TP --items data/test/items.jsonl \
    --out results/traj_command_a_int4.jsonl --temperature 0.7 "$@"
  ;;
accuracy-score)
  $PY scripts/int4_accuracy.py
  ;;
accuracy)
  bash "$0" test "$@"
  bash "$0" accuracy-score
  ;;
distil)
  bash "$0" teacher "$@"
  bash "$0" distil-score
  ;;
distil-score)
  $PY scripts/distil.py score --teacher results/teacher_command_a_int4.jsonl --tag int4 > /dev/null
  $PY scripts/distil.py build --teacher results/teacher_command_a_int4.jsonl --tag int4
  $PY scripts/distil.py build --teacher results/teacher_command_a_int4.jsonl --tag int4 --raw-final
  ls -la results/teacher_command_a_int4.logprobs.jsonl
  $PY - <<'EOF'
import json
f = lambda p: json.load(open(p))
api, q = f("results/d1_teacher_filter.json"), f("results/d1_teacher_filter_int4.json")
print(f"{'D1 train (353)':28} {'API bf16':>10} {'int4':>10}")
for k in ("has_sql", "kept_by_single_db_filter", "kept_by_counterfactual_filter"):
    print(f"{k:28} {api[k][0]:10.3f} {q[k][0]:10.3f}")
print(f"{'lucky (single, not verified)':28} {api['lucky_kept_only_by_single_db']:10} {q['lucky_kept_only_by_single_db']:10}")
for fam in api["by_family_n_single_verified"]:
    a, b = api["by_family_n_single_verified"][fam], q["by_family_n_single_verified"].get(fam, [0, 0, 0])
    print(f"  {fam} single/verified/n        {a[1]:>3}/{a[2]:>3}/{a[0]:<3}  {b[1]:>3}/{b[2]:>3}/{b[0]:<3}")
# D2 failed because the API teacher adds a status != 'cancelled' filter almost everywhere (325 of 353; gold: 71)
habit = lambda p: sum("cancel" in r["messages"][-1]["content"].split("```sql")[-1].lower() for r in map(json.loads, open(p)))
print(f"{'answers filtering cancelled':28} {habit('results/teacher_command_a.jsonl'):10} {habit('results/teacher_command_a_int4.jsonl'):10}")
EOF
  ;;
*) echo "unknown stage $stage"; exit 2 ;;
esac
echo "== $stage done $(date -u +%FT%TZ)"
