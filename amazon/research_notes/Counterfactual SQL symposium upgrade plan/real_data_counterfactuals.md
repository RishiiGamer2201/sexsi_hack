# Counterfactual / distinguishing databases for real text-to-SQL benchmarks: tools, costs, and an experiment plan

Scope: how to move the counterfactual-database (CF) reward and audit from our single synthetic retail schema to Spider, BIRD, Spider 2.0 and others; what each option costs; and which subset to use for the 9-day pre-deadline run (deadline 2026-11-30) and for the longer run before the presentation. Research date: 2026-11-21. No paid compute was used.

## Q1. Which tools and papers generate distinguishing or test-suite databases for arbitrary schemas? Is the code public, and does it work on SQLite?

### Takeaway
There are three usable families. (a) Zhong et al. 2020 random fuzzing with neighbour-query distillation: Spider suites are released, the generator code is in a separate repo, and it is SQLite-native. (b) SMT bounded verification: SpotIt / SpotIt+ on VeriEQL, ICLR 2026. Code is public, it was run on all of BIRD dev and the Spider 2.0-lite SQLite subset, and it takes about 1–4 s per pair. (c) LLM- or plan-guided synthesis: SynSQL 2026 and ParSEval (PVLDB 2025). Their results are strong, but I could not confirm public code for either. XData and EvoSQL are older systems aimed at grading and SE testing. They are not practical for SQLite text-to-SQL inside 9 days.

### Cited Findings
**Zhong, Yu & Klein 2020 (EMNLP), distilled test suites**
- Method. For each gold query they generate "neighbour queries" by applying one edit at a time: replace a comparison operator, replace a numeric constant, replace a string constant, or drop a span. They then fuzz random databases and greedily keep any database that separates gold from a not-yet-distinguished neighbour. — [Zhong et al. 2020, arXiv 2010.02840](https://arxiv.org/abs/2010.02840) (PDF text read directly)
- Fuzzing distribution. Tables are generated in foreign-key order, and foreign-key columns are sampled from the parent column. Other numeric values are sampled uniformly from [-2^63, 2^63], strings come from a random-string distribution, and constants that appear in the gold query (e.g. 34, "Alice") are injected at random. — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- Scale on Spider dev: about 94 neighbours per gold query on average, and 1,000 random databases sampled per schema. Those 1,000 DBs separate more than 99% of neighbours. A single database fails to separate about 5%, and the curve flattens after about 600 DBs. — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- Output size: on average 42 databases are distilled per query for 1,034 Spider dev queries, giving 695 databases (3.27 GB) in total, shared per schema. — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- Headline number to cite. Checking only the originally released Spider DB ("single denotation accuracy") has a false-positive rate averaging 6.5% (std 1.0, max 9.0%) across 21 Spider dev submissions. By difficulty the mean is easy 3.6%, medium 5.9%, hard 8.0%, extra 11.0%; the extra-hard maximum is 17.6%. — [Zhong et al. 2020, Table 2](https://arxiv.org/abs/2010.02840)
- Known blind spots: neighbours that differ only in floating-point precision, and conditions that need an exact match (e.g. a row equal to exactly the average age) are missed. Gold-value insertion can loosen the metric, e.g. "=" vs "LIKE". — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- Stated requirements of the framework: (1) strongly typed inputs, so that a fuzzing distribution can be defined; (2) … (the remainder of the sentence was truncated in the extraction). — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- The official repo taoyds/test-suite-sql-eval (Apache-2.0) ships the evaluation code for Spider, SParC, CoSQL and 8 classical datasets. The databases are a separate download in SQLite format at `database/[db_id]/[db_id].sqlite`. The README warns that gold queries must not be changed, because the suites were generated from them. — [taoyds/test-suite-sql-eval](https://github.com/taoyds/test-suite-sql-eval)
- The generation code lives in "Ruiqi's repo" ruiqi-zhong/TestSuiteEval. It has `fuzz/`, `sql_util/`, `predictions/` and `database/` folders, a `demo.ipynb` showing the core functions, and an `ESMFalseNegatives.tsv`. The README says it will not be updated. I could not see a licence on the page. — [ruiqi-zhong/TestSuiteEval](https://github.com/ruiqi-zhong/TestSuiteEval)

**SpotIt (ICLR 2026) and SpotIt+ (2026): SMT bounded-equivalence counterexample databases**
- SpotIt is built on the VeriEQL bounded equivalence checker (Z3) with bound K=5. Each call gets 1 core, 8 GB RAM and a 600 s CPU timeout. They ran all 1,533 BIRD dev question–SQL pairs (11 DBs) for 10 systems, sending only pairs that already pass EX to SpotIt. — [SpotIt, arXiv 2510.26840v2](https://arxiv.org/html/2510.26840v2)
- Extensions added on top of VeriEQL: dates encoded as y/m/d integers, strings, strftime/JulianDay/date shift, SubStr, Concat, LIKE, prefix/suffix tests, casts, and set semantics. Not supported: window functions (RANK, LAG) and recursive CTEs. ORDER BY with LIMIT is imprecise and can produce spurious counterexamples. Degenerate empty-vs-NULL counterexamples are excluded. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- Coverage and speed on BIRD dev: 93.6–97.1% of EX-passing pairs are supported, at an average of 0.93–3.93 s per pair. 93.3–96.2% of counterexamples validated. — [SpotIt, coverage table](https://arxiv.org/html/2510.26840v2)
- Accuracy, EX-test → EX-SpotIt. Values are as extracted from the table by the fetch tool; the five rows below reproduce the stated 9.8–13.5 point drops:
  - csc-32b: 71.32 → 58.80
  - gena-2: 70.53 → 59.84
  - Alpha: 69.36 → 55.87
  - Chess: 63.62 → 52.87
  - slm: 63.43 → 51.37

  Overall drops are 9.8–13.5 points, or 10.2–14.3 for SpotIt+. The abstract's "11.3–14.2%" does not match the table. — [SpotIt](https://arxiv.org/html/2510.26840v2), [ICLR 2026 page](https://iclr.cc/virtual/2026/poster/10007969)
- Spider 2.0-lite (135 SQLite questions): OmniSQL goes from 34.1% to 22.2% EX with 60.9% of pairs supported; GPT-5 goes from 42.2% to 36.3% with 50.9% supported. 52.6% of the unsupported Spider 2.0 queries involve window functions. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- SpotIt+ adds database-constraint mining (rule-based mining plus LLM validation) so that counterexamples are realistic. — [SpotIt+, arXiv 2603.04334](https://arxiv.org/abs/2603.04334)
- The public repo is ai-ar-research/SpotIt-plus. It contains `run_rule_based.py` (SpotIt+-NoV, no LLM), `run_llm.py`, a `--vanilla` flag for the SpotIt baseline, and a VeriEQL submodule. It needs Python ≥3.10 and a custom Z3 build copied from VeriEQL. An OpenAI key is needed only for LLM constraint extraction. Runs are per question with `--bound` 2–5. No predictions or counterexample DBs are shipped. A LICENSE file exists, but its type was not visible. Another version of the paper cites atremante26/SpotItPlus. — [ai-ar-research/SpotIt-plus](https://github.com/ai-ar-research/SpotIt-plus), [search summary of paper versions](https://arxiv.org/html/2603.04334)

**LLM / plan-guided database synthesis**
- SynSQL (Habibollah & Rafiei, arXiv 2604.27261, Apr 2026) generates test databases from the question and schema, not from gold SQL. It has three stages: schema selection, question-guided data synthesis, and constraint-aware critique with refinement. On Spider, BIRD and Spider 2.0 with 10 systems, accuracy drops 3–14% compared with the original DBs. No code URL is on the abstract page. — [SynSQL](https://arxiv.org/abs/2604.27261)
- ParSEval (Chen, Miao, Zhang, Wang; PVLDB 18(11), 2025) is plan-aware test-DB generation with branch coverage over logical plan operators. It supports up to 40% more query pairs than verification-based tools, finds more non-equivalent pairs than test-case tools, and runs 21× faster. It has an "artifact available" badge, but I found no link on the landing page. — [ParSEval PVLDB page](https://vldb.org/pvldb/volumes/18/paper/ParSEval%3A%20Plan-aware%20Test%20Database%20Generation%20for%20SQL%20Equivalence%20Evaluation), [PDF](https://www.vldb.org/pvldb/vol18/p4750-miao.pdf)
- SQLMorph (ICDE 2026; arXiv 2609.08950) is query mutation for benchmark expansion (Join Query Expansion, Textual Query Augmentation) plus execution precision/recall metrics. It mutates the questions and queries, not the databases. — [SQLMorph](https://arxiv.org/abs/2609.08950)
- The ETM paper notes that Chu et al. (2020) used altered databases to reduce false positives, but that this approach is slow on large databases. — [ETM, arXiv 2407.07313](https://arxiv.org/html/2407.07313v3)

**Classical SQL test-data generation**
- XData (Chandra, Sudarshan et al., VLDB Journal 2015) generates datasets that "kill" mutants of an instructor query and is used for grading student SQL. There is a follow-up for complex queries (Somwase, Das, Sudarshan, arXiv 2409.18821, 2024). The tool page is at IIT Bombay; I found no GitHub repo. — [XData arXiv 1411.6704](https://arxiv.org/abs/1411.6704), [db-book XData page](https://www.db-book.com/teaching_material-dir/Xdata-dir/index.html), [Somwase et al. 2024](https://arxiv.org/abs/2409.18821v1)
- EvoSQL (SERG Delft) does search-based test-data generation for SQL and outputs JUnit tests. It is Java/Gradle with an instrumented HSQLDB, Apache-2.0, and has old Travis CI configs. No SQLite support was mentioned. — [SERG-Delft/evosql](https://github.com/SERG-Delft/evosql)

### Inferences
- Ranked by cost-to-adopt for SQLite benchmarks:
  1. SpotIt-plus rule-based / `--vanilla`: public, already run on BIRD dev and Spider2-lite SQLite, CPU only, no LLM needed.
  2. Our own CF generator, generalised (see Q2).
  3. Zhong fuzzing: code public but unmaintained, and its random-string distribution suits BIRD poorly.
  4. ParSEval / SynSQL: code not confirmed.
  5. XData / EvoSQL: wrong ecosystem.
- SpotIt is the natural independent oracle for our CF reward on BIRD. It searches for counterexamples formally, while our method uses rule-based edits of real data. Agreement between the two strengthens the argument that "our copies were written by us" does not bias the results.
- SpotIt's realism problem (counterexamples can violate implicit constraints, which is why SpotIt+ exists) is a point in our favour. Copies derived by editing the real DB keep real value distributions and formats, such as BIRD's text dates.

### Gaps
- Licence types of TestSuiteEval and SpotIt-plus were not visible in the fetches. Open the LICENSE files before vendoring them.
- Code availability for SynSQL and ParSEval is unconfirmed. Check the ParSEval PDF artifact section.
- I did not research SQLancer-style DBMS fuzzers in this session. They target DBMS logic bugs, not query-vs-query equivalence, so treat them as out of scope unless verified.
- The Zhong paper does not report the CPU time used to generate the suites.

## Q2. Can mutation-based approaches (mutate gold SQL, search for a DB that separates them) be applied cheaply to BIRD dev (1,534 Qs) or Spider dev? Expected CPU runtime?

### Takeaway
Yes. Both published variants already ran on these sets: Zhong (mutation plus fuzzing) on Spider dev, and SpotIt (prediction vs gold) on all of BIRD dev at about 1–4 s per pair. Both fit in a few CPU-hours to roughly one CPU-day on our machines. The main engineering risk is not compute but BIRD value semantics: text dates, evidence-dependent constants and REAL division. Pure random fuzzing does badly on these. Instead, generate counterfactual copies by editing the real database and its observed values.

### Cited Findings
- Zhong's procedure uses about 94 neighbours per query and 1,000 random DBs per schema, and separates more than 99% of neighbours on Spider dev. — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- The neighbour operators are: replace comparison, replace numeric constant, replace string constant, drop span. One edit is applied at a time to avoid accidental equivalence (e.g. "> 34" vs ">= 35" on integers). — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- SpotIt runtime on BIRD dev averages 0.93–3.93 s per pair under a 600 s timeout, with 1 core and 8 GB per call. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- The XData line of work frames the same idea as "killing SQL query mutants" with generated data. — [XData](https://arxiv.org/abs/1411.6704), [Extending XData to kill SQL query mutants in the wild](https://repository.ias.ac.in/128474)
- BIRD has 12,751 question–SQL pairs over 95 databases in 37 domains. Dev is 1,534 questions over 11 DBs. — [bird-bench.github.io](https://bird-bench.github.io/), [SpotIt search summary](https://arxiv.org/pdf/2510.26840v1.pdf)
- BIRD's official VES evaluation uses a 3 s per-query timeout, 5 repetitions. — [BIRD repo](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird)

### Inferences (cost estimates; none measured by us yet)
- **SpotIt on BIRD dev, one system.** About 1,000 EX-correct pairs × about 2 s comes to about 0.5–1 CPU-hour, plus the timeouts. 10 systems is about 5–15 CPU-hours, or under 1 hour wall-clock on a 32-core box. The L4 VM's CPUs are enough, and no GPU is needed.
- **Zhong-style suite for BIRD dev.**
  - Size: 1,534 golds × about 100 neighbours is about 150k neighbour queries. Greedy distillation runs gold plus surviving neighbours on up to 1,000 small synthetic DBs per schema.
  - Runtime: small DBs run in milliseconds, so this is roughly tens of CPU-hours. Without row caps on the fuzzed DBs, BIRD's wide tables could push it higher.
  - Main cost: engineering. Random strings make most BIRD gold queries return empty sets, because filters like `strftime(...)='2012'`, codes such as 'POS' or evidence constants never match.
  - Fix: sample column values from the real DB (bootstrap plus perturbation) instead of the uniform/random-string distribution.
- **Generalising our own CF generator (recommended).** Treat each real DB as the seed, and derive copies by schema- and gold-driven rule edits. Each rule maps to one of our bug families:
  - Fan-out: duplicate child rows behind foreign keys. This exposes missing DISTINCT and double counting.
  - Orphans: insert parent rows with no children, or children with dangling foreign keys. This separates LEFT from INNER JOIN.
  - NULL injection in nullable columns the gold query touches. This separates COUNT(col) from COUNT(*) and exposes AVG-ignores-NULL and NOT IN with NULL.
  - Boundary rows at each gold constant c (= c, c±1, c±epsilon). This exposes > vs >= and off-by-one errors.
  - Ties at ORDER BY … LIMIT k boundaries. This exposes tie-handling and argmax-via-LIMIT errors.
  - Case and whitespace variants of string literals. This exposes = vs LIKE and case sensitivity.
  - Random row subsampling of the real DB. This gives a realistic, generic separator.

  Each copy is about one SQLite file copy plus a few hundred INSERT/UPDATE statements. BIRD dev's 11 DBs total a few GB, so make copies per schema (not per question) and cap them at about 5–10 copies per schema per family. Then evaluate per question.
- **Mutation as validation.** Run Zhong's neighbour operators on BIRD and Spider gold SQL with sqlglot to get neighbours. "% of neighbours separated by the CF suite" is then a schema-agnostic coverage metric for the reviewer table, and it rebuts "bug families were written by us": neighbours are generated mechanically by someone else's published operators.
- **Caveat.** BIRD answers involve REAL arithmetic. Compare with rounding or tolerance, or float-precision mutants will look like spurious failures. Zhong reports the same blind spot.

### Gaps
- No published CPU-hour figure exists for running Zhong fuzzing on BIRD. I found no "test-suite for BIRD" release in this session.
- BIRD per-DB sizes were not fetched.

## Q3. How do known BIRD annotation errors / ambiguous gold SQL affect reward audits, and which cleaned subsets exist?

### Takeaway
BIRD gold quality is poor enough to dominate any naive audit. An expert audit found 52.8% of BIRD Mini-Dev examples erroneous, and 31 of 36 "all-systems-disagree" BIRD dev questions have problematic gold. In SpotIt's sample, most EX-pass/CF-fail discrepancies traced to gold, not predictions. Use corrected subsets for any false-accept number, and report gold-error-attributed flags separately.

### Cited Findings
- **Jin et al. 2026** (CIDR 2026 / PVLDB 19, arXiv 2601.08778v3) audited with an o3 agent ("SAR-Agent") plus human SQL experts.
  - BIRD Mini-Dev: 52.8% erroneous (263/498).
  - Spider 2.0-Snow: 62.8% erroneous (76/121 with public gold). The CIDR version says 66.1%.
  - Earlier versions of the paper cite 32.3% (Arcwise) and 36.1% as prior figures.
  - [arXiv 2601.08778v3](https://arxiv.org/html/2601.08778v3), [CIDR PDF](https://vldb.org/cidrdb/papers/2026/p5-jin.pdf), [PVLDB PDF](https://www.vldb.org/pvldb/vol19/p931-jin.pdf)
- Error taxonomy, as % of erroneous examples on BIRD Mini-Dev (Spider 2.0-Snow in brackets):
  - E1, SQL does not match the question logic: 29.3% (48.7%)
  - E2, SQL does not match the data or schema: 57.8% (57.9%)
  - E3, wrong domain knowledge: 10.7% (11.8%)
  - E4, ambiguous question or output format: 29.7% (23.7%)

  [Jin et al.](https://arxiv.org/html/2601.08778v3)
- Corrected BIRD dev subset: 100 random dev examples (62 easy / 28 moderate / 10 challenging). 48 needed correction: 41 SQL, 19 question, 17 evidence, 6 DB, 1 schema. Rankings on the original subset correlate with full dev at r_s=0.85, but with the corrected subset only at r_s=0.32 (p=0.23). Relative EX changes ran from −7% to +31% across 16 agents; e.g. CHESS went from 62% to 81%. — [Jin et al.](https://arxiv.org/html/2601.08778v3)
- Jin et al. repo (CC-BY-SA-4.0) contains:
  - Arcwise-Plat-SQL (SQL-only fixes) and Arcwise-Plat (also fixes questions, evidence and schema), corrected BIRD Mini-Dev versions released 2026-02-21.
  - The corrected 100-example dev subset (Google Drive).
  - `text_to_sql_agents/` holding 16 BIRD-leaderboard agents with generated queries on the original and corrected dev subsets.
  - SAR-Agent code (Python 3.12, o3).

  [uiuc-kang-lab/text_to_sql_benchmarks](https://github.com/uiuc-kang-lab/text_to_sql_benchmarks)
- SAR-Agent costs about $0.44 per example on BIRD and $1.11 on Spider 2.0-Snow. Precision is 83% on BIRD Mini-Dev and 89% on Spider 2.0-Snow. — [Jin et al.](https://arxiv.org/html/2601.08778v3)
- Wretblad et al. (ACL 2024): 49% of the financial-domain examples (52/106) had noise. They release two corrected financial sets: SQL-only, and SQL plus question. On corrected gold, zero-shot baselines beat SOTA prompting methods. Repo: niklaswretblad/the-effects-of-noise-in-text-to-SQL. — [Wretblad et al.](https://arxiv.org/html/2402.12243v4), [ACL 2024](https://preview.aclanthology.org/autopr/2024.acl-short.34)
- In SpotIt's manual analysis of 50 random csc-32b discrepancies (EX-pass but counterexample found), 26% were genuinely incorrect predictions and about 10% were ambiguous; the rest were attributed mainly to gold SQL. For 36 questions where all 10 systems disagreed with gold, 31 had problematic gold, 3 were ambiguous and 2 were genuine errors. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- FLEX (NAACL 2025) uses an LLM judge instead of EX. EX shows both false positives (coincidental matches) and false negatives (bad gold). Re-evaluation on Spider and BIRD gave an average −3.15 from false-positive corrections and +6.07 from false negatives (arXiv figures; the NAACL version reports different aggregates). — [FLEX arXiv 2409.19014](https://arxiv.org/html/2409.19014v4), [ACL Anthology](https://aclanthology.org/2025.naacl-long.228)
- Official cleaned releases from BIRD:
  - Sep 2023 "cleaner dev set".
  - Mini-Dev, 500 examples in SQLite, MySQL and PostgreSQL (Jun 27 2024; re-uploaded Jul 10 2025).
  - bird-sql-dev-1106, a "cleaner development split" (Nov 13 2025); submissions should say they used it.
  - Mini-Dev 2026 update, with annotation fixes and replaced instances (Oct 28 2026).

  Licence is CC BY-SA 4.0 since Apr 27 2024. — [bird-bench.github.io](https://bird-bench.github.io/), [BIRD repo](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird)
- The BIRD authors acknowledge that "errors and ambiguities may still exist" after about 700 hours of review. — [BIRD repo](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird)

### Inferences
- For a reward audit, a CF reward compares prediction against gold on more databases, so it amplifies gold bugs. A wrong gold with a JOIN fan-out bug will "fail" a correct prediction on the fan-out copy. The raw "EX-pass but CF-fail" rate on original BIRD is therefore an upper bound on false accepts, plus a gold-bug detector. Report three columns: genuine prediction error / ambiguous / gold error, using a manually adjudicated sample (SpotIt's 50-sample protocol is a citable precedent).
- Preferred BIRD subsets, in order:
  1. Arcwise-Plat-SQL (corrected Mini-Dev, about 500 questions, SQL-only fixes, so questions are unchanged).
  2. The 100-question corrected dev subset, which has 16 agents' predictions already: zero generation cost.
  3. bird-sql-dev-1106 for full-dev scale.
  4. Mini-Dev 2026.

  Do not report headline numbers on uncorrected Mini-Dev.
- Spider 2.0-Snow gold is about 63% erroneous and needs Snowflake credentials. For the real-data audit, Spider 2.0 should be limited to the 135-question Spider2-lite SQLite subset, and only as a stretch goal.

### Gaps
- Exact sizes of Arcwise-Plat / Arcwise-Plat-SQL (497 vs 498 vs 500) were not shown on the README. Check the data folder.
- How far bird-sql-dev-1106 overlaps with, or supersedes, Jin et al.'s corrections is unknown.
- Licence of the Wretblad repo was not checked.

## Q4. How do we measure the false-accept rate of a single-DB reward vs a multi-DB reward on real benchmark data without training?

### Takeaway
Use existing predictions, plus a few open-model runs on our own VM, as a fixed pool of candidate SQL. Score each prediction three ways:
- R1: EX on the original DB.
- Rk: our CF suite.
- An independent oracle: Zhong test suite on Spider, SpotIt `--vanilla` / rule-based on BIRD, plus a manual sample.

False-accept is the fraction of R1-accepted predictions that the oracle shows to be wrong. Prediction pools already exist for Spider (our ESM+ set of 8 systems; TestSuiteEval `predictions/`) and BIRD (the 16 agents on the corrected 100-question subset).

### Cited Findings
- Zhong et al. reported the single-DB false-positive rate across 21 Spider dev submissions: mean 6.5%, max 9.0%. This is the exact metric design to replicate. — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- The TestSuiteEval repo includes a `predictions/` folder. — [ruiqi-zhong/TestSuiteEval](https://github.com/ruiqi-zhong/TestSuiteEval)
- uiuc-kang-lab has generated queries from 16 BIRD-leaderboard agents on the original and corrected 100-question dev subsets. — [uiuc-kang-lab/text_to_sql_benchmarks](https://github.com/uiuc-kang-lab/text_to_sql_benchmarks)
- SpotIt evaluated 10 systems on all of BIRD dev, among them CHESS, Alpha-SQL, CSC-SQL 7B/32B, GenaSQL, GSR, OmniSQL (majority vote), RSL-SQL and SLM-SQL. The repo expects user-supplied predictions such as `predictions/alpha_sql.json` and does not ship them. — [SpotIt](https://arxiv.org/html/2510.26840v2), [SpotIt-plus](https://github.com/ai-ar-research/SpotIt-plus)
- SpotIt's numbers translate into these shares of EX-accepted answers rejected by a distinguishing DB:
  - csc-32b: (71.32−58.80)/71.32 ≈ 17.6%
  - Chess: ≈ 16.9%
  - slm: ≈ 19.0%

  Only about 26% of sampled flags were genuine prediction errors. — computed from [SpotIt](https://arxiv.org/html/2510.26840v2)
- Spider2-lite: 547 tasks (BigQuery 214, Snowflake 198, SQLite 135), MIT licence. Gold is released only for some examples, and the authors do not recommend fine-tuning on it. Evaluation is `evaluate.py --mode sql|exec_result` against gold exec results. SQLite DBs go in `spider2-lite/resource/databases/spider2-localdb`. — [xlang-ai/Spider2](https://github.com/xlang-ai/Spider2), [evaluation_suite](https://github.com/xlang-ai/Spider2/tree/main/spider2-lite/evaluation_suite)

### Inferences (protocol)
1. **Candidate pool, no training.**
   - Spider dev: our 8 ESM+ systems (already have), plus any TestSuiteEval predictions.
   - BIRD: the 16 uiuc agents (100 corrected questions).
   - Open models on the L4 VM with vLLM: e.g. OmniSQL-7B/32B or Qwen2.5-Coder, greedy plus N=8 samples on Arcwise-Plat-SQL Mini-Dev and/or bird-sql-dev-1106.

   Sampling N candidates per question also produces the reward-hacking-relevant population: wrong-but-EX-passing samples that an RL policy would be rewarded for.
2. **Rewards.**
   - R1 = EX on the original DB.
   - Rk = EX on all k CF copies.
   - Oracle O = Zhong TS (Spider) or SpotIt (BIRD), with a manually adjudicated sample of 50–100 disagreements as final ground truth.
3. **Metrics.**
   - False-accept FA(R) = P(O rejects | R accepts).
   - False-reject FR(R) = P(O accepts | R rejects), to show CF copies do not punish correct paraphrases.
   - Agreement between Rk and O (Cohen's kappa).
   - Neighbour-separation coverage (% of mechanically generated Zhong neighbours that Rk separates).
   - Ablation by bug family on real schemas.
4. **Gold-error control.** Run on original and corrected gold (the uiuc 100-subset has both). Show that FA estimates on corrected gold are stable while raw flags drop. This turns the BIRD gold-quality issue into a result instead of a confound.
5. **Cost.**
   - Open-model generation is about 1–2 GPU-hours on the L4 for 500–1,534 questions × 8 samples (inference only).
   - CF and SpotIt scoring is CPU-only, a few CPU-hours.
   - Manual adjudication of about 100 cases is roughly 4–6 person-hours.
   - Optional SAR-Agent gold checks cost about $0.44 per example with o3 ($220 for 500). This is paid, so skip it unless approved.

### Gaps
- I did not verify whether the TestSuiteEval `predictions/` folder holds the 21 leaderboard submissions or only examples.
- Publicly downloadable full-dev BIRD predictions for SpotIt's 10 systems were not located. Their own repos might release them; unchecked.
- L4 generation throughput was not measured. The 1–2 GPU-hour figure is an estimate.

## Q5. What realistic results would make a convincing "real-data audit" table, and which benchmark/subset for the 9-day and longer experiments?

### Takeaway
For 9 days, run two compact real-data audits.
- **Spider dev**: CF suite vs Zhong TS on the 8 ESM+ systems we already have. Cheapest, and shows our auto-generated copies agree with an independent published suite.
- **BIRD**: corrected subsets. Use the 100-question corrected dev subset, which has 16 agents' existing predictions, plus Arcwise-Plat-SQL Mini-Dev with 2–3 open models. Score with our auto CF suite and SpotIt rule-based as a second oracle, and adjudicate 50–100 flags by hand.

Before the presentation, scale to bird-sql-dev-1106 full dev, add the Spider2-lite SQLite 135, and use CF rewards in RL on BIRD train. Realistic magnitudes: single-DB false-accept of about 5–10% on Spider (published 6.5% mean; ours 8.1–14.9%). On BIRD, 15–20% of EX-accepted answers will be raw-flagged, but only part of that will be genuine prediction errors once gold errors are removed.

### Cited Findings
- Single-DB false-positive rate on Spider dev: 6.5% mean, 9.0% max (21 systems). — [Zhong et al. 2020](https://arxiv.org/abs/2010.02840)
- BIRD dev EX → SpotIt drops of 9.8–13.5 points across 10 systems. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- Only 26% of 50 sampled SpotIt discrepancies were genuine prediction errors, and about 10% were ambiguous. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- SynSQL reports 3–14% drops on Spider, BIRD and Spider 2.0 with generated DBs. — [SynSQL](https://arxiv.org/abs/2604.27261)
- Corrected gold reshuffles BIRD rankings: r_s falls to 0.32. — [Jin et al.](https://arxiv.org/html/2601.08778v3)
- On Spider2-lite SQLite, SpotIt supports only 51–61% of pairs because of window functions. — [SpotIt](https://arxiv.org/html/2510.26840v2)
- Licences: Spider is CC BY-SA 4.0 (HF card for the Yale LILY dataset; one mirror mislabels it CC BY 4.0). BIRD is CC BY-SA 4.0 since Apr 27 2024. The Spider2 repo is MIT. test-suite-sql-eval is Apache-2.0. EvoSQL is Apache-2.0. The uiuc corrected data is CC-BY-SA-4.0. — [HF xlangai/spider](https://huggingface.co/datasets/xlangai/spider/blob/main/README.md?code=true), [bird-bench.github.io](https://bird-bench.github.io/), [Spider2](https://github.com/xlang-ai/Spider2), [test-suite-sql-eval](https://github.com/taoyds/test-suite-sql-eval), [EvoSQL](https://github.com/SERG-Delft/evosql), [uiuc-kang-lab](https://github.com/uiuc-kang-lab/text_to_sql_benchmarks)

### Inferences

**Costed menu, cheapest first**

| Option | Code | SQLite | Runtime / cost | Pitfalls |
|---|---|---|---|---|
| A. Zhong TS DBs (Spider dev, done) | public, Apache-2.0 | yes | already have; minutes to evaluate | Spider only; gold queries must not change |
| B. Our CF generator, generalised to real schemas (rule edits on real DB per bug family) | ours | yes | about 1–2 dev-days to generalise; CPU minutes to hours | must show it is not hand-tuned per schema: drive it from schema plus gold AST only, and report neighbour coverage |
| C. SpotIt / SpotIt+-NoV on BIRD | public (SpotIt-plus, VeriEQL submodule) | BIRD SQLite | about 1–4 s per pair; under 1 CPU-hour per system; custom Z3 install | ORDER BY+LIMIT spurious CEX; no window functions or recursive CTEs; LLM constraint mode needs OpenAI (paid) |
| D. Zhong fuzzing re-run on BIRD | public (TestSuiteEval `fuzz/`), unmaintained | yes | tens of CPU-hours (est.) plus porting | random strings and dates kill BIRD filters; needs value sampling from the real DB |
| E. SynSQL / LLM-synthesised DBs | not confirmed | ? | LLM API cost | realism and validity checks; reviewers may question LLM bias |
| F. ParSEval | artifact badge, link not found | ? | 21× faster than test-case baselines (paper) | availability |
| G. XData / EvoSQL | XData: IITB site only; EvoSQL: Java/HSQLDB | no / unclear | porting cost high | wrong ecosystem |

**9-day plan (by Nov 30)**
1. Days 1–3: generalise the CF generator to arbitrary SQLite schemas (option B). Run it on Spider dev and on the BIRD Mini-Dev SQLite DBs.
2. Days 3–5:
   - Spider dev: R1 vs Rk vs Zhong TS on the 8 ESM+ systems. Table: FA(R1), FA(Rk), agreement with TS, FR(Rk).
   - BIRD: the 16 agents × 100 corrected questions, original vs corrected gold.
3. Days 4–6: SpotIt `--vanilla` on the same BIRD pairs as an independent oracle (CPU). Generate open-model predictions on Arcwise-Plat-SQL with the L4 if time allows, and stop the VM afterwards.
4. Days 6–7: manually adjudicate 50–100 disagreements into genuine / ambiguous / gold error.
5. Days 7–9: write-up.

**Pre-presentation plan**
- bird-sql-dev-1106 full dev (1,534) with 5–10 systems.
- Spider2-lite SQLite 135, noting the window-function coverage limits that SpotIt also hits.
- Mechanical neighbour coverage (Zhong operators via sqlglot) on BIRD.
- RL training with Rk on BIRD train, compared against R1, to show reduced reward hacking on real data.
- A cross-dialect check on Mini-Dev MySQL/PostgreSQL.

**Convincing table shape**

Rows: systems (8 Spider ESM+; 16 BIRD agents, or 4–6 representative ones plus the mean).

| Columns |
|---|
| EX (R1) |
| CF-EX (Rk) |
| Oracle-EX (TS on Spider / SpotIt on BIRD) |
| FA(R1) and FA(Rk) vs oracle |
| FR(Rk) |
| % of R1-accepts flagged by Rk that manual review confirms wrong / ambiguous / gold error |
| Rk–oracle agreement (kappa), plus the share of oracle-only and Rk-only flags |
| A "corrected gold" variant on BIRD |

Expected story: Rk catches most of what TS/SpotIt catch on real schemas, at seconds per question. Single-DB FA on real data is 5–10% on Spider and higher on BIRD. A sizeable share of raw BIRD flags are gold errors, which is a finding in its own right.

**Reviewer-facing honesty points**
- State that CF copies cannot certify equivalence: they give an upper bound, like Zhong's TS.
- Report false-reject on correct paraphrases.
- Report gold-error-attributed flags separately.

### Gaps
- No published "test-suite for BIRD" artefact was found. If one exists, it would be a direct baseline.
- Throughput and cost of generating open-model predictions on the L4 were not measured.
- Whether the BIRD evaluator compares result sets with set semantics (ignoring duplicates and order) was not verified in this session. Check `llm/src/evaluation.py` before designing duplicate-sensitive CF families. If it uses set equality, fan-out bugs that only change multiplicity will be invisible to both R1 and Rk unless Rk uses bag comparison.
