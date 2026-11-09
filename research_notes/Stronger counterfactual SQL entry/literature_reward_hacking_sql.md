# Literature map: false positives, lucky passes and reward hacking in execution-based text-to-SQL evaluation and RL (2024–2026), and how it relates to our counterfactual-DB reward

Research date: 2026-11-09. About 25 searches and fetches. Nothing found was first published in Oct–Nov 2026. The newest items are DualSQL (16 Sep 2026), ReViSQL v4 (21 Aug 2026) and a v5 revision of Cai et al. (5 Oct 2026). These are flagged inline.

## Q1. Test-suite accuracy (Zhong et al. 2020) and successors: database generation, false-positive reduction on Spider/BIRD, 2024–2026 follow-ups including RL rewards

### Takeaway
Distilled test suites (2020) are the seminal "run on many databases" idea, used for evaluation only. In 2025–2026 the field moved to **formal bounded-equivalence search** for a distinguishing database (SpotIt on BIRD; VeriEQL inside an RL reward in ReViSQL), not to random or targeted DB copies. On BIRD dev, this kind of check lowers top-system accuracy by roughly 10–14 points. I found no peer-reviewed paper that uses bug-family-targeted generated DB copies as an RL reward. The closest is ReViSQL's VeriEQL-based reward.

### Cited Findings
- **Zhong, Yu, Klein, "Semantic Evaluation for Text-to-SQL with Distilled Test Suites", EMNLP 2020, arXiv 2010.02840.** They randomly generate many databases, then distill a small suite with "high code coverage for the gold query". They evaluated 21 Spider leaderboard models and manually checked 100 examples, where the method was always correct. Suites were released for 11 datasets. The abstract's error figures (2.5% on average, 8.1% worst case) are **false negatives of Spider's then-official exact-set-match metric**, not false positives of single-DB EX. — [arXiv abs](https://arxiv.org/abs/2010.02840); [ACL PDF](https://aclanthology.org/2020.emnlp-main.29.pdf)
- A 2025 validate-and-fix paper (SQLDriller, SJTU IPADS) uses Test Suite Accuracy on BIRD dev. It says TSA has "much fewer false positives" than EX, but also that its own fixes "inevitably introduce a few false positives". — [SQLDriller PDF](https://ipads.sjtu.edu.cn/zh/publications/SQLDriller.pdf)
- One argument holds that EX on BIRD is reasonable because BIRD DBs "contain a large number of values, minimizing the chances of false positives". This is the assumption our slice-size result (29% invisible bugs at 50 customers vs <1% at 500) speaks to directly. — [CodeS, arXiv 2402.16347](https://arxiv.org/pdf/2402.16347)
- **SpotIt: "Evaluating Text-to-SQL Evaluation with Formal Verification", Klopfenstein, He, Wang, Tremante, Wu, Narodytska (Amherst College, SFU, VMware Research by Broadcom), arXiv 2510.26840 (v2, Mar 2026).** A search snippet lists it as ICLR 2026; the arXiv page names no venue.
  - Method: an SMT-based bounded equivalence engine searches for a database that tells the generated SQL apart from the gold SQL. It ran on all 1,533 BIRD-dev pairs for 10 top leaderboard systems.
  - Accuracy drops: csc-32b 71.32 EX → 58.80 (SpotIt) → 57.82 (SpotIt+); Alpha 69.36 → 55.87; omni-maj 66.88 → 54.69; slm 63.43 → 51.37. The paper's own text gives inconsistent ranges (11.3–14.2% in one place, 9.8–13.5% in another).
  - Ranking shifts: csc-32b goes from 1st to 4th.
  - Settings and coverage: bound K=5, with marginal gains beyond K=3. Coverage is 93.6–97.1% of queries. Window functions, recursive CTEs and ORDER BY+LIMIT are unsupported. A counterexample takes about 0.9–3.9 s on average, and 93–96% of counterexamples validate.
  - Manual review of 50 csc-32b disagreements: only 26% were genuinely wrong generated SQL, about 10% were ambiguous questions, and the majority were problematic gold SQL. Of 36 questions that all 10 systems failed under SpotIt+ but passed under EX, 31 had problematic gold SQL.
  - The paper does not use SpotIt as an RL reward. — [arXiv html v2](https://arxiv.org/html/2510.26840v2)
- **SpotIt+ (arXiv 2603.04334)** adds mined database constraints, with an LLM judging whether a mined constraint is a genuine domain property, so that counterexamples look realistic. Per a third-party review, average time to a counterexample drops from 1.7 s to 0.9 s. — [arXiv PDF](https://arxiv.org/pdf/2603.04334v1); [review](https://www.themoonlight.io/review/spotit-verification-based-text-to-sql-evaluation-with-database-constraints)
- **VeriEQL (He, Zhao, Wang, Wang, et al.; arXiv 2403.03193; OOPSLA 2024 per the ACM DOI 10.1145/3649849).** It encodes both queries plus integrity constraints into SMT (Z3). It either proves bounded equivalence or returns a counterexample DB. It was evaluated on more than 20,000 benchmarks, and 96% of non-equivalent pairs are refuted with fewer than 3 tuples. — [arXiv](https://arxiv.org/abs/2403.03193); [ACM](https://dl.acm.org/doi/10.1145/3649849)
- An SFU news release (Jan 2026) says a VeriEQL extension can check LLM-generated SQL against gold SQL for text-to-SQL evaluation. This is the only source for that claim, and it gives no details. — [SFU news](https://www.sfu.ca/fas/computing/news-events/news/2026/january/new-sfu-research-strengthens-data-systems-with-advanced-sql-veri.html)
- **rl-sql (GitHub, devChaudhari7).** Not peer reviewed. It builds 158 schemas × 3 seeded DB instances and counts a prediction only if it matches gold on every instance. Its stated reason: with a single DB, a wrong query can match by chance, and RL turns that into an exploit. — [GitHub](https://github.com/devChaudhari7/rl-sql)

### Inferences
- Our method sits between Zhong-style random test suites and SpotIt/VeriEQL-style solver-found counterexamples. Our copies are **code-generated and targeted at specific bug families**: they include answer-changing copies that defeat answer smuggling, and answer-preserving copies that expose fan-out and duplicate-join bugs. They need no SMT and work for any SQL the engine runs, including window functions, which SpotIt and VeriEQL do not support. They are also hidden from the agent. This is the clearest novelty claim. The honest framing is "a cheap, solver-free, bug-targeted cousin of test suites and bounded verification, used as an RL reward".
- VeriEQL needs very few tuples (fewer than 3 for 96% of refutations). Minimal adversarial DBs may therefore beat large copies. Our "invisible at 500 customers <1%" result concerns bugs that are invisible on the *visible* DB. Small, targeted counterexample DBs are the complementary lever.

### Gaps
- I did not find the number of databases per distilled suite, or a single-DB-EX false-positive rate from Zhong 2020. The abstract gives exact-match false negatives only.
- I did not find a published paper that uses Zhong-style test suites directly as a GRPO reward. The rl-sql repo is the only example, and it is unreviewed.

## Q2. Studies measuring false positives and annotation errors in BIRD/Spider gold SQL and execution accuracy

### Takeaway
Gold SQL in BIRD is very noisy: 52.8% of BIRD Mini-Dev instances have annotation errors, and 61.1% of a BIRD-train sample has at least one error. Single-DB EX both over- and under-rewards. For an RL reward this means some "false negatives" come from gold being wrong, and a stricter verifier anchored to wrong gold cannot fix that.

### Cited Findings
- **Jin, Choi, Zhu, Kang (UIUC Kang lab), "Pervasive Annotation Errors Break Text-to-SQL Benchmarks and Leaderboards", arXiv 2601.08778 (Jan 2026).**
  - Annotation error rates: BIRD Mini-Dev 52.8%; Spider 2.0-Snow 62.8%.
  - They re-evaluated 16 open-source BIRD agents: relative performance changes ranged from −7% to +31%, and ranks moved by up to ±9.
  - Spearman correlation with full BIRD Dev is 0.85 for the uncorrected subset but 0.32 (p=0.23) for the corrected one. — [arXiv abs](https://arxiv.org/abs/2601.08778)
  - **Conflict:** a CIDR 2026 version ("Text-to-SQL Benchmarks are Broken") is reported by search snippets as 66.1% for Spider 2.0-Snow and −3% to +31% shifts. I did not open that PDF. — [CIDR PDF](https://www.vldb.org/cidrdb/papers/2026/p5-jin.pdf)
- **Wretblad et al., "Understanding the Effects of Noise in Text-to-SQL", ACL 2024 (short).** Per a secondary snippet, about 32% of problems in a BIRD dev subset had errors, and correcting them changed rankings: zero-shot GPT-3.5 beat DIN-SQL and MAC-SQL. I did not verify the number in the PDF. — [ACL Anthology](https://aclanthology.org/2024.acl-short.34.pdf)
- **ReViSQL / BIRD-Platinum (Zhu, Jin, Choi, Kang; UIUC + Bridgewater AIA Labs), arXiv 2603.20004 (v4 21 Aug 2026).**
  - Of about 2.5k BIRD-train instances sampled, 61.1% had at least one error. Gold SQL was corrected in 52.1%, questions in 26.2%, and external knowledge in 18.2%; 1.5% were discarded as unanswerable.
  - The o3 LLM reviewer had 90.6% precision but only 24.5% recall.
  - Training on uncorrected BIRD Train *lowered* Kimi-K2.6 accuracy by 7.0% and 5.0% on Arcwise-Plat-SQL and -Full, while corrected data raised it by 7.2% and 5.0%. — [arXiv html](https://arxiv.org/html/2603.20004)
- **NL2SQL-BUGs (Liu et al., HKUST-GZ), arXiv 2503.11984 (KDD 2025 per project; v2 Jun 2025).** It has a 9-category, 31-subcategory semantic-error taxonomy and 2,018 expert-annotated instances. LLMs detect these errors with 75.16% accuracy on average. It found previously unknown errors in 16 Spider dev gold queries (1.55%) and 106 BIRD dev gold queries (6.91%). — [arXiv](https://arxiv.org/abs/2503.11984)
- **FLEX (Kim, Jeon, Choi, Choi, Cho), arXiv 2409.19014 (NAACL 2025).** It is an LLM-based evaluation metric. Agreement with human experts rises from Cohen's κ 62 (EX) to 87.04, and model scores rise by over 2.6 points on average. EX underestimates models because of annotation issues and overestimates them on challenging questions. A search snippet adds that on hard BIRD questions EX's false-positive ratio exceeds its false-negative ratio. — [arXiv](https://arxiv.org/abs/2409.19014); [ACL PDF](https://aclanthology.org/2025.naacl-long.228.pdf)
- **SpotIt (see Q1).** When verification disagrees with EX on BIRD dev, the gold SQL is wrong more often than the prediction. — [arXiv](https://arxiv.org/html/2510.26840v2)
- **Arctic-Text2SQL-R1.** Many reference queries return empty results. Removing them dropped about 1,400 BIRD-train and 1,700 Spider-train samples. — [arXiv v2](https://arxiv.org/html/2505.20315v2)

### Inferences
- Our audit used *gold-mutants* (realistic buggy variants of gold) on our own generated DB, with gold assumed correct. That sidesteps the BIRD gold-noise problem, which is a strength to state explicitly. It also means our "0/2847 correct queries rejected" is a false-negative rate measured against our own gold, not BIRD-style noisy gold.
- Empty-result golds trivially reward `SELECT ... WHERE 1=0`-style hacks. Arctic and ReViSQL both filter them. Our answer-changing copies already defeat constant-answer smuggling, but empty-result golds deserve a check.

### Gaps
- I did not find a precise, BIRD-wide single-DB EX false-positive rate (EX passes that are semantically wrong) from peer-reviewed work other than SpotIt's roughly 10–14 point drop. Part of that drop is gold error, not false positives.

## Q3. RL for text-to-SQL papers 2025–2026: rewards, reward hacking and lucky passes, small-model gains

### Takeaway
Almost every 2025 RL-SQL paper uses single-DB execution match, sometimes with format, syntax, partial-credit, schema-linking, n-gram or LLM-judge terms. Before 2026 most of them ignore lucky passes. In 2026 two groups explicitly attacked execution false positives in the reward. ReViSQL used VeriEQL and measured 32.8% false-positive positive rewards. DualSQL used a stricter result matcher (REX), and it gave only a small gain on the strict metric with no gain on EX. That pattern matches our null.

### Cited Findings
- **ReViSQL (arXiv 2603.20004, UIUC/Bridgewater, v4 Aug 2026).** The closest prior work to ours.
  - **False-positive measurement:** in a 300-step pilot on Kimi-K2.6, VeriEQL flagged 28.8–38.4% of positive result-based rewards as false positives (average 32.8%). The rate "does not decrease as training progresses".
  - **Reward:** 0 if results mismatch; 1 if results match and VeriEQL accepts or returns ⊥ (timeout or unsupported SQL such as window functions); 1−β = 0.8 if results match but VeriEQL refutes. The authors deliberately soft-downweight rather than zero these cases, so verifier failures are not fully penalized.
  - **Process reward:** rule-based terms penalize ignoring external knowledge. Ignoring evidence dropped from 8/33 failures (24.2%) to 1/23 (4.3%).
  - **Ablation:** reward shaping (verification plus process terms combined) added +2.8% (SQL) and +3.8% (Full), removing 24.6% and 38.0% of remaining errors. The two components are not ablated separately.
  - **Data matters most:** clean data versus raw BIRD-train made a 13.9–17.1% difference.
  - **Hacking behaviours named:** `SELECT 1 WHERE False` on empty-gold items; false positives push "systematic logical errors" that match the example DB; a model trained on uncorrected data applied DISTINCT correctly in only 5/30 problems that needed it.
  - **Setup:** Qwen3-235B-A22B and Kimi-K2.6, LoRA r32, group size 16, CISPO loss. No models of 8B or smaller. — [arXiv html](https://arxiv.org/html/2603.20004); [Bridgewater blog](https://www.bridgewater.com/aia-labs/putting-task-expertise-into-rl-to-achieves-state-of-the-art-on-text-to-sql)
- **DualSQL (Chen et al., Ohio State + Google), arXiv 2609.18135, 16 Sep 2026.** Very recent.
  - **REX metric:** "Robust Execution Match" uses max-matching between result sets. It is sensitive to duplicates, requires row order only if the gold has ORDER BY, and searches for a column permutation using a linear sum assignment solver. Plain EX's blindness to duplicates and ordering is described as a false-positive source.
  - **REX vs EX as reward (Qwen3-8B single-agent, BIRD-dev):** EX-trained gives 69.2 EX / 63.7 REX; REX-trained gives 69.6 EX / 66.7 REX. So +3.0 on the strict metric and +0.4 on EX. No perturbed or multiple DBs are used.
  - **Other numbers:** the 4B model gets 68.0 EX / 64.0 REX on BIRD-dev. A format-violation reward hack is noted. — [arXiv html](https://arxiv.org/html/2609.18135v1)
- **Arctic-Text2SQL-R1 (Yao et al., Snowflake), arXiv 2505.20315, Findings of ACL 2026.**
  - **Reward:** 1 if the execution result matches (strictest BIRD criteria), 0.1 if syntactically valid and executable, 0 otherwise. The authors say elaborate designs "can encourage reward hacking and brittle behaviors" and finer-grained rewards "induced 'lazy' behaviors"; no alternative gave significant improvement.
  - **7B results:** 68.9 BIRD-dev and 88.8 Spider-test, initialized from OmniSQL SFT. Starting from Qwen2.5-Coder-7B-Instruct without SFT gives 63.9 BIRD-dev greedy.
  - **Filtering:** empty-result golds and queries over 5 s were removed. Synthetic data was kept only if at least 1 of 10 samples was correct (a pass@k filter).
  - Per a search snippet I did not verify in the text, the authors acknowledge that the execution reward can pay semantically wrong queries that happen to produce matching results, and point to flexible comparison and richer synthetic DBs. — [arXiv v2](https://arxiv.org/html/2505.20315v2); [ACL](https://aclanthology.org/2026.findings-acl.1345.pdf)
- **Reasoning-SQL (Pourreza et al., Google; arXiv 2503.23157).** GRPO with partial rewards: LLM-as-judge, syntax, schema-linking, n-gram similarity, plus execution. The 14B model beats o3-mini by 4% on BIRD. I found no reward-hacking analysis in the abstract or snippets. — [arXiv](https://arxiv.org/html/2503.23157v2)
- **SQL-R1 (Ma et al., DataArcTech; arXiv 2504.08600; NeurIPS 2025).** Rewards are format (±1), execution, result (+3 correct / −3 wrong) and length. It reports 88.6% Spider and 67.1% BIRD (the 14B per the repo; sources conflict on whether 66.6% is the 7B figure). Base models include Qwen2.5-Coder-3B and 7B. — [GitHub](https://github.com/DataArcTech/SQL-R1); [alphaXiv](https://www.alphaxiv.org/abs/2504.08600)
- **Think2SQL (Papicchio et al.; arXiv 2504.15077).** It argues binary EX is sparse and uses a dense, gated partial-credit execution reward (cell precision, recall and cardinality). The 14B model reaches 0.602 weighted EX on BIRD. A secondary source says Think2SQL-4B gets 59.6% EX on BIRD dev; I did not verify this. — [arXiv html](https://arxiv.org/html/2504.15077v5)
- **Reward-SQL (arXiv 2505.04671).** Its GRPO with process plus outcome reward gives 61.8% on BIRD dev versus 59.6% for outcome-only. The headline is 70.3% with an 8B model. — [arXiv](https://arxiv.org/html/2505.04671)
- **Graph-Reward-SQL (Findings EMNLP 2025).** An execution-free graph-matching reward model (GMNScore), motivated partly by false positives of pure execution rewards. — [ACL PDF](https://aclanthology.org/2025.findings-emnlp.694.pdf)
- **MARS-SQL (Yang et al., HKUST; arXiv 2511.01008; ICML 2026 poster).** Three agents (grounding, generation, validation), with multi-turn RL using execution feedback for the generator. The validator selects among candidates and is not a reward. It reports 77.84% BIRD dev and 89.75% Spider test. — [arXiv](https://arxiv.org/abs/2511.01008v1); [ICML](https://icml.cc/virtual/2026/poster/65053)
- **Also seen but not examined:** PaVeRL-SQL (partial-match rewards, arXiv 2509.07159); SERL-SQL (arXiv 2608.00485); R³-SQL (arXiv 2604.25325); CogniSQL-R1-Zero (arXiv 2507.06013); "Sparks of Tabular Reasoning via Text2SQL RL" (arXiv 2505.00016). — [PaVeRL](https://arxiv.org/pdf/2509.07159); [SERL-SQL](https://arxiv.org/pdf/2608.00485); [R3-SQL](https://arxiv.org/pdf/2604.25325); [CogniSQL](https://arxiv.org/pdf/2507.06013); [Sparks](https://arxiv.org/pdf/2505.00016)

### Inferences
- **Novelty vs ReViSQL.** ReViSQL already shows that execution-reward false positives are large (about 33%) and that verifying them inside the reward is worth doing. Its verifier is SMT (VeriEQL), it soft-downweights, and its gain is confounded with process rewards on 235B-scale models. Ours is solver-free counterfactual execution with a hard reward, on a 3.35B model, with a clean single-variable ablation. Our 29.5% → 16.8% mutant pay rate is in the same range as their 32.8% false-positive share.
- **Our null is consistent with DualSQL.** A stricter matcher moved EX by only +0.4 at 8B, and gains showed up mainly on the strict metric. Our headline metric is "verified accuracy". The project context does not say whether that metric is single-DB or counterfactual. It is worth reporting both, because the stricter-reward run may gain specifically on the strict metric.
- **Disagreement rate explains the null.** ReViSQL's false positives were about 33% *of positive rewards* on a strong model. Ours disagreed on only about 7% of rollouts, because a 3.35B model at roughly 10% accuracy produces few positives to begin with. The strict reward therefore changes very few advantages.
- **Cheap adoptions:**
  1. ReViSQL-style soft penalty (0.8 instead of 0) for "passes visible DB, fails a counterfactual copy", so the reward is less sparse for a weak model.
  2. Filter empty-result golds and use Arctic's pass@k data filter (keep items where at least 1 of k samples is correct) to increase signal.
  3. Arctic's 0.1 reward for executable SQL.
  4. DualSQL's REX-style duplicate- and order-aware matching as a cheap complement to answer-preserving copies.

### Gaps
- I did not find any RL-SQL paper that uses multiple or perturbed databases as the reward, other than the unreviewed rl-sql repo. Nor did I find one that runs a clean strict-vs-lenient reward ablation at 7B or smaller, apart from DualSQL at 4B/8B (and its EX-vs-REX ablation is 8B).
- I could not verify the exact small-model numbers for SQL-R1-3B or Think2SQL-4B from the primary PDFs.

## Q4. Metamorphic, differential and mutation testing of SQL; equivalence checkers; use as RL rewards

### Takeaway
Metamorphic and differential testing of SQL is mature for DBMS bug finding (SQLancer lineage, QTRAN) and is emerging for text-to-SQL hallucination detection (SQLHD, metamorphic prompting). Formal checkers (VeriEQL, SpotIt) now evaluate LLM SQL. Only ReViSQL uses one (VeriEQL) inside an RL reward. Outside SQL, "Isomorphic Perturbation Testing" (2026) is a close conceptual analogue to our answer-changing copies, applied as an RL verifier.

### Cited Findings
- **SQLHD, "Hallucination Detection for LLM-based Text-to-SQL Generation via Two-Stage Metamorphic Testing".** It uses 8 metamorphic relations that alter wording or schema and 9 logic-aware relations that alter the database, and flags any result deviation as a hallucination. No gold SQL is needed, and it is not used for RL. — [ResearchGate](https://www.researchgate.net/publication/399175418_Hallucination_Detection_for_LLM-based_Text-to-SQL_Generation_via_Two-Stage_Metamorphic_Testing)
- **Metamorphic prompting for validating LLM-generated SQL (MRSQLGen, ACM 2026).** It rewrites the prompt into related reformulations and checks that execution results satisfy the expected relation. — [ACM](https://dl.acm.org/doi/pdf/10.1145/3797146)
- **QTRAN (ACM 2025).** It extends metamorphic-oracle DBMS logic-bug detection, where results on any test DB should satisfy a predefined relation. — [ACM](https://dl.acm.org/doi/pdf/10.1145/3728908)
- **Dr.Spider (Chang et al., ICLR 2023).** Programmatic DB perturbations (schema renames, content-representation changes) for robustness evaluation. — [arXiv 2301.08881](https://arxiv.org/pdf/2301.08881)
- **VeriEQL, SpotIt and SpotIt+.** See Q1: bounded SMT equivalence with counterexample databases. Only ReViSQL uses VeriEQL as a reward (see Q3).
- **Helff et al. (TU Darmstadt, hessian.AI, DFKI et al.), "LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking", arXiv 2604.15149 (Apr 2026; listed at an ICLR 2026 workshop).** Domain: inductive logic programming (SLR-Bench).
  - **Extensional vs isomorphic verification:** extensional verifiers let models enumerate instance labels instead of inducing rules. Isomorphic Perturbation Testing bijectively renames object constants and re-verifies. Real rules survive the renaming; enumerations do not.
  - **Training result (Olmo-3-7B-Think-DPO):** with an extensional verifier, the hacking gap opens around step 250 and reaches about 3.5 of 10 reward points by step 500. With an isomorphic verifier, the gap stays near zero.
  - **Shortcut prevalence:** 40 shortcuts at complexity levels 1–10 versus 458 at 11–20, rising with reasoning effort (gpt-5-mini 0/32/84 at low/medium/high). Shortcuts appear only in RLVR-trained models.
  - **Not reported:** held-out accuracy of isomorphic-trained versus extensional-trained models. — [arXiv html](https://arxiv.org/html/2604.15149)
- **"Before the Model Learns the Bug: Fuzzing RLVR Verifiers", arXiv 2606.01066.** Deliberately buggy math, JSON tool-call and code verifiers repeatedly accept wrong completions; stricter variants remove the measured false positives. — [alphaXiv](https://www.alphaxiv.org/abs/2606.01066)

### Inferences
- Our answer-changing copy is the SQL analogue of IPT: a genuine query generalizes across instances, while a smuggled literal does not. Helff et al. show that the hacking gap opens late (around step 250) and grows with task difficulty. A short GRPO run on a weak 3.35B model may end before hacks become prevalent. That is one candidate explanation for our null, and it motivates the "hacks paid 54.1% → 1.9%" audit as the main evidence rather than accuracy.
- Combining the two is novel as far as I can find: bug-family-targeted metamorphic DB copies (answer-changing plus answer-preserving) used as an RL reward for text-to-SQL. The answer-preserving copy, which exposes fan-out and duplicate joins, has no direct counterpart in the papers above. REX handles duplicates only at result-comparison level, on the same DB.

### Gaps
- I did not search SQLancer, Cosette or QED in depth. They are not needed for the novelty claim. I found nobody using Cosette or QED as an RL reward.

## Q5. General RLVR reward-hacking and weak/spurious reward literature: why a stricter verifier may not change outcomes for small models

### Takeaway
Strong evidence shows that GRPO gains on small models often come from amplifying existing behaviours, not from reward precision. Random, flipped or format-only rewards recover much of the gain for some model families (Qwen), but not for others. This is a plausible, citable explanation for our null. It also suggests a cheap diagnostic: a random-reward or format-only control run.

### Cited Findings
- **Shao et al., "Spurious Rewards: Rethinking Training Signals in RLVR", arXiv 2506.10947, ICML 2026 (PMLR v306).**
  - **Qwen2.5-Math-7B on MATH-500:** random reward +21.4 points, incorrect-label reward +24.1, ground truth +29.1.
  - **Mechanism:** attributed to the GRPO clipping bias, which amplifies existing high-probability behaviours ("code reasoning" rises from 65% to over 90%).
  - **Other model families:** little transfer to general Qwen2.5, Llama 3.1/3.2 and OLMo2, which see minimal or negative change.
  - **Recommendation:** include spurious-reward baselines as diagnostic controls. — [PMLR](https://proceedings.mlr.press/v306/shao26d.html); [ICML](https://icml.cc/virtual/2026/poster/61082); [alphaXiv](https://alphaxiv.org/overview/2506.10947v1)
- **Lv, Xie, Sun, Kang, Yan, "The Climb Carves Wisdom Deeper Than the Summit: On the Noisy Rewards in Learning to Reason", arXiv 2505.22653 (May 2025).**
  - **Flipped rewards:** Qwen2.5-7B with 40% of math rewards flipped still reaches 72.02% on MATH-500 versus 75.85% clean. It collapses only at a 50% flip rate.
  - **Reasoning-phrase rewards:** rewarding only reasoning phrases, with no correctness check, gives over 70%.
  - **Reward-model accuracy:** 85% and 75% accurate reward models perform comparably; 65% is worse. Llama-3.1-8B is much less robust.
  - Some figures here come from secondary summaries. — [arXiv](https://arxiv.org/abs/2505.22653); [review](https://www.themoonlight.io/review/the-climb-carves-wisdom-deeper-than-the-summit-on-the-noisy-rewards-in-learning-to-reason)
- **Cai, Wang, Liu, Liu, Niu, Sugiyama, "Reinforcement Learning with Verifiable yet Noisy Rewards under Imperfect Verifiers", arXiv 2510.00915.** v1 Oct 2025; the latest revision, v5, is dated 5 Oct 2026, which is very recent. It models verifier errors as asymmetric false-positive and false-negative rates. A forward correction needs only the false-negative rate, and an online "appeals" LLM verifier estimates it. Both corrections improve math RLVR. — [arXiv](https://arxiv.org/abs/2510.00915)
- **Huang, Zeng, Zeng, Zhu, He, "Pitfalls of Rule- and Model-based Verifiers – A Case Study on Mathematical Reasoning" (retitled "From Accuracy to Robustness…"), arXiv 2505.22203.**
  - **Rule-based verifiers:** false negatives are non-negligible and grow as the policy gets stronger, which hurts RL.
  - **Model-based verifiers:** they raise recall (84% → 92% on Skywork-OR1) but get hacked through false positives during RL.
  - **Key finding:** "classification accuracy of a verifier does not necessarily reflect its resistance to reward hacking". — [arXiv](https://arxiv.org/html/2505.22203v2)

### Inferences
- Our null (GRPO-single 12.7% vs GRPO-counterfactual 9.0% vs SFT 9.4%) fits this literature.
  1. The two rewards disagreed on only about 7% of rollouts, which is far below the 40% flip rate that still trained fine in Lv et al. Even a "worse" reward should then train similarly, so outcome differences are likely dominated by seed or run variance.
  2. RL gains at this scale may come mostly from format and behaviour amplification, not reward precision.
  3. The stricter reward lowers the positive rate for a weak policy, which makes advantages sparser. That could plausibly explain 9.0% < 12.7% without the stricter reward being "wrong".
- Seed variance is an inference, not a measurement. Run at least 2–3 seeds, or report confidence intervals, before claiming the counterfactual reward *hurts*.
- **Cheap adoptions:**
  1. Add a random-reward or format-only GRPO control (Shao et al. recommend this). It shows how much of the 12.7% is reward-agnostic.
  2. Report false-positive and false-negative rates of both rewards on the rollouts themselves, as in Cai et al. and Huang et al.
  3. Frame our contribution as verifier robustness to hacking, not accuracy gain. Huang et al. directly support the claim that static verifier accuracy and RL hackability are different axes.

### Gaps
- I found no spurious-reward replication on text-to-SQL specifically. Whether random rewards help Cohere Aya-family models is unknown, since the Spurious Rewards effect is model-family dependent.
- I did not research code unit-test hacking papers (e.g. ImpossibleBench, CodeRL) in depth, given the tool-call budget.

## Q6. Do stricter or more accurate verifiers improve RL outcomes? (precision vs recall)

### Takeaway
The evidence is mixed. Higher-precision verifiers clearly help when the base policy is strong enough to exploit the weak verifier, or when verifier false positives are frequent: HardTests in code, ReViSQL in SQL, IPT in ILP. At small scale and low disagreement, effects on headline accuracy are small: DualSQL got +0.4 EX and +3.0 on the strict metric. Recall (avoiding false negatives) matters too. A strict verifier that rejects correct answers hurts training more as the policy improves.

### Cited Findings
- **HardTests / HARDTESTGEN (He et al., LeiLi lab), arXiv 2505.24098, NeurIPS 2025, with an ICLR 2026 version.** LLM-synthesized tests filtered by oracle programs. Precision is +11.3 points (ICLR version: +11.22) and recall +17.5 points over prior synthetic tests, with up to +40 points precision on hard problems. Rejection sampling and RL with HardTests verifiers improve downstream code generation. — [NeurIPS](https://neurips.cc/virtual/2025/131673); [ICLR](https://iclr.cc/virtual/2026/poster/10006843); [arXiv](https://arxiv.org/pdf/2505.24098)
- **ReViSQL.** The verification-aware plus process reward gave +2.8 and +3.8 points at large scale. — [arXiv](https://arxiv.org/html/2603.20004)
- **DualSQL.** A REX reward gives +3.0 on the strict metric and +0.4 EX for Qwen3-8B. — [arXiv](https://arxiv.org/html/2609.18135v1)
- **Helff et al.** An isomorphic verifier eliminates the hacking gap, but held-out accuracy is not reported. — [arXiv](https://arxiv.org/html/2604.15149)
- **Huang et al.** Rule-verifier false negatives increasingly hurt RL as policies improve. Lenient model verifiers get hacked. — [arXiv](https://arxiv.org/html/2505.22203v2)
- **Lv et al.** Reward models at 75% and 85% accuracy train comparably; 65% is worse. This suggests a threshold effect rather than linear benefits. — [arXiv](https://arxiv.org/abs/2505.22653)

### Inferences
- **Positioning.** Our reward audit (hacks paid 54.1% → 1.9%, 0/2847 false negatives) shows higher precision *with no measured recall loss*. That is the profile the literature says matters most. The weak link is that the 3.35B policy rarely produces the hacks or lucky passes that the stricter reward removes, so there is little to fix during training. Prior work shows benefits mainly where false positives make up a large share of positive rewards (about 33% in ReViSQL).
- A cheap test of this explanation: deliberately inject or prompt hack-prone behaviour, or train longer or with harder items. Then check whether the single-DB run's hack rate grows over steps (Helff-style divergence) while the counterfactual run's does not. That would turn the null into a positive "prevents a failure mode that emerges with training" result.

### Gaps
- I found no paper giving a quantitative verifier-precision vs downstream-accuracy curve for text-to-SQL at 7B or smaller.
- I found no published replication on Cohere models.
