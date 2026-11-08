# Progress log

> **Rule: update this file after each and every step** (a run launched or finished, a bug found or fixed, a decision made, access changed). Add a dated entry at the top of the log, and keep "Current state" and "Next" accurate. Commit and push it with the work it describes.

## Current state (Nov 8, night)

- **Running on the VM:** full SFT (`scripts/vm_sft.sh`, log `runs/sft.log`): 1386 examples, 2 epochs, about 65 min. It then checks the SFT model's format on 32 test items and powers the VM off itself (`scripts/vm_autostop.sh`), unless a teammate is logged in.
- **E4 base model done** on the local GPU (`results/traj_base.jsonl`, 331 items × 8 samples). The local card ran it in 9 min, so it can run every E4 generation once the merged models are copied over.
- **Pipeline:** smoke test passes end to end on the team VM. It covers tests, tiny SFT, 2 GRPO steps, adapter merge, eval and scoring (`scripts/vm_smoke.sh`, `scripts/vm_smoke_eval.sh`).
- **VM `sqlcf-l4`** (asia-south1-a, 1× L4): start it with `bash scripts/vm_start.sh`, which retries through L4 stockouts. Stop it whenever no job is running. SSH from WSL's gcloud (user `admin_wsl`); the Windows gcloud key is not on the VM.
- **Gates:**
  - G1 (freeze the reward form): open.
  - G2 (GRPO step time): open. It needs real-config steps (G=6, 4 prompts).
- **Access:**
  - Aksh: sudo account on the VM, plus IAM rights to start and stop it.
  - Shreshth: no SSH key on the VM yet.

## Next

1. When SFT finishes, read the format check: has_sql rate, tool calls per trajectory, invalid tool calls.
2. GRPO-B (`R_exec_rex`) with `scripts/vm_grpo.sh R_exec_rex grpo_B`. Time its first steps to decide gate G2.
3. Gate G1 from GRPO-B's first steps, with `python scripts/gate_g1.py runs/grpo_B_rewards.jsonl --G 6 --first 96`. FN on gold is 0 for every form, so the tie-break decides: the form with the most groups whose reward has non-zero variance.
4. GRPO-C with the G1 form and the same budget as B.
5. E4 eval on base, SFT, B and C, then scoring.

## Log

### Nov 8

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
