# Progress log

> **Rule: update this file after each and every step** (a run launched or finished, a bug found or fixed, a decision made, access changed). Add a dated entry at the top of the log, and keep "Current state" and "Next" accurate. Commit and push it with the work it describes.

## Current state (Nov 9)

- **Precision fix verified.** SFT retrained on the local GPU, then merged in fp32 and saved as fp16.
  - On 58 of its own training items (greedy), 1.00 verify [0.94, 1.0]; the bf16 merge got 0.26.
  - Adapter: `runs/sft/adapter` (local); merged model: `runs/sft/merged` (fp16, 6.3 GB, local).
- **VM: TERMINATED.** 60 more L4 stockouts in asia-south1-a (about 2 h), so nothing has run on it since the fix. Moving zones needs the user's OK.
- **GRPO signal: OK** (125 of 445 groups mixed). E4 for base and SFT is done with the fixed model and real samples.
- **Pipeline:** the smoke test passed before the fix. The fix changes TRL's weight sync (`sqlcf/precision.py`), so run the smoke test again before GRPO-B.
- **VM `sqlcf-l4`** (asia-south1-a, 1x L4): start it with `bash scripts/vm_start.sh`, which retries through stockouts. Stop it whenever no job is running. SSH from WSL's gcloud (user `admin_wsl`).
- **Gates:**
  - G1 (freeze the reward form): open.
  - G2 (GRPO step time): passes. 190 s per step, so 60 steps take about 3.2 h.
- **Access:**
  - Aksh: sudo account on the VM, plus IAM rights to start and stop it.
  - Shreshth: no SSH key on the VM yet.

## Next

1. **GRPO-B as soon as the VM starts** (`scripts/laptop_kick_grpo.sh` retries through stockouts).
   - It copies the local verified SFT adapter up, then launches `vm_grpo.sh R_exec_rex grpo_B`.
   - Step 1 doubles as the smoke test for the TRL sync patch: train-prompt reward should be about 0.9. About 0.01 would mean vLLM is serving base weights.
2. Gate G1 from GRPO-B's first steps (`scripts/gate_g1.py`). Then GRPO-C with the same arguments, then E4 for B and C on the local GPU.
3. **Team decision:** keep the current GRPO prompts (signal is fine, but B and C barely differ), or add templates with a high blind rate so the counterfactual reward matters during training.
4. **User decision:** L4 stockouts in asia-south1-a have lasted hours. Moving zones needs the user's OK.

## Log

### Nov 9

- **Eval sampling bug (fixed in 90e8fae).** `SamplingParams(seed=...)` set a per-request seed, so every copy of a prompt sampled identically. 331 of 331 E4 groups and 444 of 445 GRPO-prompt groups were clones.
  - That made pass^k flat and the CIs effectively n=1, and it hid every mixed GRPO group.
  - The greedy own-items check (0.26 to 1.00) is not affected. GRPO training samples through TRL, so it is not affected either.
- **E4, fp16 models, real samples** (331 test items x 8, T=0.7, local GPU). Replaces all earlier E4 numbers.

  | Metric | Base | SFT |
  |---|---|---|
  | Verified | 0.009 | **0.117** [0.106, 0.130] |
  | Single-DB | 0.014 | 0.151 |
  | Silent errors | 0.045 | 0.632 |
  | Has final SQL | 0.46 | 0.985 |
  | Invalid tool calls | 0.64 | 0.16 |
  | pass^1 / pass^2 / pass^4 | 0.009 / 0.001 / 0 | 0.117 / 0.075 / 0.046 |
  | Verified, F1 / F2 / F3 / F4 | 0.05 / 0 / 0 / 0.006 | **0.76** / 0.003 / 0.014 / 0.05 |

  SFT beats base on verified: McNemar p=3.6e-8, paired bootstrap +10.8 pp [8.3, 13.5].
  - Test templates are new compositions. On them SFT pattern-matches the closest training template and returns plausible but wrong SQL, hence 63% silent errors.
    - F2_units_paid filters on `order_date` instead of payment date.
    - F3_avg_order averages per item instead of per order.
- **GRPO signal check** (SFT, fp16, 445 GRPO prompts, G=6, T=1.0): **125 mixed groups (28%)**, mean verified 0.94, and every train template has mixed groups. So GRPO-B can use the current prompt set.
  - **Caveat for B vs C:** only 8 of 2670 rollouts pass the original DB but fail a counterfactual, and those are the only rollouts where R_exec and R_cf differ.
  - So on these prompts B and C get nearly the same reward. Any difference has to come from rollouts that drift into such shortcuts during GRPO, or show up on test.
  - A prompt mix weighted toward templates with a high blind rate (E1) would sharpen the contrast. That is a design decision; see "Next".
- **SFT retrained on the local RTX 5070 Ti** (batch 1 x 16 accumulation, otherwise the same config as on the VM).
  - WSL threw `CUDA error: unknown error` mid-run 3 times, at steps 21, 84 and 34. The Windows log shows no driver reset, and CUDA works again right after.
  - Fix: `--save-every 10` with auto-resume in `scripts/local_sft.sh`. The successful run took 2 attempts and 1629 s.
- **Fix verified:** the fp32-to-fp16 merge verifies 1.00 on SFT's own 58 items (bf16: 0.26). It also has 0 silent errors and 0 invalid tool calls.
- `scripts/group_signal.py` counts, per GRPO group, how many rollouts verify. On the old bf16 rollouts: 370 of 445 prompts all-fail, 66 all-pass, 9 mixed.

### Nov 8

- **The VM couldn't be started:** 15 L4 stockouts in a row, so the adapter was not fetched; the VM is TERMINATED.
  - The local GPU is taken by another project, so the merge check moved to the VM (`vm_verify_merge.sh`). It is chained to GRPO-B so the VM does not have to be restarted through stockouts again.
  - Local venv: pinned `datasets<5`; 5.1.0 needs a newer `huggingface_hub` than transformers 4.57 allows.
- **Root cause of the weak SFT results: the LoRA merge in bf16 (fixed in 2ae4f3e).**
  - A LoRA update is about 0.4% of a weight, roughly one bf16 rounding step. Adding it in bf16 rounds most of it away: 38-61% of the weights in `runs/sft/merged` are bit-identical to base.
  - The merged model got only 26% of its own SFT training items right under greedy decoding. Key tokens there have a teacher-forced loss of 4-8.5 nats, against a training loss of 0.007.
  - Ruled out: HF and vLLM give the same loss, and the SFT and eval prompt renderings match (`scripts/check_render_match.py`).
  - TRL's vLLM weight sync has the same flaw: it merges and unmerges in place in bf16 every step. Rollouts lose the update, and the base weights drift.
  - **Fix (`sqlcf/precision.py`):**
    - Merges are computed in fp32 and saved in fp16. fp16 matches fp32 on Tiny Aya (loss 1.3558 vs 1.3557; bf16 gives 1.3636).
    - GRPO continues the SFT adapter on the original bf16 base; TRL keeps a frozen copy as the KL reference.
    - vLLM runs in fp16 and gets fp16(W + dW), computed out of place.
    - `evaluate.py` serves in fp16. Test: `tests/test_precision.py`.
  - **Correction to the GRPO-B entry below:** the prompts were not memorized. Over all 445 GRPO prompts (G=6), 354 failed every rollout and only 12 had mixed outcomes. The 0.96 reward at step 1 was a small sample. All E4 SFT numbers below come from the broken bf16 model and will be redone.
- **E4 SFT result** (local GPU, 331 items × 8 samples, 13.5 min):

  | Metric | SFT | Base |
  |---|---|---|
  | Verified accuracy | 0.019 | 0.004 |
  | Single-DB accuracy | 0.025 | |
  | Has final SQL | 0.51 | |
  | Silent errors | 0.41 | |
  | Invalid tool calls | 0.37 | |

  SFT beats base on verified accuracy: McNemar p=0.031, paired bootstrap +1.5 pp [0.1, 3.1]. Only 7 of 331 test items get mixed outcomes across their 8 samples.

  VM models fail to load locally, because the VM's newer transformers saves the tokenizer as class `TokenizersBackend`. `local_eval.sh` now copies in the base tokenizer files; fine-tuning does not change the tokenizer.
- **GRPO-B aborted after step 1** (190 s per step, so G2 itself would pass with 60 steps ≈ 3.2 h).
  - Reward on the train prompts was 0.96, and 75% of groups had zero reward variance. Every check vector was all-True or all-False.
  - **Cause:** SFT and GRPO prompts come from the same 11 templates. `SFT_BASES` splits them by base DB only, so after 2 epochs of SFT the GRPO prompts are memorized. Test templates are disjoint and almost always failed.
  - So GRPO had no signal on the train prompts, and none on unseen templates either. B and C would also see identical rewards.
  - Stopped to save about 3 h of GPU. This is the "overfitting to templates" case in plan.md.
- **GRPO-B launched** at about 20:25 IST, with the default config.
- **SFT done.** 174 steps in 64 min; final train loss 0.042. The VM powered itself off at 14:48Z, and an L4 stockout cost 2 retries when restarting it.
- **SFT format check** on 32 test items, 1 sample each:

  | Metric | Value |
  |---|---|
  | Has final SQL | 1.00 |
  | Tool calls per trajectory | 2.0 |
  | Invalid tool calls | 0.19 |
  | Correct on the test DB | 0/32 |
  | Verified | 0/32 |

  The model follows the oracle pattern rigidly: one probe query, the answer query, then the final answer. When the answer query returns `ERROR`, it submits the same SQL anyway, because the oracle trajectories never show a repair. Its mistakes are near misses, such as `oi.customer_id` where `o.customer_id` is right. GRPO should fix this if sampled groups contain some correct rollouts.
- **SFT at epoch 1.09:** loss 0.007, token accuracy 0.997, entropy 0.01. The model is memorizing the templated oracle trajectories. **Risk:** GRPO groups whose rollouts all get the same reward give no learning signal. **Check:** run `gate_g1.py` on GRPO-B's first steps. If few groups have reward variance, rerun SFT for 1 epoch (about 32 min).
- **E4 base result** (2648 trajectories, Wilson 95% CIs):

  | Metric | Value |
  |---|---|
  | Verified accuracy | 0.004 [0.002, 0.007] |
  | Single-DB accuracy | 0.010 |
  | Has final SQL | 0.62 |
  | Silent errors | 0.012 |
  | Smuggled | 0.000 |
  | Invalid tool calls | 0.75 |
  | Tool calls per trajectory | 1.77 |

  The untrained model almost never answers correctly, and 3 in 4 of its tool calls fail.
- **Gate G1 tooling.** `scripts/gate_g1.py` rescores the check vectors in the reward log under the mean, strict and soft forms. G1 can then be decided from GRPO-B's first steps, with no extra GPU run.
- **Prepared GRPO launch.** `scripts/vm_grpo.sh REWARD NAME [train.py args]` runs one condition and then powers the VM off.
- **SFT is learning.** Loss fell from 0.49 to 0.16 by epoch 0.17, and token accuracy reached 0.96.
- **Base eval moved to the local GPU.**
  - Installed vLLM 0.22.1 in the local `.venv-train`.
  - Added `evaluate.py --gpu-mem`; the local card uses 0.75 because the desktop holds about 2 GB.
  - A 4-item test ran in 317 s, most of it model load and compile.
- **Full SFT launched** on the VM at about 19:00 IST (`scripts/vm_sft.sh`).
- **Smoke test passed** on the VM. Timings:
  - SFT: 22 s/step (16 examples per step).
  - GRPO: 9.6 s and 18.4 s per step (G=2, 1 prompt).
  - Eval: about 2 min per model for 4 items.

  Rewards are still 0: after 0.05 SFT epochs the model writes wrong or missing final SQL, and it often puts a tool call and its final SQL in one turn.
- **Fixed: eval crashes.**
  - vLLM's LoRA support fails on Tiny Aya's tied embeddings. GRPO adapters are now merged (`runs/<run>/merged`), and eval serves merged models.
  - FlashInfer's sampler fails to compile on the VM, so eval disables it.
  - The venv's `ninja` was not on PATH.
- **Fixed: GRPO trained on the wrong tokens.** AgentTune's multi-turn token stream dropped the chat-template tokens between turns, so the trainer scored tokens in a context vLLM never saw (importance ratio ~1e-5). vLLM prompts also had a double BOS.
  - Fix: `patches/agenttune-multiturn-ids.patch` re-renders the finished conversation and puts the loss only on assistant turns. `scripts/vm_setup.sh` applies it.
  - Check: `scripts/check_token_gap.py`, on CPU.
  - Side effect: vLLM's importance-sampling correction is off, so GRPO is purely on-policy.
- **Fixed: GRPO memory.**
  - TRL loads the policy in fp32 by default; it is now loaded in bf16.
  - A 4 GiB logits allocation ran out of memory; GRPO now uses batch 1 with gradient accumulation of G×prompts.
  - vLLM sleep mode segfaults on wake-up, so it is off.
- **VM:**
  - asia-south1-a had an L4 stockout for about 1.5 h; `scripts/vm_start.sh` retries the start.
  - Moving the VM to another zone needs the lead's OK.
  - `~/.ssh/config` must be mode 600, or SSH rejects it once teammates share the group.
- **Access:**
  - Aksh: VM user `aksh` with sudo, in the lead's user group, able to read the HF token, plus IAM `compute.instanceAdmin.v1` on the VM.
  - A grant mistakenly made to a placeholder email was revoked within minutes; the audit log shows no activity from it.
- **VM setup:** created `sqlcf-l4`, pinned the vendor repos, installed torch 2.11, vLLM 0.22.1 and TRL 1.7.1, and copied the data and the hackathon HF read token to the VM.
- **Earlier (CPU):**
  - Built the datasets: audit 1302 items, train 907, test 331, SFT 462 trajectories.
  - E0 reward audit: H2 not met; the false-positive cut is 43% against the pre-registered 50%.
  - E1 blind rate: S size 0.292.

  See `plan.md`, "Status".
