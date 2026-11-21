# Baselines, comparison rewards and adversarial evaluations for a counterfactual-database text-to-SQL reward

Scope: what a reviewer will expect next to our reward (final SQL run on the original DB plus hidden counterfactual copies, paid only if every result matches), and how to run each item cheaply. Today is 2026-11-21 and the paper is due 2026-11-30. Each item is tagged **[before deadline]** or **[later]**. No paid API was called while researching this. Prices come from public pages; see the caveats below.

Audit pool we already have: 1,814 mutants (13 types), 2,839 constructed hacks and 2,847 correct queries, about 7,500 candidate SQLs over 1,302 items. Test set: 331 items. Policy: Tiny Aya Global 3.35B.

---

## Q1. Which reward baselines should go into the audit table?

### Takeaway
The cheapest high-value additions are (a) one larger single database and (b) a Zhong-style distilled test-suite reward. Both are pure CPU work on the generator and harness we already have, and both answer the obvious question "isn't this just more or bigger test data?". The next tier is an LLM-as-judge reward with an Amazon Nova model, which costs single-digit dollars on the full audit and has a documented hacking literature, and a formal checker run on the subset it supports. Dense rewards (SQL-R1, Reasoning-SQL) matter mainly for the training study, not the audit.

### Ranked list (what to do, how, cost, and what would strengthen or weaken the paper)

1. **Single larger DB, e.g. 500 and 5,000 customers (same generator, one DB, strict multiset match)** [before deadline]
   - How: regenerate each item's original DB at 10x and 100x scale, then score all ~7,500 audit SQLs. Report false-positive rate (FPR) on mutants and hacks and false-negative rate (FNR) on correct queries.
   - Cost: CPU only, minutes to a few hours with SQLite. No GPU and no API.
   - Strengthens: the larger DB still passes structural mutants (for example a wrong join or filter that agrees on the data) or constructed hacks, while copies of the *same total size* catch them. That shows the gain comes from counterfactual structure, not volume.
   - Weakens: a 5,000-row single DB matches our FPR. Then the claim narrows to "the same detection at lower cost / smaller DBs".
   - Note: also report a compute-matched variant (total rows across the original plus k copies equals the size of the large DB).

2. **Zhong-style distilled test-suite reward** [before deadline]
   - What it is: Zhong, Yu and Klein (EMNLP 2020) fuzz many random DBs (1,000 for Spider) and *distill* a small suite with high code coverage for the gold query. Test-suite accuracy approximates "same denotation on every DB" — [ACL Anthology](https://aclanthology.org/2020.emnlp-main.29); [arXiv 2010.02840](https://arxiv.org/abs/2010.02840v1). They found the standard Spider metric has a 2.5% average false-negative rate (8.1% worst case), and they manually verified their method on 100 examples — [ACL Anthology](https://aclanthology.org/2020.emnlp-main.29). Code and suites for 11 datasets: github.com/ruiqi-zhong/TestSuiteEval — [ACL Anthology](https://aclanthology.org/2020.emnlp-main.29).
   - How: generate N random DBs per item with our generator (N around 100 to 1,000), keep the DBs that distinguish gold from neighbour queries, and use the distilled suite as the reward.
   - Cost: CPU, hours.
   - Why reviewers will ask: this is the closest prior work, and our "informed copies" are conceptually a distilled suite. The paper has to say exactly what differs: hidden from the policy and used *as an RL reward under optimisation pressure*, rather than as an offline metric. Running it as a baseline turns that framing into a measurement.
   - Strengthens: equal or better FPR from fewer DBs, or test-suite rewards being gamed in training while ours is not.
   - Weakens: test-suite accuracy matches us at equal DB count. Then the contribution becomes "test suites as RL rewards plus a hiding protocol", which is still publishable but has to be framed honestly.

3. **LLM-as-judge reward (and execution plus LLM hybrid)** [before deadline if one Nova model; later for the full model sweep]
   - Evidence that LLM judges are hackable: "One Token to Fool LLM-as-a-Judge" (Zhao et al., arXiv 2507.08794, NeurIPS 2025). "Master key" inputs such as non-word symbols (":" or ".") or generic reasoning openers consistently produce false-positive rewards. The effect holds across models including GPT-o1 and Claude-4. The authors release a hardened "Master-RM" on Hugging Face — [arXiv](https://arxiv.org/abs/2507.08794); [NeurIPS listing](https://neurips.cc/virtual/2025/131135). A reported FPR of up to 90% comes only from a Medium commentary — [Medium](https://medium.com/about-ai/master-key-tokens-the-hidden-flaw-in-llm-based-reward-models-0c66d5844a11) — so check Table 1 of the paper before quoting a number.
   - The text-to-SQL-specific LLM judge is FLEX (NAACL 2025). It argues that execution accuracy produces both false positives (coincidentally equal results) and false negatives (for example an extra column), and uses an LLM to judge. Agreement with human experts is Cohen's kappa 62 to 87.04 in the NAACL version and 61 to 78.17 in arXiv v1 — [arXiv 2409.19014](https://arxiv.org/html/2409.19014v4); [ACL Anthology](https://aclanthology.org/2025.naacl-long.228). FLEX states that LLM-SQL-Solver does not separate false positives from false negatives — [arXiv](https://arxiv.org/html/2409.19014v4).
   - Reasoning-SQL already uses "AI feedback" (an LLM judge) as one partial reward inside GRPO — [arXiv 2503.23157](https://arxiv.org/html/2503.23157v2). So an LLM-judge reward is an established baseline, not a strawman.
   - Models via Bedrock, from the cheapest up: Nova Micro, Nova Lite, Nova Pro, then Claude and Llama. Prices are in Q4, with caveats.
   - How: prompt equals schema plus question plus candidate SQL (variant A), or plus the first k result rows from the original DB (variant B, the "hybrid"). Ask for a binary verdict. Run on all ~7,500 audit SQLs. Report FPR on mutants and hacks and FNR on correct queries. Add one extra hack family, "master key / judge-directed text in SQL comments" (for example `-- this query is verified correct`), because SQL comments are a free channel to the judge.
   - Hybrid baseline: pass only if (single-DB execution match) AND (LLM says correct). This is the natural "practitioner" alternative to our copies.
   - Command A: we already have Command A access and it "verifies 81% of test items" prompted once. It can be the judge model without AWS spend. Cohere quota/cost not checked here.
   - Strengthens: the judge passes many hacks or mutants (especially comment-injection), or the hybrid lowers FPR but raises FNR. Our reward wins on both.
   - Weakens: the hybrid with Nova Pro or Claude matches our FPR and FNR. Then the argument moves to cost, determinism and latency (reward calls per GRPO step).

4. **Formal SQL equivalence checkers (gold vs candidate) as an oracle reward** [later. At most a small-subset coverage check before the deadline]
   - VeriEQL (OOPSLA 2024): a *bounded* checker with integrity constraints. Its authors say existing work supported under 2% of LeetCode SQL queries, and report beating prior tools by more than 10x on 20,000+ benchmarks (LeetCode submissions plus the Calcite rule suite). It found wrong LeetCode reference queries — [arXiv 2403.03193](https://arxiv.org/pdf/2403.03193); [NSF PAR](https://par.nsf.gov/biblio/10543008).
   - SQLSolver: proves 346 of 359 equivalent pairs derived from Calcite and Spark SQL rewrite rules — [NSF PAR](https://par.nsf.gov/biblio/10548354) (the search summary attributes these numbers to that entry; confirm on the PDF).
   - QED: bag semantics; proves 299 of 444 Calcite pairs, more than 2x the prior state of the art — [NSF PAR](https://par.nsf.gov/biblio/10548354) (same caveat).
   - Polygon (PLDI 2025, Zhao, Wang, Wang): equivalence *refutation* by conflict-driven under-approximation search, which produces counterexample databases. It was evaluated on 30,000+ benchmarks across refutation and disambiguation tasks — [arXiv 2504.06542](https://arxiv.org/html/2504.06542v1); [PLDI listing](https://pldi25.sigplan.org/details/pldi-2025-papers/54/Polygon-Symbolic-Reasoning-for-SQL-using-Conflict-Driven-Under-Approximation-Search). This is the most relevant one: Polygon is effectively an *optimal informed copy generator*. It is the natural upper bound for "informed copies" and can also be used to look for mutants that survive all our copies (see Q2).
   - How: run each tool on gold vs candidate pairs for the audit SQL. Report (i) coverage (the share of pairs the tool accepts) and (ii) agreement with our labels on the covered pairs.
   - Cost: CPU. The time cost is installation and SQL-dialect translation (SQLite vs the tool's grammar).
   - Strengthens: low coverage on realistic queries (window functions, LIMIT/ORDER BY, string functions, NULL handling), so checkers cannot serve as a general RL reward. Where they do cover, they agree with us.
   - Weakens: Polygon finds counterexamples for many SQLs that our reward accepts. That is a real false-positive rate we must report, though it is also an honest "upper bound" row.

5. **Dense / partial-credit rewards (SQL-R1, Reasoning-SQL, Arctic)** [audit row before deadline because it is cheap; training comparison later]
   - SQL-R1: format + executability + result-correctness + length reward — [survey arXiv 2611.00171](https://arxiv.org/pdf/2611.00171); [PaVeRL-SQL](https://arxiv.org/html/2509.07159v1).
   - Reasoning-SQL (Pourreza et al., Google): partial rewards for schema linking, AI feedback, n-gram similarity and syntax, combined with GRPO — [arXiv 2503.23157](https://arxiv.org/html/2503.23157v2); [Google Research](https://research.google/pubs/reasoning-sql-reinforcement-learning-with-partial-rewards-for-reasoning-enhanced-text-to-sql/).
   - Arctic-Text2SQL-R1 (Snowflake, Findings ACL 2026): only execution correctness plus syntax validity. The authors say finer-grained rewards "often backfired", encouraging "lazy" behaviours — [arXiv 2505.20315](https://arxiv.org/abs/2505.20315v2); [Snowflake blog](https://www.snowflake.com/en/blog/engineering/arctic-text2sql-r1-sql-generation-benchmark/); [HF card](https://huggingface.co/Snowflake/Arctic-Text2SQL-R1-7B). This is independent support for our thesis that reward shaping invites hacking. Cite it.
   - How: implement the n-gram, schema-linking and syntax terms (each a few lines of Python), score the audit pool, and report the mean reward that hacks and mutants get relative to correct SQL.
   - Strengthens: partial rewards give high credit to hard-coded or literal hacks (schema terms and n-gram overlap are trivially satisfied).

### Inferences
- Rough LLM-judge cost on the full audit: ~7,500 calls × ~1,500 input + ~100 output tokens ≈ 11.3M input + 0.75M output tokens. With third-party list prices (Q4), that is about $0.5 for Nova Micro, about $0.9 for Nova Lite and about $11 for Nova Pro, roughly halved with batch inference. Token counts are our assumption; prices are unverified on the AWS page.
- The 7,500-SQL audit with every CPU-only row (1, 2, 5) fits in one to two days. A single Nova Lite judge row (3) adds about one day including prompt work.
- Our "blind vs informed copies" axis maps onto "random DBs vs distilled test suite vs Polygon counterexample". Presenting all three as one spectrum reads as rigorous.

### Gaps
- Official Bedrock per-token prices for Nova did not render on aws.amazon.com/bedrock/pricing or aws.amazon.com/nova/pricing (dynamic tables). Confirm in the console before quoting them.
- Code availability: the VeriEQL VLDB 2024 demo paper points to a repo at github.com/whatsmyname/VeriEQL-demo — [VLDB 2024 demo PDF](https://web.eecs.umich.edu/~xwangsd/pubs/vldb24demo.pdf) (per search summary; repo not opened). I found no confirmed public repos for Polygon, SQLSolver or QED. Licences and supported SQL grammars are unverified.
- Unread lead: "Efficient Dialect-Agnostic SQL Equivalence Refutation" (arXiv 2610.22442, Oct 2026) — [arXiv](https://arxiv.org/pdf/2610.22442). It may suit SQLite better than the Calcite-grammar tools. Read it before choosing a checker.
- I did not find a published FPR for LLM judges specifically on *SQL hacks* (literal answers, hard-coded IDs). That number would be new, and ours to produce.

---

## Q2. Adaptive attacks: how do we red-team our own reward properly?

### Takeaway
Adaptive-attack norms are explicit. A defence is only as credible as the strongest attack that *targets its specific mechanism*. Fixed attack sets (our 13 mutant types plus constructed hacks) are a non-adaptive evaluation and will be called that. The minimum credible package is an attacker that knows the copy generator, plus at least one optimisation-based attack (GRPO against the reward), plus a held-out bug family.

### Cited Findings
- Tramer, Carlini, Brendel and Madry, "On Adaptive Attacks to Adversarial Example Defenses" (NeurIPS 2020): stronger adaptive attacks broke 13 defenses. Adaptive attacks cannot be automated and need tuning to the specific defense. Target the few components that matter most. Design the attack loss carefully. Do not reuse a previous paper's "adaptive" attack without adapting it — [arXiv 2002.08347](https://arxiv.org/abs/2002.08347v2); [NeurIPS](https://papers.nips.cc/paper/2020/hash/11f38f8ecd71867b42433548d1078e38-Abstract.html).
- Nasr, Carlini et al., "The Attacker Moves Second" (arXiv 2510.09023, USENIX Security '26): tuned and scaled gradient descent, RL, random search and human red-teaming bypassed 12 recent LLM defenses. Most had attack success above 90% against originally reported near-zero rates. Human red-teaming beat all of them. Defenses should be tested against adaptive attackers who spend significant compute — [arXiv](https://arxiv.org/abs/2510.09023v1); [USENIX](https://www.usenix.org/conference/usenixsecurity26/presentation/nasr).
- Arctic-Text2SQL-R1 reports policies drifting into "lazy" reward-exploiting behaviours under fine-grained rewards. That is direct evidence that GRPO itself acts as an adaptive attacker on SQL rewards — [Snowflake blog](https://www.snowflake.com/en/blog/engineering/arctic-text2sql-r1-sql-generation-benchmark/).
- Master-key attacks on LLM judges can be *generated automatically* (embedding search over a 1.5M-sentence corpus), so a fixed list understates the attack surface — [SoK arXiv 2603.29403](https://arxiv.org/pdf/2603.29403) (per search summary; not opened).

### Ranked attack evaluations
1. **White-box attacker LLM that knows the copy generator** [before deadline]
   - Give a strong model (Command A, already available) the generator source or a description, the schema, the original DB and the gold result. Task: "write SQL that returns the gold result on the original DB but is not semantically equal to gold", and "write SQL that would pass all counterfactual copies without solving the task". Use k attempts per item with execution feedback on the *original DB only*. This is the realistic channel: the policy sees the original DB, not the copies.
   - Report attack success = passes our reward AND is judged wrong (wrong by Polygon or by manual check on a sample).
   - Cost: ~331 to 1,302 items × k=5 calls on Command A. Hours.
   - Strengthens: success is near 0 with blind copies and only rises when the attacker is *also* shown the copies (an informed attacker gives an upper bound).
   - Weakens: the attacker finds a generic trick, for example exploiting which columns the generator never perturbs. That is still useful: report it and patch the generator.
2. **GRPO against the reward on a deliberately exploitable environment** [before deadline only if a run fits on sqlcf-l4; otherwise later]
   - Plant an exploit (for example a dataset where gold results are guessable or IDs are constant across the original DB) and train Tiny Aya with (i) single-DB match, (ii) set match, (iii) our reward. Show the hack rate over steps.
   - This is the "attacker moves second with RL" condition, and it is the most persuasive item for an RL venue.
   - Strengthens: the single-DB reward is hacked within N steps and ours is not.
   - Weakens: ours is hacked too (report it as the scope limit).
3. **Held-out bug families not in our 13 types** [before deadline, cheap]
   - Hold out entire mutation families at design time, or add new ones: NULL-semantics bugs (`=` vs `IS`, `COUNT(col)` vs `COUNT(*)`), off-by-one in LIMIT/OFFSET, ORDER BY tie-breaking, date-boundary predicates, DISTINCT dropped under joins, integer-division and rounding, case-sensitive LIKE, and correlated vs uncorrelated subquery.
   - This tests whether the copy generator generalises beyond the bugs it was implicitly designed for.
4. **Counterexample search for surviving mutants (Polygon or fuzzing)** [later]
   - For SQLs our reward accepts, search for any DB on which they differ from gold. Each counterexample found is a measured false positive. Fuzzing with our own generator at high N is the cheap version.
5. **Human red-team, 1 to 2 hours per team member** [before deadline]
   - "The Attacker Moves Second" found human red-teaming succeeded against every defense. A short, documented human session (with the number of attempts and successes) is cheap and pre-empts the criticism.

### Inferences
- What a fair evaluation needs, mapped onto our setting: (1) state the threat model (what the policy sees: original DB, schema, question; never copies or generator seed); (2) attack the specific mechanism, meaning the generator's perturbation distribution; (3) include an optimisation-based attacker (GRPO itself); (4) report the attacker's compute and number of attempts; (5) release the attack code; (6) report the informed-attacker upper bound honestly.
- The "blind copies" condition only helps if the copies stay hidden. The paper should state that leaking copy contents or the generator seed through the reward signal is the main residual risk, and measure it with the informed-attacker row.

### Gaps
- I found no published adaptive-attack study on *execution-based* text-to-SQL rewards specifically. That supports a novelty claim, but I could not confirm it exhaustively.

---

## Q3. Policy baselines for the training study

### Takeaway
Prompted, untrained evaluation of 3B to 7B open text-to-SQL models on the 331-item test set and on Spider dev is cheap on the L4 with vLLM and should be done before the deadline. OmniSQL-7B and Arctic-Text2SQL-R1-7B are the strongest public reference points. Re-training other policies with our reward is "later".

### Cited Findings
- Arctic-Text2SQL-R1 comes in 7B, 14B and 32B and uses GRPO with execution plus syntax rewards. 32B reaches 71.83% EX on BIRD and 14B 70.04% — [Snowflake blog](https://www.snowflake.com/en/blog/engineering/arctic-text2sql-r1-sql-generation-benchmark/); [HF Snowflake/Arctic-Text2SQL-R1-7B](https://huggingface.co/Snowflake/Arctic-Text2SQL-R1-7B).
- OmniSQL comes in 7B, 14B and 32B, trained on SynSQL-2.5M plus the Spider and BIRD train sets. Spider dev is reported with *test-suite accuracy*, other sets with EX, using greedy and maj@8 decoding without schema linking or revision — [HF seeklhy/OmniSQL-7B](https://huggingface.co/seeklhy/OmniSQL-7B); [arXiv 2503.02240](https://arxiv.org/html/2503.02240v2). The paper notes Qwen2.5-Coder-7B-Instruct fine-tuned on Spider and BIRD drops to 43.8% and 31.4% EX on out-of-domain ScienceBenchmark and EHRSQL — [arXiv](https://arxiv.org/html/2503.02240v2).
- The OmniSQL card's exact numbers did not render. Pull them from the paper tables.

### Ranked list
1. **Prompted references on the 331-item test set and Spider dev (all scored with every reward in Q1)** [before deadline]
   - Models: Qwen2.5-Coder-3B-Instruct (size-matched to Tiny Aya 3.35B), Llama-3.2-3B-Instruct (size-matched, general), OmniSQL-7B and Arctic-Text2SQL-R1-7B (specialist ceilings), plus Qwen2.5-Coder-7B-Instruct. Add Qwen3 small models only if time allows.
   - How: vLLM on the L4 (24 GB fits 7B in bf16), greedy decoding, the same prompt as our policy.
   - Cost: each model is roughly minutes for 331 items and about an hour for Spider dev (1,034 questions), mostly loading and engine startup.
   - Key metric: the *gap between single-DB EX and our reward* per model. Specialist RL-trained models (Arctic, trained on execution reward) showing a larger gap would support "execution-only RL breeds coincidentally-correct SQL". A gap that does not appear is neutral to weakening.
   - Stop the VM after the runs (team rule).
2. **Amazon Nova as a prompted reference (Micro/Lite/Pro)** [before deadline if the team approves the spend; see Q4]
   - 331 items × ~2k tokens is about 0.7M tokens per model, so cents for Micro and Lite and under $1 for Pro at third-party list prices.
   - Spider dev is about 2M tokens per model. Still small.
3. **Re-train a second policy (Qwen2.5-Coder-3B) with single-DB vs our reward** [later]
   - This shows the result is not Tiny Aya-specific. A GPU-day-scale job.

### Inferences
- Size-matched 3B baselines are what reviewers check first. The 7B specialists are context, not competitors.
- Using Spider's own test-suite accuracy (Zhong) as an external metric on Spider dev ties Q1 and Q3 together.

### Gaps
- Exact Spider-dev and BIRD-dev numbers for OmniSQL-7B and Qwen2.5-Coder-3B/7B were not extracted. Read them from the OmniSQL paper tables.

---

## Q4. What does an Amazon audience care about, and can the audit test an AWS pipeline?

### Takeaway
AWS ships two production NL-to-SQL paths: Bedrock Knowledge Bases with a structured data store, and Amazon Q generative SQL in Redshift Query Editor v2. For neither did I find a public accuracy evaluation. The KB `GenerateQuery` API returns SQL without executing it. That makes it a clean target: our counterfactual audit could score an AWS-generated SQL stream directly. This is a strong symposium hook, but it needs a Redshift or SageMaker Lakehouse setup and spending, so it is "later" unless the team approves a tiny Redshift Serverless test.

### Cited Findings
- Bedrock Knowledge Bases connect to structured stores and convert natural-language questions to SQL. They are exposed through `Retrieve`, `RetrieveAndGenerate`, and a standalone **`GenerateQuery`** API that "converts natural language queries into SQL queries ... You can use this operation independently and insert it into your workflow" — [AWS docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-structured.html).
- Supported stores at launch were Amazon Redshift and SageMaker Lakehouse, with Redshift as the query engine — [AWS What's New, Dec 2024](https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-bedrock-knowledge-bases-structured-data-retrieval); [create KB docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-structured-create.html). There is an Aurora PostgreSQL path via zero-ETL — [AWS ML blog](https://aws.amazon.com/blogs/machine-learning/query-amazon-aurora-postgresql-using-amazon-bedrock-knowledge-bases-structured-data).
- Bedrock pricing: structured-data KB "is charged for each request to generate a SQL query". The rate was not visible in the fetched page — [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/). Batch inference for select models is 50% below on-demand — [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/).
- Amazon Q generative SQL (Redshift Query Editor v2) generates SQL from prompts and schema. Accuracy can be improved with query history and custom context (table and column descriptions, PK/FK, sample queries). AWS advises users to verify outputs. It launched in preview at re:Invent 2023 — [AWS docs](https://docs.aws.amazon.com/redshift/latest/mgmt/query-editor-v2-generative-ai.html); [AWS Big Data blog](https://aws.amazon.com/blogs/big-data/write-queries-faster-with-amazon-q-generative-sql-for-amazon-redshift). I found no published accuracy benchmark.
- Nova prices, per 1M tokens on-demand (**third-party aggregators, not the AWS page**): Micro $0.035 in / $0.14 out; Lite $0.06 / $0.24; Pro $0.80 / $3.20 — [developersdigest](https://www.developersdigest.tech/models/provider/amazon); [cloudprice](https://cloudprice.net/models/nova-micro); [anotherwrapper (Nova Pro, dated Aug 25 2026)](https://anotherwrapper.com/llm-pricing/nova-pro). The official Bedrock and Nova pricing tables did not render when fetched — [Nova pricing](https://aws.amazon.com/nova/pricing/).

### Ranked list for an Amazon audience
1. **Nova Micro/Lite/Pro as LLM-judge reward baselines and as prompted policies** [before deadline, with team sign-off on spend of roughly $1 to $15 total]
   - This is the most direct "Bedrock-relevant" row. Use the Bedrock Converse API, with Batch to halve cost.
2. **Framing paragraph: "verifying AWS-style NL2SQL output"** [before deadline, no cost]
   - Cite `GenerateQuery` and Amazon Q generative SQL. Argue that customers run unverified generated SQL against their own data, that AWS itself advises verification, and that counterfactual copies are a deployable verifier for this.
3. **Actually scoring `GenerateQuery` output with our audit** [later, for the 2027 presentation]
   - Load the 331 test DBs into Redshift Serverless, create a structured KB, call `GenerateQuery` per question, then execute on the original plus copies (in SQLite after dialect translation, or in Redshift).
   - Report the share of AWS SQL that passes single-DB EX but fails copies.
   - Strengthens: a non-zero coincidental-correctness rate on a production system is a memorable symposium result.
   - Risk: Redshift dialect differences, setup time and cost.

### Inferences
- An Amazon audience will value (i) Nova numbers, (ii) cost per reward call relative to an LLM judge, which is our likely win since execution on small SQLite copies is near-free and deterministic, and (iii) a path to verifying Bedrock KB / Q SQL output.

### Gaps
- Official per-request price for KB structured-data SQL generation: not found.
- Whether Amazon Q generative SQL is still preview, and its current regions: unclear (the docs mention three US regions in one localisation).
- No public AWS accuracy evaluation for either NL2SQL feature was found.
