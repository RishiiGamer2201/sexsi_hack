# Amazon Trusted AI Symposium 2027: audience, framing and presentation (poster / demo / talk / artifacts)

Compiled 2026-11-21. This file extends `../amazon_symposium_prior.md`, which already covers the full 2027 call text, the 2026 edition, the 7 known accepted works, the Chatterbox/Nova poster and the topic mapping. That material is not repeated here. "VERIFIED" means read on an official or primary page today; "INFERENCE" or "GUESS" means not stated by any source.

## 1. What exactly does the 2027 call say about format, presentation, selection, travel and location?

### Takeaway
I re-fetched the official page today and it confirms the prior notes. It is a **call for posters**: one day, invitation-only, **Feb 18 2027, New Delhi**, deadline Nov 30 2026, notification Dec 31 2026. The page says **nothing** about orals, lightning talks, demos, poster size, travel support, selection criteria or keynotes ("Coming soon"). Plan for a poster session. Treat any talk or demo slot as an unconfirmed bonus.

### Cited Findings
- The page header reads "Call for posters: Open". Posters "must be submitted via email to trusted-ai-symposium@amazon.com". "All submission is non-archival. Double submission is acceptable" — [Amazon Science, TAI Symposium 2027](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)
- Up to 4 pages, plus references and appendices; NeurIPS LaTeX template; PDF; standard academic structure; author names, affiliations and email required — [same page](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)
- "Jointly hosted by Amazon Web Services (AWS) Public Policy and the Amazon AGI team". Amazon advisory committee: Rahul Gupta and Michael Johnston. IIT Delhi: Conference Chair Prof. Arpan Kumar Kar; Programme Chairs Prof. Agam Gupta and Prof. Arghya Ray; Prof. P. V. Ilavarasan (HoD, Management Studies) — [same page](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)
- "Due to high demand, invitations are issued selectively, and only confirmed attendees will receive detailed event logistics via email in early February 2027." Keynotes: "Coming soon". The RSVP deadline is listed with no date — [same page](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)
- **Not stated on the page** (checked today): oral, talk, lightning or demo formats; poster size; travel or accommodation support; evaluation criteria; specific venue — [same page](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027)
- The 2026 day was talks plus networking breaks "culminating in a poster session". Only 1 attendee's post reports this — see prior notes, [LinkedIn post](https://www.linkedin.com/posts/vagelispapalexakis_llm-jailbreaks-hallucination-activity-7420021181799510017-wTVe)
- The only real 2026 poster we have (Amazon Nova RAI + Chatterbox) was 48x36 in landscape — [Red Hat PDF](https://www.redhat.com/rhdc/managed-files/Chatterbox_Amazon_Nova.pdf)
- For comparison, NeurIPS 2025 main-conference posters are 24W x 36H in portrait, hung with push pins and no adhesive. The NeurIPS 2026 page gives workshop posters as 61 x 85 cm portrait — [NeurIPS 2025 Poster Instructions](https://neurips.cc/Conferences/2025/PosterInstructions), [NeurIPS 2026 Poster Instructions](https://neurips.cc/Conferences/2026/PosterInstructions) (search snippets; not opened in full)

### Inferences
- The session will most likely be poster-only, with the day's talks given by keynotes or invited speakers. So the poster, and a 2-minute walk-up pitch, is the main thing to get right.
- The poster size is unknown. A 2026 Amazon-authored poster was 48x36 landscape, while NeurIPS-style boards are portrait. Build the poster so it can be re-flowed: 3 columns landscape or 2 columns portrait. Ask the organisers for the size in the acceptance email reply (around Dec 31).
- Travel to Delhi is not funded by anything we can see. Assume it is self-funded.
- Because selection is "selective", the PDF is our only pitch. It has to read well for a mixed Amazon-scientist and IIT Delhi management/IS panel; see section 2.

### Gaps
- Number of accepted posters, review rubric, whether any submitter gets a talk or lightning slot, and whether demos or laptops are allowed at the poster boards. None of these is published anywhere I could find.
- Whether remote or virtual presentation is allowed. Not stated.

## 2. What do Amazon's trusted-AI researchers prize right now, and is there a natural link to automated reasoning / formal verification?

### Takeaway
Amazon's public trusted-AI messaging in 2025–26 rests on three things:
1. **Verification and automated reasoning** (Bedrock Guardrails Automated Reasoning checks; Byron Cook's "neurosymbolic AI" as the path to trust).
2. **Evaluation of agents in production** (AWS "lessons from building agentic systems at Amazon"; AgentCore Evaluations).
3. **Safety evaluation during model building** (Nova 2.0 Lite frontier-safety evaluation; continuous red-teaming of Nova 2 checkpoints).

Our counterfactual-DB reward is a lightweight, **test-based cousin of bounded SQL equivalence checking**. That is a real and citable bridge to formal verification (VeriEQL/SpotIt). Amazon also has its own text-to-SQL error-detection work (SQLENS, NeurIPS 2025). Our project can be framed as "verification of agent outputs (SQL is code) before they become rewards".

### Cited Findings
**Automated reasoning (Amazon's flagship trust theme)**
- Automated Reasoning checks in Amazon Bedrock Guardrails went GA on Aug 6 2025, after a re:Invent 2024 preview. They validate generative-AI outputs against an "Automated Reasoning policy" that encodes domain rules, and AWS claims "up to 99% verification accuracy" — [AWS What's New, Aug 2025](https://aws.amazon.com/about-aws/whats-new/2025/08/automated-reasoning-checks-amazon-bedrock-guardrails); [AWS News Blog](https://aws.amazon.com/blogs/aws/minimize-ai-hallucinations-and-deliver-up-to-99-verification-accuracy-with-automated-reasoning-checks-now-available)
- Natural-language test Q&A generation for these policies was added in Nov 2025, and the Sydney region on Jun 16 2026 — [AWS What's New Nov 2025](https://aws.amazon.com/about-aws/whats-new/2025/11/automated-reasoning-checks-include-natural-language); [AWS What's New Jun 2026](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-guardrails-sydney)
- Stated limits: English (US) only, no streaming APIs, no prompt-injection protection — [Bedrock user guide](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html) (search summary; not opened in full)
- Byron Cook (introduced as "Amazon Distinguished Scientist and VP"), Feb 17 2026 — [All Things Distributed](https://allthingsdistributed.com/2026/02/a-chat-with-byron-cook-on-automated-reasoning-and-trust-in-ai-systems.html):
  - "That lack of trust is often what's blocking deployment into production."
  - "The only way to deliver that much-needed trust is through neurosymbolic AI."
  - "the definition of good and bad behavior is a specification"
  - "we can simply apply the previously deployed automated reasoning tools to the changes made by agentic tools"
  - "combine automated reasoning tools like Lean with reinforcement learning"
  - "We have some great stuff happening within Kiro and Amazon Nova in this space."
  - SQL and databases are not mentioned.

**SQL verification bridge (formal methods meets text-to-SQL evaluation)**
- **SpotIt** (ICLR 2026) replaces test-based text-to-SQL scoring with bounded SMT verification: it searches for a database that distinguishes the predicted query from the gold query. Built on VeriEQL. Across 10 methods on BIRD, reported accuracy **drops 11.3%–14.2%** compared with the official test-based evaluation, and when they disagree it is often the **gold SQL** that is wrong — [arXiv 2510.26840](https://arxiv.org/abs/2510.26840); [ICLR 2026 poster](https://iclr.cc/virtual/2026/poster/10007969)
- **SpotIt+** mines constraints from example DBs, with an LLM filter for genuine domain properties, so the counterexample DBs look realistic — [arXiv 2603.04334](https://arxiv.org/abs/2603.04334)
- **VeriPIE** uses bounded-equivalence counterexamples as evidence for choosing between text-to-SQL candidates — [arXiv 2610.17493](https://arxiv.org/abs/2610.17493)
- **Amazon's own text-to-SQL reliability work:** SQLENS, "an end-to-end framework for fine-grained detection and correction of semantic errors in LLM-generated SQL" (Gong, Lei, Qin, Vaidya, Narayanaswamy, Kraska; NeurIPS 2025). It reports up to 20% better execution accuracy for existing systems — [Amazon Science](https://www.amazon.science/publications/sqlens-an-end-to-end-framework-for-error-detection-and-correction-in-text-to-sql)
- **Amazon enterprise text-to-SQL:** "Beyond the harness" (COLM 2026 workshop) runs on 5,176 production queries from "a major online retailer". It is scored by **AST similarity**, not execution, and its BEAVER gain is reported as not significant (p = 0.12) — [Amazon Science](https://www.amazon.science/publications/beyond-the-harness-end-to-end-optimization-of-context-artifacts-for-enterprise-text-to-sql)

**Evaluation and agent-safety themes**
- AWS's "Evaluating AI agents: Real-world lessons from building agentic systems at Amazon" (about Feb 2026) argues that black-box, final-outcome-only evaluation hides why agents fail. It covers standardised metrics, use-case-specific assessment and human oversight — [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon) (search snippet; not opened in full)
- Amazon ships agent evaluation as a product: Bedrock AgentCore Evaluations and Strands Evals — [AWS ML Blog: AgentCore Evaluations](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations); [Strands Evals guide](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-for-production-a-practical-guide-to-strands-evals) (search snippets)
- Nova 2.0 Lite was evaluated under Amazon's Frontier Model Safety Framework (CBRN, offensive cyber, automated AI R&D) using benchmarks, expert red-teaming and uplift studies; arXiv Jan 27 2026 — [arXiv 2601.19134](https://arxiv.org/abs/2601.19134)
- The Nova technical report describes FLIRT-based automated red-teaming — [arXiv 2506.12103](https://arxiv.org/abs/2506.12103)
- External framing the reviewers will recognise: NIST CAISI's series "Cheating On AI Agent Evaluations" (Nov 28 2025) — [NIST CAISI](https://www.nist.gov/caissi/1-background-ai-models-can-cheat-evaluations):
  - Reward hacking now appears in evaluations, not only in training.
  - "task implementations and scoring functions must capture the evaluator's intent"
  - Cheating "can mean that an evaluation is not measuring what we think it is"
  - Cheating is defined by the violation of evaluator intent, not by whether the model knew.

### Inferences
- **The cleanest bridge to Amazon's verification theme:**
  - Our counterfactual-DB grading is **differential testing**: grade the SQL on K hidden DB variants.
  - SpotIt/VeriEQL is **bounded symbolic verification**: search *all* small DBs for a distinguishing instance.
  - Position ours as the cheap, solver-free, RL-throughput point on a spectrum: single-DB EX < counterfactual-DB (ours) < bounded SMT equivalence (SpotIt) < full equivalence proof (undecidable in general).
  - This lets us claim "verification-flavoured reward" **without** claiming formal methods, and it hands Amazon AR people an obvious next step: a SpotIt-style solver generating the counterfactual DBs, or used as an occasional audit oracle.
  - Cite SpotIt's 11–14% accuracy drop as independent evidence that single-DB execution match over-credits.
- Map Cook's "specification" line onto our work: the question plus the gold SQL is the spec, and a single DB is a weak test of it. That is one sentence in the intro, not a section.
- **SQL is code.** Cook's "apply automated reasoning to the changes made by agentic tools", Amazon's SQLENS, and the committee's Nova AI Challenge (safe code generation; see prior notes) all point at verifying code produced by agents. Lead with "verifying the code an agent writes before paying it reward".
- The **AgentTune disclosure** is a concrete instance of NIST's "scoring functions must capture evaluator intent": a public reward library that scored something other than what it claimed. Presented as responsible disclosure, fixed upstream, it shows red-teaming and responsible-AI practice, which this audience values.
- **Do not overclaim.** Bedrock AR checks verify natural-language claims against policies; they do not check SQL. Say "in the spirit of", not "integrates with".

### Gaps
- I found no amazon.science post that ties automated reasoning to SQL or text-to-SQL specifically. The SQLENS page did not show its method in the fetched text, so whether it uses formal methods is unknown.
- I could not open the full AWS agent-evaluation blog text; findings come from snippets.
- Michael Johnston's and Rahul Gupta's 2026 publications beyond the Nova Challenge and the Chatterbox poster were not re-searched; see prior notes.

## 3. How should we frame our project (including the null training result) for this audience?

### Takeaway
Lead with **"audit the reward before you train"** and **"a verifiable reward is an evaluation product"**, not with "RL improves text-to-SQL".
- The null training result becomes the evidence that the audit is cheap insurance: you learn the reward is gameable *before* spending GPU hours, and the counterfactual reward does not cost accuracy.
- The small Spider transfer gain is a secondary, honestly hedged observation.
- Negative and null results have recognised homes in ML (ICBINB), and the 2026 accepted set already included audits and measurement papers.

### Cited Findings
- The ICBINB workshop series (NeurIPS 2021–23; ICLR 2025–26) explicitly solicits negative results, failure modes and empirical falsification. Its ICLR 2026 edition ("Where LLMs Need to Improve") took 4-page short papers with a non-archival option — [ICLR 2026 ICBINB CFP](https://groups.google.com/g/ML-news/c/ZOPDi5FT39M); [NeurIPS 2023 ICBINB CFP](https://mailman.srv.cs.cmu.edu/pipermail/connectionists/2023-August/040207.html); [NeurIPS 2022 CFP](https://mailman.srv.cs.cmu.edu/pipermail/connectionists/2022-August/038485.html)
- ICBINB awards include an "Entropic Award" for the most surprising negative result and a "Didactic Award" for the most pedagogical paper — per the search summary of the CFPs above (award names not re-verified on a CFP page)
- Amazon's own poster at the 2026 symposium (Nova RAI + Chatterbox) is an operational-lessons poster:
  - claim-style "Learnings" subheadings, such as "Average safety robustness does not imply across-the-board enhancement";
  - the finding that the RL-time judge "needed updates ... to maintain a higher than 95% accuracy".
  - [Red Hat PDF](https://www.redhat.com/rhdc/managed-files/Chatterbox_Amazon_Nova.pdf)
- A recent Amazon text-to-SQL paper openly reports a non-significant public-benchmark result (p = 0.12) — [Amazon Science: Beyond the harness](https://www.amazon.science/publications/beyond-the-harness-end-to-end-optimization-of-context-artifacts-for-enterprise-text-to-sql)
- Concurrent external work frames reward hacking as an evaluation-integrity problem: RewardHackingAgents treats "evaluation integrity as a first-class benchmark outcome" — [arXiv 2603.11337](https://arxiv.org/abs/2603.11337). A 17-model study finds reward hacking about 10x more frequent on open-ended research-pipeline tasks — [arXiv 2609.28614](https://arxiv.org/abs/2609.28614). Both come from search snippets and should be checked before citing.

### Inferences (recommended framing)
- **One-sentence pitch (draft):** "Execution-match rewards for SQL agents pay for queries that are right by luck. We grade the final SQL on hidden counterfactual copies of the database, audit rewards before training, found and disclosed a live exploit in a public reward library, and show the safer reward costs nothing in accuracy."
- **Contribution order for this audience:**
  1. The **reward audit** (an evaluation and red-teaming artifact): false-accept rates of each reward on lucky, hacked and wrong SQL.
  2. The **disclosed AgentTune exploit**: a real-world red-team finding, responsibly disclosed and fixed upstream.
  3. The **counterfactual-DB reward**: verification by counterfactual execution, positioned against SpotIt.
  4. Training: the null in-domain result plus the small Spider transfer.
- **Null result language:**
  - Say "no measurable in-domain accuracy cost from the stricter reward" (the safety tax is about 0).
  - Frame the null as "the audit, not the training run, is where the value is": it costs CPU-minutes, while training costs GPU-hours.
  - Use a "monitoring metric" angle: the single-DB vs counterfactual reward gap, logged per checkpoint, is a cheap reward-hacking alarm. This mirrors the Chatterbox "evaluate every checkpoint" practice.
  - Do not call the Spider gain significant unless the CI excludes 0. Amazon's own papers report p-values honestly.
- **Governance hook for the IIT Delhi management/IS chairs:** one paragraph on auditability. Wrong analytics from an SQL agent is a silent business and governance risk, and a pre-training reward audit report is an accountability artifact. The prior notes have the India AI Governance Guidelines tie-in. Keep it to 2–3 sentences.
- **Claim-style section headers** in the paper and on the poster, as Amazon's own poster does. For example:
  - "Single-DB rewards pay for lucky SQL"
  - "Counterfactual grading closes the gap at no accuracy cost"
  - "A public reward library was exploitable (now fixed)"

### Gaps
- I found no source on how this panel scores null results specifically. The framing advice is inference from the venue's mixed audience and Amazon's own poster style.

## 4. What does a strong poster, live demo and short talk look like for safety/evaluation work?

### Takeaway
Use a **#betterposter-style** layout:
- One plain-English main finding in huge type, with a single "lucky SQL passes on DB0, fails on DB1–DBk" figure.
- Side columns holding the audit table, the exploit case study and training curves.
- A QR code to the paper, repo and demo.

Pair it with a **"try to fool the reward"** laptop demo, since visitors come to poster sessions to interact. Prepare a 30-second and a 2-minute version of the pitch.

### Cited Findings
- #betterposter (Mike Morrison) prints the **main finding in large type and plain language** in the centre, so a passer-by gets it in seconds. Templates ask for the finding "in plain English" with key words bolded, and put a **QR code** in the footer ("Scan QR code to get the full paper") — [Overleaf Better Poster template](https://www.overleaf.com/latex/templates/better-poster-latex-template/gmkgjvxqbyyt); [MIT Comm Lab on #betterposter / #evenbetterposter](https://mitcommlab.mit.edu/be/2023/09/27/toward-an-evenbetterposter-improving-the-betterposter-template) (search snippets; not opened in full)
- Point a QR code at a link hub (Drive folder, LinkTree) so one code serves several items — [PosterNerd billboard posters](https://www.posternerd.com/tutorials/billboard-posters) (search snippet)
- The MIT Comm Lab critique says the #betterposter centre panel should still carry evidence, not only a slogan — [MIT Comm Lab](https://mitcommlab.mit.edu/be/2023/09/27/toward-an-evenbetterposter-improving-the-betterposter-template) (title/snippet only; content not read)
- Amazon's own 2026 symposium poster: 3 columns landscape; numbered claim-style learnings; 3 simple matplotlib plots; 2 bold takeaways in the conclusion — [Red Hat PDF](https://www.redhat.com/rhdc/managed-files/Chatterbox_Amazon_Nova.pdf)
- NeurIPS poster logistics: push pins only, no adhesive posters — [NeurIPS 2025 Poster Instructions](https://neurips.cc/Conferences/2025/PosterInstructions) (search snippet)

### Inferences (concrete design)
- **Poster layout** (landscape 3 columns, or portrait re-flow):
  - *Centre:* main finding, e.g. "**1 in N 'correct' SQL rewards is luck.** Grading on hidden counterfactual DBs catches it — at no accuracy cost." Use our real number. Under it, Fig. 1: one real lucky query, a green tick on DB0 and red crosses on 2–3 counterfactual DBs.
  - *Left:* problem and threat model (an RL policy optimising a proxy reward), then the method in 3 boxes.
  - *Right:*
    - the audit table (false-accept per reward);
    - an "Exploit found in the wild" box (AgentTune, disclosed, fixed upstream, with the commit or issue link);
    - the training panel with honest null plus transfer and CIs;
    - "Limitations" in 2 bullets.
  - *Footer:* QR code to a link hub (paper PDF, repo, demo URL, audit CLI), affiliations, and the Amazon TAI 2027 logo text if allowed.
  - Reuse the paper's TikZ figures directly; the NEURIPS_PAPER_RULES §22 "poster-readiness" already plans this.
- **Live demo, "Can you fool the reward?" (highest-leverage artifact for a poster session):**
  1. The visitor picks a question and types or edits SQL, or picks from pre-made "hacks" (hard-coded literal, LIMIT 1 guess, dropped JOIN that happens to match).
  2. The side-by-side shows the single-DB EX reward (✓) against the counterfactual reward (✗), with the counterfactual DB rows that broke it.
  3. A running scoreboard of "visitors who fooled the counterfactual reward" doubles as honest red-teaming. Log the attempts; they can become an appendix or follow-up.
  4. It must run **offline on a laptop**: SQLite plus pre-built counterfactual DBs, no GPU, no network. Conference Wi-Fi in a large Delhi venue is a risk (GUESS).
  5. Host the same app online behind the QR code: a static page with sql.js/SQLite-WASM, or a small HF Space under the team's `sqlcf-lexsi` org.
- **Talk (if a slot is offered; none is announced):**
  - 3 slides for a lightning slot: problem with the lucky query, method plus audit number, exploit plus null.
  - 6–8 slides for 10 minutes.
  - Open with the live "fool the reward" query.
- **Walk-up pitch scripts:**
  - 30 s: problem, number, fix.
  - 2 min: add the exploit story and "audit before you train".
  - Have one "so what for Amazon" line ready: verification of agent-written code before it becomes reward, a cheap cousin of SMT equivalence checking, and complementary to SQLENS-style error detection.

### Gaps
- I did not open the full #betterposter or MIT pages; findings are from snippets.
- I found no official NeurIPS or ICLR demo-track guidance specific to safety/evaluation demos. The demo design above is inference.
- It is unknown whether the venue will provide power or tables at poster boards (GUESS: bring a charged laptop and a phone backup).

## 5. Which artifacts increase impact (live demo, audit tool, leaderboard, open-source package)?

### Takeaway
Ranked by value for effort before Feb 18 2027:
1. A **pip-installable reward-audit CLI/package** that takes any reward function plus a text-to-SQL dataset and returns false-accept/false-reject rates on counterfactual DBs.
2. The **"fool the reward" web demo**, the same code in the browser.
3. A **public disclosure write-up** of the AgentTune exploit, linking the upstream fix.
4. A small **"reward robustness" leaderboard** of public text-to-SQL reward functions, only if time allows.

Amazon already sells evaluation as a product (AgentCore Evaluations, Strands Evals, Bedrock AR checks), so "evaluation tooling you can drop into an RL pipeline" speaks this audience's language.

### Cited Findings
- AWS frames agent evaluation as a production product and a blueprint (AgentCore Evaluations; Strands Evals; "production-ready evaluation framework") — [AWS ML Blog: AgentCore Evaluations](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations); [AWS ML Blog: Building trust in AI agents](https://aws.amazon.com/blogs/machine-learning/building-trust-in-ai-agents-a-production-ready-evaluation-framework-with-amazon-bedrock-agentcore/) (search snippets)
- Bedrock AR checks are shipped as a policy-plus-validator API that is "billed per validation request", which is verification packaged as a service — [Bedrock user guide](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html) (search summary)
- The 2027 benefits include "Potential pathways to ongoing partnerships with Amazon" and Amazon Research Award information for India — [Amazon Science 2027 page](https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027) (see prior notes for quotes)
- Related tooling exists and should be compared against, not ignored: SpotIt / SpotIt+ (open bounded-verification evaluators for text-to-SQL) — [arXiv 2510.26840](https://arxiv.org/abs/2510.26840); [arXiv 2603.04334](https://arxiv.org/abs/2603.04334). An "Agent-Eval Checklist" with automated benchmark-flaw discovery — [arXiv 2605.12673](https://arxiv.org/html/2605.12673) (search snippet; not verified)

### Inferences
- **The audit package is the artifact Amazon people can actually use.** It turns the paper's method into "run this before your GRPO job". Include:
  - a 10-line README example;
  - a JSON report output (an "audit card");
  - adapters for common RL reward signatures (TRL/verl-style `reward_fn(prompts, completions)`).
  - One command, one table. This matches "evaluation-as-a-product" and gives the ARA and partnership hook something concrete.
- **The audit card as a governance artifact:** a one-page per-reward report (false-accept rate, exploit classes tested, DB variants used, date, version). It speaks to the IIT Delhi governance chairs and to Amazon's RAI documentation habits (model cards in the Nova tech report). This is low cost: render the JSON to Markdown.
- **The demo reuses the package.** The same Python works in Pyodide, or the logic can be ported to sql.js, which avoids a second codebase. Pre-compute the counterfactual DBs for about 20 demo questions.
- **Leaderboard: lowest priority.** It needs maintenance, and with few public SQL reward libraries it may have about 3 rows. A static table of "rewards we audited" in the README gives about 80% of the value.
- **Nova touchpoint (optional):**
  1. Score Nova (Lite or Micro) zero-shot SQL with both rewards and show that the single-DB reward over-credits it too.
  2. Put that one row in the audit table and on the poster. Amazon AGI hosts the event, so this is a cheap relevance signal.
  3. It needs the owner's sign-off and credentials. Per team rules, no cloud action without approval, and RunPod is never to be used for this.
- **Disclosure page:** a dated timeline (found, reported, fixed upstream, commit link) with no exploit code beyond what the upstream fix already makes public. This shows responsible red-teaming practice.
- **QR targets:** put all of the above behind one link hub so the poster carries a single QR code.

### Gaps
- No source states what artifacts this symposium's reviewers reward. The ranking above is inference from Amazon's product and blog emphasis and from general poster-session dynamics.
- Whether the venue allows demo laptops or extra screens at poster boards is unknown.
