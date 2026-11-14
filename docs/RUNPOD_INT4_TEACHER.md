# D3: int4 Command A as a local distillation teacher (RunPod)

**What.** D1/D2 used the full Command A (111B) through the Cohere API as the teacher. D3 runs the same teacher
locally in int4 (`gghfez/command-a-03-2025-AWQ`: AWQ, W4A16, group 128, compressed-tensors, 68.2 GB) with the
same prompts, temperature and items. Then the D1 filter and D2 student SFT are repeated on its answers.

**We do not quantise.** The int4 weights are a ready-made community quantisation (llm-compressor AWQ, see the
repo's `recipe.yaml`). The pod downloads them and vLLM loads them as they are. Other vLLM-ready options are
`gghfez/c4ai-command-a-03-2025-AWQ`, `Bedovyy/c4ai-command-a-03-2025-gptqmodel-4bit` (GPTQ int4) and
`aikitoria/c4ai-command-a-03-2025-FP8-Dynamic` (FP8, 2 × 80 GB). Any of them can be used via
`TEACHER=<repo> bash scripts/runpod_teacher.sh ...`. All quantised versions:
https://huggingface.co/models?other=base_model:quantized:CohereLabs/c4ai-command-a-03-2025

**Questions it answers.**
1. Does int4 lose teacher accuracy (test: 81.0% verified for the API teacher)?
2. Does int4 make *more lucky answers* (right on the original DB, wrong on a copy)? Single-DB filtering
   would let those into the distillation data. The API teacher made 47 of these on the 353 train items.
3. Does a student distilled from the int4 teacher end up like the API-distilled one (`sft_distil`)?

**Split of work.**
- RunPod pod (one large GPU, about 1 h): teacher generation and scoring.
- GCP VM (L4, already set up): student SFT and eval.
- Mac: only copies files between the two.

| Step | Where | Time | Cost (RunPod read, 2026-11-13) |
|---|---|---|---|
| setup + 68 GB download | pod | 10–20 min | |
| smoke (1B int4 model) | pod | 3 min | |
| phase 1: test (331 items) + accuracy report | pod | 15–20 min | |
| *decide* | you | | pod idles at the hourly price |
| phase 2: teacher (353 items) + D1/D2 data | pod | 10–15 min | |
| **pod total** | | **~1 h** | **H100 NVL $3.19/h secure → ~$3–4** |
| student SFT + eval | GCP VM | ~2 h | VM credits |

## GPU choice

The weights take ~66 GB of GPU memory. vLLM also needs room for the KV cache and CUDA graphs. That rules out
80 GB cards: they would need `--eager` and a tiny KV cache, and are likely to fail with out-of-memory errors.

| Card | VRAM | $/h secure (community) | Notes |
|---|---|---|---|
| **H100 NVL** | 94 GB | 3.19 (2.59) | first choice: Hopper, int4 Marlin kernels well tested |
| RTX PRO 6000 (Blackwell) | 96 GB | 2.69 (1.69) | cheaper; newer arch, vLLM 0.22.1 supports it |
| 2 × A100 SXM 80 GB | 160 GB | 4.38 (2.78) | set `TP=2` |
| H200 | 141 GB | 5.29 (3.59) | plenty of room, pricier |

Community cloud is cheaper, but the pod can be taken back. The run resumes (finished ids are skipped), so
community is fine if you watch it.

## 1. Create the pod (RunPod console)

1. Pods → Deploy → pick **H100 NVL** (fallbacks: the table above), 1 GPU.
2. Template: **RunPod PyTorch** (any 2.x with CUDA ≥ 12.8). Set "CUDA version" filter ≥ 12.8.
3. **Container disk 40 GB**, **Volume disk 150 GB** mounted at `/workspace` (model 68 GB + venv + data).
4. Tick **SSH terminal access** / "expose TCP port 22". Your SSH public key must be in RunPod settings.
5. Deploy. In "Connect", copy the **SSH over exposed TCP** line: `ssh root@<IP> -p <PORT> -i ~/.ssh/id_ed25519`.

## 2. Copy the repo (from the Mac)

```bash
cd ~/Desktop/Workspace/lexis/sexsi_hack
POD="root@<IP>"; PORT=<PORT>
rsync -az -e "ssh -p $PORT" --exclude .git --exclude '.venv*' --exclude .cache --exclude data \
  --exclude runs --exclude vendor --exclude external --exclude .secrets.env --exclude '__pycache__' \
  ./ $POD:/workspace/sexsi_hack/
```

`.secrets.env` is excluded on purpose: neither model repo is gated, so the pod needs no token. Never copy
`CO_API_KEY` to a rented machine.

## 3. Run on the pod: phase 1, accuracy check

```bash
ssh -p $PORT $POD
cd /workspace/sexsi_hack
bash scripts/runpod_teacher.sh setup        # venv, data, starts the 68 GB download in the background
bash scripts/runpod_teacher.sh smoke        # must end with "== SMOKE OK"
bash scripts/runpod_teacher.sh wait         # until "download complete"
# detached, so a dropped SSH session does not kill it
setsid nohup bash scripts/runpod_teacher.sh accuracy > runs/pod_accuracy.log 2>&1 < /dev/null &
tail -f runs/pod_accuracy.log
```

`accuracy` runs the 331 test questions with the same prompt and T=0.7 as the API run. Then it prints the
following, and writes it to `results/e5_int4_accuracy.json`:
- verified and single-DB accuracy, API vs int4, with 95% CIs;
- lucky passes and `has_sql`;
- verified accuracy per bug family;
- how often each model adds the `cancelled` filter;
- the paired difference with an exact McNemar test.

**Decide.** The API reference is 81.0% verified. A reasonable rule: McNemar p ≥ 0.05 and a gap of ≤ ~3 points
means no measurable loss, so go to phase 2. 331 questions cannot resolve smaller gaps. Also check
`has_sql` ≈ 100%: if the int4 model stops writing a ```sql block, that is a prompt or template problem, not
accuracy.

Keep the pod running while you decide. Phase 2 reuses the downloaded model; a new pod means another 68 GB
download.

## 3b. Phase 2, distillation teacher (only if phase 1 looks good)

```bash
setsid nohup bash scripts/runpod_teacher.sh distil > runs/pod_distil.log 2>&1 < /dev/null &
tail -f runs/pod_distil.log
```

The 353 train questions get a plan + SQL at T=0.3. The teacher also saves its **top-20 next-token
log-probs** at every step to `results/teacher_command_a_int4.logprobs.jsonl` (~40 MB), for logit distillation (D4).
Then the D1 filter runs and builds two student files:
- `data/sft_distil_int4.jsonl`: answer (text) distillation, D3;
- `data/sft_distil_int4_raw.jsonl`: the same rows, but the final turn is the teacher's exact text, so the saved
  log-probs line up with it (D4).
The final table compares the API and int4 teachers: kept by the single-DB filter, kept by the counterfactual
filter, lucky answers, per family, and the `cancelled` habit.

If phase 1 is not good: skip phase 2, copy `results/traj_command_a_int4.jsonl` and
`results/e5_int4_accuracy.json` back, and terminate the pod. The accuracy result is still a finding.

## 4. Copy results back, then stop the pod

```bash
# on the Mac
# phase 1 files (always), then phase 2 files (if you ran it); missing ones are skipped
for f in results/traj_command_a_int4.jsonl results/e5_int4_accuracy.json runs/pod_accuracy.log \
         results/teacher_command_a_int4.jsonl results/teacher_command_a_int4.logprobs.jsonl results/d1_teacher_filter_int4.json \
         data/sft_distil_int4.jsonl data/sft_distil_int4_raw.jsonl runs/pod_distil.log; do
  mkdir -p $(dirname $f); rsync -az -e "ssh -p $PORT" $POD:/workspace/sexsi_hack/$f $f || echo "skip $f"
done
```

Then **Stop** the pod in the console; it bills per second while running. A stopped pod still bills its volume
(~$0.10/GB/month: 150 GB ≈ $0.50/day). **Terminate** it once the files are safely on the Mac.

## 5. Student SFT + eval on the GCP VM

```bash
# on the Mac
rsync -az scripts/ aksh@34.93.227.186:~/sexsi_hack/scripts/
rsync -az evaluate.py aksh@34.93.227.186:~/sexsi_hack/
rsync -az data/sft_distil_int4.jsonl data/sft_distil_int4_raw.jsonl aksh@34.93.227.186:~/sexsi_hack/data/
rsync -az results/teacher_command_a_int4.jsonl results/teacher_command_a_int4.logprobs.jsonl \
  results/traj_command_a_int4.jsonl results/d1_teacher_filter_int4.json aksh@34.93.227.186:~/sexsi_hack/results/
# on the VM: D3 (answer distillation), then D4 (logit distillation); one GPU, so one after the other
cd ~/sexsi_hack
setsid nohup sh -c 'bash scripts/vm_next.sh distil-int4 && bash scripts/vm_next.sh logit-distil' \
  > runs/next_distil.log 2>&1 < /dev/null &
```

This uses the same SFT settings as `sft_ho` and `sft_distil` (2 epochs, lr 1e-4, LoRA r=16, effective batch 16).
The eval is E4: 331 test items × 8 samples, T=0.7. The last line prints verified accuracy for
`sft_ho`, `sft_distil`, `sft_distil_int4`, `command_a` and `command_a_int4`.

### D4: logit distillation (`vm_next.sh logit-distil`, `scripts/logit_distil.py`)

Loss = CE on every assistant turn (as SFT) + α · KL(teacher ‖ student) on the final turn, at the positions where
the two tokenisers line up. Two runs, same code, data, seed and steps:
- `kd_a0`: α = 0, the CE-only control;
- `kd_a1`: α = 1.

Both start from the base model with a fresh LoRA, like `sft_ho`. The stage first prints `kd_stats`:
- `aligned_share`: the share of answer positions where both tokenisers start a token at the same character;
- `mapped_mass_share`: the share of the teacher's top-20 probability that maps onto single Tiny Aya tokens.

If both are low (< ~0.3), the KL term carries little signal: report that and do not over-read the result.

The final line prints verified accuracy and the paired bootstrap CI for `kd_a1` vs `kd_a0`, and each vs `sft_ho`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `CUDA out of memory` at load | `teacher --gpu-mem 0.95 --max-model-len 3072`; still failing → `--eager`; else 2 GPUs with `TP=2` |
| download stalls / `du` stops growing | `pkill -f snapshot_download`, rerun the download line from `setup` (it resumes) |
| `No space left on device` | volume < 120 GB; HF_HOME must be on `/workspace`, not the container disk |
| pod reclaimed (community) | new pod, same volume if network volume; else repeat; `teacher`/`test` skip finished ids |
| `distil.py` assert "build_sft selection changed" | data on pod differs from VM: rebuild data (`rm -rf data runs/distil`, `setup`) |
| int4 answers have no SQL block | look at one answer; chat template issue → report before training anything |
| smoke: "tokens spell the text (+ end token) in 0/8" | vLLM token strings do not rebuild the text; D4 alignment would drop every row. The log-probs file also saves the token ids (`ids`, `top_ids`), so the text can be re-decoded with the teacher tokenizer |
| `logit_distil.py` OOM on the L4 | the final turn is long: `--max-len 3072`; logits are only kept for the completion |

## Dry run done on the Mac (no GPU)

`teacher_local.py --backend replay` feeds the API teacher's answers through the new code path. Results:
- `distil.py score` reproduced `results/d1_teacher_filter.json` exactly;
- `distil.py build` produced a byte-identical `sft_distil`;
- resume skips finished ids;
- `runpod_teacher.sh accuracy-score` and `distil-score` printed their tables, including a report of missing answers.

The vLLM path is checked by the `smoke` stage on the pod. It uses the same int4 compressed-tensors format,
before the 68 GB model is loaded.

D4 (logit distillation) dry run, CPU, scratch venv with torch + transformers + peft + AgentTune:
- `teacher_local.py --backend hf --logprobs 20` wrote fake teacher log-probs in vLLM's format, from a tiny Qwen2
  with a 152k vocabulary. The tokens spelled the answer text exactly in 40/40 rows, with top-20 at every step.
  The smoke stage's check passed on that output.
- `distil.py build --raw-final`: 353 rows, 211 with the teacher's exact text as the final turn. Only the final
  turn differs from the D2 build, and the D2 build is still byte-identical.
- `logit_distil.py stats`, real Command A tokenizer (255,033 tokens) on the API teacher's 211 verified answers,
  student `trl-internal-testing/tiny-Cohere2ForCausalLM` (262,144-token vocabulary, the same size as Tiny Aya's):
  **90.3% of answer positions align, 96.2% of teacher tokens are a single student token.** Tiny Aya's own tokenizer
  is gated and was not checked; the VM's `stats` step measures it.
- `logit_distil.py train` with α = 1 and α = 0 ran end to end and saved adapters. The tiny model is too small to
  learn, so whether KL falls is first visible in the VM run's log.
- `tests/test_logit_distil.py` (3 tests, passed):
  - the KL is 0 when student and teacher match, and free logits trained on it converge to the teacher's probabilities;
  - character-level vs word-level alignment gives exactly the expected positions and mapped mass;
  - alignment stops at a broken byte-level token, and a missing text is counted.
