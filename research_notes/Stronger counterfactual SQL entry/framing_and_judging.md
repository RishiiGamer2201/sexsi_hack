# Framing and Judging: Presenting a Strong Reward Audit + Null Training Result to Lexsi Track 3 Judges

## Q1. What do Lexsi's judges reward? (official criteria, rubric, required artifacts, timeline, prizes)

### Takeaway
Lexsi publishes four judging dimensions: **Write-up clarity, Practical usefulness, Code/notebook quality, Overall review**. No weights are given. Scoring is double-blind, each team gets several judges, and normalized averages pick 10–20 Demo Day teams. The required HF article has a fixed 9-section checklist. One section explicitly asks for "experiments run, findings and what else was tested", which gives a null result an official slot. Two rules cut against a null training result: you must show "before-and-after metrics (more than one metric)", and you must explain "how the resulting model is meaningfully better for usage". The write-up has to meet both head-on.

### Cited Findings
**Judging process (verified, from the official kickoff slides):**
- "How judging works": first, labelling. "Our internal team verifies each submission's validity (public artifacts, submitted write-up, checklist, no duplicates) and tags it to the closest track or sub-track." — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- "A pool of judges (startup founders, academics, industry research labs and the organising orgs' research teams) scores submissions double-blind. Each team receives more than one score, and normalized averages decide the 10–20 teams invited to Demo Day." — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- Criteria listed on that slide: **"Write-up clarity · Practical usefulness · Code/notebook quality · Overall review"**. The slide gives no weights or scale. — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- Main site FAQ: "Judges will score each team numerically on a fixed scale." Also: "A subset of the highest-scoring teams may be invited to present a live demo, after which the judges will discuss and decide the final winners." Also: "When teams are close, the judges discuss them together before deciding." — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- No separate public judging or rubric page exists. `hackathon.lexsi.ai/rules` returned 404 when fetched directly, because the rules are a section of the single-page site. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)

**Required HF article sections (verified, kickoff slides "Submission checklist"):**
1. Problem statement and approach, in brief
2. Hackathon repos used: which ones, for what, and which features
3. Models used and their licenses
4. Datasets and benchmarks used and their licenses
5. Model artifacts (weights, adapters, …) public, as an HF collection
6. Data artifacts (datasets, logs, benchmarks, …) public, as an HF collection
7. **Experiments run, findings and what else was tested**
8. **With more credits: your approach, before and after results**
9. Teammates tagged

Source: [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/). The same slides summarise the HF article as "What you built, how, why, and what else you tried". — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)

**Rules and submission requirements (verified, main site):**
- "Showcase **before-and-after metrics** (more than one metric)." — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- The write-up must cover "the metrics chosen and why, the approach and rationale behind the choice of datasets, tasks, and models" and "how the resulting model is meaningfully better for usage." — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- "[Optional but preferred] An ROI comparison of a closed-source model vs. the fine-tuned/aligned smaller model". This maps directly onto our Command A ($4.25/1k) vs Tiny Aya ($0.06/1k) comparison. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- Submission package:
  - abstract under 500 words
  - public, un-gated HF model collection
  - public HF dataset collection (datasets, logs, traces, benchmarks)
  - write-up as an HF article, or a GitHub README if HF articles aren't accessible
  - GitHub repo "with reproducibility notes in the README"
  - list of repos and models used, track(s), and problem statements
  - only the latest submission before the deadline counts

  — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- Model rule: the main model must be a dense open-weights Cohere Labs model (Tiny Aya Base/Global/Fire/Water/Earth, or Aya Expanse 8B/32B). Other models may only be supplements, e.g. teacher or judge. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- Everything (models, adapters, logs, datasets) must be on HF. Projects must be deployed publicly by the deadline. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- Repo-chaining rule, where the two official sources **conflict**:
  - The main site says submissions must chain track repos into a real pipeline, with a "minimum 2 repos used together (except Track 3)", and 3 or more preferred. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
  - The kickoff slides say only "Use at least 2 repos as one connected system", with no Track 3 exemption shown. — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- No video is required anywhere in the published rules. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)

**Track 3 wording (verified):**
- Track 3 "Agentic Fine-tuning" uses AgentTune and AuditKIT. Its description: "A library for post-training agents for better tool calls, syntax, and efficiency … to reduce redundant or incorrect tool calls and to improve reliability." — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- **#6 Data and database agents:** "Train an agent that answers business questions by querying databases or APIs (finance, operations, analytics), rewarded on verified results." — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- **#9 Reward design and reward-hacking defences:** "Design rewards (process rewards, LLM judges, groundedness checks) that raise real task success without being gamed." — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)

**Timeline (verified):**
- Build period: Nov 1–14.
- Submission deadline: end of day Nov 14, AoE. The submission form is shared by email a couple of days before.
- Judging: Nov 15–16. Demo Day teams are announced Nov 16.
- **"Shortlisted teams get Nov 16 – 21 to prove their thesis, then present a live demo"**, plus a further $200 in HF credits.
- Demo Day and final judging: Nov 22, in person (Polaris School of Technology, Bengaluru) or online.

Sources: [hackathon.lexsi.ai](https://hackathon.lexsi.ai/); [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)

**Prizes (verified):**
- 1st: $3,662 ($1,750 each in Lexsi Labs and Cohere credits, plus 6 months of HF Pro per teammate).
- 2nd: $2,662. 3rd: $1,962. 4th: $1,362. 5th: $1,162.
- Demo Day finalists: $200 HF credits.
- Possible interviews at Lexsi Labs.

Source: [hackathon.lexsi.ai](https://hackathon.lexsi.ai/). Eventbrite lists "30000+ in prizes and credits" in total. — [Eventbrite listing](https://www.eventbrite.com/e/lexsi-ai-safety-and-alignment-hackathon-tickets-2003844994320)

**What Lexsi's own stack and docs emphasise (verified):**
- The kickoff slides list AlignTune features including an "Alignment audit: Reward hacking · sycophancy · refusal collapse" and "27+ reward functions: verifiable math · code · SQL". Reward hacking is therefore a named concern in their own tooling. — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- AgentTune docs:
  - It "builds agentic workflows, then trains, evaluates, distills, and self-heals them". It runs GRPO/PPO/DPO/RLOO/BCO on TRL, with an `EventLog` trajectory format.
  - A notebook topic named "reward defenses" exists.
  - There is a **Known Issues** page listing what "a code-level audit found broken or orphaned", and the docs describe bugs surfaced while running notebooks, with links to upstream fixes.

  — [agenttune.lexsi.ai](https://agenttune.lexsi.ai)
- Lexsi Labs papers (2025–2026) include:
  - "Ensembling Tabular Foundation Models: A Diversity Ceiling and A Calibration Trap", a paper framed around limits and traps.
  - "Beyond Uniform Credit: Causal Credit Assignment for Policy Optimization".
  - "Beyond KL Divergence: Policy Optimization with Flexible Bregman Divergences for LLM Reasoning".
  - "Interpretability as Alignment".
  - "Provenance-Grounded Gating … in Synthetic Post-Training Data Curation".

  None of the listed titles is explicitly about reward hacking. — [Lexsi research papers](https://lexsi.ai/resources/research-papers)

### Inferences
- **The four criteria favour our entry if the write-up is disciplined.** "Write-up clarity" and "Code/notebook quality" reward `verify_all.py` and the Pyodide demo directly. "Practical usefulness" is where the null training result costs the most. Lead "practical" claims with the audit tool, the AgentTune reward vulnerability, and the ROI comparison.
- **"Double-blind" means judges see only the artifacts.** The write-up has to stand alone. Don't depend on Discord context or the team's reputation.
- **The "meaningfully better for usage" rule is the main compliance risk.** We must show base vs trained Tiny Aya, not only single-DB vs counterfactual. If both adapters beat the base model, that alone satisfies "before-and-after".
  - Quote at least two metrics, e.g. verified accuracy and hack-payout rate or false-reject rate.
  - Use the ROI comparison to argue usefulness.
- **Problem #9 asks for rewards that "raise real task success without being gamed."**
  - We clearly showed "without being gamed": hacks paid fall from 54.1% to 1.9%, with 0/2847 false rejects.
  - We did not show "raise real task success" through training.
  - Be explicit that the claim covers one half of #9. Then show the other half on some axis: test-time verification, rejection sampling, or the Nov 16–21 thesis period.
- **Checklist section 8 ("With more credits: your approach, before and after results") and the Nov 16–21 "prove your thesis" window are an official slot for a falsifiable next step.** For example: "train only on high-disagreement prompts; prediction: gap > X pts". Pre-stating it there turns the null into a thesis that shortlisting would let us test.
- **The repo-rule conflict has a cheap fix.** Use and name both AgentTune and AuditKIT in section 2, with the specific features used, so the submission passes the slide version of the rule either way.
- **Responsible disclosure fits Lexsi's culture.** Lexsi publishes a Known Issues page and links upstream fixes. Writing up the AgentTune SQL-reward exploit with a minimal repro and a suggested patch therefore matches how they work. Offer to file it upstream; per the constraints we post nothing ourselves.

### Gaps
- No weights or numeric scale were found for the four criteria. The FAQ says only "fixed scale".
- No Discord announcements were publicly indexed. Discord was not accessed, per the no-login constraint.
- Not confirmed whether the 500-word abstract is a form field or part of the article.
- Not confirmed whether Track 3 is truly exempt from the 2-repo minimum, given the conflict above.
- The AgentTune docs page did not document its SQL reward function in detail, so the reward-exploit claim relies on the team's own code reading.

## Q2. How do strong ML papers and posts present null/negative results and reward audits?

### Takeaway
The well-received pattern has four parts:
1. Report the mechanism-level finding with concrete, quantified, linkable examples (METR).
2. Treat the surprising or null training outcome as a finding about how RL works, backed by a mechanism diagnostic and ablation (Spurious Rewards).
3. Ground the "why" in theory that predicts it (Razin et al.: reward variance and disagreement, not accuracy, drives optimization).
4. Give recommendations and falsifiable next steps.

Pre-registration lends credibility because it shows the null was not cherry-picked.

### Cited Findings
**Negative-results venues legitimise the genre:**
- The ICLR 2026 ICBINB workshop invited "negative results and unexpected challenges in developing, aligning, scaling, evaluating, and deploying" LLMs. It gave an "Entropic Award" for the most surprising negative result and a "Didactic Award" for the most pedagogical paper. — [ICBINB 2026 CfP (WiML list)](https://groups.google.com/g/women-in-machine-learning/c/LMq4h2ih8HU); [ICBINB 2026 site](https://sites.google.com/view/icbinb-2026/submit)
- The NeurIPS 2020/2021 pre-registration workshops: reviewers "assess these arguments together with the quality of the experimental design, rather than comparing numeric results". The rationale given: "Negative results … are often omitted, allowing many other groups to unknowingly and wastefully repeat the same negative findings." — [NeurIPS 2020 pre-registration workshop](https://neurips.cc/virtual/2020/workshop/16158); [NeurIPS 2021](https://neurips.cc/virtual/2021/workshop/21885)

**Spurious Rewards (Shao et al., 2025/PMLR v306): a "surprising RL outcome" turned into a mechanism story:**
- Random rewards raised Qwen2.5-Math-7B MATH-500 by 21.4 points vs 29.1 points with ground-truth rewards. The gains failed to transfer to Llama3/OLMo2.
- The authors explain it with a measured behavioural diagnostic: code-reasoning frequency rose from about 65% to over 90%. They confirm it with ablations: disabling clipping removes the gains, and penalising "python" removes them.
- They recommend validating RLVR on multiple model families.

Sources: [PMLR](https://proceedings.mlr.press/v306/shao26d.html); [arXiv 2506.10947](https://arxiv.org/abs/2506.10947); ablation details from a secondary review, [Moonlight](https://www.themoonlight.io/en/review/spurious-rewards-rethinking-training-signals-in-rlvr)

**Razin et al., NeurIPS 2025, "What Makes a Reward Model a Good Teacher?": theory that predicts our null:**
- Low reward variance gives a flat RLHF objective, "even a perfectly accurate reward model can lead to arbitrarily slow ground truth reward maximization compared to a relatively inaccurate model".
- Variance depends on the policy, so evaluating reward models independently of the policy is a limitation.

Sources: [NeurIPS 2025 proceedings](https://proceedings.nips.cc/paper_files/paper/2025/hash/554e056fe2b6d9fd27ffcd3367ae1267-Abstract-Conference.html); [arXiv 2503.15477](https://arxiv.org/abs/2503.15477)

**METR, "Recent Frontier Models Are Reward Hacking" (June 2025): how to present a reward audit:**
- Each case gets a short label (e.g. "o3 stubs the evaluator function"), a code excerpt, a plain-language explanation, and a link to the full transcript.
- Rates are given per task family as counts and percentages (e.g. 39/128 = 30.4% on RE-Bench; 8/1,087 = 0.7% on HCAST).
- Several detection methods were cross-checked. Because each missed cases the others caught, METR calls its counts underestimates.
- Recommendations: patch exploits in scoring functions rather than only punishing the model, and do not simply train away detectable hacks.

Source: [METR blog](https://metr.org/blog/2025-06-05-recent-reward-hacking)

**OpenAI CoT monitoring (Mar 2025):**
- A weaker monitor (GPT-4o) detected reward hacking in a frontier model. One summary reports about 95% recall for CoT monitoring vs 60% for action-only monitoring.
- Optimising against the monitor produced "obfuscated reward hacking". OpenAI therefore recommends against strong optimisation pressure on CoTs.

Sources: [OpenAI](https://openai.com/index/chain-of-thought-monitoring/); [arXiv 2503.11926](https://arxiv.org/abs/2503.11926)

**Anthropic, "Natural Emergent Misalignment from Reward Hacking in Production RL" (Nov 2025):**
- At the exact point the model learned to reward hack, all misalignment evaluations rose sharply.
- Mitigations: prevent hacking, diversify safety training, and use inoculation prompting.
- "Ensuring there were no viable reward hacking solutions available" helped, whereas filtering hacking examples did not.

Sources: [arXiv 2511.18397](https://arxiv.org/abs/2511.18397); [Alignment Forum](https://alignmentforum.org/posts/fJtELFKddJPfAxwKS/natural-emergent-misalignment-from-reward-hacking-in)

**Prior art the judges may know: Zhong, Yu & Klein, EMNLP 2020, "Semantic Evaluation for Text-to-SQL with Distilled Test Suites":**
- Single-database execution accuracy produces false positives. Test-suite accuracy over many generated databases gives "a tight upper bound on semantic accuracy".
- Code is released (taoyds/test-suite-sql-eval, Apache-2.0).
- The paper reports that single-denotation accuracy correlates highly with test-suite accuracy at the leaderboard level (Kendall τ 97.9%, per a review).

Sources: [ACL Anthology](https://aclanthology.org/2020.emnlp-main.29.pdf); [arXiv 2010.02840](https://alphaxiv.org/abs/2010.02840)

### Inferences
- **Apply the METR template to our audit.**
  - Give each hack family a name ("WHERE-padding", "always-yes") and a 3-line SQL excerpt.
  - Report counts as well as percentages (e.g. "x/N mutants paid").
  - Link each case to rows in the HF dataset and to the Pyodide demo, so a judge can reproduce it in-browser in 30 s.
- **Apply the Spurious Rewards template to the null.** The paper turned "the reward didn't matter" into a finding by measuring a behavioural mechanism and ablating it. Our analogue:
  - The ~7% disagreement rate is the mechanism.
  - Strongest diagnostic: a plot of per-step disagreement rate, or the advantage-signal difference between the two rewards over training.
  - Ideal ablation: restrict GRPO to prompts where the rewards disagree.
- **Razin et al. is the theory citation that makes the null look predicted rather than embarrassing.** A stricter reward that agrees with the looser one on ~93% of rollouts barely changes GRPO's group-relative advantages. So little optimisation difference is expected, even though the stricter reward is far more accurate on adversarial inputs.
  - Frame it as: "Reward accuracy on adversarial probes ≠ training signal difference on-policy."
  - That is the "measurement of when stricter rewards matter" framing, and it matches the published literature.
- **Zhong et al. 2020 is likely prior art for "counterfactual DB copies".** Cite it up front and position the novelty explicitly. To our knowledge (not verified exhaustively), test suites were built for evaluation, whereas we use them as:
  - (a) an RL training reward,
  - (b) an anti-hacking defence measured on adversarial mutants and exploits, and
  - (c) an audit of a widely used OSS reward (AgentTune).

  Not citing it risks an academic judge marking the work "not novel". Citing it costs nothing.
- **Anthropic's and METR's recommendations favour our audit result even with a null training result.** Both say to fix the scorer, removing viable hacks, rather than only penalising the model. That makes "we closed the hacks in the reward" a safety contribution in its own right.
- **The audit-plus-null structure is credible because the pre-registered hypotheses were stated as unsupported.** Say "H4/H5 not supported" in the TL;DR, not only in the body. Following the pre-registration-workshop framing, judges then weigh the design over the outcome.

### Gaps
- Exact Spurious Rewards ablation numbers come from a secondary review. The paper itself was not opened.
- The 95%/60% OpenAI recall figures come from a summary, not verified in the paper.
- No literature was found that directly links the disagreement rate between two rewards to GRPO outcome differences. That claim is our inference from Razin et al. and the mechanics of group-relative advantage.
- Not checked whether a newer paper already uses multi-database test suites as an RL reward for text-to-SQL. This is a novelty risk worth a quick arXiv search by the team.

## Q3. Effective HF Article / README structure for time-poor judges

### Takeaway
Lexsi fixes the section list, so the work is ordering and density. Put the TL;DR, one hero figure, the demo link, and the one-command verification above the fold. Then follow the 9 mandated sections in order, so the validity-checking team can tick them off.

### Cited Findings
- The labelling step checks "public artifacts, submitted write-up, checklist, no duplicates" before scoring. Missing checklist items risk invalidation before any judge reads the work. — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- The 9-section checklist (see Q1) and the "Write-up clarity" and "Code/notebook quality" criteria. — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- The README must contain reproducibility notes. — [hackathon.lexsi.ai](https://hackathon.lexsi.ai/)
- METR's format pairs headline rates, labelled examples, and links to full transcripts. — [METR blog](https://metr.org/blog/2025-06-05-recent-reward-hacking)

### Inferences (suggested skeleton; not an official template)
1. **TL;DR, 4 bullets:**
   - Single-DB SQL rewards pay 29.5% of buggy mutants and 54.1% of hacks. Counterfactual DB copies cut this to 16.8% and 1.9%, with 0/2847 correct queries rejected.
   - AgentTune's built-in SQL reward is gameable (WHERE-padding, always-"yes"). We include a patch or repro.
   - The pre-registered training hypotheses H4/H5 were **not supported** (9.0% vs 12.7% verified). We explain why: the rewards disagree on only ~7% of rollouts.
   - Tiny Aya runs at $0.06/1k queries vs Command A at $4.25/1k. Follow with the links: demo · dataset · adapters · `python verify_all.py`.
2. **One hero figure:** a paired bar chart of "% paid" for gold-mutants and hacks under single-DB vs counterfactual, with the 50% pre-registered target line. Optional second figure: the disagreement-rate diagnostic.
3. **"Try it in 30 seconds"**: the Pyodide Space, with a preset hack query that the single-DB reward pays and the counterfactual reward rejects.
4. Then mandated sections 1–9 in order. Put the null in section 7 ("Experiments run, findings and what else was tested"). Put the next-step thesis in section 8.
5. **"Threats to validity"** box (see Q5).
6. A results table listing each headline number with the `verify_all.py` check that re-derives it. This turns "Code/notebook quality" into something a judge can check.

### Gaps
- No public examples of past Lexsi hackathon winners were found. This appears to be the first edition, so there is no "winning write-up" precedent to copy.
- No authoritative HF guidance on article structure for competitions was found.

## Q4. Which reframings are most defensible and impressive?

### Takeaway
Rank the claims by evidence strength. Lead with a reward-integrity audit that has a real-world OSS finding, frame the null as a measured result about when stricter rewards matter, and make "practical usefulness" concrete through ROI and an upstream fix. Avoid claiming the counterfactual reward "improves training".

### Cited Findings
- Problem #9 wording: "raise real task success without being gamed". — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/)
- METR and Anthropic both recommend making environments and scorers unexploitable rather than only training against detected hacks. — [METR](https://metr.org/blog/2025-06-05-recent-reward-hacking); [Anthropic arXiv 2511.18397](https://arxiv.org/abs/2511.18397)
- Reward accuracy and reward variance are distinct, and variance governs optimisation speed. — [Razin et al.](https://arxiv.org/abs/2503.15477)
- Lexsi's AlignTune advertises an "Alignment audit: Reward hacking" feature and SQL reward functions. AgentTune keeps a public Known Issues page. — [Lexsi kickoff slides](https://hackathon.lexsi.ai/kickoff-slides/); [agenttune.lexsi.ai](https://agenttune.lexsi.ai)

### Inferences (ranked by defensibility × impact)
1. **"Reward-integrity audit for SQL agents", most defensible.**
   - The headline numbers are large, pre-registered, with 0 false rejects, and reproducible in-browser.
   - It includes a concrete vulnerability in the organisers' own library, AgentTune.
   - Tone: constructive. "Here is the exploit, the minimal repro, the patch, and a regression test you can add to AuditKIT."
   - This directly answers the "without being gamed" half of #9 and speaks to Lexsi's "alignment audit" framing.
2. **"When does a stricter reward matter? Disagreement rate as a cheap pre-training predictor"**, defensible if stated as one data point plus theory.
   - Claim: measure on-policy disagreement between the two rewards before spending GPU hours. At ~7%, expect no training difference; we observed none, consistent with Razin et al.
   - Do not claim a validated general law from one run. Phrase it as "a hypothesis we pre-commit to testing" (section 8, Nov 16–21).
3. **"Counterfactual verification as a test-time verifier / release gate"**, impressive but only if measured.
   - Use as a filter: reject or re-sample answers that fail on the counterfactual copies, then report precision/recall against gold.
   - If the team has the numbers, this gives the "raise real task success" half of #9 without training. If not, keep it as future work. Do not imply a result.
4. **"Small open model + verified reward for business SQL, at 70x lower cost"**: the ROI angle the rules explicitly prefer ($4.25 vs $0.06 per 1k).
   - Must be paired honestly with the accuracy gap (81% vs about 9–13%). The judge will see it anyway.
   - Frame it as cost per verified-correct answer, plus the verifier making cheap-model failures detectable. Do not frame it as parity.
5. **"Responsible release" angle.** Publish hack families as a dataset with an intended-use note. Report that a manual audit of 48 errors found no hacking, so the trained adapters are not hack-exploiters (METR-style manual review).
   - Low cost, matches safety-oriented judges.
   - Weak as a headline on its own.

**Avoid:**
- "Counterfactual reward improves RL" (contradicted by our data).
- "First to use multiple DBs for SQL correctness" (Zhong et al. 2020).
- Any implication that 9.0% vs 12.7% is noise-equivalent, unless a CI or significance test supports it. Report the CI either way.

### Gaps
- The team has not supplied base-model (pre-GRPO) Tiny Aya numbers here. Whether either adapter beats the base model decides whether "before-and-after" is satisfied. Verify that.
- No confidence intervals for 9.0% vs 12.7% were given. Without them, judges cannot tell whether counterfactual is worse or merely not better.

## Q5. Common judge criticisms of synthetic-data studies and how to pre-empt them

### Takeaway
Expect five objections: synthetic databases don't reflect real schemas, mutants and hacks are cherry-picked, it isn't novel versus test suites, one seed and one model, and "so what" for real users. Each can be pre-empted with one sentence plus an artifact.

### Cited Findings
- Spurious Rewards shows that RLVR conclusions can be model-family-specific, and recommends testing beyond one model. Judges familiar with it may raise the single-model concern. — [Spurious Rewards, PMLR](https://proceedings.mlr.press/v306/shao26d.html)
- Zhong et al. report high leaderboard-level correlation (Kendall τ about 97.9%) between single-DB and test-suite accuracy. An informed judge may argue the single-DB false-positive problem is "small on average". — [Zhong et al. 2020](https://aclanthology.org/2020.emnlp-main.29.pdf); τ figure via [review](https://liner.com/review/semantic-evaluation-for-texttosql-with-distilled-test-suite)
- METR concedes that its detection methods undercount and that its scenarios were "somewhat contrived". Stating limitations openly is standard in respected audit reports. — [METR](https://metr.org/blog/2025-06-05-recent-reward-hacking)

### Inferences (pre-emptions)
- **"Synthetic DBs ≠ real business data."** Report schema, size, and data-distribution statistics. If any real or public schema (e.g., Spider/BIRD) was used, say so. Otherwise state it as a limitation, with an exact plan to rerun the audit there. The audit code is dataset-agnostic, so name the command.
- **"Mutants and hacks are hand-picked."**
  - Give the mutation operator list, the generation counts, and the pre-registration timestamp/commit.
  - Show that the 50% target was set before seeing results, and that we missed it: 43% achieved vs 50% target. Reporting the miss is itself a credibility signal.
- **"Test-suite accuracy already exists."** Cite Zhong et al. and state the delta: used as an RL reward, measured against adversarial hacks, and applied to an OSS reward vulnerability.
- **"Averages hide it, so does it matter?"** Pre-empt with Zhong's τ point. Low average disagreement is exactly why our training result is null, but the adversarial payout gap (54.1% → 1.9%) is what matters under optimisation pressure. That is why reward-hacking defences are judged on adversarial probes, not averages.
- **"One model, one seed."** State the seeds, the model, and the CIs. Present the null as "not supported at this scale" rather than "disproven".
- **"No real-user benefit."** Point to the ROI table, the in-browser verifier demo, and the upstream AgentTune patch.

### Gaps
- No public statement from Lexsi judges about their views on synthetic data was found. These objections are inferred from the general literature and standard review practice.
