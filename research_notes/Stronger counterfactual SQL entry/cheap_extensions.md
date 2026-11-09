# Cheap, high-impact extensions for the counterfactual-DB verifier (about 1 day, under $10)

Scope: extensions that answer the judges' likely question, "does this matter on real benchmarks and real models?" Project context, such as the F1–F4 bug families, the 29.5%→16.8% and 54.1%→1.9% audit numbers and the Command A results, is taken as given and not re-researched. Each cited fact links to its source. Unsourced estimates and opinions appear only under "Inferences" or "Gaps".

---

## Q1. Can we build counterfactual or perturbed DB copies for Spider dev or BIRD dev cheaply? What tools exist?

### Takeaway
For Spider dev, the copies already exist. The Zhong et al. distilled test suites (Apache-2.0) ship a set of perturbed DBs for each Spider DB plus an evaluator, so "verify on many DBs" can run on a real benchmark today at no GPU cost. BIRD has no public test suite, so any BIRD copies would have to come from our own generator.

### Cited Findings
- `taoyds/test-suite-sql-eval` is Apache-2.0. Its README links a Google Drive file with test-suite databases for **11 text-to-SQL datasets**: Spider, SParC, CoSQL, ATIS, Academic, Advising, Geography, IMDB, Restaurants, Scholar and Yelp. The DBs are unzipped into `database/`, and the only dependencies are `sqlparse` and `nltk`. BIRD is not covered. — [test-suite-sql-eval README](https://github.com/taoyds/test-suite-sql-eval)
- Evaluator CLI: `python evaluation.py --gold gold.txt --pred pred.txt --db database/ --table tables.json --etype exec`.
  - `exec` (test suite) is the default `--etype`; `match` and `all` are the other options.
  - `--plug_value` inserts gold values into predictions, `--keep_distinct` keeps DISTINCT keywords, and `--progress_bar_for_each_datapoint` helps find stuck executions.
  - The gold file format is `SQL \t db_id` per line.
  - The README gives no runtime figures. It says only that the bound is computed "efficiently", and it caches the classical datasets in `cache.pkl` because they "take a long time to run". — [test-suite-sql-eval README](https://github.com/taoyds/test-suite-sql-eval)
- Method (Zhong, Yu, Klein, EMNLP 2020):
  - A small test suite of databases is "distilled" for high code coverage of the gold query, out of "a large number of randomly generated databases".
  - The authors evaluated 21 Spider-leaderboard models and manually checked the metric on 100 examples, where it was always correct.
  - The old Spider metric had a 2.5% false-negative rate on average and 8.1% in the worst case.
  - The abstract gives no direct EX-vs-TS false-positive number. — [arXiv 2010.02840](https://arxiv.org/abs/2010.02840)
- The CodeS paper argues that BIRD relies on single-DB EX because its databases hold many values, which lowers the chance of false positives. It also notes the TS script lacks test suites for some DBs (for example Dr.Spider), so CodeS reported EX there. — [CodeS, arXiv 2402.16347](https://arxiv.org/pdf/2402.16347) (via search snippet; I could not parse the PDF text)
- OmniSQL already reports **test-suite accuracy (TS)** for Spider dev, Spider-Syn and Spider-Realistic, and EX elsewhere, including BIRD. TS on Spider is therefore standard in current text-to-SQL papers. — [OmniSQL README](https://github.com/RUCKBReasoning/OmniSQL)

### Inferences
- **Spider dev route (cheap, high value).** Treat each Spider dev DB plus its distilled test-suite DBs as our "counterfactual copies". Score any prediction twice:
  - EX on the original DB only (the "single-DB reward");
  - pass on all suite DBs.
  This puts our core claim on a real benchmark with zero new generator code.
- **Wording.** Zhong's DBs are random fuzz distilled for coverage, not targeted answer-changing edits. Frame them as "an independent, third-party instance of the multi-DB idea". The framing then argues: our targeted copies are cheaper and more precise, and the effect already shows up with generic fuzzed copies.
- **BIRD route (riskier).** There is no off-the-shelf suite. Generic operators applied to the tables and columns the gold SQL touches would work:
  - duplicate or delete rows;
  - inject NULLs;
  - create ties on ORDER BY or LIMIT columns;
  - shift values across WHERE thresholds.
  The gold SQL then acts as the oracle on each copy, as in test-suite accuracy. This is roughly half a day of code and should be attempted only after items 1–3 of the ranking below. BIRD DB sizes make copying slower than Spider; I did not verify the sizes.

### Gaps
- No exact download size or runtime for the Spider test-suite DB zip was found. The README omits both.
- I found no BIRD or BIRD mini-dev equivalent of a distilled test suite in any source.
- I found no Spider 2.0-lite perturbation tool.

---

## Q2. Are there public prediction files we can re-score offline (EX vs TS, "lucky pass" rate)? Known EX vs TS gaps?

### Takeaway
Yes, and this is the highest-value zero-cost experiment. Two public sources together cover about 12 systems on Spider dev, and OmniSQL also includes sampled outputs:
- **OmniSQL** shares a Google Drive bundle of predictions (7B/14B/32B, greedy plus sampled) for Spider dev/test, BIRD dev and six other sets.
- The **ESM+ repo** ships Spider dev prediction text files for 9 systems, including GPT-4 Turbo, Claude 3 Opus, DAIL-SQL, DIN-SQL and C3.

The literature also shows that even test-suite execution (EXE) keeps a 10–23% false-positive rate against a stricter semantic metric.

### Cited Findings
- **OmniSQL prediction results.**
  - Download: Google Drive file `1Mj6uNQxg-eghNK3-u7Zr0Z7iVuQKSgmz`.
  - Content: SQL generated by OmniSQL-7B/14B/32B on **Spider dev, Spider test, BIRD dev, ScienceBenchmark, Spider2.0-SQLite, EHRSQL, Spider-DK, Spider-Syn and Spider-Realistic**.
  - Strategies: greedy and majority voting. The sampling files carry `pred_sqls`, i.e. multiple samples per question.
  - Released "to assist the community in performing analyses without requiring extensive GPU resources". — [OmniSQL_prediction_results/README.md](https://github.com/RUCKBReasoning/OmniSQL/blob/main/OmniSQL_prediction_results/README.md)
- **OmniSQL licences.** The models are Apache-2.0 on HF (for example `seeklhy/OmniSQL-7B`). The SynSQL-2.5M data is Apache-2.0. The GitHub API returned no licence for the repo. — [HF API seeklhy/OmniSQL-7B](https://huggingface.co/seeklhy/OmniSQL-7B), [OmniSQL README](https://github.com/RUCKBReasoning/OmniSQL)
- **OmniSQL's own BIRD evaluator** compares results as **sets**: `frozenset(execution_res)` and `if set(predicted_res) == set(ground_truth_res)`.
  - Row order and duplicate rows are ignored.
  - Modes: `greedy_search`, `major_voting` (groups samples by execution result) and `pass@k`.
  - CLI: `--pred --gold --db_path --mode`. — [evaluate_bird.py](https://raw.githubusercontent.com/RUCKBReasoning/OmniSQL/main/train_and_evaluate/evaluate_bird.py)
- **ESM+ repo (`bossben/ESMp`).**
  - Ships `spider_dev/` and `spider_test/` folders with `gold.txt` plus prediction files: `GPT4Turbo.txt`, `Claude.txt` (Claude 3 Opus), `C3.txt`, `DAIL.txt`, `DIN.txt`, `RASAT+PICARD.txt`, `RESDSQL.txt`, `Graphix.txt` and `STAR.txt`.
  - Dev predictions were "taken directly from the corresponding githubs", except RASAT+PICARD, which was reproduced. Spider-test predictions were reproduced.
  - The evaluator is modelled on test-suite-sql-eval. The GitHub API showed no licence. — [ESMp README](https://github.com/bossben/ESMp)
- **ESM+ paper, Table 4.** On the Spider evaluation set, test-suite execution accuracy (EXE) false-positive rates against ESM+ judgments are:

  | System | EXE FP rate |
  |---|---|
  | DAIL | 16.3% |
  | DIN | 19.5% |
  | C3 | 23.0% |
  | Super | 15.0% |
  | RESDSQL+NatSQL | 10.0% |
  | RESDSQL+PICARD | 10.0% |
  | CodeS | 12.1% |

  All EXE false-negative rates are 0.0%. The paper notes that prompting-LLM systems have higher FP than fine-tuned ones. Its canonical example is `SELECT name FROM dogs` vs `... WHERE age < 10`, which match only because no dog is aged 10 or over. That is exactly the "lucky pass" pattern.
  - Spider dev EXE: DAIL 82.9, DIN 81.7, C3 79.8, Super 86.1, R+N 82.8, G+P 80.1, R+P 76.7, CodeS 83.5. — [ESM+, arXiv 2407.07313](https://ar5iv.labs.arxiv.org/html/2407.07313)
  - Caveat: these FP rates are measured against ESM+'s own (structural) labels, not human labels.
- **FLEX (NAACL 2025)** uses an LLM-judge metric. Re-evaluating top Spider and BIRD models shows ranking shifts and an average −3.15 points from correcting false positives. This figure comes from a summary; the versions report kappa 78.17 vs 87.04 (against 62.00 for EX). — [FLEX arXiv 2409.19014](https://arxiv.org/html/2409.19014v2), [ACL Anthology](https://preview.aclanthology.org/setup/2025.naacl-long.228)
- **NL2SQL-BUGs** used GPT-4o-assisted review to flag gold SQL with previously unknown semantic errors: 16 in Spider dev (1.55%) and 106 in BIRD dev (6.91%). — [arXiv 2503.11984](https://arxiv.org/abs/2503.11984)
- **Pervasive Annotation Errors (2026).** A corrected 100-example BIRD dev sample changed 16 agents' EX by −4% to +19% (summary) and shifted ranks by up to 9 positions. Versions report different figures (−7% to 31% relative), so check before quoting. — [arXiv 2601.08778](https://arxiv.org/pdf/2601.08778)

### Inferences
- **Experiment.** For each of the roughly 12 Spider dev prediction files (9 from ESM+ plus OmniSQL 7B/14B/32B greedy), compute:
  - EX on the original DB, using `evaluation.py` pointed at the plain Spider `database/`;
  - TS on the test-suite DBs;
  - **lucky-pass rate = #(EX pass ∧ TS fail) / #(EX pass)**.
  It needs CPU only. Running the evaluator twice per file should take minutes to under an hour; I did not measure this.
- **Payoff.** This turns "single-DB rewards pay buggy queries" from a synthetic finding into a real-model, real-benchmark one. It also gives a per-system bar chart, prompting LLMs vs fine-tuned, that echoes the ESM+ FP ordering.
- **Gold quality.** Pair the result with NL2SQL-BUGs and the annotation-error papers as context: gold quality limits any verifier, and our approach does not fix gold errors. Saying so pre-empts that criticism.
- **BIRD dev predictions.** OmniSQL's BIRD files can be re-scored only with EX until we generate BIRD copies (Q1). They can still be audited for comparator effects: set vs multiset vs ordered comparison changes the score, which is a cheap side result.

### Gaps
- I did not verify a published, side-by-side Spider-dev EX vs TS table for DIN-SQL or DAIL-SQL from the primary papers; the search snippets were inconclusive. Compute the gap ourselves from the files above rather than quoting it.
- Licences for the ESM+ prediction files and the OmniSQL Drive bundle are unstated. They are probably fine for research re-scoring with attribution, but cite them as "public prediction files".
- The DAIL-SQL and DIN-SQL GitHub repos were not checked directly for their own prediction files. ESM+ says it took them from those repos.

---

## Q3. Running open small models (Qwen2.5-Coder, OmniSQL, Arctic, XiYan) or Command A on our synthetic set: feasibility on one L4

### Takeaway
All the candidate 7B models are Apache-2.0 on HF and are text-to-SQL specialists with strong public numbers. A 4–5 model sweep of our synthetic test set with vLLM on one L4 is plausibly 1–3 GPU-hours, about $1–2 at $0.74/h. It would show that lucky passes are not a Tiny Aya or Command A artifact.

### Cited Findings
HF licences, checked through the HF model API:

| Model | Licence |
|---|---|
| `Snowflake/Arctic-Text2SQL-R1-7B` | apache-2.0 |
| `seeklhy/OmniSQL-7B` | apache-2.0 |
| `Qwen/Qwen2.5-Coder-1.5B-Instruct` | apache-2.0 |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | apache-2.0 |
| `Qwen/Qwen2.5-Coder-3B-Instruct` | "other" (not Apache) |
| `XGenerationLab/XiYanSQL-QwenCoder-3B-2504` | apache-2.0 |
| `XGenerationLab/XiYanSQL-QwenCoder-7B-2504` | apache-2.0 |
| `NovaSky-AI/SkyRL-SQL-7B` | no licence field returned |

  — [HF Hub API](https://huggingface.co/api/models/Snowflake/Arctic-Text2SQL-R1-7B)
- **Arctic-Text2SQL-R1-7B** starts from Qwen2.5-Coder / OmniSQL checkpoints. Its execution accuracy:

  | BIRD-dev | Spider-test | Spider2.0-SQLite | Spider-DK | EHRSQL | ScienceBenchmark | Average |
  |---|---|---|---|---|---|---|
  | 68.9 | 88.8 | 15.6 | 81.5 | 36.7 | 51.8 | 57.2 |

  Code is at `snowflakedb/ArcticTraining`. — [Arctic-Text2SQL-R1, arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2)
- **OmniSQL** comes in 7B, 14B and 32B sizes. Its README shows a vLLM example with `seeklhy/OmniSQL-7B`, greedy decoding (temperature 0, max_tokens 2048) and a Transformers alternative. — [OmniSQL README](https://github.com/RUCKBReasoning/OmniSQL)
- **SkyRL-SQL-7B** is a multi-turn RL model trained on about 600 examples. It reports an average +7.2% EX over its base model, up to +9.2% on specific benchmarks. — [secondary blog summary](https://machinelearningatscale.substack.com/p/text-to-sql-just-got-a-lot-better) (not verified against the primary source)

### Inferences
These are estimates, not measured:
- **Memory.** A 7B model in bf16 needs about 15 GB of weights, which fits the L4's 24 GB with room for KV cache. 1.5B and 3B models are trivial.
- **Time.** With vLLM offline batching, a few thousand prompts × 8 samples × about 300 output tokens should take tens of minutes per 7B model on an L4.
- **Cost.** Four models (Qwen2.5-Coder-7B, OmniSQL-7B, Arctic-R1-7B, XiYan-7B) plus 1.5B should fit in about 2–3 VM hours, or $1.5–2.2.
- **Prompting.** Use each model's own prompt format; OmniSQL's prompt template is in its repo. Score with our existing harness (single-DB vs all copies).
- **Metrics.** Report three numbers per model: verified accuracy, single-DB accuracy and lucky-pass share. The key slide is "even the strongest open SQL specialists get X% lucky passes on fan-out or join templates".
- **Command A** is already done, so re-use it as the API baseline row.
- **VM.** Stop the VM straight after the runs, per team rule.

### Gaps
- I found no published L4 vLLM throughput numbers for these models. Benchmark a 50-prompt run first and extrapolate.
- SkyRL-SQL-7B's licence was not returned by the HF API.

---

## Q4. Test-time use: best-of-n with counterfactual copies, and related execution-reranking numbers

### Takeaway
Gold-free multi-DB agreement is the right test-time framing. Run all n samples on the original DB plus the copies, cluster samples by their **vector** of results across DBs, and pick the largest cluster. This is MBR-exec or self-consistency over richer inputs. LEVER shows that single-DB execution voting barely helps SQL (75.3 → 75.2), while a learned verifier reaches 81.9. Distinguishing inputs is the missing ingredient, and that is what our copies provide.

### Cited Findings
- **LEVER (ICML 2023), Codex code-davinci-002, Spider dev EX.**

  | Method | Spider dev EX |
  |---|---|
  | Greedy | 75.3 |
  | MBR-Exec | 75.2 |
  | Coder-Reviewer | 74.5 |
  | EP+ML | 77.3 |
  | **LEVER** | **81.9 ± 0.1** |

  Samples per question: 20 at train and 50 at test. LEVER also improves InCoder by +13.2% and CodeGen by +20.6% on Spider. — [LEVER, arXiv 2302.08468](https://ar5iv.labs.arxiv.org/html/2302.08468); InCoder/CodeGen figures from [summary](https://liner.com/review/lever-learning-to-verify-languagetocode-generation-with-execution)
- A LEVER summary notes that execution-result aggregation "has limited benefit for SQL datasets" compared with Python-output tasks. — [Emergent Mind summary of 2302.08468](https://www.emergentmind.com/papers/2302.08468)
- OmniSQL and Arctic ship majority voting (self-consistency) by execution result: `major_voting` in `evaluate_bird.py`, and `self_consistency.py` in `projects/arctic_text2sql_r1/bird_eval/`. — [OmniSQL evaluate_bird.py](https://raw.githubusercontent.com/RUCKBReasoning/OmniSQL/main/train_and_evaluate/evaluate_bird.py), [ArcticTraining tree](https://github.com/snowflakedb/ArcticTraining/tree/main/projects/arctic_text2sql_r1)
- No CodeT numbers on Spider appear in LEVER. CodeT is not a LEVER baseline. — [LEVER](https://ar5iv.labs.arxiv.org/html/2302.08468)

### Inferences
- **Selection rules.** With our 8 samples per item per model, already scored on all DBs, compare:
  1. first sample (greedy proxy);
  2. majority vote on the original DB (MBR-exec / self-consistency);
  3. **majority vote on the result vector over original DB + copies** (gold-free);
  4. oracle pass@8.

  Report verified accuracy for each rule, plus the share of picked samples that are lucky passes.
- **Expected result.** Rule 2 sometimes picks a lucky-pass cluster, because many wrong queries coincide on one DB. Rule 3 splits those clusters apart. That gives a clean "verifier is useful at inference too, without gold" story.
- **Honesty point.** Our audit verifier compares against gold SQL on each copy, so it is a training-time and eval-time reward. Only rule 3 is legitimate at test time. Say this explicitly.
- **Real-benchmark replay.** The same rule-3 experiment runs on Spider dev using OmniSQL's sampled `pred_sqls` from the Drive bundle, with the Zhong test-suite DBs standing in as copies. That costs $0 and puts the test-time result on a real benchmark too.

### Gaps
- No MBR-exec numbers for open 7B SQL models were found. Our numbers would be new.
- I did not verify how many samples per question the OmniSQL sampling files contain.

---

## Q5. Open text-to-SQL RL reward implementations we can audit with our mutants

### Takeaway
The SkyRL-SQL reward (Apache-2.0, `skyrl-gym`) is a short, importable function. It pays 1.0 when a **frozenset** of predicted rows equals the gold rows on a **single DB**. That makes it an ideal second audit target after AgentTune: order-blind, duplicate-blind, single-DB, and the agent can query the very DB it is scored on during multi-turn exploration. Arctic-R1's reward is also single-execution EX (1 / 0.1 / 0), and OmniSQL's evaluator is set-based.

### Cited Findings
- **SkyRL** (`NovaSky-AI/SkyRL`, Apache-2.0), file `skyrl-gym/skyrl_gym/envs/sql/utils.py`, function `calculate_reward_single(completion, reference, db_file, timeout=30)`:
  - Returns −1.0 when the format check fails (`<think>` / `<solution>` tags).
  - Otherwise executes the predicted and gold SQL on the same `db_file`. Each runs inside `BEGIN TRANSACTION` and is then rolled back.
  - Collects rows as `frozenset(cur.fetchall())`.
  - Returns 1.0 if `pred_results == gt_results`, else 0.0. Rows are compared as a set, so order and duplicates are ignored.
  - The entry point is `compute_score_single(completion, reference, db_file)`.
  - In `env.py`, the reward is computed only at the end, on the concatenated chat history. Intermediate exploratory SQL tool calls get 0 reward, and the episode ends when `<solution>` appears or max turns is reached. — [SkyRL sql/utils.py](https://github.com/NovaSky-AI/SkyRL/blob/main/skyrl-gym/skyrl_gym/envs/sql/utils.py), [SkyRL sql/env.py](https://github.com/NovaSky-AI/SkyRL/blob/main/skyrl-gym/skyrl_gym/envs/sql/env.py)
- **SkyRL training recipes** live in `examples/train/text_to_sql/` (`run_skyrl_sql.sh`, FSDP and Megatron variants) and `docs/content/docs/recipes/skyrl-sql.mdx`. — [SkyRL repo tree](https://github.com/NovaSky-AI/SkyRL)
- **Arctic-Text2SQL-R1 reward:** 1 if execution results "exactly align with ground truth", 0.1 if the SQL is syntactically correct and executable, and 0 otherwise. Results are compared "using the strictest available criteria (e.g. BIRD benchmark guidelines)".
  - Training data: BIRD train (8,017 filtered), Spider train (6,972) and dev (985), and Gretel-Synth (11,811).
  - The 0.1 executability bonus pays any runnable query. — [arXiv 2505.20315v2](https://arxiv.org/html/2505.20315v2)
  - The BIRD evaluation code is at `snowflakedb/ArcticTraining/projects/arctic_text2sql_r1/bird_eval/`. — [ArcticTraining](https://github.com/snowflakedb/ArcticTraining/tree/main/projects/arctic_text2sql_r1)
- **Reasoning-SQL** replaces pure EX with partial rewards: LLM-as-judge, syntax check, schema linking and n-gram similarity. — [arXiv 2503.23157](https://arxiv.org/html/2503.23157v2)
- **ReEx-SQL** uses a five-part reward: format, execution, exact match, entity match and exploration. — [arXiv 2505.12768](https://arxiv.org/html/2505.12768v1)
- Kulkarni & Srikumar (2025) use execution-based GRPO rewards that penalise failures and reward correct answers. — [arXiv 2506.06093](https://arxiv.org/html/2506.06093v1)

### Inferences
- **Audit A (SkyRL, about 2 h, CPU only).**
  - `pip install` or vendor `skyrl_gym/envs/sql/utils.py` (Apache-2.0, so attribution is enough).
  - Wrap each of our gold-mutants and hack queries in `<think>x</think><solution>SQL</solution>`.
  - Call `compute_score_single(..., gold_sql, original_db)` and report the % paid.
  - Then wrap the same function as `min` over our copies and report again.
  - This reproduces the AgentTune result on a second, widely used, actively maintained RL stack.
- **Comparator side finding.** Because SkyRL and OmniSQL compare `frozenset`s, mutants that drop `ORDER BY`, drop `DISTINCT` or duplicate rows are paid on **every** DB. Counterfactual copies cannot fix that; only a stricter comparator can (multiset, plus ordered when gold has ORDER BY). The two orthogonal holes are the DB-side hole (our copies) and the comparator hole. Report both and quantify each on our mutants. That makes the PS #9 (reward-hacking defences) story more complete.
- **Multi-turn observation hack (SkyRL).** The agent can run exploratory SQL against the same DB it is rewarded on, see the answer, and emit a literal `SELECT 'x' UNION ...`. The single-DB reward pays it, while counterfactual copies (answer-changing) would reject it. Our existing "hack queries" category probably already covers literal answers; label that row "observable-answer hack (reachable in SkyRL-style multi-turn envs)".
- **Arctic.** The 0.1 executability bonus means any runnable query earns 10% of max reward. That is a minor hack surface: show the expected reward of a trivial `SELECT 1`-style policy under it. The core EX reward is the same single-DB check, so the Audit A numbers transfer qualitatively. Phrase this as inference, since Arctic's reward source code was not located.

### Gaps
- I did not find the exact Arctic-R1 reward source file in ArcticTraining (only `bird_eval/`). It is possibly in a verl fork, which I did not verify.
- verl, OpenRLHF and TRL text-to-SQL reward examples were not checked within the call budget.

---

## Q6. Anything else cheap that strengthens the claim, and the overall ranked shortlist

### Takeaway
NL2SQL-BUGs gives a human-annotated corpus of real buggy SQL, as distinct from our code-generated mutants. A second training seed and a DB-size invisibility curve are cheap robustness items. They rank below the real-benchmark and real-reward audits.

### Cited Findings
- **NL2SQL-BUGs** (HKUST-GZ, arXiv 2503.11984) has 2,018 expert-annotated instances, each with an NL question, schema, SQL and error annotations. Its taxonomy has 9 main categories and 31 subcategories, and LLMs average 75.16% detection accuracy. The project page is nl2sql-bugs.github.io. — [arXiv 2503.11984](https://arxiv.org/abs/2503.11984), [project page mirror](https://scriptagc.wasmer.app/https_nl2sql-bugs_github_io)
- Test-suite accuracy remains the Spider standard: OmniSQL reports TS on Spider dev, Syn and Realistic. — [OmniSQL README](https://github.com/RUCKBReasoning/OmniSQL)

### Inferences — ranked shortlist
Ranked by payoff per hour for judges. All costs are estimates.

| # | Experiment | Data and tools | Steps | Time | Cost | Judge payoff |
|---|---|---|---|---|---|---|
| 1 | **Real-model lucky-pass rate on Spider dev** | Spider dev + Zhong test-suite DBs (Apache-2.0); prediction files from ESM+ (9 systems incl. GPT-4 Turbo, Claude 3 Opus, DAIL, DIN, C3) and the OmniSQL Drive bundle (7B/14B/32B) | Download; normalise to `SQL\tdb_id` / one-per-line; run `evaluation.py --etype exec` against (a) original DBs, (b) test-suite DBs; compute EX, TS, lucky-pass share per system; bar chart | 2–3 h | $0 (CPU) | **Highest.** Directly answers "real benchmark / real models", and gives a per-system "X% of EX passes are lucky" chart |
| 2 | **Audit SkyRL-SQL's reward with our mutants and hacks** | `skyrl_gym/envs/sql/utils.py` (Apache-2.0) | Import `compute_score_single`; score gold-mutants and hack queries on the original DB vs min over copies; add a multiset/ordered comparator ablation | 2 h | $0 | High: a second public RL stack and a new comparator-hole finding (PS #9) |
| 3 | **Gold-free multi-DB self-consistency (best-of-n)** | Our 8 samples/item (have); OmniSQL sampled `pred_sqls` on Spider dev + test-suite DBs | Compare the 4 selection rules from Q4; report accuracy and lucky-pass share of picks; cite LEVER's MBR-exec 75.2 vs greedy 75.3 | 2–3 h | $0 | High: shows the method is useful at inference, not just as a reward |
| 4 | **Open SQL specialists on our synthetic set** | vLLM on L4: Qwen2.5-Coder-7B/1.5B, OmniSQL-7B, Arctic-R1-7B, XiYan-7B (all Apache-2.0) | Benchmark 50 prompts, then the full run with n=8; score with the existing harness; stop the VM | 2–3 h wall, about 2–3 GPU-h | about $1.5–2.2 | Medium-high: shows lucky passes across model families, including RL-trained SQL models |
| 5 | **NL2SQL-BUGs: human-written buggy SQL** | NL2SQL-BUGs 2,018 instances (licence and underlying DBs unverified) | Take the instances labelled erroneous; check what share pass single-DB EX vs gold, and what share our generic copies (or the test suite, if Spider-based) reject | 2–4 h | $0 | Medium: answers "your bugs are synthetic" with human-annotated bugs |
| 6 | **BIRD mini-dev counterfactual copies via generic operators** | BIRD dev DBs; our generator adapted (row dup/delete, NULLs, ties, threshold shifts on gold-touched columns) | Implement operators; validate 0 false rejects of gold; score OmniSQL BIRD-dev predictions | 4–6 h | $0 | Medium but risky: a second real benchmark, but the most engineering |
| 7 | **Second seed and DB-size invisibility curve** | Existing pipeline | Re-run one audit with a new seed; sweep DB rows (e.g. 10/100/1k/10k) and plot the single-DB pay-rate of buggy mutants | 1–2 h | ≤ $0.5 | Low-medium: robustness polish; the size curve pre-empts "BIRD has big DBs, so FP is rare" (the CodeS argument) |

- **Suggested day plan:** items 1 + 2 in the morning; 3 + 4 in the afternoon, with the VM running only for 4; 7 if time remains. Items 5 and 6 only if 1–4 land early.
- **Framing for the write-up:**
  - "Single-DB execution rewards pay lucky passes on real benchmarks: Spider dev, N public systems, X–Y%."
  - "A widely used open RL reward (SkyRL-SQL) pays our mutants at Z% and our copies cut this to W%."
  - "The same copies give gold-free best-of-n gains."
  Each claim is backed by a third-party artefact the judges can verify.

### Gaps
- The NL2SQL-BUGs dataset licence and which DBs it is built on (Spider or BIRD) were not verified. Check the project page before committing to item 5.
- I found no published "invisibility vs DB size" curve; it would be new.
- I did not check whether the ESM+ prediction files' line counts align with the official Spider dev (1,034 questions).
