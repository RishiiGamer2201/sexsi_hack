# Research Notes — Counterfactual Database Rewards for Small SQL Agents

Team **Teen_khapeetars** (Shreshth Rai, Rishii Kumar Singh, Aksh Aggarwal) · Lexsi Labs AI Safety & Alignment Hackathon · compiled 2026-11-08

Sources: four parallel research passes (hackathon rules, prior art/novelty, tooling/feasibility, competitor scan). Every fact has a link. Items marked **UNVERIFIED** could not be confirmed from a primary source.

---

## TL;DR

1. **Fit is strong.** Track 3 problem statements #6 ("…rewarded on **verified results**") and #9 ("design rewards … that raise real task success **without being gamed**") describe our project almost word for word. Claim both.
2. **Biggest hook: the organisers' own SQL reward can be gamed.** AgentTune's flagship GRPO example is a SQL agent, and its built-in SQL rewards (`correctness_reward`, `query_reward`) never compare query results. A yes/no guess or a padded `WHERE` gets paid. Measuring that, then closing it with counterfactual DBs, is direct and useful feedback to Lexsi.
3. **Novelty is narrow but real.** Multi-DB checks already exist for *evaluation* (Zhong 2020, Ai 2026) and counterexample DBs exist for *SFT* (SQLoom). ReViSQL fixed false-positive rewards with a *symbolic verifier* at frontier scale. **No paper found uses bug-family-targeted counterfactual DBs as the online RL reward, at ~3B, with per-family FP/FN rates, a held-out family and answer-smuggling measurement.** The phrase "counterfactual database instances" is already used (Ai 2026), so we cannot claim the term.
4. **Compute is the binding constraint.** $20 HF credit ≈ 11 L40S-hours ≈ one SFT run plus two short GRPO runs and no reruns. We need a second GPU source or must cut GRPO to ~60–80 steps per condition.
5. **Expect a small GRPO effect.** On Tiny Aya, other teams got +5 pp from GRPO over SFT (Kataa) or nothing (PRINCE2). The headline must therefore be the **reward audit (FP/FN rates)**, which needs no GPU. Accuracy is secondary.
6. **Direct competitors:** SafeQuery (same SQL domain and model; claims 100% accuracy on one gold DB) and Kataa (naive vs hardened reward, null result, no FP-reward metric). Neither does counterfactual-DB rewards.

---

## 1. The hackathon

Source: [hackathon.lexsi.ai](https://hackathon.lexsi.ai/) ([H]); kickoff slides [hackathon.lexsi.ai/kickoff-slides](https://hackathon.lexsi.ai/kickoff-slides/) ([S]).

### 1.1 Organisers and logistics
- **Host:** Lexsi Labs ("Frontier Model Science lab", Mumbai/Paris/London). **Partners:** Cohere Labs, Hugging Face. **Outreach partners:** AISafety.com, AI Safety India.
- **Kickoff:** [luma.com/66jkhulx](https://luma.com/66jkhulx), Bengaluru. "$30,000+ in prizes and credits."
- **Discord:** discord.gg/dtEDQ2Z3eg (#hackathon-lexsi). Idea validation and issues go through tickets at discord.gg/CFSTMN7xTh (#report-issues). Office hours run several times a week (Discord Events).
- **Code and models:** [github.com/Lexsi-Labs](https://github.com/Lexsi-Labs), [huggingface.co/Lexsi](https://huggingface.co/Lexsi).

### 1.2 Timeline
| Date | Event |
|---|---|
| Nov 14, end of day AoE | Build closes. Resubmission allowed; the latest submission counts. The form is emailed a few days before. |
| Nov 15–16 | Judging. Up to 20 finalists announced Nov 16. |
| Nov 16–21 | Finalists "prove your thesis". The slides ask the article to include a "with more credits" plan. |
| Nov 22 | Demo Day (in person or online). |

### 1.3 Track 3 problem statements (verbatim, [H])
6. **Data and database agents:** "Train an agent that answers business questions by querying databases or APIs (finance, operations, analytics), rewarded on verified results."
9. **Reward design and reward-hacking defences:** "Design rewards (process rewards, LLM judges, groundedness checks) that raise real task success without being gamed."

The other Track 3 statements are tool calling, efficient trajectories, distillation, RAG, multi-hop data, business workflows and self-healing. Numbering follows list order on the site.

### 1.4 Rules that constrain us
- **Model:** the core submission must use **Tiny Aya (Base/Global/Fire/Water/Earth) or Aya Expanse 8B/32B**. Other models are allowed only as teacher, validator or judge. Qwen, Llama and others **cannot be the trained policy**.
- **Repos:** chain the track's repos into a real pipeline. The 2-repo minimum does not apply to Track 3, but **3+ repos are preferred**. Track 3 toolkits are AgentTune and AuditKIT. CuratorKIT (Track 1) is also usable.
- **Teams:** 1–3 people. Switching track is allowed until the deadline.

### 1.5 Required deliverables
- Registered email.
- Abstract under 500 words.
- **Public, un-gated HF model collection** (adapters).
- **Public HF dataset collection** (datasets, logs, traces, benchmarks).
- Write-up: HF Article, or GitHub README if Articles are unavailable.
- GitHub repo with reproducibility notes.
- List of repos and models used, plus track and problem statements.
- **Before/after results on more than one metric.**
- **Public deployment** (demo or repo link).
- *Optional but preferred:* **ROI comparison** of a closed API model vs our self-hosted small model (GPU-hours, $/hr, tok/s, realistic volume).

**Article sections requested by the slides:**
1. Problem and approach
2. Repos and features used
3. Models and licences
4. Datasets and licences
5. Model collection
6. Data collection
7. Experiments, findings and what else we tried
8. "With more credits: approach, before/after"
9. Teammates tagged

### 1.6 Judging ([S])
- An internal validity check (public artifacts, write-up, checklist, no duplicates), then tagging to the closest track.
- **Double-blind** scoring by several judges (founders, academics, industry labs, organisers' research teams). Normalised averages pick 10–20 finalists.
- **Rubric shown:** Write-up clarity /10 · Practical usefulness /10 · Code/notebook quality /10 · Overall /100. How these combine is not published.
- Implication: the write-up and practical usefulness weigh as much as the code.

### 1.7 Compute and prizes
- **$20 HF credits** per team (ZeroGPU or Jobs), sent to the team lead; expire 30 days after redemption. The coupon was emailed Nov 1, 5:30 PM IST, so **check spam**. Colab and Kaggle free tiers are suggested. Finalists get another $200.
- **Prizes:** 1st $3,662 cash + $3,500 credits · 2nd $2,662 + $2,500 · 3rd $1,962 + $1,800 · 4th $1,362 + $1,200 · 5th $1,162 + $1,000. The top 5 also get 6 months of HF Pro per teammate.

### 1.8 Lexsi Labs research focus (speak their language)
- **Focus areas:** interpretability, alignment, safety, tabular foundation models, governance/drift.
- **Papers:** AlignTune (2602.09621), CuratorKIT (2606.21631), Provenance-Grounded Gating (2606.11127), Interpretability as Alignment (2509.08592), circuit-based unlearning and refusal.
- **Recurring vocabulary:** "verified outcome", "provenance", "programmatic metrics", "reward hacking defences".

---

## 2. Lexsi tooling

### 2.1 AgentTune ([repo](https://github.com/Lexsi-Labs/AgentTune), [paper 2610.13335](https://arxiv.org/abs/2610.13335))
- Training lifecycle for tool-using agents: build → collect → evaluate → train → distill → heal. Two-tier **EventLog**: light (tool calls, results, rewards) and full (token spans, logprobs).
- **Programmatic trajectory metrics:**

  | Metric | Measures |
  |---|---|
  | TAC | tool-argument correctness |
  | ARR | redundant-call ratio |
  | SCSR | self-correction success |
  | RAD | reasoning-to-action density |
  | LCF | loop-collapse frequency |
  | PAS | plan adherence |
  | TER | tool efficacy |
  | PMED / ASE | path edit distance / action-state efficiency vs a golden trajectory |

- **API:** `create_agentic_trainer("grpo"|"ppo"|"dpo"|"rloo"|"bco", model=, tools=[python fns], train_dataset=, reward_funcs=[...], peft_config=dict(r=16, lora_alpha=32,...), use_vllm=True, vllm_mode="colocate", num_generations=, beta=)`. The dataset needs a chat-format `prompt` column. Extra dataset columns arrive in the reward function's kwargs.
- **Reward signature:** two readings disagree. The README gives `fn(completions, answer=None, **kwargs) -> list[float]`. The agentic GRPO doc gives `completions: list[list[dict]]` (full message lists, including `role:"tool"` turns). **Verify on day 1.**
- **Defaults to override:** `max_completion_length=256` (far too small for multi-turn), `num_generations=4`, `beta=0.04`, temperature 0.7.
- **Internals:** built on TRL. It patches `GRPOTrainer._generate_single_turn` with a multi-turn tool rollout. The Tiny Aya example uses `max_steps_per_turn=3`.
- **Outputs:** `trajectories.jsonl` (its `reward` field is null, so log rewards ourselves), the adapter, and `lexsi_provenance.json`. AuditKIT reads these via `auditkit.agent_eval.episodes_from_agenttune(path)`.
- **Tiny Aya specifics:**
  - The Cohere chat template does not render `tools`. AgentTune falls back to putting tool schemas in the system prompt (~1.4K tokens) and returning tool results as user turns.
  - `tools_fallback_prompt=None` makes it raise an error instead.
  - It also parses Cohere's native action format.
- **Install:** Python 3.12+, transformers ≥5.15, pins **PyTorch 2.11**. vLLM is optional and Linux/CUDA only. **Risk:** a vLLM build matching that torch pin and supporting `cohere2` is not confirmed in docs; it worked for team Kataa.
- **Known issues** ([known-issues.md](https://github.com/Lexsi-Labs/AgentTune/blob/main/docs/community/known-issues.md)):
  - The CLI has no `--tools` flag, so agentic training is Python API only.
  - `ToolRegistry` imports every builtin, so a missing `langchain_community` breaks it. Pass plain functions instead.
  - `SQLDatabaseTool()` from the registry has no `db_uri`. Construct `SQLDatabaseTool(db_uri=...)` or write our own tool.
  - Shadowed reward names: `format_reward` resolves to the weaker `use_case.py` version.
  - `DistilledJudge`, `hybrid_prm_reward`, ROUGE and BLEU silently return 0 on error or missing dependencies.
  - `AuditReader.extract_dpo_pairs` returns `[]`.
  - The paper itself admits "one default reward configuration scores a well-formed, a malformed, and a missing tool call identically."
- **Licence:** Lexsi Source Available License (non-commercial, not OSI, forbids weakening safety behaviour).
- **Repo status:** 12 stars, 6 open issues, last push Nov 4.

#### 2.1.1 AgentTune's built-in SQL rewards can be gamed (our hook)
From [`builtin_rewards/sql.py`](https://github.com/Lexsi-Labs/AgentTune/blob/main/src/agenttune/agentic/rewards/builtin_rewards/sql.py) and [rewards-reference.md](https://github.com/Lexsi-Labs/AgentTune/blob/main/docs/reference/rewards-reference.md). The flagship example is the BioGRID SQL agent (Qwen3-1.7B).

| Reward | What it checks | Exploit |
|---|---|---|
| `correctness_reward` | Parses `*yes*`/`*no*` from the text and matches the gold label | Guessing scores ~50%; always answering the majority label scores more |
| `query_reward` | +0.4 per query containing `WHERE`; penalties for `LIMIT 1`, >3 queries, or no `WHERE`; +2 when "has any rows" matches the yes/no gold | Pad any query with a trivial `WHERE` that returns rows |
| `structure_reward` | call → response format | Satisfied without a correct query |

None of these executes the agent's query and compares the result to the gold result. A SQL-agent team that copies the README setup inherits this.

### 2.2 AuditKIT ([repo](https://github.com/Lexsi-Labs/AuditKIT), [docs](https://auditkit.lexsi.ai))
- `pip install auditkit` (Python 3.10+).
- **Core functions:** `ak.evaluate()`, `compare_models()` (bootstrap significance), MLflow tracking, run fingerprinting.
- **`auditkit.agent_eval`:**
  - The headline is a **verified outcome** from an oracle: `FinalStateAssertion`, `ArtifactAssertion`, `AnswerAssertion`, `CustomPredicate(fn, version=)` or `AssertionOracle`. Verdicts are success, failure, unknown or error.
  - "A judge never overrides a verified state check." Disagreements land in `row.disagreement`. The summary flags "answers that claim success while the verified outcome failed", which is effectively **our silent-error metric**.
  - `trials=N` gives `pass_at_k`, `all_k`, consistency and variance. Independence is only claimed with `reset_confirmed=True`.
  - `rescore()` re-scores recorded episodes offline. `write_sidecar()` exports results as JSONL.
- **Known issues:**
  - `paired_bootstrap` p-values sat at ~0.5 regardless of effect in v1.1.3. Fixed by [PR #23](https://github.com/Lexsi-Labs/AuditKIT/issues/20) on Nov 7, so **install from main** and also compute our own tests.
  - Built-in benchmarks (mmlu, gsm8k) fail to load.
  - `win_rate`, `elo_score` and `preference_accuracy` silently fall back to token overlap.

### 2.3 Fallback if AgentTune breaks
- Plain TRL `GRPOTrainer(environment_factory=SQLEnv)` ([TRL OpenEnv docs](https://huggingface.co/docs/trl/en/openenv)):
  - Public methods on the environment class become tools.
  - `reset(**kwargs)` gets the dataset columns: DB path, gold SQL, counterfactual DB paths.
  - The reward function receives `environments`.
  - `max_completion_length` caps the whole episode.
- **Caveat (inference, UNVERIFIED):** TRL parses tool calls through the chat template, and Tiny Aya's template has no tool support. We would need a custom parser or `rollout_func`, which is what AgentTune already does. Not worth switching to verl, SkyRL or ART with 6 days left.

---

## 3. Base model: Tiny Aya Global

- **HF id:** `CohereLabs/tiny-aya-global` ([card](https://hf.co/CohereLabs/tiny-aya-global), [Cohere docs](https://docs.cohere.com/v2/docs/tiny-aya.md)). Architecture `cohere2`, 3.35B, BF16.
- **Context:** 8K input / 8K output. Sliding-window attention (4096) in 3 of every 4 layers, global attention in the fourth.
- **Licence: CC-BY-NC-4.0, gated.** Every teammate and HF Job needs the licence accepted and a token.
  - **Open question:** can a LoRA adapter of a gated model be published un-gated, as the rules require? Ask in a Discord ticket.
- **No code or SQL benchmarks** on the card. GPQA-Diamond 28.28. The card says reasoning and math are weaker.
- **Tool use is weak out of the box:**
  - PRINCE2 measured base exact-call accuracy at 3.3%.
  - Kataa: base Tiny Aya decided only 49% of tasks, with 19% accuracy.
  - **An SFT warm start is mandatory.**
- **RL results on Tiny Aya:**
  - [Kataa](https://github.com/UEddy/Kataa): SFT, then GRPO for 90 steps × 8 rollouts. About +5 pp over SFT.
  - [PRINCE2](https://github.com/PRINCE2-AI/lexsi-agentic-hinglish): two GRPO runs, McNemar p=1.0, no effect. Before the SFT warm start, `frac_reward_zero_std=1`.
- Aya Expanse 8B is the only larger allowed option, at ~2.5× the compute. Treat it as the "prove your thesis" upgrade.

---

## 4. Compute reality

**HF Jobs pricing per hour** ([pricing](https://huggingface.co/docs/hub/jobs-pricing)). The default timeout is 30 minutes, so **always pass `--timeout`**.

| GPU | $/hr |
|---|---|
| T4 | 0.40 |
| L4 | 0.80 |
| A10G-small | 1.00 |
| **L40S** | **1.80** |
| A100-80G | 2.50 |
| H200 | 5.00 |

**Measured by other teams:**
- **Kataa, 1× L40S:** SFT (under 2 h), GRPO 90 steps × 8 rollouts with colocated vLLM (under 3 h), eval of 300 tasks in 191 s. Total **$17.91**.
- **PRINCE2, T4 without vLLM:** 381 s per GRPO step with G=2. Unusable.

**Estimates (UNVERIFIED; benchmark one step on day 1).** LoRA r=16, colocated vLLM, 4 prompts × G=8, 2–3K tokens, 3–5 turns:

| GPU | Steps per hour |
|---|---|
| H100 / H200 | 40–60 |
| A100 / L40S | 20–35 |
| L4 / A10G | 6–12 (tight memory) |

**When the reward moves.** A SkyRL-SQL reproduction (7B, 653 examples) went 38→58% at step 5 and 70% at step 10 with ~6.4K rollouts ([model](https://huggingface.co/lecunyin/Qwen2.5-Coder-7B-SkyRL-SQL)). At 32 rollouts per step, the same rollout count is ~200 steps. Expect visible movement at 50–150 steps, *if groups have reward variance*.

**Budget:** SFT ~1.5 h + B ~4 h + C ~4 h + eval ~1 h ≈ 11 L40S-hours ≈ $20. That is exactly our credit, with zero slack.

---

## 5. Prior art and novelty

### 5.1 Citation check (corrections to our original plan)
| Citation | Status / correction |
|---|---|
| Pasupat & Liang, [1606.06900](https://arxiv.org/abs/1606.06900) | **ACL 2016.** "Fictitious worlds" rule out 92.1% of spurious logical forms. A training-time precedent. |
| XData, [1411.6704](https://arxiv.org/abs/1411.6704) | Chandra, Chawda, Kar, Reddy, Shah, Sudarshan. **VLDB Journal 2015.** Mutant-killing data generation. |
| Zhong, Yu & Klein, [2010.02840](https://arxiv.org/abs/2010.02840) | EMNLP 2020. Distilled test suites, **evaluation only**. |
| ParSEval | Chen, Miao, Zhang, Wang. PVLDB 18(11):4750–4762. Plan/branch coverage. |
| ReViSQL, [2603.20004](https://arxiv.org/abs/2603.20004) | **Current title:** "Human-Level Text-to-SQL via Reinforcement Learning on Verified Data, Without Pipeline Engineering". **32.8% is in the body, not the abstract**: a 300-step Kimi-K2.6 pilot on BIRD, with VeriEQL refuting 28.8–38.4% of positive rewards, not falling over training. **The reward is a soft penalty: 0.8 (β=0.2) if refuted; a ⊥ verdict keeps reward 1.** VeriEQL is bounded at 2 tuples per table, 30 s. Only Kimi-K2.6 and Qwen3-235B; **nothing ≤8B**. |
| Graph-Reward-SQL, [2505.12380](https://arxiv.org/abs/2505.12380) | Findings EMNLP 2025. Execution-free GMN reward. Test suites used only in evaluation; says execution-reward FP and FN are "unavoidable". |
| SQLoom, [2611.03298](https://arxiv.org/abs/2611.03298) | Fu et al., submitted 2 Nov 2026. **SFT with a set-contrastive loss, no RL.** Counterexample DBs: FK-closed sub-DB, then mutate (duplicate rows with fresh PKs, constant-boundary values, extra 1:N children, ties). Qwen3-1.7B. |
| AceReason-Nemotron, [2505.16400](https://arxiv.org/abs/2505.16400) | NVIDIA. The test-curation pipeline is mentioned only. |
| HardTests, [2505.24098](https://arxiv.org/abs/2505.24098) | RL on Qwen3-4B. Weak TACO tests *hurt* (36.95 vs 38.48 base); HardTests helped (39.42). |
| RobustTests, [2608.24135](https://arxiv.org/abs/2608.24135) | EMNLP 2026. Tests synthesized from near-correct faulty code, with a dense pass-rate reward. |
| Jin et al., [2601.08778](https://arxiv.org/abs/2601.08778) | Annotation error rates of 52.8% on BIRD Mini-Dev and 62.8% on Spider 2.0-Snow. |
| NL2SQL-BUGs, [2503.11984](https://arxiv.org/abs/2503.11984) | KDD 2025. Taxonomy of 9 categories and 31 subcategories. Use it to label our families. |
| tau-bench, [2406.12045](https://arxiv.org/abs/2406.12045) | Source of pass^k. |
| AgentTune, [2610.13335](https://arxiv.org/abs/2610.13335) | A library; cite it because we use it. |

### 5.2 New must-cite work found
- **Ai 2026, "Bounded Semantic Planning and Deterministic Compilation for Reliable Enterprise Text-to-SQL"** ([2608.16663](https://arxiv.org/abs/2608.16663)). It **already uses the term "counterfactual database instances"** for multiplicity-changing variants that expose grain-unsafe (fan-out) SQL. It is **evaluation only** (38 enterprise questions, GPT-class models), with no training.
- **DualSQL** ([2609.18135](https://arxiv.org/abs/2609.18135), Google/OSU). A strict single-DB comparator (REX: multisets, column permutation, ORDER BY) used as the RL reward, motivated by EX false positives. Trained at **4B/8B**, so it is the closest small-scale reward-FP precedent.
- **Progress-SQL** ([2606.06825](https://arxiv.org/abs/2606.06825)): test suites used for evaluation only.
- **CodeContests+** ([2506.05817](https://arxiv.org/abs/2506.05817)): only 67.1% of generated tests were valid.
- **Other SQL RL papers.** None uses multi-DB rewards:
  - [SQL-R1](https://arxiv.org/abs/2504.08600): 3B goes 50.5→54.6 on BIRD dev.
  - [Arctic-Text2SQL-R1](https://arxiv.org/abs/2505.20315): reward 1 exec-match / 0.1 executes / 0 otherwise; finer shaping caused "lazy" optima.
  - [Think2SQL](https://arxiv.org/abs/2504.15077): includes 3B.
  - [SkyRL-SQL](https://novasky-ai.notion.site/skyrl-sql): 653 examples, multi-turn.
  - [Reasoning-SQL](https://arxiv.org/abs/2503.23157), [CogniSQL-R1-Zero](https://arxiv.org/abs/2507.06013), [MARS-SQL](https://arxiv.org/abs/2511.01008), [ExeSQL](https://arxiv.org/abs/2505.17231), [Reward-SQL](https://arxiv.org/abs/2505.04671).

### 5.3 Closest work, ranked by threat
1. **ReViSQL:** same motivation (FP execution rewards), fixed with a verifier. Frontier scale, a single DB, no families, no FN analysis of its own reward.
2. **SQLoom:** nearly the same counterexample mechanism and families, at 1.7B, but used for SFT, not online RL.
3. **Ai 2026:** same term and fan-out idea, evaluation only.
4. **Pasupat & Liang:** the conceptual ancestor at training time.
5. **Zhong 2020, Graph-Reward-SQL, Progress-SQL:** multi-DB used for evaluation only.
6. **DualSQL:** a ≤4B reward-FP fix, but on a single DB.
7. **XData, ParSEval:** generator baselines.
8. **HardTests, RobustTests, CodeContests+:** the code-RL analogue.

### 5.4 Novelty verdict
**Plausibly novel (to our knowledge, Nov 2026):**
- Execution on **code-generated, bug-family-targeted counterfactual DBs as the online GRPO reward** for text-to-SQL.
- **Per-family FP/FN reward rates**, and generalization to a **held-out bug family** never seen in the reward.
- **Business-semantic families** (cancelled/soft-deleted rows, superseded tier rows, refunds), beyond purely structural mutations.
- **Answer-smuggling measurement**: hard-coded literals found during exploration. No SQL-RL paper found measures this.
- All of it at ~3B, plus an audit of a widely shipped library reward (AgentTune).

**Do NOT claim:**
- First to show execution rewards give FPs (ReViSQL, Graph-Reward-SQL, DualSQL).
- First to use multiple or counterfactual DBs against spurious matches (Pasupat & Liang, Zhong, XData, Ai).
- First to generate counterexample DBs for training (SQLoom).
- First to fix FP rewards in SQL RL (ReViSQL, DualSQL).
- "Single-DB checks are 32.8% FP" as a general fact. It is one model on BIRD in a pilot, under a bounded verifier.
- Any SOTA claim.

**Safe novelty sentence:**
> To our knowledge, this is the first study to use execution on code-generated, bug-family-targeted counterfactual databases as the online RL reward for a small (~3B) text-to-SQL agent, and to measure that reward's per-family false-positive and false-negative rates, its generalization to a held-out bug family, and answer smuggling. Prior work applied multi-database checks to evaluation (Zhong et al. 2020; Ai 2026) or supervised fine-tuning (SQLoom), or used symbolic verification on a single database (ReViSQL).

---

## 6. Competitor landscape (public as of Nov 8)

No official gallery exists, but the rules force public HF collections and repos, so many entries are visible. Discord was not checked (login needed).

| Project | Problem stmt | Approach / status | Threat |
|---|---|---|---|
| **SafeQuery** ([model](https://hf.co/Siva2022/safequery-tiny-aya-global-sft-lora), [tasks](https://hf.co/datasets/Siva2022/safequery-retail-tasks), [traces](https://hf.co/datasets/Siva2022/safequery-eval-traces)) | #6 | Tiny Aya Global SFT LoRA on a 200k-order retail SQLite DB: read-only checks, cost limits, refusals, injection resistance. Task success 11.7→98.3%, accuracy 3.2→100%, but invalid tool calls rose 1.5→16.7%. Has a `grpo_train.jsonl`; no reward described; scoring undocumented. | **High (same domain).** Their single-DB "100%" is exactly what counterfactual DBs stress-test. |
| **Kataa** ([repo](https://github.com/UEddy/Kataa)) | #9 + safety | Margin-call agent. SFT, then GRPO naive vs hardened reward. Accuracy 19→73%; unsafe-among-decided 61→25%. A pre-set gate rejected the DPO repair. ROI table vs Mistral Large ($0.32 vs $11.72 per 1k). **Honest null:** the two rewards were indistinguishable. | **High (#9).** Sets the rigor bar. Never measures FP-reward rate. |
| **Hinglish Expense Agent** ([repo](https://github.com/PRINCE2-AI/lexsi-agentic-hinglish), [demo](https://huggingface.co/spaces/primce/hinglish-expense-agent), [article](https://huggingface.co/spaces/primce/hinglish-track3-article)) | tool calling | Reward on final ledger state. Hard-90 3.3→93.3% (Wilson CI), McNemar 81 fixed / 0 broken. GRPO had zero effect, reported openly. "Judge's 60-second view" table and a 20-check verify script. | Medium. **Best-packaged entry; copy the format.** |
| Oya ([repo](https://github.com/Timidan/lexsi-hack)) | tool calling | Wallet agent in Pidgin/Yoruba scored on wallet state. SFT + DPO, GGUF build, voice demo. | Low–medium |
| Strategy agent ([repo](https://github.com/HatemSaadallah/lexsi-strategy-agent)) | distillation | Command A+ → Tiny Aya. 2-judge rubric 0.65→1.48 with CI. ROI $0.03 vs $0.25. | Low |
| Reflexive Agents ([repo](https://github.com/CharlieGalvin/lexsi-labs-reflexive-agent)) | self-heal, #9 listed | τ²-bench, GRPO/BCO, Aya Expanse 32B. No results yet. | Medium (claims #9) |
| SafeToolCall ([repo](https://github.com/ridakalam52-design/safetoolcall-tiny-aya)) | tool calling + #9 | Programmatic rewards "so the model can't game an LLM judge". No numbers yet. | Medium (#9 framing) |
| RewardHackLab ([model](https://hf.co/Artemis2100/rewardhacklab-tiny-aya-global-lexsi-2026)) | #9 by name | 0/6 completions; describes itself as "not a reward-hacking mitigation". | Name only |
| DataAgent ([repo](https://github.com/umarshareef0165-netizen/lexsi-dataagent)) | #6 | Prompting only on a toy DB; no fine-tune. | Low |
| ToolBoundary, Permit, triage, GRPO schema extraction, others | various | See the competitor report. | Low |

Searches for "text-to-sql aya", "sql agent tiny aya", "counterfactual database reward", "lexsi sql" and similar found **no other SQL reward-hacking entry**.

### 6.1 What the strongest entries do (and judges at similar events reward)
- **Before/after tables with uncertainty:** Wilson CIs, paired McNemar ("81 fixed, 0 broken"), bootstrap CIs.
- **Pre-registered gates and honest nulls.** Kataa and PRINCE2 both report nulls, and it reads as credible.
- **Verification by environment state**, not an LLM judge.
- **An ROI table vs a closed model.**
- **One-command reproduction**, with every number traceable to a stored run (`verify_all.py`, ScarTissue's "every number generated from stored runs").
- **A live demo with a visible tool trace.** A "judge's 60-second view" at the top of the README.
- **Comparable events:**
  - Expedition Aya judged on creativity, impact and scientific integrity ([FAQ](https://sites.google.com/cohere.com/expedition-aya/faq)).
  - Apart praised generality, benchmark potential and clear insights ([post](https://www.lesswrong.com/posts/kHt9e6hzTnxfm3Em3/results-from-the-ai-testing-hackathon)).
  - OpenEnv write-ups ([HackWatch](https://github.com/Afras99/HackWatch), [FATHOM](https://pratham-math-fathom-blog.static.hf.space/index.html)) say reward design caused most failures and recommend stress-testing rewards with adversarial policies *before* GRPO.

---

## 7. Technical design inputs

### 7.1 Reward recipes from the literature
| Source | Reward |
|---|---|
| Arctic-R1 | 1 exec-match / 0.1 executes / 0 otherwise. Simple beats shaped. |
| SkyRL-SQL | Format + exec-match, binary. No KL. Multi-turn learned faster. Failure modes: early overconfidence, resubmit loops, context bloat. |
| SQL-R1 | Format ±1, exec ±2, result ±3, length term (weights UNVERIFIED). |
| ReViSQL | Exec-match × (1 − 0.2·[verifier refutes]). |
| RobustTests | Dense pass-rate across tests. This is our `mean(Ci)` and reduces zero-variance groups. |

### 7.2 Counterfactual generator design (borrowed ideas)
1. **Two kinds of variant (from Ai 2026).**
   - *Answer-preserving* variants keep the gold result unchanged while wrong SQL diverges. They target fan-out and duplicates.
   - *Answer-changing* variants change the gold result itself.
   - **Every item needs at least one answer-changing variant.** Otherwise a hard-coded literal passes every Ci and smuggling goes undetected.
2. **SQLoom mutations:** duplicate rows with fresh PKs, constant-boundary values, extra 1:N children, then validate PK, FK, NOT NULL and types.
3. **Adversarial seeding (HardTests / RobustTests):** generate variants against the model's own near-miss rollouts or our hand-written gold mutants.
4. **Distillation (Zhong 2020):** choose the minimal K variants that kill a pool of gold-query mutants. This keeps cost per rollout low.
5. **Tie and determinism check:** run gold SQL on each variant twice with shuffled insert order. Drop the variant if the result changes.
6. **Gold validation:** keep the pandas cross-check. Annotation error rates of 50%+ in public benchmarks (Jin 2026) mean gold bugs become false-negative rewards.
7. **Mechanics:** copy with `VACUUM INTO 'cf_k.db'`, perturb with a fixed seed, precompute gold results offline. The C reward is then CPU-only and costs the same GPU time as B.

### 7.3 Result comparator
- Compare as **multisets**. BIRD's `set()` comparison hides DISTINCT and duplicate bugs, the very family we target.
- Order-sensitive only when the gold SQL has `ORDER BY`.
- Allow column permutation (DualSQL REX). Ignore column names.
- Round floats to 4 decimal places.
- Per-item grading mode: set, list or subset (ReViSQL).
- 5 s timeout via `conn.set_progress_handler`. Open the DB read-only (`file:...?mode=ro`).
- Reference implementation: [test-suite-sql-eval `exec_eval.py`](https://github.com/taoyds/test-suite-sql-eval).

### 7.4 GRPO pitfalls and fixes
| Pitfall | Fix |
|---|---|
| Empty gold result | Drop the item, since any empty query would "match". |
| Zero-variance groups | After SFT, keep prompts with pass rate in (0,1) over 8 samples. This is worse under the stricter C reward, so consider a 0.1 executes floor. |
| Format collapse | Episodes with no final SQL get 0. |
| Context overflow | 8K minus ~1.4K tool prompt. Truncate tool output to ~20 rows / ~1.5K chars and cap at 5 turns. |
| Resubmit loops | Cap turns. Report AgentTune ARR/LCF. |
| Literal smuggling | Answer-changing variants defeat it. Log the rate of literal-only SQL as a metric. |

### 7.5 Statistics
- **McNemar (exact):** `scipy.stats.binomtest(b, b+c, 0.5)` on discordant pairs, same tasks.
- **pass^k (τ-bench):** `E_task[C(c,k)/C(n,k)]` with n=8, temperature 0.7, k=1,2,4.
- **Paired bootstrap:** 10K task resamples for the CI on accuracy differences. Wilson CIs for single proportions.
- Do not trust AuditKIT `paired_bootstrap` unless it is on main after Nov 7.

### 7.6 Data and schema sources
- **Our own synthetic generator** (Faker + templates) is the fastest route and guarantees gold answers.
- Reference schemas: Chinook/Northwind, τ-bench retail, Spider business DBs (`customers_and_invoices`, `department_store`, etc.; names UNVERIFIED), BIRD `debit_card_specializing`.
- **Cross-check target:** SafeQuery's public retail task set (CC licence to check), as a respectful stress test.

---

## 8. Open questions and risks
| # | Item | Status / action |
|---|---|---|
| 1 | Can a LoRA adapter of gated CC-BY-NC Tiny Aya be published un-gated? | Ask in a Discord #report-issues ticket today. |
| 2 | Has the $20 HF coupon been redeemed by the team lead? | Check email and spam. |
| 3 | Second compute source (university GPU, personal GPU, Kaggle T4×2/P100, Colab) | Needed; the $20 covers exactly one pass. |
| 4 | AgentTune + vLLM + `cohere2` install on the torch 2.11 pin | Smoke-test on day 1. TRL fallback is ready. |
| 5 | Exact AgentTune agentic reward signature | Verify on day 1 with a print-reward. |
| 6 | GRPO effect may be null at 3B | Headline is the reward audit. Pre-register the gate. |
| 7 | Discord announcements and office-hour times unknown | One teammate joins and reads #hackathon-lexsi. |
| 8 | Public write-up | Describe the 4th family only as "superseded and corrected records" in SQL terms. No RAG framing. |
