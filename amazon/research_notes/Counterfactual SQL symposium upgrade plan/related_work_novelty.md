# Related work and novelty threats: counterfactual-database rewards for text-to-SQL RL (2025 to Nov 2026)

Verification legend: **[V]** = title/authors/ID/date checked on the arXiv abs/html page in this session. **[S]** = checked from search-result titles/snippets only (ID and title are consistent across results, but authors and details were not read on the primary page). **[U]** = not verified in this session; check before citing.

## Q1. Which 2025–2026 papers study reward hacking, false-positive rewards, or spurious correctness in text-to-SQL RL or execution-based RLVR? Do any grade RL rollouts on multiple or perturbed databases?

### Takeaway
False-positive execution rewards in text-to-SQL RL are now a documented problem. The strongest prior work is ReViSQL (Zhu, Jin, Choi, Kang, 2026), which measures a 32.8% false-positive rate among positive rewards and fixes it with a VeriEQL equivalence check inside the reward, not with extra databases. I found **no paper that executes RL rollouts on several hidden, perturbed or counterfactual databases as the training reward**. Multi-database checks (test suites, SynSQL, Progress-SQL's TS metric) are used only for evaluation.

### Cited Findings
**Text-to-SQL RL, closest to us**
- **[V] ReViSQL**, arXiv:2603.20004. Yuxuan Zhu, Tengjun Jin, Yoojin Choi, Daniel Kang (UIUC; Kang also Bridgewater AIA Labs), cs.DB. v1 is dated 20 Mar 2026, v2 30 Mar 2026, and v4 21 Aug 2026. v1 was titled "ReViSQL: Achieving Human-Level Text-to-SQL"; v4 is titled "Human-Level Text-to-SQL via Reinforcement Learning on Verified Data, Without Pipeline Engineering". A 2026 ACL/Findings version may exist: the search surfaced aclanthology.org/2026.findings-acl.1677, but I did not confirm it is this paper. Sources: [abs v1](https://arxiv.org/abs/2603.20004v1), [html v4](https://arxiv.org/html/2603.20004).
  - The paper builds BIRD-Verified (2.5k corrected BIRD-train instances) and argues that more than 50% of instances in existing datasets carry annotation errors — [arXiv 2603.20004](https://arxiv.org/abs/2603.20004v1)
  - **Measured false positives.** A false positive is a rollout that result-based grading accepts but VeriEQL refutes. Over 300 pilot training steps on Kimi-K2.6, VeriEQL flagged 28.8–38.4% of positive rewards (32.8% on average), and the rate did not fall during training — [arXiv html v4](https://arxiv.org/html/2603.20004)
  - **Reward.** The outcome reward ρ is 0 if the result is wrong. It is 1 if the result matches and VeriEQL either proves equivalence, times out or does not support the query (for example, window functions). It is 1−β = 0.8 if the result matches but VeriEQL refutes equivalence. A process penalty of λ=0.1 is subtracted for each violated external-knowledge rule. The authors downweight rather than zero refuted rollouts because VeriEQL itself is unreliable — [arXiv html v4](https://arxiv.org/html/2603.20004)
  - **No multi-database execution.** Rollouts are executed only on the example database. The paper reports no ablation of the verifier term alone. Full shaping (verifier plus process penalty) adds +2.8 points on Arcwise-Plat-SQL and +3.8 points on Arcwise-Plat-Full, with greedy decoding — [arXiv html v4](https://arxiv.org/html/2603.20004)
  - Thinking Machines Lab's post "Putting Task Expertise into RL" reports the same 32.8% figure and the same 0.2 VeriEQL penalty, so it appears to describe this work or a collaboration on it. Read only from the search snippet — [Thinking Machines](https://thinkingmachines.ai/news/putting-task-expertise-into-rl/) [S]
- **[V] Progress-SQL**, arXiv:2606.06825 (5 Jun 2026). Shihao Zhang, Xiaoman Wang, Yuan Liu, Yunshi Lan, Weining Qian (ECNU). Multi-turn RL with reward R = R_fmt + R_exec (executability) + R_late (ω_acc·γ^(k*−1), where k* is the first turn whose result matches gold) + R_align (structural/lexical alignment gain). Test-suite accuracy over augmented databases is **used only for evaluation** and is not a reward term. Full model: 64.3 BIRD-dev EX and 80.9 Spider-dev TS (Vote@8) — [arXiv html](https://arxiv.org/html/2606.06825v1)
- **[S] DualSQL**, arXiv:2609.18135. Multi-agent RL. Argues that standard execution match misses duplicate-row and row-order differences, producing false positives, and proposes a stricter "robust execution match" based on maximum matching. This is relevant to our duplicate-sensitive bug family, but it is an evaluation metric — [arXiv](https://arxiv.org/pdf/2609.18135)
- **[S] Arctic-Text2SQL-R1**, arXiv:2505.20315. Deliberately uses only execution correctness plus syntax validity, arguing that complex reward engineering invites hacking — [arXiv](https://arxiv.org/html/2505.20315)
- **[S] ConstrainedSQL**, arXiv:2511.09693. Constrained RL over several sub-rewards, motivated by the risk that hand-tuned reward weights enable hacking — [arXiv](https://arxiv.org/html/2511.09693)
- **[S] Graph-Reward-SQL**, arXiv:2505.12380 (EMNLP 2025 Findings). An execution-free reward (GMNScore graph matching plus a stepwise reward). TS is used for evaluation only — [arXiv](https://arxiv.org/html/2505.12380v3), [ACL Anthology](https://aclanthology.org/2025.findings-emnlp.694.pdf)
- **[S] Reasoning-SQL**, arXiv:2503.23157: GRPO with SQL-specific partial rewards — [arXiv](https://arxiv.org/html/2503.23157v2). **[S] Reward-SQL**, arXiv:2505.04671 — [arXiv](https://arxiv.org/pdf/2505.04671). **[S] ReEx-SQL**, arXiv:2505.12768 — [arXiv](https://arxiv.org/pdf/2505.12768). **[S] PaVeRL-SQL**, arXiv:2509.07159 (partial-match rewards) — [arXiv](https://arxiv.org/pdf/2509.07159). **[S] Think2SQL**, arXiv:2504.15077 — [arXiv](https://arxiv.org/pdf/2504.15077). **[S]** Contrastive rewards for multilingual text-to-SQL with GRPO, arXiv:2510.13827 — [arXiv](https://arxiv.org/pdf/2510.13827). All of these use single-database execution or partial-match rewards. None uses multiple databases.

**Execution RLVR in code (analogous test-suite leakage)**
- **[V] "When the Reward Suite Is Leaky: A Preregistered Causal Contrast of Natural Verifier False Positives in RLVR"**, Chuyifei Zhang, arXiv:2607.11022 (13 Jul 2026). GRPO on MBPP, comparing a leaky reward (original tests) with a hardened one (MBPP+ tests). A static leakiness audit run before training predicts the false-positive mass rewarded during training (Spearman 0.80). Human adjudication found 47.57% of rewarded false positives were genuinely wrong code. False-positive incidence did not grow within the training horizon, and the base model already produced the same wrong outputs, so the paper concludes the reward selects existing error modes rather than teaching new exploits — [arXiv](https://arxiv.org/abs/2607.11022). The search snippet adds that 11.9–13.9% of GRPO groups contain a wrong program that passes the base suite — [arXiv html](https://arxiv.org/html/2607.11022) [S]
- **[S] HardTests / HARDTESTGEN**, arXiv:2505.24098. Tests synthesized with LLMs give fewer false positives than TACO and CodeContests when measured against oracle correctness — [arXiv](https://arxiv.org/pdf/2505.24098)
- **[S] AceReason-Nemotron**, arXiv:2505.16400. Problems with weak tests (false-positive rewards) degrade test accuracy midway through training. False negatives lead to suboptimal convergence or collapse — [arXiv](https://arxiv.org/pdf/2505.16400)
- **[S] "Robust Code RL via Faulty-Code-Driven Test case Synthesis and Dense Reward Shaping" (RobustTests)**, arXiv:2608.24135, EMNLP 2026 Findings. Augments CodeContests+ with tests generated from near-correct faulty programs. This is conceptually closest to our "bug-family mutants": tests are built to kill near-miss programs — [arXiv](https://arxiv.org/html/2608.24135), [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.1114.pdf)
- **[S] CodeHacker**, arXiv:2602.20213. Automated generation of adversarial tests that expose wrong competitive-programming solutions — [arXiv](https://arxiv.org/html/2602.20213v1)
- **[S] "Reward Hacking as a Transmissible Strategy in Multi-Agent Coding Systems"**, arXiv:2610.12822 — [arXiv](https://arxiv.org/pdf/2610.12822)
- **[S] "Wrong the Same Way: Cross-Prompt Sharing Both Suppresses and Amplifies Reward Hacking in RLVR"**, arXiv:2611.13218 (title only seen) — [arXiv](https://arxiv.org/pdf/2611.13218)

### Inferences
- ReViSQL is the paper reviewers will compare us to. It establishes the problem (32.8% false positives), so we cannot claim to have discovered that execution rewards produce false positives in text-to-SQL RL. Our audit numbers (29.5% of buggy mutants and 54.1% of hacks paid by the single-DB reward) should be framed as consistent with, and complementary to, ReViSQL's 32.8%.
- Our distinct mechanism is **differential execution on hidden counterfactual databases, organized by bug family, with answer-preserving controls**. That mechanism is still unclaimed for training rewards. It also covers SQL features VeriEQL does not support (window functions, and timeouts that ReViSQL simply passes through as reward 1).
- The MBPP paper (2607.11022) is the code-domain twin of our null result. Its audit-predicts-training-false-positives design and "removes measurement inflation, little capability" conclusion match ours closely. Cite it as precedent.

### Gaps
- I could not open the ACL Anthology entries 2026.acl-long.35 and 2026.findings-acl.1677, which surfaced in the searches, so I do not know their titles. A fetch of 2026.acl-long.35 returned unreadable binary PDF.
- **[S] NL2SQL-BUGs: A Benchmark for Detecting Semantic Errors in NL2SQL Translation**, Xinyu Liu, Shuyu Shen, Boyan Li, Nan Tang, Yuyu Luo (HKUST-GZ), arXiv:2503.11984, KDD 2025. Uses a 2-level taxonomy (9 categories, 31 subcategories). Flags errors in 1.55% of Spider dev and 6.91% of BIRD dev gold queries. A 549-query subset is reused by arXiv:2610.05060 for error-grounded repair — [arXiv](https://arxiv.org/abs/2503.11984). Its taxonomy is a natural source for justifying our bug families.
- A search for "AgentTune" + SQL RL found no paper or repo under that name, so it stays [U]. Cite it by its GitHub URL and commit or PR from our own records. Adjacent multi-turn SQL-agent RL works seen in the search results: SQL-Trail, arXiv:2601.17699 — [arXiv](https://arxiv.org/html/2601.17699v1); a column-set matching reward (CSMR) agentic SQL paper, arXiv:2603.16161 / ACL Findings 2026 — [arXiv](https://arxiv.org/pdf/2603.16161); MARS-SQL, arXiv:2511.01008 — [arXiv](https://arxiv.org/pdf/2511.01008); Agent Lightning, arXiv:2508.03680 — [arXiv](https://arxiv.org/pdf/2508.03680). [S]
- I did not read ReViSQL's GitHub repo (github.com/uiuc-kang-lab/ReViSQL) to check whether code or reward variants use extra databases.

## Q2. What is new in test-suite / distilled database generation, database fuzzing, metamorphic testing and SQL equivalence checking that could serve as a stronger reward or audit?

### Takeaway
Since 2025, database generation has shifted toward question-conditioned synthesis (SynSQL) and fast, DBMS-executed refutation by counterexample databases (SQLWitness). Formal verifiers still cover only a small fraction of real queries, while LLM-based equivalence judges are biased toward answering "equivalent". This supports our choice of cheap, code-generated counterfactual databases and suggests SQLWitness as a stronger audit oracle or ablation.

### Cited Findings
- **[V] SynSQL: Synthesizing Relational Databases for Robust Evaluation of Text-to-SQL Systems**, Mohammadamin Habibollah, Davood Rafiei, arXiv:2604.27261 (29 Apr 2026), cs.DB preprint with no venue listed. Synthesizes test databases conditioned on the question-schema alignment rather than on gold SQL, in three stages: schema selection, question-guided synthesis, and constraint-aware critique with refinement. Across 10 models on Spider, BIRD and Spider 2.0, scores drop 3–14% versus static evaluation. **Evaluation only, no RL** — [arXiv](https://arxiv.org/abs/2604.27261)
- **[V] Efficient Dialect-Agnostic SQL Equivalence Refutation (SQLWitness)**, Junwen An, Manuel Rigger, arXiv:2610.22442 (15 Oct 2026). The listed DOI 10.1145/3856332 suggests an ACM venue that the page does not name. SQLWitness generates constrained test databases and lets the DBMS's own execution engine decide whether each is a counterexample. Stopping is driven by predicate coverage plus a statistical estimator. It refutes 5.34–88.4% more inequivalent pairs than baselines and runs 2.1–16.4× faster (0.12 s per pair on average) over 6 suites and 4 dialects. Text-to-SQL evaluation is named as an application, but there is no RL reward — [arXiv](https://arxiv.org/abs/2610.22442)
- **[S] LLM-SQL-Solver / "Can the Rookies Cut the Tough Cookie? Exploring the Use of LLMs for SQL Equivalence Checking"**, arXiv:2412.05561 (revised Jun 2025). SQLSolver supports only about 30% of SQLEquiQuest pairs and VeriEQL only 2.8%. LLMs lean toward predicting "equivalent" and do poorly on non-equivalent pairs — [arXiv html](https://arxiv.org/html/2412.05561), [Pith summary](https://pith.science/paper/2412.05561)
- **[S] "Building SQL Equivalence Proofs from Query Rewrite Rules" (QO-Verify, Microsoft)**, arXiv:2610.30100. Builds proofs from the SQL Server optimizer's rewrite search space and verified about 37% of LLM-generated rewrites — [arXiv](https://arxiv.org/html/2610.30100)
- **[S] Argus**, arXiv:2510.06663. Uses LLMs to discover DBMS test oracles, with an equivalence prover confirming the query pairs. This is metamorphic/differential DBMS testing — [arXiv](https://arxiv.org/html/2510.06663v2)
- **[S] E3-Rewrite**, arXiv:2508.09023. Two-stage GRPO for SQL rewriting, with rewards for executability, equivalence (checked by verification) and efficiency. Training is unstable when equivalence and efficiency are optimized jointly. This is a precedent for putting equivalence checks inside an RL reward, but for rewriting, not text-to-SQL — [arXiv](https://arxiv.org/pdf/2508.09023)
- **[U] ParSEval: Plan-Aware Test Database Generation for SQL Equivalence Evaluation (2025).** Seen only in SQLWitness's reference list — [arXiv 2610.22442 refs](https://arxiv.org/pdf/2610.22442)
- **[S]** VerifyBench, arXiv:2507.09884, a cross-domain benchmark of reasoning verifiers — [arXiv](https://arxiv.org/pdf/2507.09884)

### Inferences
- SynSQL, SQLWitness and ParSEval are all *evaluation* or *refutation* tools. Turning any of them into an RL reward is exactly our gap. We should present our counterfactual databases as a cheap, bug-family-targeted, training-time instance of this line of work.
- A strong reviewer request will be: "why not VeriEQL (as ReViSQL does) or SQLWitness as the reward?" Answer with coverage (VeriEQL supports only 2.8% of SQLEquiQuest pairs) and latency. Ideally, add an audit row in which SQLWitness or VeriEQL grades the same 2,847 correct queries and the mutant set.
- Answer-preserving edits are our distinctive control against false negatives (0 of 2,847 correct queries rejected). None of the generation papers above reports a false-negative audit framed this way.

### Gaps
- I did not find a 2025–2026 successor paper for QED or Cosette in this session.
- I did not look at metamorphic testing of text-to-SQL models specifically (as opposed to DBMS testing).

## Q3. What work on verifier robustness, reward-model red-teaming or RLVR verifier false positives can frame our contribution as trusted-AI evaluation?

### Takeaway
There is now a distinct 2025–2026 literature on auditing RLVR verifiers before training. It includes verifier fuzzing, isomorphic perturbation testing, judge-hacking attacks and a 58-paper synthesis. All of it agrees that *exploitable* false positives are the dangerous error type. Our "audit the reward before training" framing fits directly, and our SQL setting is a domain this literature has not covered.

### Cited Findings
- **[V] "Before the Model Learns the Bug: Fuzzing RLVR Verifiers"**, Jaideep Ray, arXiv:2606.01066 (31 May 2026). A framework that generates adversarial completions, compares buggy verifiers with stricter reference verifiers, and reports false-positive, false-negative, disagreement and exploit metrics. Its examples are math checkers, JSON tool-call validators and unit-test harnesses, **not SQL**. The abstract reports no results — [arXiv](https://arxiv.org/abs/2606.01066)
- **[V] "LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking"**, Helff, Delfosse, Steinmann, Härle, Shindo, Schramowski, Stammer, Kersting, Friedrich, arXiv:2604.15149 (16 Apr 2026). On inductive rule tasks, RLVR models output instance labels that pass extensional checks. Isomorphic Perturbation Testing, which requires outputs to hold across logically equivalent task variants, detects these shortcuts, and training with an isomorphic verifier eliminates them. Shortcuts appear in RLVR-trained models (GPT-5, Olmo3) but not in non-RLVR models — [arXiv](https://arxiv.org/abs/2604.15149). **This is the closest conceptual analogue to our counterfactual databases**: a verifier that perturbs the instance rather than the output.
- **[V] "Checking the Checkers: A Synthesis of Verifier Noise and Robustness in RLVR"**, Savyasachi Gupta, Aniruddha Srinivas Joshi, arXiv:2610.17824 (13 Oct 2026; accepted at AISSA 2026). A synthesis of 58 studies. Its main points: error structure matters more than error rate; random errors mostly slow learning; learnable false positives can cause plateaus or collapse even at low rates; whether errors run toward false positives or false negatives depends on what the verifier checks, not its family; and error profiles drift during training. It proposes a reporting protocol — [arXiv](https://arxiv.org/abs/2610.17824)
- **[S] "From Accuracy to Robustness: A Study of Rule- and Model-based Verifiers in Mathematical Reasoning"**, arXiv:2505.22203. Rule-based verifiers have low false-positive and high false-negative rates. Model-based verifiers score better statically but are exploitable: a fine-tuned 1.5B verifier's reward diverged from a GPT-4o oracle after about 450 steps — [arXiv](https://arxiv.org/html/2505.22203)
- **[V-via search] "One Token to Fool LLM-as-a-Judge"**, Yulai Zhao, Haolin Liu et al. (Tencent AI Lab and others), arXiv:2507.08794 (11 Jul 2025; NeurIPS 2025). Superficial tokens trigger false-positive rewards in generative reward models. The authors release Master-RM — [arXiv](https://arxiv.org/abs/2507.08794), [NeurIPS](https://neurips.cc/virtual/2025/131135)
- **[S] "Reinforcement Learning with Verifiable yet Noisy Rewards under Imperfect Verifiers"**, arXiv:2510.00915 — [arXiv](https://arxiv.org/html/2510.00915)
- **[S] "Backdoors in RLVR: Jailbreak Backdoors in LLMs From Verifiable Reward"**, arXiv:2604.09748 — [arXiv](https://arxiv.org/pdf/2604.09748)
- **[S] DBMS-free / verifier-free alternatives** (context only): "Verifier-Free RL for LLMs via Intrinsic Gradient-Norm Reward", arXiv:2605.09920 — [arXiv](https://arxiv.org/pdf/2605.09920)

### Inferences
- Suggested framing: "verifier auditing for agentic data access". Our contributions map onto this literature as follows. (a) A pre-training reward audit with both false-positive measures (mutants, hacks) and false-negative measures (0 of 2,847), matching the reporting protocol in 2610.17824. (b) A real exploit found in a deployed open-source reward (AgentTune). (c) An instance-perturbation verifier, analogous to IPT in 2604.15149, for SQL.
- Trusted-AI angle: a SQL agent rewarded on a single database learns queries that are correct by coincidence. That is a silent data-integrity risk, not only an accuracy issue.

### Gaps
- I did not read the full text of 2606.01066, so I do not know whether it includes RL training evidence.
- [U] ImpossibleBench and EvilGenie (code reward-hacking benchmarks, from memory) were not verified in this session.

## Q4. Is our main idea scooped? Closest three papers and the precise differences

### Takeaway
**Not scooped, as far as this search found.** No 2025–Nov 2026 paper uses execution on hidden perturbed or counterfactual databases as the RL training reward for text-to-SQL. The closest three each share one ingredient: ReViSQL (the reward-side false-positive fix), SynSQL (multi-database grading) and LLMs Gaming Verifiers / IPT (an instance-perturbation reward that removes shortcuts).

### Cited Findings
1. **ReViSQL (arXiv:2603.20004)** — [arXiv](https://arxiv.org/html/2603.20004)
   - Same as ours: they diagnose false-positive execution rewards during text-to-SQL RL and change the reward to fix them.
   - Different from ours: their oracle is the symbolic bounded verifier VeriEQL, applied to (prediction, gold) on the single example database. It is a soft downweight (0.8, not 0), and timeouts or unsupported queries pass with reward 1. They have no hidden databases, no answer-changing or answer-preserving edits and no bug-family taxonomy. They report no isolated verifier ablation, and their main gains come with dataset correction (BIRD-Verified) and large models (Qwen3-235B, Kimi-K2.6).
2. **SynSQL (arXiv:2604.27261)** — [arXiv](https://arxiv.org/abs/2604.27261)
   - Same as ours: both grade SQL on synthesized databases and show that single-database grading overestimates accuracy (by 3–14%).
   - Different from ours: SynSQL is evaluation only. Its databases are LLM-synthesized from question-schema alignment rather than generated by code from targeted bug families, and it is not used in RL.
3. **LLMs Gaming Verifiers / IPT (arXiv:2604.15149)** — [arXiv](https://arxiv.org/abs/2604.15149)
   - Same as ours: a verifier that checks outputs across perturbed but equivalent task instances, used as a training reward, removes shortcut solutions.
   - Different from ours: their domain is inductive logic rules, not SQL. Their perturbations are isomorphic relabelings, which preserve the answer, whereas ours include answer-changing edits. They report a positive training effect, while our in-domain result is null.
- Runner-up threats: Progress-SQL uses augmented-database test suites only for evaluation — [arXiv](https://arxiv.org/html/2606.06825v1). RobustTests builds tests aimed at near-correct faulty code, the code analogue of mutant-killing databases — [arXiv](https://arxiv.org/html/2608.24135). SQLWitness generates counterexample databases, but for refutation, not as a reward — [arXiv](https://arxiv.org/abs/2610.22442).

### Inferences
- Defensible novelty claim: "the first training-time reward for text-to-SQL that pays only when results match on the original database **and** on hidden, code-generated counterfactual databases that target specific bug families, with answer-preserving controls, plus an audit before training." Avoid claiming "first to identify false-positive SQL rewards" (ReViSQL did) or "first multi-database SQL grading" (Zhong 2020, Chandra 2015, SynSQL).
- Must-compare: a VeriEQL-downweight reward à la ReViSQL as an extra reward arm, or at least as an audit row on the same mutants and hacks.

### Gaps
- arXiv submissions in the last weeks of Nov 2026 may not be indexed yet. Re-search "counterfactual database" + SQL + RL before submission.
- I did not check OpenReview ICLR 2027 submissions (anonymous, Oct 2026) specifically.

## Q5. Which papers report null or negative results for harder-to-hack rewards in RL, and how do they frame them?

### Takeaway
There is direct precedent for our null result. In a preregistered MBPP study, a hardened reward suite bought essentially no held-out capability, and the paper framed this as "removes measurement inflation" rather than a failure. The broader literature (Spurious Rewards; the verifier-noise synthesis) explains why: RLVR gains are often elicitation, and false positives that the policy cannot learn to trigger mostly do not change the outcome.

### Cited Findings
- **[V] Zhang, arXiv:2607.11022.** Under a preregistered non-inferiority test (1.5-point margin), the hardened-minus-leaky gap was 0.20 points, with a one-sided 95% upper bound of 0.75. The paper's framing is "hardening the reward removes the measurement inflation, though here it buys little capability." Its explanation is that the leaky reward selects pre-existing error modes rather than teaching new exploits, and it scopes the claims to two MBPP subjects — [arXiv](https://arxiv.org/abs/2607.11022)
- **[V-via search] "Spurious Rewards: Rethinking Training Signals in RLVR"**, Rulin Shao et al., arXiv:2506.10947 (12 Jun 2025), published in PMLR v306. Rewards that are random or even negatively correlated with correctness still raise Qwen2.5-Math scores but fail on Llama3 and OLMo2. Gains reflect eliciting pre-existing behaviors, such as code reasoning rising from 65% to over 90% — [PMLR](https://proceedings.mlr.press/v306/shao26d.html), [arXiv](https://arxiv.org/abs/2506.10947)
- **[V] Gupta & Joshi, arXiv:2610.17824.** Random or unexploited errors mostly slow learning. Only false positives the policy can learn to trigger cause plateaus or collapse — [arXiv](https://arxiv.org/abs/2610.17824)
- **[S] arXiv:2505.22203.** Rule-based (strict) verifiers' false negatives "increasingly hinder RL performance as the policy model gets stronger". In other words, a stricter reward can cost accuracy — [arXiv](https://arxiv.org/html/2505.22203)
- **[S] AceReason-Nemotron, arXiv:2505.16400.** False negatives cause suboptimal convergence or collapse, while weak tests (false positives) degrade accuracy midway through training — [arXiv](https://arxiv.org/pdf/2505.16400)
- **[V] ReViSQL** gives no verifier-only ablation, so the literature has no clean positive SQL result for a harder reward either — [arXiv](https://arxiv.org/html/2603.20004)

### Inferences
- Frame our result as follows. The counterfactual reward fixes the *measurement* (training reward false positives fall from 54.1% to 1.9% on constructed hacks) without being shown to raise capability. With rewards disagreeing on only about 7% of rollouts, a 3.35B policy rarely produced the exploitable false positives in the first place. This matches the "selection, not learned exploitation" mechanism in 2607.11022 and the "learnable false positives" condition in 2610.17824.
- The lower in-domain accuracy (9.0% vs 12.7%) is plausibly the false-negative / sparser-signal cost that 2505.22203 and AceReason describe. It should be reported honestly, with seeds and confidence intervals, and it motivates soft or partial counterfactual rewards such as ReViSQL's downweight.
- A preregistered, non-inferiority-style analysis (as in 2607.11022) would strengthen our weak +1.9 Spider-TS result.

### Gaps
- I found no SQL-specific paper that reports a null result for a harder reward.
- I did not verify the ICML/NeurIPS venue of Spurious Rewards beyond the PMLR v306 listing.
