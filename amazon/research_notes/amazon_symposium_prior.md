# Amazon Trusted AI Symposium: prior editions and what gets accepted

Compiled 2026-11-21. Sources are linked inline. PDFs are in `research_notes/pdfs/amazon_prior/` (untrusted downloads, text extracted with pdftotext).

**Short answer:** there has been only **one** earlier edition, Trusted AI Symposium **2026** (New York, Jan 21 2026). No accepted-poster list, program, best-poster award or judging rubric was ever published. I found **7 accepted works** through self-reports by their authors; 3 of them have a readable PDF. **No awards** of any kind were found. The only stated selection rule ever published is the 2026 "Nova priority" line. It is **absent** from the 2027 call.

---

## 1. The 2027 call (verbatim key text)

Source: https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2027 (fetched 2026-11-21; the page's banner still says "2026", a template leftover).

- Date and venue: **February 18, 2027, New Delhi, India**. One day, invitation-only.
- Overview: "Join leading researchers from India's academic institutions, industry, and policy community for an intensive, one-day symposium on the frontier of Trusted AI, held in New Delhi. Jointly hosted by Amazon Web Services (AWS) Public Policy and the Amazon AGI team, this invitation-only gathering brings together distinguished scholars to address a central challenge: building powerful AI systems that are inherently safe and reliable."
- Key dates:
  - "Abstract submission deadline: November 30, 2026"
  - "Notification of acceptance: December 31, 2026"
  - "RSVP deadline: Due to high demand, invitations are issued selectively, and only confirmed attendees will receive detailed event logistics via email in early February 2027."
  - "Event date: February 18, 2027"
- Submission: "Deadline is November 30, 2026 and Posters must be submitted via email to trusted-ai-symposium@amazon.com. All submission is non-archival. Double submission is acceptable"
- What to submit:
  - "Format your submission following this NeurIPS LaTex template; submit as PDF." The link points to `https://media.neurips.cc/Conferences/NeurIPS2025/Styles.zip`, so **use the NeurIPS 2025 style**.
  - "Submissions may be up to 4 pages, with references and appendices allowed on additional pages beyond the 4-page limit."
  - "Abstracts should follow a standard academic format (introduction, methods, results, conclusions)"
  - "Include author names, affiliations, and email"
- Topics ("We welcome submissions across all aspects of Trusted AI, including but not limited to:"):
  - AI governance & policy: Frameworks, compliance, and regulatory approaches; **aligned with India's national AI framework and policy bodies**
  - Evaluation & benchmarking in RAI: Metrics, testing methodologies, and assessment frameworks
  - Risk mitigation: Techniques for reducing AI harms and unintended behaviors
  - Security & safety: Adversarial robustness, secure deployment, and threat modeling
  - Agent safety & reliability: Safety in agentic, autonomous, and multi-agent systems
  - Explainability & interpretability: Making AI decisions transparent and understandable
  - Reasoning & verification: Formal methods and logical reasoning in AI systems
  - Observability & monitoring: Runtime monitoring and system transparency
  - Red-teaming & stress testing: Adversarial testing and failure mode discovery
  - Uncertainty quantification: Calibration, confidence estimation, and risk assessment
  - Multi-modal safety: Trust across vision, language, and other modalities
  - **Multi-lingual and Indic-language safety and fairness**: Safety and fairness across languages and cultures
  - Content moderation: Detection and filtering of harmful content
  - Watermarking & provenance: Digital fingerprinting and attribution
  - Deception: Detection of deceptive behaviors by models
- Keynote speakers: "Coming soon".
- Participant benefits ("Selected presenters will receive:"): networking; research collaboration ("Potential pathways to ongoing partnerships with Amazon"); job opportunities ("Engage with Amazon recruiters and hiring managers in India-based teams"); visibility ("Showcase your work to key decision-makers in Trusted AI"); "ARA engagement: Learn about upcoming Amazon Research Award (ARA) opportunities in India."
- Advisory Committee:
  - Amazon: **Rahul Gupta, Michael Johnston**.
  - IIT Delhi: Prof. P. Vigneswara Ilavarasan (HoD, Department of Management Studies). Conference Chair: Prof. Arpan Kumar Kar. Programme Chairs: Prof. Agam Gupta and Prof. Arghya Ray. All IIT Delhi.
- **Not stated anywhere:**
  - review process (no OpenReview or CMT; submissions go by email);
  - evaluation criteria;
  - number of reviewers;
  - travel support (none is mentioned, so assume travel to Delhi is self-funded);
  - awards.
- **Changed from 2026:**
  - The "Nova priority" sentence and the Nova-credits benefit are **gone**.
  - The length went from 1-2 pages to **up to 4 pages**.
  - An India governance clause and Indic languages were added.
  - IIT Delhi (management/IS faculty, not CS) became programme chairs, which raises the odds of non-ML reviewers.

## 2. Prior edition: Trusted AI Symposium 2026 (New York)

Sources: Wayback snapshots of https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2026, taken [Dec 12 2025](https://web.archive.org/web/20251212182021/https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2026) and [Aug 13 2026](https://web.archive.org/web/20260813145248/https://www.amazon.science/conferences-and-events/trusted-ai-symposium-2026). The live page now returns 404. The logistics page `amazonmeetingsandevents.com/trustedaisymposium2026` returns 403 and the archive holds only a redirect.

- Date and venue: **January 21, 2026, New York**. Presenters' pages put it at Amazon's office "JFK 27". Host: "the Amazon AGI team behind the Nova models". One day, invitation-only.
- Day format, from a [LinkedIn post](https://www.linkedin.com/posts/vagelispapalexakis_llm-jailbreaks-hallucination-activity-7420021181799510017-wTVe) by a UC Riverside professor: "The day was packed with interesting talks and networking breaks culminating in a poster session". So the format was keynotes, then networking breaks, then **one poster session**. No oral presentations by submitters were reported.
- Dates: deadline Dec 19 2025. Notification was first given as Jan 5 2026, later changed to Jan 7 2026. Logistics were sent by Jan 16 2026.
- Format: "NeurIPS 2025 LaTex template ... **Extended abstract (1-2 pages)** describing your research, methodology, and key findings". The IMRaD abstract format, the authors/affiliations/email requirement and the non-archival/double-submission rules were the same as 2027.
- **The only stated selection criterion in either edition:** "Indicate if the work uses or evaluates Amazon Nova models. Papers that discuss, evaluate, or utilize Amazon Nova models will receive priority in the selection process." The Aug 2026 snapshot adds a free Nova API tier, `nova.amazon.com/dev/api`, for the North American region.
- Topics: the same 15 as 2027, minus the India and Indic wording. Item 12 was "Multi-lingual considerations".
- Keynotes: **Aaron Roth** (Amazon Scholar; UPenn; calibration, conformal prediction, multicalibration) and **Elias Bareinboim** (Columbia Causal AI Lab).
- Benefits: the same as 2027, plus "Amazon Nova credits".
- Organisers: Rahul Gupta, Amazon AGI Responsible AI. Two search snippets tie him to organising it (LinkedIn snippets only; not readable).

## 3. Related Amazon tracks (context, not the same venue)

- **Amazon Nova AI Challenge, Trusted AI track (2024-25).** 10 university teams: 5 built red-teaming bots and 5 built safe coding assistants, in multi-turn adversarial tournaments against coding LLMs. The proceedings paper is [arXiv 2508.10108](https://arxiv.org/abs/2508.10108), 42 pages, "1st Proceedings of Amazon Nova AI Challenge (Trusted AI 2025)". **Its authors include Michael Johnston and Rahul Gupta, the two Amazon members of the 2027 Advisory Committee.** So the Amazon reviewers' own work is **safety of AI-assisted software and code generation, automated red-teaming, and safety alignment of coding agents**. That is the nearest Amazon-internal neighbour to a SQL-writing agent. PDF: `2508.10108_nova_challenge_trusted_ai.pdf`.
- **USC + Amazon Center on Trustworthy AI annual symposium** ([2025 edition](https://trustedai.usc.edu/fourth-annual-symposium)). This one is internal to the centre: keynotes, funded-project talks and talks by Amazon fellows. It had no open poster call and no awards. It is not relevant to submission strategy.

## 4. Accepted works found (2026 edition)

All of these are self-reported by the authors. Amazon never published a list. Nothing below is invented; where the title or PDF is unknown, the entry says so.

| # | Title | Authors / affiliation type | Topic | Evidence | PDF read? |
|---|---|---|---|---|---|
| 1 | **Supercharging Federated Intelligence Retrieval** | Stripelis et al., **Flower Labs** (industry startup) | Secure federated RAG; TEEs/confidential compute; cascaded inference with **Amazon Nova Micro** | Footnote on the PDF: "Presented at the Amazon Trusted AI Symposium 2026, New York, NY, USA." [arXiv 2603.25374](https://arxiv.org/abs/2603.25374) | Yes. **This is the actual symposium submission.** |
| 2 | **Beyond ROUGE: N-Gram Subspace Features for LLM Hallucination Detection** | Jerry Li (student), Evangelos Papalexakis (professor), **UC Riverside** | Hallucination detection with N-gram tensors plus SVD/Tucker/CP features | Listed as "Amazon Trusted AI Symposium 2026" on [jeli04.github.io](https://jeli04.github.io/). [arXiv 2509.05360](https://arxiv.org/abs/2509.05360) | Yes. arXiv version is 5 pages, ACM format. The symposium submission was probably a NeurIPS-style re-format. |
| 3 | (title not public) LLM jailbreaks | Sowmya Kadali (student), Papalexakis, UC Riverside | Understanding LLM jailbreaks | [LinkedIn post](https://www.linkedin.com/posts/vagelispapalexakis_llm-jailbreaks-hallucination-activity-7420021181799510017-wTVe); [UCR page](https://www.cs.ucr.edu/~epapalex/) says "two of our accepted posters" | No |
| 4 | **Confounding Robust (Deep) Reinforcement Learning: A Causal Approach** | Mingxuan Li (PhD student), Junzhe Zhang, Elias Bareinboim; **Columbia**, Syracuse | Off-policy deep RL that is robust to unobserved confounding; worst-case-safe policy; 12 confounded Atari games | [mingxuan.me](https://mingxuan.me/): "accepted at Amazon Trusted AI Symposium 2026!". PDF [causalai.net/r132.pdf](https://causalai.net/r132.pdf) (NeurIPS 2025 paper, arXiv 2510.21110) | Abstract and intro only. It is a 34-page NeurIPS paper. Bareinboim was a **keynote speaker**. |
| 5 | **Multi-agent verification for safe preference alignment** (symposium talk title) | Elias Hossain et al., UCF (student-led) | k-of-n multi-agent verifiers filter preference pairs before DPO; contamination bound; Qwen2-7B | [eliashossain001.github.io](https://eliashossain001.github.io/), "Amazon Trusted AI Symposium, JFK 27, New York". The related paper is "Fault-Tolerant Preference Alignment via Multi-Agent Verification" ([OpenReview u73knIzvbY](https://openreview.net/forum?id=u73knIzvbY), ICLR 2026 workshop; [project page](https://eliashossain001.github.io/mpv/)) | No. The OpenReview PDF returned 403. Read from the project page. |
| 6 | (title not public) Auditing LLMs for child safety | Nikhil Sharma (JHU, student), with Ayush Gupta (Honda Research Institute) | Safety audit of LLMs for children | [nikhilsksharma.com/about](https://www.nikhilsksharma.com/about): "Presented our upcoming work on auditing LLMs for Child Safety!" | No |
| 7 | **Integrating Safety Testing into GenAI Development: Lessons from Amazon Nova and Red Hat – Chatterbox Collaboration** | Christophe Dupuy, **Rahul Gupta** (Amazon Nova Responsible AI), Stuart Battersby, Danny Coleman (Red Hat – Chatterbox Labs) | Continuous red-team testing of Nova 2 checkpoints during training; ASR vs SWE-bench; judge drift | The poster itself carries a "Trusted AI Symposium" logo: [redhat.com PDF](https://www.redhat.com/rhdc/managed-files/Chatterbox_Amazon_Nova.pdf) | Yes. This is the **actual poster**, 48x36 in landscape. |

Weaker leads I could not verify, because LinkedIn blocks fetching:
- An AWS researcher presented three posters on "measuring and operationalizing trust in agentic and multimodal systems".
- A "conformal safety layer" multi-agent act-or-defer poster. The closest match is [arXiv 2604.07667](https://arxiv.org/abs/2604.07667), but nothing ties it to the symposium.
- Elena Ghazi (Harvard) lists "Amazon Trusted AI Symposium 2026" against differential-privacy deployment-registry work, according to a search snippet of her Google Site, which is behind a login. That work's "Best Poster/Demo" was at **NYC Privacy Day 2025**, not at this symposium.

**Awards:** none found. No best-poster page, no announcement, and no award line on any presenter's page.

### 4.1 Close reading of the three papers with PDFs

**(1) Supercharging Federated Intelligence Retrieval** (Flower Labs). This is the model to copy for format.
- Length: 6 pages in the NeurIPS 2025 style. About **3 pages of main text**, then 1.5 pages of references and a 1-page appendix (corpus table and prompt sample). It met the 2026 limit of 1-2 pages "+refs" loosely, at about 3 pages.
- Abstract: **3 sentences**, with no numbers. Problem, then system, then the second contribution.
- Structure:
  1. Intro, ending in **4 contribution bullets**
  2. Related Work & Background, with bold run-in paragraphs that end in an explicit **Threat Model** paragraph
  3. Methods
  4. Evaluation: settings, then one table, then a "Results Analysis" paragraph
  5. Conclusion (one paragraph)
- Figures and tables: 1 system-pipeline figure (with three inference "modes") and 1 main results table (accuracy and latency per mode on 3 benchmarks). The appendix holds one more table.
- Why it fit Trusted AI:
  - security and safety, with a threat model;
  - privacy-preserving deployment;
  - it **explicitly uses Amazon Nova Micro** and says "more powerful Nova Pro/Premier models are a promising direction". That plays straight to the 2026 Nova-priority clause.
- Results are modest: 4 clients, a 1.7B model on CPU. **The bar is clearly a clean, working system with a threat model, not SOTA.**

**(2) Beyond ROUGE** (UC Riverside, student first author).
- Length and format: 5 pages, ACM two-column (arXiv version). Keywords; abstract of about 8 sentences in problem → gap → method → evaluation form.
- Sections: Intro (with a contributions list) → Method (formal definitions) → Experiments (baselines including a GPT-4o judge) → a **"Performance from Textual Bias"** robustness check (ruling out a shortcut) → Conclusion → a GenAI disclosure.
- Figures and tables: 3 figures (pipeline, a group-size curve, ablation bars) and 3 tables.
- Why it fit: it is a hallucination-detection metric, so it falls under "Evaluation & benchmarking". Cheap and interpretable. It **explicitly checks whether the classifier exploits a spurious shortcut**, which is the same instinct as a reward audit.

**(7) The Nova/Chatterbox poster** (Amazon RAI and an industry partner; co-authored by the 2027 committee member Rahul Gupta).
- Layout: a 3-column landscape poster. Header: Trusted AI Symposium logo, title, authors, then Amazon Nova branding.
- Sections: 1 Introduction → 2 Operational Setup (a train/test-team separation diagram) → 3 Learnings, as **four numbered, claim-style subheadings** (e.g. "3.2 Average safety robustness does not imply across-the-board enhancement") → 4 Conclusion, with 2 bold takeaways.
- Plots: 3 simple matplotlib plots (ASR vs SWE-bench trajectory, ASR before and after per technique, ASR under combined techniques).
- Content that matters to us:
  - "Improving capability ... conducting special operations during RL (e.g. building specialized reward models...)" leads to safety evolving "in opposite directions".
  - "As model capabilities evolved, we observed that the judge that assessed model capabilities also needed updates ... to maintain a higher than 95% accuracy".
  - The **anti-contamination framework**: test prompts kept hidden from the training team.

  These are reward-model and evaluator-reliability themes, **the exact neighbourhood of reward hacking**. The organiser's own poster is about evaluators drifting during RL.

**(4) Confounding-robust deep RL.** This is a full NeurIPS 2025 paper accepted as a non-archival double submission. It shows that RL-safety work ("safe policy for the worst-case environment") is in scope, and that the keynote's lab submitted.

## 5. Inferred acceptance patterns

These are inferences from 7 data points, not stated rules.

1. **Scope is broad and practical.** The accepted works cover hallucination detection, jailbreaks, child-safety audits, preference-data verification, confounding-robust RL, secure federated RAG and red-team operations. All of them can be summed up in one line as "we measured or reduced a concrete failure mode of an LLM or agent".
2. **Re-use of existing work is normal.** 3 of the 4 papers with known titles were already on arXiv, at NeurIPS or at an ICLR workshop before the deadline. The call explicitly allows double submission. Our existing reward-audit and GRPO results can go straight in.
3. **Mix of affiliations.** Students (UCR, UCF, JHU, Columbia), faculty labs, startups (Flower), and Amazon itself. Student-first-author work gets in.
4. **Empirical, honest and small-scale is fine.** The Flower paper used a 1.7B model on CPU, and UCR used HaluEval with an MLP. Nobody needed frontier-scale compute. A 3.35B model trained with GRPO is in range.
5. **Amazon-model usage was rewarded in 2026.** It is not mentioned in 2027, but the hosts are still "the Amazon AGI team" (the Nova builders), so any Nova touchpoint is still a cheap plus. Examples: Nova as a baseline policy, a judge, or a comparison on the same SQL tasks.
6. **The reviewers' own interests,** taken from the committee members' publications:
   - Gupta and Johnston: red-teaming and safety of **code-generating** assistants (Nova AI Challenge), and evaluator and judge drift during RL (the Chatterbox poster).
   - Keynote taste in 2026: calibration and conformal prediction (Roth), and causal robustness (Bareinboim).
   - For 2027: IIT Delhi management and policy chairs, which means governance and deployment-risk framing will land with them.
7. **Selection is about attendance as much as quality.** The event is "invitation-only" and "invitations are issued selectively". The pages give no rubric, and acceptance means a poster slot. A clear, readable 4 pages with one strong figure is what a busy mixed panel can judge.

## 6. Recommendations for our paper (RL reward hacking / counterfactual-database verifiable rewards / text-to-SQL agent / reward audit / GRPO on a 3.35B model)

### 6.1 Topic mapping

Name the topics in the intro or contributions, in this priority order:

1. **Evaluation & benchmarking in RAI (primary).** The reward audit is an assessment framework. A single-database execution-match reward is a *metric that can be gamed*, and we measure how often it accepts wrong SQL. Report the audit as false-accept and false-reject rates of each reward against counterfactual ground truth.
2. **Red-teaming & stress testing.** The policy under RL acts as an automated red-teamer of the reward. Show the hacks GRPO discovers: SQL that is right on the one visible DB and wrong on perturbed DBs, such as hard-coded literals, overfit LIMIT/ORDER, or missing joins that happen to match. Present them as a failure-mode taxonomy table.
3. **Reasoning & verification.** Counterfactual databases turn "execution match" into **differential testing**, a lightweight verification of semantic equivalence. Be honest that this is not formal methods: "Verification by counterfactual execution".
4. **Agent safety & reliability.** A text-to-SQL agent executes queries against real data stores, and silently wrong analytics are a reliability and safety hazard. This links to the committee's Nova AI Challenge focus on safe **AI-assisted code generation**: SQL is code.
5. **Observability & monitoring** (secondary). If we track a reward-hacking signal during training, such as the gap between single-DB and counterfactual reward, frame it as a training-time monitor. This echoes the Chatterbox poster's "evaluate every checkpoint".
6. **Deception** (only lightly, if at all). Reward hacking is specification gaming, not intent to deceive. Use one sentence at most, so as not to overclaim.
7. **AI governance & policy (India)** (one paragraph, optional but likely valued by the IIT Delhi chairs). The India AI Governance Guidelines (MeitY, Nov 5 2025) build on seven "sutras", including "Trust is the Foundation", "Accountability", "Understandable by Design" and "Safety, Resilience & Sustainability". One sentence can tie verifiable rewards and audit reports to accountability and safety for LLMs deployed over public or enterprise databases. Do not invent India-specific experiments.
   - Indic languages: add something only if we actually run it. For example, if we can evaluate a few questions in Hindi on the same databases, that is a genuine hook. Otherwise skip it.

### 6.2 Format and structure

Copy the Flower paper's shape, the only accepted submission we can actually see.

- Use the **NeurIPS 2025 style** (`Styles.zip` linked from the call), with the final or preprint option so author names, affiliations and emails show. Add a first-page footnote in the Flower style, e.g. "Submitted to the Amazon Trusted AI Symposium 2027, New Delhi." Fill **4 main pages**, put references and appendix after them, and email the PDF to trusted-ai-symposium@amazon.com before **Nov 30 2026**, ideally with a day of buffer.
- **The abstract must read as IMRaD**, since the call says "introduction, methods, results, conclusions". Use 4-6 sentences, one or two each for motivation, method, results with 2-3 hard numbers, and conclusion. Unlike the Flower abstract, put the numbers in: a mixed panel that includes management faculty will skim the abstract first.
- Sections:
  1. Introduction (problem, the 3-4 contribution bullets, and a one-line topic mapping)
  2. Background and threat model. Name the "adversary": an RL policy that maximises a proxy reward. Name the assumption: the reward sees only one DB instance.
  3. Methods: counterfactual-database reward, reward audit protocol, GRPO setup (3.35B model, data, budget).
  4. Results: the audit table, the training curves, and the hack taxonomy.
  5. Limitations and conclusion (2-3 sentences of honest limits, e.g. a single model size and counterfactual DB coverage).
- Visuals (both reference papers used 1 pipeline figure + 1 or 2 result tables or plots; the poster used 3 simple plots):
  - **Fig. 1:** a pipeline. Question → policy SQL → executed on the original DB plus K counterfactual DBs → reward. Include an inset of a real hacked query that passes the original DB and fails a counterfactual one.
  - **Table 1:** reward audit (false-accept and false-reject rate per reward variant).
  - **Fig. 2:** GRPO training curves, single-DB reward vs counterfactual reward, with held-out true accuracy. This is the "reward goes up, truth doesn't" picture.
  - **Table 2 (small):** hack taxonomy with counts.
  - Put extra examples, hyperparameters and the counterfactual-DB generator details in the appendix, which does not count toward the 4 pages.
- Make a robustness check visible, as Beyond ROUGE did: show the counterfactual reward isn't itself exploitable in an obvious way, or report where it still is. Reviewers here like seeing the authors attack their own metric.
- **Nova touchpoint (optional, low cost):** run Amazon Nova (e.g. Nova Micro or Lite via Bedrock or the Nova API) as a zero-shot text-to-SQL baseline, scored by both rewards, to show that even frontier-API outputs are mis-scored by single-DB rewards. Priority is no longer stated for 2027, but the hosts build Nova. Do this only if it is allowed under the team's compute and credential rules: no cloud actions without the owner's sign-off.
- Make the title claim-like, as the poster's subheadings were. Pattern: "<Proxy> Rewards Are Hackable: Counterfactual-Database Verification for Trustworthy RL of Text-to-SQL Agents".
- The poster (if accepted) uses a 48x36 in landscape, 3-column layout (see the Chatterbox example). Plan the 4-page figures so they reuse directly as poster panels.

### 6.3 What not to do
- Don't present it as a pure capability/accuracy paper. The trust framing (a metric that can't be trusted, and a fix for it) must lead.
- Don't claim formal verification, deception, or Indic results unless they are actually done.
- Don't pad to 4 pages with related work. The accepted examples had about 1 paragraph per related area.

## 7. What was searched (for the record)
- amazon.science 2027 page (live); 2026 page (404 live, read via Wayback CDX snapshots of Dec 2025 and Aug 2026); amazonmeetingsandevents.com (403).
- Web searches:
  - `"Trusted AI Symposium" Amazon`, `"Amazon Trusted AI Symposium"`, `"Trusted AI Symposium 2026" arxiv`;
  - `"presented at the Amazon Trusted AI Symposium"`, `"Trusted AI Symposium" "New York, NY" 2026`;
  - best-poster/award queries, LinkedIn/X queries, IIT Delhi queries;
  - author-specific follow-ups (Papalexakis, Kadali, Sharma, Ghazi, Hackett, Eschrich, Feng, Zhang).
- arXiv API searches on comments and abstracts for "Trusted AI Symposium". The only hit was the Nova Challenge proceedings.
- Blocked or unreadable: LinkedIn profiles (HTTP 999), X (402), the OpenReview PDF (403), and Elena Ghazi's Google Site (login).
- No 2025 or earlier edition of this symposium exists on amazon.science. The Wayback CDX for `amazon.science/conferences-and-events/trusted-ai-symposium*` lists only the 2026 page.
