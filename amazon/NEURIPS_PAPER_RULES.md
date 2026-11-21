# NeurIPS-template paper rules: Amazon Trusted AI Symposium 2027 (4 pages)

The single rulebook for our 4-page paper: RL reward hacking and counterfactual-database verifiable rewards for a text-to-SQL LLM agent (GRPO). Part I comes from the paper study. Part II comes from the user's own paper-writing guides.

**Evidence key.** Every rule cites its source:
- **E1**: NeurIPS 2020–22 papers (n = 13). **E2**: 2023–24 (n = 12). **E3**: 2025–26 (n = 14).
- **WS**: NeurIPS-workshop papers with exactly 4 content pages (n = 8).
- **T**: the official `neurips_2025.sty` / `.tex`.
- **AM**: the Amazon 2027 call and the 2026 edition (3 accepted works were readable).

A count such as "8/10" uses only the papers where the item applies (for example, papers that have tables). **The template wins every conflict, and the Amazon constraints win over the template.**

Source notes: `amazon/research_notes/{neurips_2020_2022, neurips_2023_2024, neurips_2025_2026, template_and_4page, amazon_symposium_prior}.md`.

---

# Part I — Rules from paper study (Nov 21, 2026)

## 0. Hard constraints (Amazon, must follow)

- Format with the official NeurIPS LaTeX template; submit as PDF.
- Up to 4 pages, with references and appendices allowed on additional pages beyond the 4-page limit.
- Abstracts follow a standard academic format (introduction, methods, results, conclusions).
- Include author names, affiliations and email.
- Deadline Nov 30, 2026; submit by email to trusted-ai-symposium@amazon.com; non-archival; double submission OK.

**Resolved template decisions**

- Use `\usepackage[preprint]{neurips_2025}`. It shows names, has no line numbers, and its footer reads "Preprint.". Never use `final`, which prints a NeurIPS 2025 footer.
- Drop the NeurIPS checklist.
- The abstract is ONE paragraph with an implicit intro/methods/results/conclusions order.
- Toolchain verified Nov 21: WSL pdflatex/latexmk with texlive-latex-extra + cm-super builds the template with 0 Type 3 fonts, on US Letter.
- Acknowledgments count toward the 4 pages.

**Also binding, from the template (T)**

0.1 Do not change any formatting parameter: no changes to margins, text width or height, body font sizes or spacing. The only allowed size change is `\small` for references. The template says "tweaking the style files may be grounds for rejection".
0.2 US Letter only. A4 is not allowed.
0.3 Fonts must be Type 1 or embedded TrueType. No Type 3 or bitmap fonts.
0.4 Keep the footer as "Preprint.". Do not redefine `\@noticestring`, which would be a style tweak, and do not add a venue footnote, which costs a line. The email itself names the venue. AM suggested a Flower-style footnote and the template notes said to keep "Preprint." if in doubt, so the template-safe option wins.

---

## 1. Title

1.1 Use the form "Name: claim", for example `<Name>: <claim about reward hacking / verifiable rewards in text-to-SQL RL>`. Evidence: a colon in E2 8/12 and E3 9/14. *Conflict:* E1 used the colon only for method or dataset releases (3/13) and otherwise wrote verb or claim titles. **Decision:** use the colon form, the current majority. Its subtitle carries the claim.
1.2 Use 8–12 words on at most 2 lines. Median length was 6 in E1, 10 in E2 and 11 in E3. E3 fit 2 lines in 13/14.
1.3 The subtitle states a claim or capability, not a topic (E2: DPO, Toolformer). AM's own poster used claim-style subheadings. A suggested pattern from AM: "<Proxy> Rewards Are Hackable: Counterfactual-Database Verification for Trustworthy RL of Text-to-SQL Agents".
1.4 Use Title Case. The template sets the title with initial caps. E1 used Title Case in 10/13 and E2 in 11/12. Do not switch to sentence case after the colon (only STDE in E2 did).
1.5 Coin a short, pronounceable name only if we use it throughout the paper. E2 8/12 coined a name, and E3 put a system name before the colon in 5/14.
1.6 The title names both the trust problem and the setting: "reward hacking" or "verifiable", plus "text-to-SQL". A mixed panel skims titles (AM).
1.7 No question title (E2 2/12, E3 1/14), no emoji or logo (E3 P01), and no odd capitalisation to build an acronym (E2 BIRD's "BIg").

## 2. Author block

2.1 Print every author's name, affiliation and email (AM). The `preprint` option prints them (T). Check that "Anonymous Author(s)" does not appear.
2.2 Separate authors with `\And`. Force a line break with `\AND` (T).
2.3 When all authors share an affiliation, give it once on one centred line, as single-affiliation papers do (E1 OpenAI/DeepMind/Google; WS #1). With several affiliations, use superscript numbers (E3 11/14).
2.4 Set emails in typewriter (E2 10/12). Group same-domain emails as `\texttt{\{a,b,c\}@domain}` (E1 5/13; E2 DPO, BIRD).
2.5 Use `\thanks` only for an alternative address or webpage, never for funding (T). Funding goes in the `ack` environment.
2.6 Add an equal-contribution `*` footnote only if it is true (E1 11/13, E2 9/12).
2.7 Give the code link only if the repository is public. Put it in one footnote on the abstract's last sentence (as STDE in E2 does), not under the authors with icons (E3 4/14), because icons cost lines. Abstract-end URLs (E2 6/12) cost abstract words.
2.8 Keep the title plus author block to about 0.25 page (WS).

## 3. Abstract

3.1 Write one paragraph (mandatory: T). E1 12/13, E2 12/12, E3 14/14 and WS 8/8 did so.
3.2 Follow the order Intro → Methods → Results → Conclusions without headings: 1–2 sentences of problem, 2 of method, 2 of results with numbers, and 1 of conclusion (AM requires IMRaD; T requires one paragraph).
3.3 *Conflict on length:* main-track abstracts have a median of about 190 words (E1), about 195 (E2) and about 215 (E3). 4-page workshop abstracts have a median of about 130 (WS). The accepted Flower paper used 3 sentences (AM). **Decision: 150–180 words, 6–8 sentences.** Reason: four IMRaD parts plus hard numbers do not fit in 130 words, and main-track length eats page 1.
3.4 Include at least 2 concrete numbers, each with its baseline beside it ("hack rate 31% → 4%"). E1 11/13, E2 8/12 and E3 11/14 give numbers. *Conflict:* the Flower abstract had none (AM). **Decision: include numbers**, because a mixed panel that includes management faculty reads the abstract first (AM).
3.5 Name our method once, in italics, with its acronym ("which we call *X* (X)"), as E2 10/12 do.
3.6 Emphasise at most 2 spans (E3 9/14 use 1–2; never more than about 3).
3.7 No citations in the abstract (E1 1/13, E3 P02, both unusual). Allow at most one footnote, the code link from 2.7 (E1 had footnotes in 4/13).
3.8 Start the gap sentence with "However," (E2 canonical order 11/12).
3.9 State n or the CI compactly if it fits ("mean of 3 seeds"). Every abstract number must equal its Table 1 number exactly.

## 4. Introduction and contributions

4.1 About 450 words, including the merged related work (see 6.1). Intros in WS run 180–740 words.
4.2 Follow this arc: hook → gap ("However," in E2 12/12) → "In this work, we…" (E2 12/12) → contributions → a one-line topic mapping (23.3).
4.3 Open with a concrete case: an SQL query that matches the reference on the single evaluation database but is semantically wrong. Concrete anecdotes are the usual hook for specification gaming (E1 Side Effects and Reward Hacking; E2 DPO and RBR; E3 P09 uses real incidents). A Goodhart's Law clause is optional (E2 RM-overopt).
4.4 Define reward hacking in one sentence in paragraph 1. Adapt E2 RM-overopt: "performance measured by the proxy reward increases while true quality plateaus or deteriorates."
4.5 State the research question as one italic sentence (E1 Chinchilla and Reward Hacking; E3 P04, P05, P07, 3/14). Use italics only: no bold-italic and no underline (P07 did both).
4.6 *Conflict on contribution format:* an explicit list appears in E1 8/13, E2 7/12 and E3 8/14. In WS, bullets appear in 2/8 and inline (i)–(iii) in 3/8. **Decision: inline (i)–(iii) in one paragraph, each item opening with a bold claim phrase.** Reason: it saves about 4–6 lines against `itemize` in a 4-page budget, and it is the WS majority.
4.7 Each contribution carries a number or a section pointer (E2 Part C; E3 P09 "In Section N we…"; E3 P14 (C1)–(C3)).
4.8 Reference Figure 1 in the intro (E2 11/12).
4.9 Repeat the headline numbers in the intro (E2 10/12), identical to the abstract.

## 5. Section structure and the 4-page budget

5.1 Use this order: 1 Introduction (with related work) · 2 Method · 3 Experimental setup · 4 Results · 5 Discussion and conclusion · Acknowledgments (unnumbered `ack`) · References · Appendix. It follows the canonical E1 order, E3 10/14 and the WS layout.
5.2 Headings use sentence case: "Experimental setup", not "Experimental Setup". T says headings are "lower case except the first word and proper nouns". *Conflict:* most papers use Title Case headings (E1 mixed). **T wins.**
5.3 Below a section, structure the text with bold run-in `\paragraph{…}` headers. They appear in E1 13/13, E2 12/12 and E3 13/14. Use at most 2 `\subsection`s in the whole paper.
5.4 Content must end on page 4. The References heading may start on page 5 (T, AM).
5.5 Acknowledgments count toward the 4 pages, so keep them to 1–2 lines (T A8; WS #10 put ack + funding on p4).
5.6 Page 1 holds the title, authors, abstract and the start of the intro only. Title plus abstract fill about 45–50% of the page (WS S2.1).
5.7 Word budget. The total from the abstract to the end of the conclusion is about **2,300–2,450 words** (WS median ≈ 2,400). A dense text-only page holds about 650–700 words (WS).

| Part | Words | Page share |
|---|---|---|
| Title + author block | – | ~0.25 |
| Abstract | 150–180 | ~0.25 |
| 1 Introduction, including ~120 words of related work | ~450 | ~0.8 |
| Figure 1 (TikZ method diagram), top of page 2 | caption 25–60 | ≤ 0.3 |
| 2 Method (threat model, reward equations, counterfactual-DB generation, GRPO) | ~500 | ~0.75 |
| 3 Experimental setup (run-ins) | ~200 | ~0.35 |
| Table 1 (main results) | caption 20–50 | ~0.3 |
| 4 Results (claim run-ins, optional half-width Figure 2) | ~450 | ~0.8 |
| 5 Discussion and conclusion (limitations, broader impact, conclusion) | ~250 | ~0.4 |
| Acknowledgments | ≤ 2 lines | – |

5.8 Floats: at most 3 in the main body. Figure 1 (diagram) and Table 1 (results) are mandatory; Figure 2 (training-curve plot) is optional. In WS, 7/8 have exactly one results table, the median figure count is 1.5, and floats take 0.5–1.2 pages. *Conflict:* AM suggested 2 figures plus 2 tables (adding a hack-taxonomy table). **Decision:** put the taxonomy in the appendix, or in one inline sentence with counts, because a fourth float breaks the budget.
5.9 If the draft runs over, cut in this order: related-work words, then method detail (to the appendix), then setup detail (to the appendix). Never cut Figure 1, Table 1 or the Limitations paragraph.

## 6. Related work

6.1 *Conflict on placement:* related work comes early in E2 (7/12) and late in E3 (9/14), and is merged into the intro in WS (4/8). **Decision: one paragraph of about 120 words at the end of the intro, as the run-in `\paragraph{Related work.}`.** Reason: it is the WS majority, and AM's accepted works used about one paragraph per area ("don't pad").
6.2 Cover three strands, 1–2 sentences each:
- reward hacking and over-optimisation (E1 Skalse, Stiennon; E2 RM-overopt, InfoRM; E3 P05, P09);
- RLVR, GRPO and noisy verifiers (E3 P04, P07, P10);
- text-to-SQL evaluation and weak tests (E2 BIRD; Spider; test-suite accuracy; E1 APPS "Test Case Quality").
6.3 End each strand by saying how we differ: "none of these… take into account…" (E2 InfoRM).
6.4 Group citations into one bracket: `\citep{a,b,c}` prints "[3–5]" with `compress` (E2 RBR).
6.5 Cite our own earlier work in the third person (T).
6.6 No ✓/✗ comparison table against prior work. Those suit benchmark papers (E1 APPS, E2 BIRD), not ours.

## 7. Method and math notation

7.1 Number every display equation, on the right (E2 12/12; E3). Use `equation` or `align`, never `$$` (T).
7.2 Keep at most 4 numbered equations in the main body: the proxy reward (cases), the counterfactual reward, the GRPO objective, and the hack-rate metric. WS papers carry 1–3 key equations; WS #4 carried 6.
7.3 Fixed notation, used identically in text, equations, the TikZ figure and tables:

| Symbol | Meaning | Source |
|---|---|---|
| $x \in \mathcal{D}$ | question from dataset $\mathcal{D}$ | E3 (`\mathcal` for sets/datasets) |
| $y \sim \pi_\theta(\cdot \mid x)$, $y^\star$ | generated SQL, reference SQL | E2, E3 |
| $D_0$; $D_1,\dots,D_K$ | original DB; counterfactual DBs | ours |
| $\operatorname{exec}(y, D)$ | result of running $y$ on $D$ | `\operatorname` |
| $\tilde R$ vs $R$ | proxy (single-DB) reward vs true/verifiable reward | E1 Reward Hacking |
| $\pi_\theta$, $\pi_{\text{ref}}$, $\beta$, $\mathbb{D}_{\text{KL}}[\pi_\theta \Vert \pi_{\text{ref}}]$ | policy, reference, KL weight | E2 alignment papers |
| $G$, $\{y_i\}_{i=1}^G$, $\hat A_i$, $\epsilon$, $\rho_i$ | group size, rollouts, advantage, clip range, ratio | E3 |
| $\mathbb{E}_{x\sim\mathcal{D},\,y\sim\pi_\theta(\cdot\mid x)}$ | expectation | E2, E3 |
| $:=$ | definition | E3 |
| $\mathbf{1}[\cdot]$ | indicator | E1 APPS, E2 BIRD |

7.4 Put multi-letter subscripts in `\text{}` ($\pi_{\text{ref}}$, $\mathbb{D}_{\text{KL}}$). Write the indicator as `\mathbf{1}[\cdot]`. `\mathbb{1}` does not render with amsfonts, because `\mathbb` supports capitals only.
7.5 Write the reward as a `cases` equation, as E1 CodeRL and E3 P07 do. *Conflict:* CodeRL numbered each case, (4)–(7). **Decision: one number for the whole block.** Reason: there is one referent, and it uses fewer numbers. Replace the placeholder values with our real ones:

```latex
\begin{equation}
  \tilde R(x,y) =
  \begin{cases}
    1  & \text{if } \operatorname{exec}(y, D_0) = \operatorname{exec}(y^\star, D_0),\\
    0  & \text{if $y$ executes but the results differ},\\
    -1 & \text{if $y$ fails to parse or execute}.
  \end{cases}
  \label{eq:proxy}
\end{equation}
\begin{equation}
  R(x,y) = \mathbf{1}\!\left[\operatorname{exec}(y, D_k) = \operatorname{exec}(y^\star, D_k)\ \ \forall k \in \{0,\dots,K\}\right].
  \label{eq:cf}
\end{equation}
```

7.6 Write the GRPO objective out once (E3 P07 Eq. 1). Use the sequence-level form for brevity, and say so if the implementation is token-level. The equation must match the code. If we run over budget, keep only the advantage and move the full objective to the appendix.

```latex
\begin{equation}
\mathcal{J}(\theta)=\mathbb{E}_{x\sim\mathcal{D},\,\{y_i\}_{i=1}^{G}\sim\pi_{\theta_{\text{old}}}(\cdot\mid x)}
\Big[\tfrac{1}{G}\textstyle\sum_{i=1}^{G}\min\!\big(\rho_i\hat A_i,\ \operatorname{clip}(\rho_i,1-\epsilon,1+\epsilon)\hat A_i\big)\Big]
-\beta\,\mathbb{D}_{\text{KL}}\!\left[\pi_\theta\,\Vert\,\pi_{\text{ref}}\right],
\label{eq:grpo}
\end{equation}
% with \rho_i = \pi_\theta(y_i|x)/\pi_{\theta_old}(y_i|x),  \hat A_i = (r_i - mean(r)) / std(r)
```

7.7 Define every symbol in the sentence that introduces it (E2 Part C; E2 STDE defines symbols inline).
7.8 Define the hack metric formally, once, and use the same definition everywhere (E3 P14, P09). For example:
- hack rate $h := \Pr[\tilde R = 1 \wedge R = 0]$ over policy rollouts;
- for the reward audit, false-accept rate $\Pr[\tilde R = 1 \mid R = 0]$ and false-reject rate $\Pr[\tilde R = 0 \mid R = 1]$ (AM 6.1).
7.9 Write a 2–3 sentence `\paragraph{Threat model.}`. The adversary is the RL policy that maximises the proxy reward. The assumption is that the reward sees only one database instance. The accepted Flower paper had an explicit threat model (AM).
7.10 Give discrete design choices, such as the types of DB perturbation, as one compact inline list (WS S2.5). Generator details go to the appendix.
7.11 No theorem environments unless we prove something (E2 2/12, E3 1/14). Proofs go to the appendix (E1).
7.12 No algorithm box in the main body (E3 1/14; E2 2/12, and only beside a figure). Pseudocode, if any, goes to the appendix.
7.13 Call the method "verification by counterfactual execution" or "differential testing". Never call it formal verification (AM 6.1, 6.3).
7.14 Refer to equations as `Eq.~\eqref{eq:cf}`, which prints "Eq. (2)", consistently (E2 uses "Eq. 1" or "eq. (2)", so pick one).
7.15 Use bold for vectors ($\mathbf{r}$ for the group's rewards), as E2 STDE does.

## 8. Experiments and results writing

8.1 Write the setup as run-ins: **Model.** **Data.** **Training.** **Baselines.** **Metrics.** These are the common labels in E3 and the layout WS S3 recommends.
8.2 State the decoding protocol in one sentence: temperature, top-p, max tokens and samples k (E3 P04, P07).
8.3 Define every metric once: a bold name plus its formula or a pointer to Eq. (n) (E3 P14, P09).
8.4 Give the base model's exact name and size, with its model ID in typewriter (E2 BIRD writes `gpt-4-32k`).
8.5 Each results run-in header is the claim itself, such as **Single-DB rewards are hacked.** or **Counterfactual rewards close the gap.** This appears in E1 InstructGPT, E2 RBR, E3 P01/P08/P14 and WS 6 and 8.
8.6 Each claim paragraph runs: claim → number with its baseline beside it → pointer to the Table or Figure → one sentence of interpretation.
8.7 Keep the results prose short, 100–500 words in WS. Table 1 carries the numbers (WS S2.3).
8.8 Show the genre figure: proxy reward against true accuracy over training steps. This is the canonical figure of the literature (E1 Stiennon Fig. 5, Reward Hacking; E2 RM-overopt, InfoRM).
8.9 Show one concrete hack: the SQL, why it passes $D_0$, and why it fails some $D_k$. Put it as an inset in Figure 1 or as a 2–3 line listing (E2 Reflexion and BIRD examples; AM 6.2).
8.10 Attack our own reward. Show that the counterfactual reward is not trivially exploitable, or report where it still is (AM: Beyond ROUGE's shortcut check).
8.11 Give compute and cost in one sentence: GPUs, hours and the overhead of K extra executions (T checklist item; WS S3 "Cost.").
8.12 Hyperparameters, prompts and per-seed numbers go to the appendix with a pointer (WS 6/8; E3 14/14).
8.13 Report caveats openly, as E1 GPT-3 ("datasets where it struggles") and InstructGPT ("still makes simple mistakes") do. Do not drop failing seeds.

## 9. Uncertainty and statistics

9.1 Give every main number a variability. E1 did so in 7/13; E2 had it in 3/10 tables; E3 in 3/14 tables and 5/14 plots; WS in 4/8. It is rare in recent work, so including it signals rigour for RL claims.
9.2 *Conflict:* E1 Stiennon states "error bars represent 1 SE" once, in a footnote, while E3 wants captions to be self-contained. **Decision: state the interval type and n in every caption that shows uncertainty** ("±: std over 3 seeds"), with no global footnote. Reason: captions are read on their own and reused on the poster.
9.3 In tables, give mean ± std over seeds (E1 DT; E2 RBR; E3 P14). For accuracy and hack rate, also give a 95% bootstrap CI over evaluation questions (E1 Chinchilla; E3 P12; WS 7). With a single seed, report the bootstrap CI and write "single seed" in the caption and in the Limitations paragraph.
9.4 With few RL runs, follow Precipice (E1, Outstanding Paper): use interval estimates, not point estimates. Put per-seed values in the appendix. If we claim "better", give the probability of improvement or a named test.
9.5 Write CIs in square brackets, "71.2% [68.9, 73.4]" (WS 3, 7, 8), and std with ±. *Conflict:* Chinchilla used parentheses. **Decision: brackets.** Parentheses are already used for deltas and citations.
9.6 Never write "significantly" without naming the test. Correct for multiple comparisons when we test several things (E3 P09 uses Benjamini–Hochberg).
9.7 If an LLM judge labels hacks, report its agreement with human labels, such as Cohen's κ (E3 P14).
9.8 Shaded bands in plots show the same interval as the table (E1 Side Effects ±1 std; E3 P03 std bands).

## 10. Figures in general

10.1 The main body holds Figure 1 (TikZ diagram) and optionally Figure 2 (a plot). WS has a median of 1.5 figures, and E3 implies 2–3 at most for 4 pages.
10.2 *Conflict on placement:* a page-1 figure appears in main-track papers only rarely (E1 2/13, E2 1/12, E3 1/14), but a teaser by the top of page 2 is the norm (E1 12/13, E2 9/12, E3 12/14). WS has **0/8** on page 1, with Figure 1 at the top of page 2. **Decision: no page-1 figure. Figure 1 goes `[t]` on page 2, full width, at most 30% of the page height.** Reason: the title, authors and IMRaD abstract fill page 1.
10.3 Figure 1 shows the method pipeline plus one hacked-query inset. Topic-close E3 papers pair a pipeline or environment drawing with a key result (P02, P04; AM 6.2).
10.4 Use vector graphics only: PDF for plots, TikZ for diagrams. No raster screenshots. The best E2 papers are fully vector; DPO's raster plots are the counter-example.
10.5 Size figures as a fraction of `\linewidth` (T). Never place figures by hand with `\special` (T).
10.6 Make each figure at its final width, with all text **≥ 7 pt at 100% zoom**. Failures: E1 InstructGPT at about 4 pt; E2 Mirage, RM-overopt and MT-Bench at 3–5 pt; E3 6/14 were hard to read.
10.7 *Conflict on figure font:* sans-serif is the norm (E1: 7/13 left default DejaVu Sans; E3 9/14). Serif matching the body looks cleanest (E1 CoT; E3 4/14: P04, P09, P10, P13). **Decision: serif (Times-like) in all figures.** Reason: TikZ inherits the body's Times automatically, so the diagram and the plots share one family.
10.8 Each figure must stay legible in black and white (T). Use markers and line styles as well as colour.
10.9 Give each method the same colour in every figure, highlight and poster panel. E1 did this in 4 papers (Stiennon, InstructGPT, Side Effects, Precipice).
10.10 No titles inside plots; the caption says what is shown. E3 P11's in-plot titles and E1 APPS's plot titles look least polished.
10.11 Place every float `[t]`. Never use `[h!]` or `[H]`. The template's float parameters favour tops, and WS floats sit at page tops.
10.12 Reference every figure in the text before it appears.
10.13 Multi-panel figures get one shared legend (E3) and name their panels in the caption as bold **Left:** / **Right:**. *Conflict:* E1, E2 and E3 split between "(a)/(b)" subcaptions and Left/Right. **Decision: Left/Right in the caption.** Reason: no `subcaption` package and no subcaption lines.
10.14 No clipart, cartoons, emoji or icons. E3 P14's busy infographic and P09's robots are the counter-examples. Draw ✓ with `\checkmark` (amssymb) and ✗ with `\ding{55}` (`pifont`).

## 11. Colour palette (hex codes)

*Conflict:* the convention is "ours = a warm saturated accent, baselines cool" (E2 VAR, InfoRM; E3 P10, P01). The topic convention is "proxy = red, true = blue" (E1 Reward Hacking's Goodhart curve; E3 P05, red #E45454 vs blue #5484B4). **Decision: follow the topic semantics.** The hackable proxy is warm (a warning) and our verifiable reward is the blue accent. Reason: it matches the red "hacked" and green "verified" tags, and orange against blue is colour-blind safe.

| Role | Hex | Use | Source |
|---|---|---|---|
| **Ours**: verifiable / counterfactual reward (the one accent) | `#5484B4` | lines, bars, the verifier path in Fig. 1 | E3 P05 |
| Proxy: single-DB reward (main baseline) | `#B4543C` | lines and bars | E3 P10 |
| Second baseline or ablation | `#CCB484` | lines and bars | E3 P10 |
| Neutral or other | `#8C8C8C` | other runs, de-emphasised items | E3 P10 grey baselines |
| Reference line | `#000000` | dotted, 0.8 pt | E1 5/13, E2 7/12 |
| Ink (diagram strokes and text) | `#333333` | TikZ lines | – |
| Pastel fill: policy / model | `#E4E4FC` | TikZ boxes | E3 P07 |
| Pastel fill: databases / environment | `#CCE4E4` | TikZ boxes | E3 P07 |
| Pastel fill: input / data | `#FCFCCC` | TikZ boxes | E3 P07 |
| Status fill: hacked | `#F4B6B6` + ✗ | tags and insets | E2 Reflexion |
| Status fill: verified | `#B7E1B5` + ✓ | tags and insets | E2 Reflexion |
| Status text: red / green | `#CC2424` / `#249C24` | tag words only | E3 P09 |
| Sequential ramp (ordered variable such as K or step) | `#9CCCE4` → `#0C3C6C` | sweeps | E3 P03 |
| Hyperlinks | `#0C3C6C` | cite, link and url colour | dark end of the ramp |

11.1 Use at most 5 hues per figure (E3).
11.2 Ours is the only saturated accent. Baselines are muted (E2 Part C; E3).
11.3 Never encode meaning by colour alone. Red and green tags always carry ✓/✗ and a word ("hacked", "verified"), because of the B/W rule (T) and colour-blind readers.
11.4 Name the colours in words in the caption: "Blue: ours; rust: single-DB reward" (E3 P04).
11.5 An ordered variable gets one sequential hue (E1 viridis/magma; E2 Mirage; E3 P03).
11.6 No rainbow, tab20 or saturated-primary palettes. E3 P11 looks worst, and E1 APPS and LAION look least polished.
11.7 Body text is black. Colour in the text appears only in links (E1: semantic colour in body text is rare). Table cells have no colour shading (decision; see 14.15).
11.8 Define each colour once, with `\definecolor{name}{HTML}{…}` in the preamble, and use the same hex in matplotlib.

## 12. Plot styling

12.1 Plot with matplotlib and save as vector PDF (E2 10/12 use matplotlib).
12.2 Set `pdf.fonttype = 42` (embedded TrueType). Matplotlib's default writes Type 3 fonts, which the template forbids (T).
12.3 Set `figsize` to the final width: 5.5 in for full width (the text block is 396 pt = 5.5 in in E1 13/13 and T) or 2.7 in for half width. Include the figure at that same width. Use `layout="constrained"`, not `bbox_inches="tight"`, which changes the size and so the font scale.
12.4 Fonts are STIX serif (it ships with matplotlib and looks like Times; decision 10.7). Labels are 8 pt; ticks and legend 7.5 pt; nothing below 7 pt.
12.5 Main lines are 1.5 pt (E1 1.5–2 pt; E2 DPO 1.5 pt), axes 0.6 pt and markers 3–4 pt. Give each method a different marker so the plot survives grayscale (E3 P03, P09, P10, P13).
12.6 Remove the top and right spines. The polished E1 papers do: Stiennon, InstructGPT, DT.
12.7 Use a light horizontal grid only, 0.4 pt at alpha 0.3. *Conflict:* E1 used no grid or a very light one; E2 6/12 used a light grid. **Decision: light horizontal grid**, because it helps poster readers.
12.8 Label lines directly when there are 3 or fewer (E1 Stiennon Fig. 1, the cleanest of E1; E3 P09). Otherwise use one shared, frameless legend above the panels (E2, E3).
12.9 Draw reference, chance or baseline lines in black, dotted, 0.8 pt. Dashed is reserved for the proxy metric (12.11).
12.10 Show uncertainty as a same-colour shaded band at alpha 0.2, or thin error bars with small caps (E1; E2 DPO).
12.11 Encoding for the genre plot (8.8): **colour = reward variant**, **solid = held-out true (counterfactual) accuracy**, **dashed = training proxy reward $\tilde R$**. The reward-hacking literature draws this as "proxy vs true" (E1 Reward Hacking; E2 RM-overopt).
12.12 Axis labels use sentence case and give units: "Training step", "Execution accuracy (%)". Say "log scale" when an axis is logarithmic.
12.13 Print values on bars only when there are 6 or fewer bars (E3 4/14).
12.14 No letters inside the plot area (10.13).
12.15 Shared settings:

```python
import matplotlib as mpl
mpl.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,              # no Type 3 fonts
    "font.family": "serif", "font.serif": ["STIXGeneral"], "mathtext.fontset": "stix",
    "font.size": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "lines.linewidth": 1.5, "lines.markersize": 3.5,
    "axes.grid": True, "axes.grid.axis": "y", "grid.linewidth": 0.4, "grid.alpha": 0.3,
    "legend.frameon": False,
})
OURS, PROXY, ABL, NEUTRAL = "#5484B4", "#B4543C", "#CCB484", "#8C8C8C"
fig, ax = plt.subplots(figsize=(2.7, 1.9), layout="constrained")  # 5.5 in for full width
fig.savefig("fig2.pdf")
```

12.16 Check every figure: open it at 100% and read the ticks, and confirm that `pdffonts fig2.pdf` lists no Type 3 fonts.

## 13. Diagrams (TikZ)

13.0 *Conflict:* TikZ appears in E1 2/13 (Markov's MDP figures, Reward Hacking's polytopes), E2 1/12 (STDE, a best paper) and E3 0/14. Design tools (PowerPoint, Keynote, Figma) dominate: E2 9/12 and E3 10/14. **Decision: TikZ for every architecture diagram and flowchart.** This is the user's standing preference, from their experience that it looks better. TikZ is also vector, uses the body font and takes exact palette hex codes.

13.1 Draw every diagram in TikZ, inline or via `\input{fig1.tikz}`. No PowerPoint, draw.io or raster images.
13.2 Draw at final width. Plan coordinates for `\linewidth` (13.97 cm at full width). Never `\resizebox` or `\scalebox`, and never `scale=` with `transform shape`: all of these shrink the text.
13.3 Text is the body serif, which TikZ inherits. Use `\footnotesize` (9 pt in this template) by default and `\scriptsize` (7 pt) as the floor. Nothing smaller (T font table).
13.4 Typeset math in nodes in LaTeX ($\tilde R$, $D_k$), with the same symbols as the equations (E2 STDE).
13.5 SQL in nodes is `\ttfamily`, at most about 40 characters per line and at most 3 lines (E2 BIRD uses monospace SQL).
13.6 Use 2–4 pastel fills from section 11 plus one accent: ours, `#5484B4`, on the verifier path. Pastel fills at about 15–25% saturation with one accent appear in E2 (7 papers) and E3. Hack and verified status use the status fills with ✗/✓.
13.7 Rounded boxes: `rounded corners=2pt` (E2 DPO; E3 P07 and P12 rounded pastel panels).
13.8 Thin lines: 0.6 pt boxes and 0.6–0.8 pt arrows with `-{Stealth[length=4pt]}`, in ink `#333333`.
13.9 No drop shadows, gradients or 3D. E2 VAR's 3D-style PowerPoint pipeline is the counter-example.
13.10 With 3 or more stages, add small numbered step badges: filled ink circles with white digits (E1 Stiennon, CodeRL; E3 P08, P12).
13.11 Flow runs left to right in one row, two at most. Use 6–8 nodes at most, and keep the height within 30% of the page (10.2).
13.12 Group related nodes with a thin dashed border via `fit` (E2 STDE's dashed bounding boxes).
13.13 Define the styles once in the preamble, with the colours from 11.8:

```latex
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,fit,calc,backgrounds}
\definecolor{ink}{HTML}{333333}   \definecolor{ours}{HTML}{5484B4}
\definecolor{fillM}{HTML}{E4E4FC} \definecolor{fillD}{HTML}{CCE4E4} \definecolor{fillQ}{HTML}{FCFCCC}
\definecolor{hack}{HTML}{F4B6B6}  \definecolor{ok}{HTML}{B7E1B5}
\tikzset{
  box/.style={draw=ink, line width=0.6pt, rounded corners=2pt, fill=#1,
              align=center, font=\footnotesize, inner sep=3pt, minimum height=6mm},
  box/.default=fillM,
  arr/.style={-{Stealth[length=4pt]}, line width=0.7pt, draw=ink},
  accent/.style={draw=ours, line width=0.9pt},
  group/.style={draw=ink, dashed, line width=0.4pt, rounded corners=3pt, inner sep=4pt},
  badge/.style={circle, fill=ink, text=white, font=\scriptsize\bfseries, inner sep=1pt},
}
```

13.14 Before writing any TikZ, check that `kpsewhich tikz.sty` returns a path on the WSL toolchain.
13.15 Keep Figure 1 compilable as a `standalone` file that shares the same `\tikzset` block, for export to the poster (22.3).

## 14. Tables

14.1 Put the table caption **above** the table. The template swaps the caption skips for this. *Conflict:* E1 placed it below in 7/10 tables, while E2 placed it above in 8/10 and E3 in 14/14. **T wins: above.**
14.2 Use booktabs (`\toprule`, `\midrule`, `\cmidrule`, `\bottomrule`) and no vertical rules (T: "Publication-quality tables do not contain vertical rules"; E2 10/10).
14.3 Use exactly one main results table (WS 7/8). Rows are reward variants. Columns are accuracy on $D_0$, accuracy on held-out counterfactual DBs, hack rate and, optionally, cost.
14.4 Set the table in `\small` (9 pt) at most. Never `\scriptsize`, `\tiny` or `\resizebox`: E2 MT-Bench and InfoRM, and WS #8 (barely legible), are the counter-examples. *Conflict:* T allows a size reduction only for references, but `\small` tables are near-universal (E2 10/10). **Decision: `\small` inside table floats only, never in body text.**
14.5 At most 7 columns (E3: 5–8 is typical). Move extra columns to the appendix rather than shrinking the table.
14.6 Put units in the header: `Acc.\ (\%)` (E3 6/14).
14.7 *Conflict on arrows:* ↑/↓ appear in 0/10 E1 tables, 3/10 in E2 and 2–3/14 in E3. **Decision: use ↑/↓ in the headers**, because our table mixes directions (hack rate ↓ next to accuracy ↑), which is E3's stated case for them. Explain the arrows once in the caption.
14.8 Bold the best value per column and say so in the caption (E2: bold in 7/10, stated in 3/10; E3 8/14). No underline for second-best (only E3 2/14 do it, and our table has few rows).
14.9 Put our row last, below a `\midrule`, labelled "(ours)" (E1 Chinchilla, CodeRL; E3 P07, P08, P10).
14.10 Write mean ± std compactly as `71.2{\scriptsize$\,\pm$1.3}` (E3 P14 uses small subscripts). The ± part is 7 pt, the legibility floor.
14.11 Right-align numbers and give the same number of decimals within a column (E1 Chinchilla).
14.12 Mark a missing cell with "–" (E2 VAR).
14.13 Set model and code identifiers in `\texttt` (E2 RBR, InfoRM, BIRD).
14.14 Group column headers with `\cmidrule(lr){a-b}` (E2 6/10).
14.15 No cell colour or shading. Grey group rows (E2 BIRD; E3 P14) are skipped to stay legible in B/W and to save ink.
14.16 The table fits `\linewidth` without resizing.
14.17 Use `\centering` inside the float, not the `center` environment, which adds vertical space. The template asks for centred tables.
14.18 No comparison table against prior work (6.6). The hack taxonomy table goes to the appendix (5.8).

## 15. Captions

15.1 Figure captions go below and table captions above (T; E3 14/14).
15.2 Keep the default labels "Figure 1:" and "Table 1:" and the default caption format (T; E2 12/12).
15.3 Write caption text in sentence case (T: lower case except the first word).
15.4 Keep captions at the default 10 pt. *Conflict:* about half of E2 set captions smaller. E1 kept 10 pt in 12/13, and T forbids format changes. **T wins.**
15.5 Make the first sentence a bold takeaway (the finding, not the topic). E1 5/13 open with a bold lead, E2 6/12, and E3 2/14 (P03, P05) with a bold takeaway plus 4/14 with bold panel names. Example: `\caption{\textbf{Single-DB rewards accept hacked SQL that counterfactual DBs reject.} ...}`.
15.6 Then say what is plotted, how to read the panels (**Left:** / **Right:**), what the bars or bands mean and the n, and name the colours in words (E3 P04).
15.7 Figure captions run 25–60 words (E3 typically 30–70). Table captions run 20–50 words and define every abbreviation, the arrows, the bold, ±, n and the aggregation, e.g. "mean over 3 seeds, greedy decoding" (E3 P02, P08, P13, P14).
15.8 Never write "A bar chart shows…" (E2 BIRD's weak caption).
15.9 A caption must be understandable without the body text (WS S2.2), because it becomes the poster panel text.

## 16. Citations, references and hyperlinks

16.1 *Conflict on citation style:* E1 used numeric in 7/13, alpha in 1/13 and author-year in 5/13, rising to 4/6 in 2022. E2 used numeric in 11/12 and E3 in 11/14. T accepts either if it is consistent. **Decision: numeric.** Load it with `\PassOptionsToPackage{numbers,compress}{natbib}` placed **before** `\usepackage[preprint]{neurips_2025}` (T). Reason: it is the current majority and shorter in running text.
16.2 Use `\citet{key}` when the authors are the grammatical subject: "Skalse et al. [12] define…" (T names `\citet`). Use `\citep{key}` otherwise: "…is hackable [12]." Never "[12] shows" or "In [12]".
16.3 Put a non-breaking space before every citation, and the citation before the punctuation: `hacking~\citep{skalse2022}.`
16.4 Aim for 15–25 references. E1 suggests about 15–30 for 4 pages, and E2/E3 15–25. **Decision: 15–25.**
16.5 Use `\bibliographystyle{plainnat}` with the `numbers` option (E2: plainnat-like references in most papers).
16.6 Candidate references, all from the study:
- Skalse et al. 2022 and Stiennon et al. 2020 (E1);
- RM over-optimisation in DAAs 2024 and InfoRM 2024 (E2);
- CodeRL 2022 (cases reward) and APPS 2021 (weak tests) (E1);
- BIRD 2023 (E2) and SQL-R1 2025 (E3);
- "Does RL really incentivize…" 2025, inference-time reward hacking 2025, monitor-based interventions 2026 and NOPO 2026 (E3);
- Precipice 2021, if we use its statistics (E1);
- also the GRPO source, Spider, test-suite accuracy and the base model.
16.7 Bib hygiene: protect capitals with braces (`{GRPO}`, `{SQL}`), prefer the published venue over arXiv when one exists, and write venue names one consistent way.
16.8 Links: `colorlinks=true` with navy `#0C3C6C` for cite, link and URL colours. Never ship the default boxes: E1 5/13, E2 8/12 and E3 8/14 did, and boxes "look unfinished" or "dated". `hidelinks` (E2 AgentDojo) is the fallback.
16.9 Write URLs with `\url{}`, in typewriter (E2 12/12).
16.10 At most 2 footnotes, placed after punctuation (T: "sparingly"; E3: 1–2 in 4 pages).
16.11 Set the PDF metadata with `\hypersetup{pdftitle={…}, pdfauthor={…}}`.

## 17. Limitations, broader impact and ethics

17.1 Write `\paragraph{Limitations.}` inside Section 5, in 2–4 sentences: one model size, the number of seeds, how far the counterfactual DBs cover failure modes, and compute. Limitations appear in the main body in E1 12/13, E2 11/12, E3 9/14 and WS 6/8.
17.2 Write `\paragraph{Broader impact.}` in Section 5, 1–2 sentences: why trustworthy rewards matter for agents deployed on databases, and the dual-use risk that a hack catalogue could teach exploits. *Conflict:* the 2020 Broader Impact section was mandatory (E1), E2 put it in the main body in only 3/12, and E3 moved it to the appendix or checklist. **Decision: keep it in the main body**, because the trust framing makes it core to this venue.
17.3 Add one "what the result is not" sentence that scopes the claim (WS #8 "What the result is not."; E3 P12 "Claims and non-claims").
17.4 Do not claim formal verification, deception results or Indic-language results unless we actually ran them (AM 6.3).
17.5 Put dataset licences (Spider, BIRD) and the model licence in the appendix (E3 P02 licences appendix; E2 D&B datasheets).
17.6 Add a one-line LLM-usage declaration in the appendix. The 2025+ checklist has item 16 "Declaration of LLM usage" (E3); E3 P14 has a "Use of LLMs" appendix; AM Beyond ROUGE had a GenAI disclosure.
17.7 The `ack` environment declares funding and competing interests (T). It is 1–2 lines and counts toward the 4 pages.
17.8 The checklist is dropped, but use its questions as a self-review: claims, limitations, reproducibility, statistics and compute (T A9).

## 18. Appendix

18.1 Order: conclusion → `ack` → References → Appendix (T; E2 B13).
18.2 After `\appendix`, use `\section{…}` (lettered A, B, …) with labels such as `app:cf`. Refer forward with `Appendix~\ref{app:cf}` (E3 14/14 use forward pointers).
18.3 Contents (WS S3):
- A: counterfactual-DB generation;
- B: hack examples (SQL plus DB snippets);
- C: hyperparameters, prompts and compute;
- D: extra results, ablations and per-seed numbers;
- E: licences and LLM-usage statement.
18.4 The main claim must be believable without the appendix (WS). AgentiQL put all its floats in the appendix and its main pages are hard to read.
18.5 Print the full prompts verbatim (E3 9/14; WS 5/8).
18.6 Never ship "Appendix ??". Compile until the log has no undefined references (E1 CodeRL shipped "??" three times).
18.7 The appendix lives in the same PDF, after the references (AM allows additional pages).
18.8 Floats, captions and typography in the appendix follow the same rules as the main body.

## 19. Typography and LaTeX hygiene

19.1 Preamble (T header lines plus our additions):

```latex
\documentclass{article}
\PassOptionsToPackage{numbers,compress}{natbib}  % before the style file
\usepackage[preprint]{neurips_2025}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{url}
\usepackage{booktabs}
\usepackage{amsfonts,amssymb,amsmath}
\usepackage{nicefrac}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{graphicx}   % the template does NOT load it
\usepackage{pifont}     % \ding{55} for the cross mark
\usepackage{wrapfig}    % only if a wrapfigure is used
% tikz + palette + \tikzset block from 13.13
\definecolor{linknavy}{HTML}{0C3C6C}
\hypersetup{colorlinks=true, citecolor=linknavy, linkcolor=linknavy, urlcolor=linknavy,
            pdftitle={...}, pdfauthor={...}}
```

19.2 Build with pdflatex or latexmk on US Letter. `pdffonts paper.pdf | grep "Type 3"` must print nothing (T; toolchain verified Nov 21).
19.3 No `geometry`, `fullpage`, `titlesec`, `\baselinestretch`, `\linespread` or layout `\setlength`s (T).
19.4 `$$…$$` is forbidden. Use `\[…\]`, `equation` or `align` (T).
19.5 Put a non-breaking space before every reference: `Figure~\ref{fig:pipeline}`, `Table~\ref{tab:main}`, `Section~\ref{sec:method}`, `Eq.~\eqref{eq:cf}`, `Appendix~\ref{app:cf}`.
19.6 Write reference names in full and capitalised: "Figure 1", "Table 1", "Section 2". Never "Fig." (E1 Chinchilla uses "Section 4.2", "Figure A3").
19.7 Label prefixes: `fig:`, `tab:`, `sec:`, `eq:`, `app:`.
19.8 Run-in headers carry a period inside the braces: `\paragraph{Setup.}`. *Conflict:* E2 split between a period (5/12), no period (4/12) and a colon (2/12). **Decision: a period**, the most readable form. Use one style throughout (E2 11/12 are consistent).
19.9 Use `\texttt` for SQL keywords, code identifiers, model IDs and tokens (E2 Part C; E3 6/14).
19.10 Italicise a term at its first definition (E2 12/12; E3 10/14). Use bold only for run-in headers, caption leads, contribution lead phrases and the best table values. *Conflict:* E3 7/14 (and E2 VAR, InfoRM heavily) bold sentences inside paragraphs. **Decision: no inline bold in the body.** Overused bold loses its signal.
19.11 No small caps for method or benchmark names (E1, E2 BIRD and E3 use them). Decision: fewer font switches.
19.12 Get `\mathbb` from amsfonts/amssymb, never `\bbold` (T). Write the indicator as `\mathbf{1}` (7.4).
19.13 Use `\-` hyphenation hints and rewording to fix overfull lines (T). Fix every overfull hbox that is visible.
19.14 Grep the log for "undefined" (references and citations), and the PDF text for "??" (`pdftotext paper.pdf - | grep -n '??'`) (E1 CodeRL).
19.15 Numbers and symbols: `10\%`; `12.8$\times$`; a true minus `$-0.6$`; en dash for ranges `3--5`; "3.35B" for parameter counts.
19.16 Quotes are ``` ``…'' ```. Never straight `"…"`.
19.17 Keep `microtype` (T loads it).
19.18 Stretched pages are normal: T sets widow and club penalties to 10000. Do not fight them with `\vspace`.
19.19 Never use `\\` to break paragraphs. Use a blank line.

## 20. Space-saving: allowed vs forbidden

**Allowed**

20.1 Cut words first. None of the 8 WS papers shrank margins.
20.2 `wrapfigure` / `wraptable` for small plots or tables (E1 6/13, E2 5/12, E3 6/14, WS 2/8). Do not use them near section starts, lists or page breaks.
20.3 Side-by-side minipages: figure + figure or figure + table (E1 5/13, E3 6/14, WS 1/8).
20.4 Run-in `\paragraph` instead of `\subsection` (E1 13/13).
20.5 Inline lists, "(i)… (ii)… (iii)…" (E3 6/14; WS 3/8).
20.6 Merged sections: related work inside the intro, and "Discussion and conclusion" (E3; WS).
20.7 Details moved to the appendix with pointers (E3 14/14).
20.8 Long URLs in footnotes (E1 LAION), within the 2-footnote cap (16.10).
20.9 `\-` hints and rewording to remove a one-word last line (T).
20.10 `\small` inside tables (14.4). `\small` references (T) are optional, since references do not count toward the limit.
20.11 Shortening Figure 1 by redrawing it in TikZ, not by scaling it.

**Forbidden**

20.12 Changing the margins, geometry, `fullpage`, body font size, `\baselinestretch`, `\linespread`, `\parskip`, the display skips or the section spacing (T).
20.13 Negative `\vspace` anywhere (T A10; E1 CodeRL's rules collide with the text).
20.14 Shrinking captions with `\small` or via the `caption` package (T; only E1 Precipice did).
20.15 `\scriptsize` or `\tiny` tables, and `\resizebox` below 7 pt (E2; WS #8).
20.16 Figure text below 7 pt (10.6).
20.17 `\enlargethispage`. The template uses it itself on page 1; we must not.
20.18 Dropping the Limitations paragraph or the acknowledgments to make room.
20.19 Moving all floats to the appendix (WS AgentiQL is the negative example).
20.20 Letting the acknowledgments spill past page 4.

## 21. Language and style

21.1 Write in the "we" voice (E2 12/12).
21.2 No contractions (E2 12/12).
21.3 Short sentences, one idea each. A mixed panel that includes management faculty reads this paper (AM).
21.4 Give the plain-language claim first and the jargon after it (AM).
21.5 Use few acronyms (RL, RLVR, GRPO, SQL, LLM). Define each at first use in the abstract and again in the body.
21.6 Fix one term per concept and never alternate. Use "proxy reward" or "single-DB reward", but one of them only. Use "verifiable" or "counterfactual" reward, one only. Use "reward hacking", not "reward gaming" or "over-optimization" (E2 InfoRM defines its synonym once and moves on).
21.7 Use American spelling. The template is US: Letter paper, the "Acknowledgments" heading.
21.8 Write "e.g.," and "i.e.," with a comma. Avoid "etc.".
21.9 Use "first" or "novel" only after checking (E1 Skalse's "first formal definition" was defensible). With a single seed, use "suggests", not "shows".
21.10 Give numbers as digits with units and the same precision as the tables.
21.11 Lead with trust, not capability (AM 6.3; see 23.1).

## 22. Poster-readiness

22.1 The poster is 48 × 36 in, landscape, 3 columns, matching the AM Chatterbox poster, the organiser's own.
22.2 All figures are vector (10.4), so they scale to poster size.
22.3 Keep Figure 1 as a `standalone` TikZ file that shares the preamble styles (13.15). Re-render the plots from their scripts at poster size instead of upscaling them.
22.4 Claim-style run-ins and headings become the poster's section headers. The AM poster used numbered claim subheadings.
22.5 Self-contained captions (15.9) become the poster panel text.
22.6 The paper and the poster share one palette (11.8).
22.7 Keep the Table 1 numbers in one CSV that drives both the LaTeX table and any poster chart, so the numbers never drift.
22.8 Write one bold takeaway sentence per result. The AM poster's conclusion had 2 bold takeaways.
22.9 Keep the hack-example SQL to 3 lines or fewer so it reads from a distance.

## 23. Topic framing for this symposium

23.1 Lead with trust: "a reward we cannot trust, and a fix". Never present the work as a pure accuracy paper (AM 6.3).
23.2 Symposium topics we map to, in priority order (AM 6.1):
1. **Evaluation & benchmarking in RAI** (primary). The reward audit is an assessment framework; report false-accept and false-reject rates per reward.
2. **Red-teaming & stress testing.** The RL policy acts as an automated red-teamer of the reward; show the hacks GRPO finds.
3. **Reasoning & verification.** "Verification by counterfactual execution" (differential testing), honestly not formal methods.
4. **Agent safety & reliability.** SQL agents act on real data; silently wrong analytics are a hazard; "SQL is code", which matches the committee's work on safe code-generating assistants.
5. **Observability & monitoring** (secondary). The single-DB vs counterfactual reward gap, tracked as a training-time monitor.
6. **Deception**: one sentence at most, or none. Reward hacking is specification gaming, not intent.
7. **AI governance & policy (India)**: one optional sentence linking audits to the accountability and safety "sutras" of the India AI Governance Guidelines (MeitY, Nov 2025). No invented India experiments. Mention Indic languages only if we actually run them.
23.3 Name 2–3 of these topics in one line in the intro (4.2).
23.4 Include the threat-model paragraph (7.9), as the accepted Flower paper did.
23.5 Include the self-attack robustness check (8.10). These reviewers like authors who attack their own metric (AM).
23.6 Speak to the committee's interests: safety of code-generating assistants, and evaluator or judge drift during RL (AM: Nova AI Challenge; Chatterbox poster). Frame the reward as an evaluator that can be gamed.
23.7 Being small-scale and honest is fine (AM: a 1.7B model on CPU was accepted). State the scale plainly and do not apologise for it.
23.8 A Nova touchpoint (Nova as a zero-shot baseline scored by both rewards) is optional. It needs the owner's sign-off for any cloud or credential use (AM 6.2). The 2027 call does not state a Nova priority.
23.9 Do not pad related work (AM 6.3; 6.1).

## 24. Exemplar papers (imitate these)

1. **Stiennon et al. 2020, *Learning to summarize from human feedback* (E1).** The over-optimisation curve, direct line labels and a numbered contributions block.
2. **Skalse et al. 2022, *Defining and Characterizing Reward Hacking* (E1).** The proxy $\tilde R$ vs true $R$ notation, a crisp definition, and the Goodhart red/blue curve.
3. **CodeRL 2022 (E1).** The cases-equation execution reward. Copy its maths; avoid its "??" and its boxed links.
4. **Agarwal et al. 2021, *Statistical Precipice* (E1).** How to report results from few RL runs.
5. **STDE 2024 (E2, best paper).** All-TikZ diagrams with pastel fills, short booktabs tables and corner arrows.
6. **SQL-R1 2025 (E3).** A text-to-SQL GRPO objective, a run-in plus cases equation per reward component, and units in table captions.
7. **NOPO 2026 (E3, spotlight).** A muted palette with one accent, serif plots, bold-best tables stated in the caption, and the verifier "Accepted/Rejected" idiom.
8. **Monitor-based interventions 2026 (E3).** A reward-hacking safety framing, serif plots, in-plot labels and rigorous statistical reporting.
9. **WS #6, *You Need Reasoning to Learn Reasoning* (2511.04902).** The closest 4-page genre: claim headings, wrapfigures and one table that carries the results.
10. **AM Flower Labs, *Supercharging Federated Intelligence Retrieval*.** An actually accepted symposium paper: threat model, 1 figure plus 1 table, and a modest scale.

## 25. Conflict index (decisions above)

| Conflict | Decision | Rule |
|---|---|---|
| Footer: venue footnote (AM) vs "Preprint." (T) | keep "Preprint.", no footnote | 0.4 |
| Title colon (E2, E3) vs verb title (E1) | colon form | 1.1 |
| Abstract ~190–215 (main) vs ~130 (WS) | 150–180 words | 3.3 |
| Abstract numbers vs none (Flower) | ≥ 2 numbers | 3.4 |
| Contribution bullets vs inline | inline (i)–(iii) with bold leads | 4.6 |
| Title Case headings (papers) vs sentence case (T) | sentence case | 5.2 |
| Float count: 4 (AM) vs ~2.5 (WS) | ≤ 3; taxonomy to the appendix | 5.8 |
| Related work early / late / merged | merged paragraph in the intro | 6.1 |
| Cases numbering: per case (CodeRL) vs one | one number | 7.5 |
| Interval stated once (E1) vs in every caption (E3) | every caption | 9.2 |
| CI in parentheses vs brackets | brackets | 9.5 |
| Page-1 figure (main) vs none (WS) | none; Figure 1 at the top of p2 | 10.2 |
| Sans vs serif figure font | serif | 10.7 |
| (a)/(b) vs Left/Right panels | Left/Right in the caption | 10.13 |
| Ours warm (convention) vs proxy red / true blue (topic) | ours blue, proxy rust | 11 |
| Grid vs no grid | light horizontal grid | 12.7 |
| TikZ (rare) vs PowerPoint (dominant) | TikZ (user preference) | 13.0 |
| Table caption below (E1) vs above (T, E2, E3) | above | 14.1 |
| `\small` tables vs T's references-only rule | `\small` in tables only | 14.4 |
| ↑/↓ arrows: none (E1) vs some (E2, E3) | use them (mixed directions) | 14.7 |
| Smaller captions (E2) vs 10 pt (E1, T) | 10 pt | 15.4 |
| Author-year vs numeric citations | numeric | 16.1 |
| Broader impact: main body vs appendix | main body, 1–2 sentences | 17.2 |
| Run-in punctuation: period / none / colon | period | 19.8 |
| Inline bold sentences vs none | none | 19.10 |

## 26. Final pre-submission checklist

- [ ] `\usepackage[preprint]{neurips_2025}`: the footer reads "Preprint."; no line numbers; no "Anonymous".
- [ ] US Letter; `pdffonts` lists no Type 3 font; every font is embedded.
- [ ] Content ends on page 4; the acknowledgments fit inside page 4; the References heading may start on page 5.
- [ ] No formatting tweaks: no negative `\vspace`, `geometry`, `\linespread`, shrunken captions or `\enlargethispage`.
- [ ] The abstract is one paragraph of 150–180 words, in IMRaD order, with at least 2 numbers that match Table 1.
- [ ] Author names, affiliations and emails are printed, with the emails spelled correctly.
- [ ] Figure 1 is TikZ, full width, at the top of page 2, ≤ 30% of the page; all text ≥ 7 pt at 100%.
- [ ] Every plot is vector, uses the serif font and the section-11 palette, has `pdf.fonttype 42`, and reads in grayscale.
- [ ] Table 1: caption above, booktabs, no vertical rules, `\small` at most, units, ↑/↓ explained, best values in bold, ± with n.
- [ ] Every caption opens with a bold takeaway and states the n and interval type where relevant.
- [ ] Every figure and table is referenced in the text with `~\ref`.
- [ ] No "??" in the PDF and no "undefined" in the log.
- [ ] Numeric citations with `\citet`/`\citep` used correctly; 15–25 references; `colorlinks` in navy with no boxes.
- [ ] No `$$`; every display equation is numbered; every symbol is defined.
- [ ] Limitations and broader-impact paragraphs are present; no claims of formal verification, deception or Indic results.
- [ ] Appendix: CF-DB generation, hack examples, hyperparameters and prompts, per-seed results, licences, LLM-usage line.
- [ ] The NeurIPS checklist is removed.
- [ ] One term per concept throughout; American spelling; no contractions.
- [ ] Email the PDF to trusted-ai-symposium@amazon.com before Nov 30, 2026, ideally a day early (AM).

---

# Part II — Additional rules from the user's paper-writing guides

**Sources.** **[AN]** is `C:/developer/research_ai/paper-writing/paper writing analysis.md`; **[PR]** is `…/paper writing prompt.md`. A § or rule id points into the named file. "→ I-x.y" marks a nuance to Part I rule x.y. Rules that Part I already covers in full are not repeated here.

## II-1. Story first (before any prose)

1. One paper, one idea. Make 1–3 refutable claims that all serve it. Everything else supports them or goes to the appendix. [AN §1.1, §4.1; PR A6.1]
2. Order the claims: core insight or method → evidence → artifact. [AN §4.1; PR A6.1] → I-4.6 (the order of the inline (i)–(iii)).
3. Each contribution is a refutable claim with a forward reference "(§4)". Never write an activity ("we study", "we conduct extensive experiments"). [AN §1.5, §4.1; PR A6.2] → I-4.7.
4. Evidence comes from qualitatively different lines of work (for us: audit, training curves, hack examples), with at least one hard-to-deny experiment. [AN §4.1]
5. Write the ABT sentence: "[Field] does X AND ___, BUT ___, THEREFORE we ___." No BUT means no story, and "AND, AND, AND" reads like a lab report. [AN §5.2; PR A6.3]
6. Phrase the BUT as an error in current assumptions, not just a gap. For us: "Execution-match rewards assume that one database reveals semantic equivalence, and that assumption fails when…". [AN §2.2, §4.8; PR Phase 2]
7. Say why the problem is hard: why naive fixes (more rows, an LLM judge) fail. Without this, reviewers ask why the fix counts as a contribution. [AN §1.4, §4.8; PR Phase 2]
8. Fill these in before drafting:
   - "The main idea of this paper is ___."
   - The ABT sentence.
   - "This is hard because naive approaches fail when ___."
   - "If this is right, ___ should act differently."

   If you cannot fill them in, you are not ready to write. [AN §2.4]
9. Answer the Heilmeier questions in one jargon-free line each: the goal; today's practice and its limits; what is new and why it will work; who cares; the risks; how we will know it worked. [AN §5.8; PR Phase 2]
10. A paper is an argument that changes how readers think, not a record of what we did. Follow the order of the argument, not of the project, and leave out the personal journey. [AN §2.1–2.2]
11. An idea spreads when it is simple enough to repeat in one sentence, answers a problem readers already care about, and has convincing evidence. [AN §2.2]
12. Spend effort where the readers are: the title, abstract, Figure 1 and captions. [AN §1.14, §2.3]
13. Keep a "top 5 reviewer risks" list. For each risk, note how the paper answers it or which experiment would fix it. [PR Phase 2]
14. Use STAR only as a memory aid; write with ABT, CCC and OCAR. STAR has no tension, no "why it is hard" and no limitations step. [AN §4.10, §5.1]
15. Apply context → content → conclusion at every level: paper, section, paragraph. [AN §5.6]

## II-2. Writing order and workflow

1. The writing order for finished research:
   1. Evidence inventory
   2. Core claim and ABT
   3. Contributions (≤ 3)
   4. Figure and table storyboard
   5. Traceability matrix
   6. Method
   7. Results
   8. Discussion and limitations
   9. Introduction
   10. Related work
   11. Conclusion
   12. Abstract
   13. Title
   14. Revision passes

   [AN §7; PR Part B]
2. Storyboard the figures and tables before writing prose. For each float, write the claim it supports, a one-line takeaway caption and where it goes. A claim with no float means evidence is missing; a float with no claim gets cut. Sketch the tables and graphs empty to see which evidence the argument needs. [AN §7, §13.3; PR Phase 2.9]
3. Keep a traceability matrix with the columns Challenge ↔ Component ↔ RQ ↔ Evidence (float + source file) ↔ Contribution ↔ Claim strength. An empty cell means either drop the claim or flag the missing experiment. [AN §19; PR A6.6, Phase 2.8]
4. Get the user's approval of the story (core idea, ABT, contributions, RQs, top risks) before writing any prose. [PR Phase 2 checkpoint]
5. Switch to "distillation mode" well before the deadline. Start by explaining the paper out loud in a few sentences. [AN §7]
6. The paper lives in `amazon/paper/`, with `sections/`, `figures/scripts/`, `tables/`, `scripts/` and `notes/`. The notes are: evidence_inventory, story, results_tables, stats, claim_source_map, glossary, llm_disclosure, self_review, revision_log. A merged section is `\input` inside its host section. [PR Part C] → I-5.1.
7. Generate every table's `.tex` with a script from the result files; never type numbers by hand. Plot scripts only read existing results. [PR Phase 3] → I-22.7.
8. Do not modify, move or delete research files; write only inside the paper directory. Save every read-only analysis script so it can be rerun. Do not rerun training unless the user asks. [PR A4.1–A4.3]
9. Mark gaps with `\todo{MISSING: <metric>, <setting>, <experiment>}` from `todonotes`. In the final build, use `\usepackage[disable]{todonotes}`, and a grep must find no `\todo`. [PR A1.2, Phase 11]
10. Ask the user only what the files and this rulebook do not answer: the author list and order, affiliations, excluded results, the closest competitor, must-cite papers, and how citations can be verified. [PR Phase 0]
11. The evidence inventory covers:
    - the final method, taken from the code, not from stale notes;
    - datasets with sizes, splits and licences;
    - baselines actually run, with their tuning budget;
    - metrics actually computed;
    - every number, with its source and n;
    - available and missing ablations;
    - abandoned approaches (candidates for ablations);
    - an integrity scan;
    - gaps ranked by reviewer risk.

    [PR Phase 1]
12. The final report to the user gives:
    - the core idea and the ABT sentence;
    - the contributions;
    - the PDF path;
    - open issues, ranked: integrity flags first, then missing results, citations to verify and author decisions;
    - the top 3 self-review weaknesses, each with its fix;
    - decisions made without the user;
    - a reminder that the authors must verify everything.

    [PR Part D]

## II-3. Integrity of numbers

1. Every number comes from a file. Record claim → path → row or key in `notes/claim_source_map.md`, and in a LaTeX comment `% src: results/main.csv row=… col=…`. [PR A1.1; AN §16.4]
2. Never make up, estimate, round up or "fill in" a number. [PR A1.2]
3. Recompute every derived number (means, std, deltas, relative gains) with a script saved in `scripts/`. No mental arithmetic. [PR A1.3; AN §16.4]
4. Say whether a reported number is the maximum, the mean or a single run. [AN §11.1] → I-9.3.
5. Run a script that extracts every number from the `.tex` files and matches it to the source map, and list any mismatch. Inconsistent numbers are a desk-reject trigger. [PR Phase 12.2; AN §3.2] → I-3.9.
6. Mark every baseline number copied from another paper and note any difference in setup. [PR A1.6; AN §11.3]
7. Flag single-run results. [PR A1.4] → I-9.3.

## II-4. Integrity of citations

1. Never invent a reference. Cite only works that are in a local `.bib`, PDF or notes file, or that were verified in this session through DOI, arXiv, DBLP, ACL Anthology, Crossref or Semantic Scholar, with title, all authors, year and venue matching. This applies to every candidate in I-16.6. [PR A2.1; AN §16.4]
2. Never generate identifiers (DOIs, arXiv IDs, pages, volumes, venues). Copy BibTeX from the source. [PR A2.2]
3. Cite a work only for what it actually says. Otherwise write `\todo{VERIFY CITATION: …}`. [PR A2.3]
4. If a citation cannot be verified, write `\cite{TODO_<name>}` and list it in the report. Hallucinated references get papers desk-rejected, and they were found in 53 accepted NeurIPS 2025 papers. [PR A2.4; AN §16.2]

## II-5. Honest science and claim calibration

1. The claim-verb ladder:

   | Evidence | Allowed wording |
   |---|---|
   | Formal proof | "proves", "guarantees" |
   | Consistent gains, variance reported, a test or non-overlapping CIs, fair tuned baselines | "outperforms", "significantly improves", "demonstrates" |
   | Gains in some settings, small margins, or no test | "competitive with", "comparable", "improves on A and B" |
   | Correlational or qualitative evidence | "suggests", "indicates", "is consistent with" |
   | Speculation (Discussion only, labelled) | "we hypothesise", "may" |
   | "State of the art" | only after a fair, same-setup comparison with the actual current best |

   [PR A3.5; AN §15] → I-21.9.
2. Hourglass rule: the abstract and intro never claim more than the results establish. Overclaiming is the first quick reason area chairs use to reject. [PR A3.6; AN §1.11, §3.1]
3. Narrower claims need less evidence, so claim exactly what the evidence supports. [AN §3.5]
4. Present the final method as a deliberate design. Never narrate failed attempts in chronological order. [PR A3.1; AN §4.7]
5. Never hide contrary evidence. Report the settings where the method loses (and why), and every benchmark and seed that was run. [PR A3.2; AN §4.7, §12.4] → I-8.13.
6. Alternatives that were tried and rejected become ablations or design-choice comparisons when their results exist. Useful negative lessons go to the appendix. [PR A3.3; AN §4.7]
7. No HARKing, no tuning on the test set (report how many times the test set was evaluated), no seed picking, no p-hacking and no selective reporting of benchmarks. [PR A3.2; AN §12.4]
8. Label speculation as speculation, and keep it out of the Results. [AN §3.2, §8.6]
9. If the results look far better than prior work, explain why the method works; results that look too good raise suspicion. [AN §3.2]

## II-6. Title and abstract (nuances)

1. The title communicates the central contribution. Put searchable keywords before cleverness. Avoid "Towards", "A Novel" and "On the". [AN §5.6; PR Phase 11] → I-1.1, I-1.5.
2. Draft 3–5 titles in different patterns ("Method: what it does", a claim as the title, problem-focused) and choose one. Write the title last. [PR Phase 11; AN §4.9]
3. Write the abstract near the end. [AN §4.9, §8.1]
4. Fit these slots into the IMRaD order of I-3.2: context → the gap, phrased as an error → (why it is hard) → insight and method ("Here we show…" marks the main result) → quantified results → implication → (artifact). [AN §5.9, §8.1; PR Phase 10] → I-3.2.
5. No undefined acronyms, and never "promising results". [AN §8.1; PR Phase 10]
6. 30-second test: within 30 seconds, a reader knows the problem, the insight and the size of the result. [AN §8.1]

## II-7. Introduction (nuances)

1. Reach the problem or the instability within 2 sentences. Banned openings: "In recent years…", "X has attracted increasing attention…", "Deep learning has revolutionized…". [AN §6; PR A7.9] → I-4.3.
2. Use four parts:
   - ¶1: the problem, with a concrete stake.
   - ¶2: the scope (what we cover and what we do not) and the challenges C1…Cn, with why naive approaches fail.
   - ¶3: X, current approaches cited as clusters (AND); Y, their structural limitation, pointing to Figure 1 (BUT); Z, our insight and method (THEREFORE).
   - ¶4: contributions with headline numbers.

   [AN §4.8, §8.2; PR Phase 7] → I-4.2.
3. Use concrete examples, not grand claims: "molehills, not mountains", never "X is very important [1–6]". [AN §4.8]
4. No "The rest of this paper is organized as follows" paragraph. Put forward references inside the contributions instead. [AN §4.8; PR A7.10]
5. Optionally, add one sentence on who should act differently. [AN §8.2; PR Phase 7]
6. The contribution must be clear by the end of page 2. In our layout, the contributions paragraph must land no later than the top of page 2. [PR A6.4; AN §1.3] → I-5.6.
7. Intro anti-patterns: the history of the field; a related-work dump with no argument; contributions written as activities; promises the results do not keep. [AN §8.2]

## II-8. Related work (nuances)

1. Group papers by idea, never one paper per sentence. End each group with "Unlike these…, which assume X, we…". [AN §8.3; PR A6.8] → I-6.3.
2. Be generous and accurate: say what prior work does well and where it stops, and never belittle it. [AN §3.3, §8.3; PR A6.8]
3. Include the closest competitor and recent close work, and say exactly which part of ours is new. [AN §3.3, §8.3; PR Phase 8]
4. Reviewer guidelines only require citing work at least 3 months older than the deadline, but citing more is safer. [AN §3.5, §8.3]
5. An introduction is not a literature review. Use prior work to show where the gap is. [AN §8.3]

## II-9. Method (nuances)

1. Open with one overview paragraph that points to the pipeline figure (Figure 1). [AN §8.4; PR Phase 4]
2. Give the problem formulation first: inputs, outputs, notation, assumptions, all minimal. [AN §8.4; PR Phase 4]
3. Present components in the order data flows through them, each as intuition → formalism → the challenge (C#) it addresses. A component with no challenge is either unnecessary or an unnamed contribution. [AN §8.4; PR A6.6, Phase 4]
4. Give the intuition before every equation, and examples before the general case. [AN §8.4, §14.4; PR A7.5]
5. No decorative maths ("mathiness"). Every equation must clarify something. [AN §3.2, §14.4; PR A7.5]
6. Add a notation table only if there are more than about 10 symbols. In our 4 pages, put it in the appendix. [AN §14.4] → I-7.3.
7. Limits of the method can be noted briefly in the Method. Limits of the interpretation belong in the Discussion. [AN §8.4]
8. Until Figure 1 is drawn, keep a TikZ drawing specification as its placeholder. [PR A8.5, Phase 4] → I-13.1.

## II-10. Experiments as questions

1. Each experiment answers a question a sceptical reviewer would ask about one intro claim: "to learn X, we did Y". Name the question, not the activity. [AN §4.5, §9.1–9.2]
2. Answer first. The first sentence of each results unit gives the answer, then the evidence, then the reason. [AN §4.5, §8.5; PR A6.5] → I-8.6 (see conflict II-21 #6).
3. Use 3 RQs, each mapped to a traceability row. [AN §9.4; PR Phase 2.7]
   - Effectiveness: does the counterfactual reward cut hacking without hurting accuracy?
   - The hard case from the intro: does it catch the hacks that the single-DB reward accepts?
   - Cost and robustness.

   Understanding and failure cases come through the hack examples.
4. The setup says why each baseline was chosen and why each metric matches the claim, and gives the fairness protocol, the seed count and the error-bar type. [AN §8.5; PR Phase 5] → I-8.1.
5. The analysis covers sensitivity, efficiency, qualitative examples and failure cases, in the appendix if space runs out. [AN §8.5; PR Phase 5]
6. Write results as lead → development, with no speculation. [AN §5.3, §8.5]

## II-11. Ablations

1. Give one ablation row per claimed component or design choice; for us, the number of counterfactual DBs K and the perturbation types. The table mirrors the contribution list. [AN §10.2; PR A9.1]
2. Change one thing per row. Keep the backbone, data, schedule, metrics, tuning budget and seeds the same. [AN §10.2; PR A9.1]
3. Report parameters and compute for each row, and add a capacity-matched control where the full model is bigger. Our reward variants share one policy, so the analogue is a compute-matched control: the same steps and rollouts, with the extra executions reported. [AN §10.1–10.2; PR A9.1]
4. A difference that falls inside seed variance is not evidence that a component matters. [AN §10.2]
5. Say whether the ablations are leave-one-out or add-one-in. If components may interact, run a small factorial design. [AN §10.2]
6. Tune on the validation split, and say so if an ablation used test data. [AN §10.2]
7. Keep ablations that show no effect, and interpret every row. Never write "each component contributes" unless every row supports it. [AN §10.2; PR A9.1]
8. A lazy ablation shows these signs: only one of several components ablated, a single seed, the easiest dataset only, no re-tuning, no capacity control, no interpretation, or appendix only. [AN §10.3]

## II-12. Baselines, metrics and statistics (nuances)

1. Tune baselines with the same search method and budget as our method, and report the budget. Hold the backbone, data, preprocessing and compute equal. For us, every reward variant gets the same GRPO budget, data and seeds. [AN §11.3; PR A9.2]
2. Include simple baselines as well as the strongest recent ones. [AN §11.3; PR A9.2]
3. Choose metrics that test the claim directly. Measure hack rate against counterfactual ground truth, not against the proxy itself, and state each metric's direction and how it is computed (averaging, thresholds). Report the metric the field expects (execution accuracy) even if another looks better. [AN §11.4; PR A9.4] → I-7.8, I-8.3.
4. Randomise every source of variance you can (seeds, data order, sampling). Five seeds can mislead. Never report the best seed. [AN §11.1] → I-9.3.
5. Choosing a test:
   - a paired t-test only if normality holds (check with Shapiro–Wilk);
   - otherwise a paired bootstrap, a permutation test or Wilcoxon signed-rank;
   - bootstrap or permutation for F1-like metrics;
   - correct for multiple comparisons.

   [AN §11.2; PR A9.3] → I-9.6.
6. With few runs, compute stratified-bootstrap CIs, IQM or probability of improvement with `rliable`, by script from the raw per-seed results. [AN §11.2; PR A9.3] → I-9.4.
7. If normality is not verified, prefer a 2-sigma error bar over claiming a 96% CI (NeurIPS checklist guidance). [AN §11.2] → I-9.2.
8. Without a test or non-overlapping CIs, write "comparable" or "within noise". [AN §11.2; PR A3.7] → I-9.6.

## II-13. Leakage, contamination, reproducibility

1. Check for leakage: no clean train/test separation, transforms fitted on all the data, duplicates across splits, temporal leakage, features that proxy the label, and a test set from the wrong distribution. Split first, fit on training data only, and remove duplicates. If you suspect leakage, stop and tell the user before writing results. [AN §12.2; PR A3.8]
2. Report the contamination risk of LLM benchmarks. Spider and BIRD questions may be in the base model's pretraining data. Give n-gram-overlap or release-date-vs-training-cutoff evidence, or state the risk in the Limitations paragraph. [AN §12.3; PR A3.8]
3. Put the reproducibility details in the appendix: parameter count, GPU hours, the hyperparameter search and the chosen values, package versions. [AN §8.9, §12.1] → I-18.3.

## II-14. Figures and tables (nuances)

1. No figure without a claim. Merge figures that share a takeaway. [AN §13.2; PR A8.4]
2. Use tables for exact comparisons and plots for trends. [AN §13.2]
3. Place each float near where it is discussed: `[t]` on that page or the next. [AN §13.2] → I-10.11.
4. Sketch each key figure 5–10 times before settling on one. [AN §13.2]
5. Plan the figures as WHAT, WHY and HOW: a teaser, where prior work fails, and a method overview. For us, Figure 1 merges HOW and WHY (the pipeline plus a hacked-query inset), and Table 1 and the optional Figure 2 give the WHAT. [AN §13.1; PR A8.5] → I-10.3 (see II-21 #5).
6. Put an ↑/↓ arrow on every metric column, not only on some. [AN §11.4, §13.2; PR A8.2] → I-14.7.

## II-15. Discussion, limitations, conclusion (nuances)

1. The Discussion explains the mechanism (why the counterfactual reward works) and what the results mean beyond the benchmark. It runs: summarise → synthesise → how it fixes the problem. [AN §5.3, §8.6; PR Phase 6]
2. Limitations are specific: assumptions that may fail, settings not tested, compute cost, failure modes, data coverage, licensing and bias, and societal risks. [AN §8.7; PR A3.4, Phase 6] → I-17.1.
3. Honest limitations raise trust, and reviewers are told not to penalise them. [AN §3.5, §8.7]
4. The conclusion is a higher-level synthesis. Restate the core claim in light of the evidence, give the broader implication, and name 1–2 specific future directions that follow from the limitations. It is not a copy of the abstract, and it has no new results and no bare list of future work. [AN §4.9, §8.8; PR A6.7, Phase 9] → I-5.7.

## II-16. Sentence and paragraph craft

1. Follow Gopen & Swan, as defaults rather than rigid rules:
   - Put the subject close to its verb.
   - Put new, emphasised information at the end of the sentence (the stress position).
   - Put old, linking information and the actor whose story it is at the start (the topic position).
   - Put the action in the verb.
   - Give context before new material.
   - Make the emphasis carried by the structure match the emphasis in the content.

   [AN §14.1; PR A7.3]
2. A sentence is too long when it has more candidates for stress than it has stress positions. [AN §14.1]
3. Every paragraph's first sentence states its point. Reading only the first sentences should give the whole argument. [AN §14.2; PR A7.2]
4. One topic per paragraph, covered in one place (no zig-zagging). Write parallel ideas in parallel form. [AN §5.6, §14.2]
5. About 75% of paragraphs are a topic sentence plus development. About 25% use LDR or OCAR at story transitions. [AN §5.3, §14.2]
6. Use relay linkage: the end of one sentence (new information) becomes the start of the next (old information). [AN §14.2]
7. Outline with one informal sentence per planned paragraph. When a paragraph fails, rewrite it whole rather than patching it. [AN §5.6, §17.1]
8. Brevity comes from choosing what to include, not from compressing. [AN §5.3, §14.3] → I-20.1.
9. Rewriting for the reader often exposes gaps in the science itself. Treat a structural problem as a thinking problem. [AN §14.1]

## II-17. Words, tense, voice

1. Use the active voice by default. Use the passive only when the object is the topic. [AN §6, §14.3; PR A7.4]
2. Use the past tense for what we did and found, and the present tense for established facts and for what the paper shows. [AN §14.3; PR A7.7]
3. "This" is always followed by a noun. Complete every comparison ("faster than X"). [AN §14.3; PR A7.6]
4. Use action verbs, not nominalisations or vague verbs (occur, facilitate, perform). Use plain words: "find out", not "endeavour to ascertain". [AN §14.3; PR A7.3]
5. Define words with an everyday meaning ("reasoning", "understanding", "verification") before using them, or avoid them. [AN §14.3] → I-7.13.
6. Hedge only where the evidence is limited. Cut empty hedges ("it is worth noting that") and empty intensifiers. [AN §14.3]
7. Keep `notes/glossary.md` to enforce one term per concept. [PR A7.1] → I-21.6.
8. Banned words and phrases. Replace each with a concrete verb or a number, and grep for them during revision. [PR A7.8; AN §16.3] → I-21.9.
   - Single words: delve(s), underscore(s), showcase/showcasing, pivotal, realm, intricate, meticulous(ly), commendable, notably, crucial, versatile, noteworthy, groundbreaking, cutting-edge, game-changer, seamless(ly), harness, utilize, facilitate, paramount, multifaceted, tapestry, landscape, remarkable, potential, findings, enhancing, exhibited, insights, particularly, innovative.
   - Phrases: "sheds light on", "paves the way", "a testament to", "plays a crucial/pivotal role", "in the realm of", "it is worth noting that", "in order to", "extensive experiments", "harness the power of".
   - Conditional: "comprehensive" (unless exhaustive), "robust" (unless measured), "leverage" (when "use" works), "significantly" (unless statistical), "novel" (at most once, for the core idea only).

## II-18. LLM use and ethics

1. Never insert hidden text, white text or prompt injections aimed at reviewers or AI reviewers. [PR A5.1; AN §3.4]
2. Never list an AI as an author. The human authors are responsible for every word, number and citation, and they must verify them all. [PR Role, A5.3; AN §16.1]
3. Draft the LLM-use disclosure in `notes/llm_disclosure.md`. Amazon's policy is unknown, so we disclose, following PR's default for an unknown venue. The authors review and approve the wording. [PR A5.2] → I-17.6.
4. Never put credentials, hostnames, usernames or private paths in the paper. Repository links go in only if the repository is public. [PR A4.4] → I-2.7.

## II-19. Revision and self-review

1. Run separate passes and log each in `notes/revision_log.md`:
   1. Structure: ABT, traceability matrix, hourglass.
   2. Evidence: source map, number-check script.
   3. Skim test.
   4. Clarity: glossary, Gopen & Swan, banned-word grep, notation.
   5. Adversarial review.
   6. Claim calibration.
   7. Citations.
   8. Compliance.
   9. Polish.

   [PR Phase 12; AN §17.1]
2. Skim test: read only the title, abstract, figures, captions, headings and first sentences, and rewrite until the story comes through. [AN §17.1; PR Phase 12.3]
3. Write a harsh Reviewer 2 review and an area-chair meta-review in `notes/self_review.md`. Score novelty, soundness, significance, clarity and reproducibility, then ask:
   - What exactly is new compared with the closest work?
   - Why wouldn't a simple baseline work?
   - Are the baselines tuned equally?
   - Is the gain larger than the noise?
   - Which component causes the gain?
   - Does the method solve the challenge stated in the intro?
   - Does the paper promise more than it delivers?
   - Is there leakage?
   - Can this be reproduced?
   - Are key references missing?

   Fix or pre-empt each point. [PR Phase 12.5; AN §17.2]
4. Find and remove the one obvious fatal flaw ("puppy with 6 toes"). Assume you have made a mistake and look for it. [AN §3.4, §17.1]
5. Outside readers:
   - Use each fresh reader only once, and ask where they got lost.
   - Test the idea on someone outside the subfield: they read it, then explain it back.
   - Optionally, send the related-work framing to the authors you compare against.

   [AN §17.3]
6. Review is noisy: in the NeurIPS 2021 consistency experiment, two committees disagreed on 23% of papers. Remove every easy reason to reject, and write for the person who makes the decision. [AN §3.6]
7. Fill the page limit. A short paper looks rushed. [AN §13.2] → I-5.4.

## II-20. Framing from reviewer guidance

1. Reviewers are told that a lack of SOTA results is not grounds for rejection; that evaluating existing methods for new insight is valuable; that simpler solutions are preferable; and that negative or niche results are not grounds on their own. So frame the audit as an insight, not a leaderboard gain. [AN §3.5] → I-23.1.
2. Originality can come from creative combinations of existing ideas, removed assumptions or a new framing of a task. Say exactly which part is new. [AN §3.3, §3.5]
3. State significance explicitly: one implication sentence each in the abstract, intro and conclusion. [AN §3.1]

## II-21. Conflicts

Amazon and template constraints win. Otherwise the reason is given.

| # | Guide rule | Conflicts with | Decision |
|---|---|---|---|
| 1 | PR Phase 0 defaults: two-column, 8 pages, anonymous, NeurIPS checklist | Amazon §0 | **Amazon wins.** One-column NeurIPS template, 4 pages, named authors, no checklist. |
| 2 | Anonymisation checks (PR A4.4, Phase 12.8; AN §3.4) | Amazon requires author names | **Amazon wins.** Keep only "no credentials or private paths" (II-18.4). |
| 3 | Fill in the venue checklist with section pointers (AN §8.10; PR Phase 11) | §0: drop the checklist | **Drop it.** Use it only as a self-review (I-17.8). |
| 4 | 2–3 contribution bullets (AN §8.2; PR A6.2, Phase 7) | I-4.6: inline (i)–(iii) | **Part I.** Inline saves 4–6 lines. The content rules II-1.2–1.3 still apply. |
| 5 | Figure 1 as a teaser on page 1, plus separate WHAT, WHY and HOW figures (AN §13.1; PR A8.5) | I-10.2 and I-5.8: no page-1 figure, at most 3 floats | **Part I.** Figure 1 at the top of page 2 merges HOW and WHY; Table 1 (and the optional Figure 2) is WHAT. |
| 6 | Results subsection titles as questions (AN §4.5, §9; PR A6.5) | I-8.5: claim run-ins | **Part I.** The run-in header states the answer. The question stays implicit, or one opening sentence lists the RQs. Reason: 4 pages leave no room for one subsection per RQ, and claim headers pass the skim test (WS 6, 8; E3). |
| 7 | Related work as a full section after the intro (AN §6; PR Phase 8) | I-6.1: one merged paragraph | **Part I.** The guides themselves defer to venue convention, and the 4-page convention is to merge (WS 4/8). |
| 8 | Bold the best and underline the second best (AN §13.2; PR A8.2) | I-14.8: no underline | **Part I.** Table 1 has few rows, so an underline adds noise. Underline only if Table 1 grows to 5 or more compared rows. |
| 9 | Figure fonts no smaller than the caption font, i.e. 10 pt (PR A8.3) | I-10.6, I-12.4: 7 pt floor, 8 pt plot labels | **Compromise.** TikZ text at 9 pt (`\footnotesize`), plot labels at 8 pt, 7 pt floor. Reason: 10 pt ticks do not fit in half-width plots, and E3 sets the bar at ≥ 80% of the caption size. |
| 10 | Number only the equations you refer to (AN §14.4) | I-7.1: number every display equation | **Part I, plus one rule:** reference every numbered equation in the text, or turn it into inline maths. |
| 11 | Abstract of 150–250 words in 5–7 sentences (AN §5.9; PR Phase 10); 4 sentences (Beck, Peyton Jones; AN §2.3, §5.9) | I-3.3: 150–180 words, 6–8 sentences | **Part I.** It fits Amazon's IMRaD requirement and the numbers inside the guides' word range. |
| 12 | Intro of about 1–1.5 pages (AN §8.2) | I-5.7: about 450 words (~0.8 page) | **Part I.** The 4-page budget. |
| 13 | Limitations as a section of its own (AN §8.7; PR A3.4) | I-17.1: run-in paragraph | **Part I.** A run-in titled "Limitations." inside Section 5, under the specificity rules of II-15.2. ARR's desk-reject rule does not bind this venue. |
| 14 | An ablation summary in the main paper, not only in the appendix (AN §10.2.10) | I-5.9, I-18.3: extra ablations go to the appendix | **Merge.** A one-sentence ablation summary, or at most 2 ablation rows in Table 1, in the main body; the full ablation table in the appendix. |
| 15 | 3–5 RQs (AN §9.4; PR Phase 2.7) | The 4-page budget (I-5.7) | **3 RQs** (II-10.3). |
| 16 | A notation table if there are more than 10 symbols (AN §14.4) | The 4-page budget | **In the appendix only** (II-9.6). |

## II-22. Could not place (not applicable to this venue)

- **Rebuttal structure and content** (AN §17.4). The symposium has no rebuttal phase: we submit by email and receive a notification.
- **Venue-specific LLM policies** for ICLR, ICML, ACL, Elsevier and Nature/IEEE/ACM (AN §16.1; PR A5.2). Only the "unknown venue → disclose" default is used (II-18.3).
- **The ARR desk-reject list and ACL Responsible NLP checklist items** (AN §3.4, §12.1). They belong to another venue; their useful parts are folded into II-13.3.
- **REFORMS and the ML Reproducibility Checklist** (AN §12.1). The file names them but gives no concrete rule beyond II-13.
- **The neuroscience-style ablation caveat** (AN §10.3). Not relevant to reward variants.
- **The capacity-matched control** (AN §10.1). Only adapted, as a compute-matched control (II-11.3), because every variant shares one policy.
- **The "missing citations count only if 3+ months old" rebuttal argument** (AN §3.5). Used only as the citation-scope nuance in II-8.4.
- **The sources list** (AN §20). Reference material, not rules.

## II-23. Additional pre-submission checks

These add to I-26.

- [ ] The number-extraction script finds that every number in the `.tex` files matches the source map (II-3.5).
- [ ] Every citation is verified; there are no `TODO_` citations and no invented identifiers (II-4).
- [ ] No `\todo` remains, and todonotes is disabled (II-2.9).
- [ ] The banned-word grep is clean (II-17.8).
- [ ] Every claim verb matches the ladder, and the hourglass holds (II-5.1–5.2).
- [ ] The skim test passes, and the self-review is written and addressed (II-19.2–19.3).
- [ ] A contamination and leakage statement is present (II-13).
- [ ] The authors have approved the LLM disclosure (II-18.3).
