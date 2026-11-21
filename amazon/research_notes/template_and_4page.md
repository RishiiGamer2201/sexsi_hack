# NeurIPS template rules + 4-page paper anatomy (for the Amazon Trusted AI Symposium 2027 paper)

Compiled 2026-11-21. Sources: `amazon/paper/Styles (1)/Styles/neurips_2025.{sty,tex,pdf}` (read in full; the official PDF is the
compiled .tex: 12 pages, US Letter, pdfTeX 1.40.25, no Type 3 fonts), test builds in `research_notes/template_test/`, and
14 workshop papers rendered and read from `research_notes/pdfs/workshop_4page/` (37 PDFs downloaded in total).

Amazon's own rules, which override the template where they differ: official NeurIPS LaTeX template, PDF, **≤4 pages of content**,
with references and appendices on extra pages; the abstract covers introduction, methods, results and conclusions; author
names, affiliations and emails are included; non-archival; double submission OK.

---

## PART A: the official template (neurips_2025.sty / .tex)

### A1. Package options and what each one prints

| Option | Anonymous? | Line numbers? | Ack section shown? | Page-1 footer (verified by compiling) |
|---|---|---|---|---|
| *(none)* = default = main-track submission | yes ("Anonymous Author(s) / Affiliation / Address / email") | yes (`lineno`) | hidden | `Submitted to 39th Conference on Neural Information Processing Systems (NeurIPS 2025). Do not distribute.` |
| `preprint` | **no** | **no** | shown | **`Preprint.`** (the .sty prints only this; the .tex text claims "Preprint. Work in progress.", but that does not match the code) |
| `final` (alone) | no | no | shown | **compile ERROR**: `Undefined control sequence \@trackname`. `final` must be paired with a track option |
| `main,final` | no | no | shown | `39th Conference on Neural Information Processing Systems (NeurIPS 2025).` |
| `position,final` | no | no | shown | `… (NeurIPS 2025) Position Paper Track.` |
| `dandb` / `creativeai` (no final) | no (they set anonymous false) | yes | hidden | "Submitted to … Do not distribute." |
| `dandb,final` / `creativeai,final` | no | no | shown | `… Track on Datasets and Benchmarks.` / `… Creative AI Track.` |
| `sglblindworkshop,final` + `\workshoptitle{X}` | no | no | shown | `39th Conference on Neural Information Processing Systems (NeurIPS 2025) Workshop: X.` |
| `sglblindworkshop` (no final) | no | yes | hidden | "Submitted to … Do not distribute." |
| `dblblindworkshop` (no final) | yes | yes | hidden | "Submitted to … Do not distribute." |
| `nonatbib` | (orthogonal) | | | Does not load natbib. Use it only if natbib clashes with another package |

The template's guidance (neurips_2025.tex, "Preprint option"): `preprint` produces "a nonanonymized version … [that] may be
distributed as you see fit, as long as you do not say which conference it was submitted to. Please **do not** use the
`final` option, which should **only** be used for papers accepted to NeurIPS."

**Recommendation for Amazon: `\usepackage[preprint]{neurips_2025}`.** It is the only option that is non-anonymous (author
names, affiliations and emails print), has no line numbers, shows the `ack` environment, and does not falsely claim NeurIPS
in the footer. Every `final` and track variant prints "39th Conference on Neural Information Processing Systems (NeurIPS 2025)…",
which would misrepresent the venue. Optional and judgment-dependent: replace the word "Preprint." with the venue name by
adding `\makeatletter\renewcommand{\@noticestring}{Amazon Trusted AI Symposium 2027.}\makeatother` after loading the
package. This changes only footer text, not layout, but strictly it is a style tweak. Ask the organizers, or keep "Preprint."
if in doubt.

Template header lines to keep (from neurips_2025.tex): `[utf8]{inputenc}`, `[T1]{fontenc}`, `hyperref`, `url`, `booktabs`,
`amsfonts`, `nicefrac`, `microtype`, `xcolor`. The template does **not** load `graphicx`, so add `\usepackage{graphicx}`.
natbib options go *before* the package: `\PassOptionsToPackage{numbers,compress}{natbib}`.

### A2. Page geometry (set by the .sty `\newgeometry`. Do not change.)
- US **Letter** (612×792 pt). A4 is explicitly not allowed ("Please prepare submission files with paper size 'US Letter'").
- Text block **5.5 in wide (33 pc) × 9 in tall (54 pc)**; top margin 1 in; left margin 1.5 in (centered); headheight 12pt,
  headsep 25pt, footskip 30pt.
- Page 1 gets `\enlargethispage{2\baselineskip}` (two extra lines) and has no page number (`\thispagestyle{empty}`). Other
  pages are numbered ("pages should be numbered").
- `\flushbottom`, `\sloppy`, `\widowpenalty=\clubpenalty=10000` (no widows or orphans, so expect some stretched pages).
- Loading the `fullpage` package triggers a warning, and its formatting is overridden.

### A3. Fonts and sizes
- Times (`ptm`) for roman, Helvetica (`phv`) for sans-serif. Typewriter text stays CM (`cmtt`; with T1 this becomes `ectt`).
- `\normalsize` 10/11 pt; `\small` 9/10; `\footnotesize` 9/10 (the same as small); `\scriptsize` 7/8; `\tiny` 6/7;
  `\large` 12/14; `\Large` 14/16; `\LARGE` 17/20 (title); `\huge` 20/23; `\Huge` 25/28.
- The **title** is 17 pt bold, centered between a 4 pt rule (top) and a 1 pt rule (bottom), with initial caps.
- **Abstract**: "Abstract" is centered, bold, 12 pt; the body is 10/11 inside a `quote` (indented ½ in on both sides) and
  **"must be limited to one paragraph."**
- Paragraphs: **no indent**, separated by 5.5 pt (half a line).
- Only Type 1 or embedded TrueType fonts are allowed; papers with Type 3 fonts will be asked to fix them. Check with `pdffonts`.

### A4. Headings
- All headings are lower case except the first word and proper nouns, flush left, bold.
- `\section`: 12 pt bold. `\subsection` and `\subsubsection`: 10 pt bold. `\paragraph`: bold run-in heading followed by 1 em.
  (The .sty also shrinks heading spacing: section −2.0ex before / 1.5ex after; subsection −1.8ex / 0.8ex.)

### A5. Figures, tables, captions
- Figures: "neat, clean, and legible"; **caption after the figure**, numbered consecutively, lower case except the first
  word; one line space before the caption and after the figure. Color is allowed, but the paper should stay legible in B/W.
  Size figures as a fraction of the line width (`\includegraphics[width=0.8\linewidth]{…}`). Never place them by hand
  with `\special`.
- Tables: centered; **caption/title before the table** (the .sty swaps the caption skips for `table`); lower case; numbered.
  **"Publication-quality tables do not contain vertical rules."** The `booktabs` package is strongly recommended
  (`\toprule`, `\midrule`, `\cmidrule`, `\bottomrule`).
- Float parameters: topfraction .85, bottomfraction .4, textfraction .1, floatpagefraction .7; abovecaptionskip 7 pt.

### A6. Citations and references
- natbib loads by default. Author-year **or** numeric citations are both fine "as long as you maintain internal consistency".
  Any reference style is acceptable if it is consistent. Use `\citet{}` for in-text citations ("Hasselmo et al. (1995)
  investigated…").
- References go under an unnumbered first-level heading (`\section*{References}`, or what bibtex produces), after the
  acknowledgments. You may reduce them to `\small` (9 pt), the only allowed font-size reduction. References do not count
  toward the page limit.
- Footnotes: use sparingly, numbered, placed after punctuation, with a 12 pc (2 in) rule. The author `\thanks` footnote is
  for webpage or alternative address, **not funding**.

### A7. Anonymity (NeurIPS rule; not wanted here)
In submission mode, the default and `dblblindworkshop` options print "Anonymous Author(s)" and ask you to cite your own work in
the third person ("Jones et al. [4]", not "our previous work"). Amazon requires names, so use `preprint` (A1). Self-citing in
the third person is still good style.

### A8. Acknowledgments
Use `\begin{ack}…\end{ack}`, which gives the unnumbered heading "Acknowledgments and Disclosure of Funding". It is placed
before the references and must declare funding and competing interests. It is auto-hidden in anonymous mode and shown with
`preprint`. The NeurIPS rules list only "references, checklist, and optional technical appendices" as not counting toward the
page limit. Acknowledgments are not on that list, so to be safe, assume they count toward the 4 pages and keep them to 1–2 lines.

### A9. The NeurIPS Paper Checklist
The template says: "Do not remove the checklist: **The papers not including the checklist will be desk rejected.**" It has
16 questions (claims, limitations, theory, reproducibility, open access, experimental details, statistical significance,
compute, code of ethics, broader impacts, safeguards, licenses, new assets, crowdsourcing, IRB, LLM usage), answered with
`\answerYes/No/NA{}` plus a justification, and it comes after the references and appendix. This is a **NeurIPS-conference**
requirement. Amazon's rules do not ask for it, so **drop it** (a non-NeurIPS venue cannot desk-reject on NeurIPS policy).
Its questions are still a good self-review list. In particular, make sure the 4 pages cover limitations, error bars or
seeds, and compute (briefly, with details in the appendix).

### A10. What is forbidden or discouraged
- "Do not change any aspects of the formatting parameters in the style files": no changes to text width or height, margins
  or font sizes (except `\small` references). "Tweaking the style files may be grounds for rejection." Do not use `fullpage`
  or `geometry` overrides.
- No Type 3 or bitmap fonts (for example, `\bbold`, or xfig patterned shapes); use `amsfonts`/`amssymb` for `\mathbb`.
  Generate the PDF directly with pdflatex.
- No `$$…$$` display math (it breaks line numbering); use `\[…\]` or `equation`/`align`.
- No vertical rules in tables. Do not hand-position figures with `\special`.
- `\vspace`: the template does **not** mention it explicitly. However, negative `\vspace` around section headings and
  captions, or `\renewcommand{\baselinestretch}`, changes "formatting parameters" in spirit, and reviewers notice it.
  Rule for us: no `\vspace` hacks and no `\small` body text. Make space by cutting words, by putting figure and table
  content side by side, or by moving material to the appendix.
- Hyphenation hints (`\-`) are allowed and recommended to fix overfull lines.

### A11. Toolchain check (WSL Ubuntu, TeX Live 2025, compiled in `research_notes/template_test/`)
- `pdflatex`/`latexmk` **work**, but the installed TeX Live is minimal (`texlive-base`, `-latex-base`,
  `-latex-recommended`, `-fonts-recommended`). **The template does not compile out of the box**:
  `! LaTeX Error: File 'environ.sty' not found` (`environ` needs `trimspaces`). The template's `\usepackage{nicefrac}`
  (from the `units` package) is also missing.
- **Type 3 font problem**: every build embeds a bitmap Type 3 font (`ectt1000`) for `\texttt` because **`cm-super` is not
  installed**. That violates the "no Type 3 fonts" rule. The official neurips_2025.pdf has 0 Type 3 fonts.
- **Fix (needs sudo, so the user must run it): `sudo apt install texlive-latex-extra cm-super`.** Afterwards, check that
  `pdffonts paper.pdf | grep "Type 3"` prints nothing.
- For the test only, I wrote two tiny self-made shims (`template_test/shims/environ.sty`, `nicefrac.sty`; they are **not** for
  the real paper). With them, every variant compiles to 12–13 Letter pages, and the footers in A1 are from those builds
  (`v_*.pdf`). Running TeX on CTAN-downloaded package sources was blocked by the session's permission policy, so I did not
  install real packages.

---

## PART B: how 4-page papers spend their space

**How I found them.** OpenReview now serves a bot challenge (HTTP 403 "ChallengeRequiredError") on its API and PDFs, so I did
not scrape it. I used the arXiv API instead, searching the comment field for NeurIPS workshop acceptances ("4 pages", SoLaR,
Safe GenAI, MATH-AI, ATTRIB, reward hacking, text-to-SQL, verifiable rewards). I downloaded 37 PDFs and measured each one
automatically (pdftotext: page where "References" starts, word counts, figure/table captions, headings). I kept the papers
whose **main body ends at exactly 4 pages or less** in the NeurIPS style, rendered pages 1–4 at 60 dpi, and looked at every
page. Many arXiv versions of "workshop papers" turned out to be extended versions of 5–12 pages (for example SoLaR 2023/24
papers: 2310.17769, 2311.00488, 2411.07122, 2411.05775 are 5–6 pages; 2412.16325 SafeGenAI is 10), so they were excluded.

### B1. Core set: 8 NeurIPS-workshop papers with exactly 4 content pages (NeurIPS style)

Word counts are approximate (from pdftotext). "Body" = abstract through conclusion, excluding references.

**1. Towards Optimizing SQL Generation via LLM Routing** (arXiv 2411.04319). Table Representation Learning @ NeurIPS 2024. 7 pp total. *Topic: text-to-SQL, BIRD.*
- 4 authors, all at one affiliation, on a single line. Abstract 111 words. Body ~2,400 words.
- Sections: Intro 400 | Preliminaries 470 (2.1 problem formulation, **2.2 related work as a ~120-word subsection**, 2.3 metrics) | Methods 420 (two router variants, 1 subsection each) | Experiments 910 (datasets, models, results) | Conclusion **60**.
- Floats: Fig 1 = a small full-width pipeline diagram at the **top of p2** (~25% of the page); Table 1 (booktabs, `\small`) at the top of p4 carries all the results. 1 fig + 1 table.
- No page-1 teaser. Implementation details (cost, router training) appear as bold `\paragraph` run-ins. Per-model details are in Appendices A and B.

**2. Evaluating the role of 'Constitutions' for learning from AI feedback** (2411.10168). Language Gamification @ NeurIPS 2024. 11 pp.
- 3 authors side by side. Abstract 133 words, ending with a code link. Body ~2,150 words.
- Intro 480 (**related work merged into the intro**) | Methods 320 (2.1–2.4) | Results 400 | Discussion 320 (limitations inside).
- Floats: Fig 1 = method diagram at the top of p2 (~45% of the page, with a long self-contained caption); Table 1 = text table of evaluation dimensions (p3); Fig 2 = 3×2 heatmap grid (top of p4). 2 figs + 1 table, about 1.2 pages of floats.
- Prompts, constitutions and vignettes are in Appendices A–D.

**3. Agentic Property-Based Testing: Finding Bugs Across the Python Ecosystem** (2510.09907). Deep Learning for Code @ NeurIPS 2025. 21 pp.
- 4 authors. **Abstract 232 words** (long, structured problem → method → numbers → release). Body ~2,400 words.
- Intro 440 | Agent 880 (numbered 6-step list for the agent loop, "Key design choices" paragraph) | Experiment ~300 (bulleted package-sampling list) | Results 360 (run-in "Summary statistics" and "Manual review" with **95% CIs inline**, compact bug list) | Discussion and Conclusion 450 (run-ins: Limitations / **Comparison to Related Work** / Conclusion).
- **0 figures, 0 tables.** Lists and run-in paragraphs carry the structure. The full prompt and all bug reports are in the 17-page appendix.

**4. Curiosity-driven RL for symbolic equation solving** (2510.17022). MATH-AI @ NeurIPS 2025. 8 pp. Single author.
- Abstract **63 words**. Body ~2,400 words.
- Intro 200 | Related Work ~230 (2 italic run-in paragraphs) | Problem Formulation ~900 (MDP definition: states/actions/reward with **6 numbered equations**, **wrapfigure** of expression trees) | Results ~700 | Discussion 285 (**wrapped colored "Box 1: Open challenges"**).
- Floats: Fig 1 (wrapfig, p2), Table 1 = full-width tiny-font table of success rates ± s.e. (top of p3), Fig 2 = 2×2 learning curves (top half of p4). 2 figs + 1 table + 1 box.

**5. Reinforcement Learning for Long-Horizon Multi-Turn Search Agents** (2510.24126). Multi-Turn Interactions in LLMs @ NeurIPS 2025. 8 pp. *Topic: RL-trained agent with GRPO and a reward design.*
- 2 authors. Abstract 88 words. Body ~2,000 words.
- Intro ~180 (**2-item contributions bullet list**) | Related Work ~150 (own section, 2 paragraphs) | Methods ~750 (3.1–3.6; tools as bullets; **reward schedule as a 4-item bullet list of reward bands**) | Results ~500 (4.1–4.3) | Discussion **68**.
- Floats: Table 1 (small, centered, half width; model vs accuracy vs turns; the best row in bold) at the top of p3; **Figs 1+2 side by side** (two half-width minipage plots) at the top of p4. 2 figs + 1 table.
- The system prompt and metric definitions are in Appendices A.1–A.2.

**6. You Need Reasoning to Learn Reasoning: Limitations of Label-Free RL in Weak Base Models** (2511.04902). MATH-AI @ NeurIPS 2025. 9 pp. *Topic: RLVR / label-free RL failure modes (closest in genre to ours).*
- 4 authors. **Abstract 202 words.** Body ~2,450 words. The densest layout in the set.
- Intro 600 (ends in a **boxed "Overview of takeaways" with 5 bold-keyword bullets**, related work woven in) | Analysis (2.1 preliminaries, 2.2–2.4 findings, each subsection title stating the finding) 740 | Method 660 (2 equations) | Results **~100** | Conclusion 90.
- Floats: 4 figures, all as **wrapfigures** at ~40% width (bar chart, histogram, two line plots), plus Table 1 wrapped on the right of p4 (`\scriptsize`, 4 model groups × 5 benchmarks, the best in bold). 4 figs + 1 table.
- The results text is tiny because the table carries the results. Extra experiments and implementation details are in the appendix.

**7. Reproducible Evaluation as the Substrate for Safe Prompt Compression in Production Agents** (2610.31972). Agents in the Wild @ NeurIPS 2026. 8 pp. *Topic: correctness-gated optimization that explicitly guards against reward hacking.*
- 3 authors (2 + 1 rows). Abstract 124 words. Body ~2,400 words.
- Intro 740 (**related work is a full paragraph on p2 inside the intro**; contributions as inline "(1)…(2)…(3)") | Methodology 950 (2.1–2.4, set notation, one **cases equation for the gated fitness**) | Results ~350 (Dataset / Compression run run-ins) | Conclusion 150.
- Floats: **only 1 small table** (top of p4: family, tokens, compression, Δ with 95% bootstrap CI). 0 figures. Text-heavy.

**8. ToolRosetta: Surface-Form Invariance of Tool-Call Guards** (2610.24055). Agents in the Wild @ NeurIPS 2026. 9 pp. *Topic: safety guards that judge surface form rather than substance (a close conceptual cousin of reward hacking).*
- 2 authors. **Abstract 247 words.** Body ~2,650 words.
- Intro 455 (related work merged; contributions as inline (i)–(iv)) | Method 930 (unit, conditions as bullets, guards and prompts, estimands) | Results 860 (**every subsection title is a claim**: "3.1 Frontier guards are stable; four of five specialized guards are not", with bold run-in claims and bracketed 95% CIs) | Discussion 150 (run-ins: "What the result is not." / "Limitations.").
- Floats: Table 1 = full-width, very small font, 11 guards × 10 columns (top of p3, ~40% of the page; at 60 dpi it is barely legible, which is a cautionary example) + Fig 1 = grouped bar chart (full width, short). 1 fig + 1 table.

### B2. 4-page short papers from other venues that use the NeurIPS style

**9. A Validated LBM Dataset and Pipeline for Surrogate Modeling of Turbulent 3D Channel Flows** (2606.16765). **EurIPS 2025** SysDiff workshop (the footer is customised to "1st Workshop on … @ EurIPS 2025", using the NeurIPS style). 10 pp.
- Abstract 138 words. Intro 390 | Pipeline 190 | Dataset and validation 840 | Baseline results 320 | Planned comparison ~200 | **Limitations 60 (own section)** | Conclusion 150.
- Floats: Fig 1 = box-and-arrow pipeline at the top of p2 (~20% of the page); Table 1 (booktabs, p3); Table 2 (booktabs, p4). 1 fig + 2 tables. Validation plots are in the appendix.

**10. Towards Multimodal Representation Learning in Paediatric Kidney Disease** (2511.13637). EurIPS 2025 MMRL4H (built with `sglblindworkshop,final`). 5 pp total.
- 3 authors. Abstract 118 words. Body ~1,600 words, the lightest text in the set because it has 3 figures with (a)/(b) subfigures.
- Intro 270 | Methodology ~550 (2.1–2.4) | Results ~300 (3.1–3.3, one figure per subsection) | Discussion 300 | **Ack + funding on p4** (counted inside the 4 pages).

**11. AgentiQL: An Agent-Inspired Multi-Expert Framework for Text-to-SQL Generation** (2510.10661). Accepted at the NeurIPS 2025 Efficient Reasoning workshop; the arXiv copy is built with **`[preprint]`** (footer "Preprint."). The body runs 4.26 pp. *Topic: text-to-SQL agent (Spider).*
- 3 authors. Abstract 153 words. Intro 280 (contributions inline (i)–(iii)) | Related Works 130 (3 bold-led categories) | Method 890 (3.1–3.4, notation-heavy prose) | Experimental results 540 | Conclusion 350 (with limitations).
- **0 floats in the body**: all 4 tables and 4 figures are in the appendix and only referenced. This works for arXiv, but the main pages are hard to read without them, so it is not a model for a poster paper.

### B3. Contrast and negative examples (not counted in the core set)
- **Plentiful Jailbreaks with String Compositions** (2411.01084), **SoLaR @ NeurIPS 2024**: 5 content pages (refs on p6), single
  author. Intro with 1.1 problem setting and **1.2 related work as a subsection**, a small 20-cell table on p2, and one tall
  figure of 5 stacked bar charts filling p4. The SoLaR papers I could find on arXiv were all 5+ pages, so SoLaR does not serve
  as a 4-page model.
- **When to Remember, When to Abstain** (2610.07100), NeurIPS 2026 Social Agent workshop: 4 pages but built in the **Meta
  corporate template**, not the NeurIPS style. This is what Amazon's "official NeurIPS template" rule forbids.

---

## Synthesis

### S1. Counts over the 8 core NeurIPS-workshop 4-pagers

| Metric | Values (papers 1–8) | Median / summary |
|---|---|---|
| Abstract words | 111, 133, 232, 63, 88, 202, 124, 247 | **median ≈ 130**, range 63–247; all single paragraph |
| Body words (abstract → conclusion) | 2.4k, 2.15k, 2.4k, 2.4k, 2.0k, 2.45k, 2.4k, 2.65k | **≈ 2,400**. Dense text-only pages hold ≈ 650–700 words |
| Figures in body | 1, 2, 0, 2, 2, 4, 0, 1 | median 1.5 |
| Tables in body | 1, 1, 0, 1, 1, 1, 1, 1 | **7 of 8 have exactly one results table** |
| Floats total | 2, 3, 0, 3, 3, 5, 1, 2 | median 2.5; floats use about 0.5–1.2 of the 4 pages |
| Page-1 teaser figure | none in all 8 | **0/8**. Fig 1 sits at the top of p2 (4 papers) or later |
| Related work | own section 2/8 (short, ~150–230 words); subsection 1/8; end-of-paper paragraph 1/8; **merged into intro 4/8** | merge, or keep ≤ 150 words |
| Explicit contributions | bullets 2/8, inline (i)…(iv) 3/8, takeaway box 1/8 | inline (i)–(iii) is the most compact |
| Explicit limitations | 6/8 (a paragraph in the Discussion; 1 own section among the extra papers) | one short paragraph |
| Conclusion length | 60–450 words; usually merged as "Discussion and Conclusion" | ~150–250 |
| Total PDF pages | 7, 11, 21, 8, 8, 9, 8, 9 | 4 body pages + 1 page of references + **1–17 appendix pages** |
| Appendix contents | prompts (5/8), hyperparameters and implementation (6/8), extra results and ablations (6/8), qualitative examples (3/8), dataset details (4/8) | everything that is not needed to believe the main claim |

### S2. Recurring patterns in 4-page papers
1. **Page 1 is title + abstract + intro only.** The title block plus abstract takes ~45–50% of p1, so the intro starts mid-page
   and usually runs onto p2.
2. **Fig 1 = method or pipeline diagram at the top of p2**, full width but short (20–45% of the page), with a self-contained
   caption. No paper uses a page-1 teaser; there is no room for one.
3. **One results table does the heavy lifting** (booktabs, `\small`/`\footnotesize`, best value in bold, CIs or ± s.e. in the
   cells). The results prose is then very short (100–500 words) and reads like a list of claims.
4. **Claims as headings**: subsection titles or bold run-in `\paragraph{…}` headings that state the finding (papers 6 and 8),
   so a skim reader gets the result from the headings alone.
5. **Methods are summarised** in 1–2 paragraphs per component, plus 1–3 key equations (reward or fitness definition) and a
   bullet or numbered list for discrete design choices (reward bands, agent steps, tools). Hyperparameters, prompts, compute
   and data construction go to the appendix with a pointer ("see App. A").
6. **Space devices that stay inside the rules**: `wrapfigure` (papers 4 and 6), side-by-side minipage figures (paper 5),
   run-in paragraphs instead of numbered subsections, inline contribution lists, and moving related work into the intro.
   None of the 8 shrinks margins. Paper 8's tiny table is the legibility limit to avoid.
7. **Statistics inline**: 95% CIs in brackets in the text (papers 3, 7 and 8) instead of extra plots.
8. **Ending**: a ~150–250-word "Discussion / Limitations / Conclusion" block, often as run-in paragraphs.

### S3. Recommended page budget for our 4-page paper (counterfactual-DB verifiable rewards vs reward hacking in a text-to-SQL RL agent)

Target: **~2,300–2,450 words from the abstract to the end of the conclusion, plus 1 figure and 1 table (optionally a second small figure)**.

| Where | Content | Budget |
|---|---|---|
| p1 top | Title (≤ 2 lines), authors + affiliations + emails (Amazon requires them; use `\And` between authors and `\AND` to force line breaks) | ~0.25 pg |
| p1 | **Abstract: one paragraph, 150–180 words**, in four implicit parts to satisfy Amazon's structure without headings: (Intro) 1–2 sentences on reward hacking in execution-based SQL rewards → (Methods) 2 sentences on the counterfactual-database verifiable reward → (Results) 2 sentences with the key numbers (accuracy and hacking rate vs baseline, with seeds or CI) → (Conclusion) 1 sentence on the takeaway | ~0.25 pg |
| p1 → p2 | **1 Introduction, ~450 words**: the problem; concrete hacking examples (a query that matches the reference output on the single eval DB but is semantically wrong); our idea; **related work merged** as one ~120-word paragraph (reward hacking/specification gaming, RLVR, text-to-SQL evaluation such as test-suite accuracy) with citations; contributions inline (i)–(iii) | ~0.8 pg |
| p2 top | **Fig 1 (method diagram)**, full width, ≤ 30% of the page: question → policy SQL → executed on the original DB **and** on K counterfactual DBs → reward only if the results match the reference everywhere; one hacked query shown passing the original and failing a counterfactual. The caption must explain the figure on its own | ~0.3 pg |
| p2 | **2 Method, ~500 words**: the reward definition as 1–2 numbered equations (baseline reward vs counterfactual reward); how counterfactual DBs are generated (bullet list of perturbation types); cost note. Generator details go to the appendix | ~0.75 pg |
| p3 | **3 Setup, ~200 words** as run-in paragraphs (Model / Data / RL algorithm / Baselines / Metrics, with "hacking rate" defined precisely). Hyperparameters and compute go to the appendix | ~0.35 pg |
| p3 top | **Table 1 (main results)**: booktabs, `\small`, rows = reward variants, columns = execution accuracy on the original DB / on held-out counterfactual DBs / hacking rate / seeds or CI; the best in bold; caption above | ~0.3 pg |
| p3 → p4 | **4 Results, ~450 words**: 2–3 bold run-in claims ("Single-DB rewards are hacked.", "Counterfactual rewards close the gap.", "Cost."), CIs inline; optional **Fig 2** (training curves: reward vs true accuracy diverging for the baseline), half width, set side by side with a short analysis paragraph or a qualitative example | ~0.8 pg |
| p4 | **5 Discussion, limitations and conclusion, ~250 words** as run-ins: what the result does and does not show; limitations (scale, seeds, DB perturbation coverage, compute); conclusion sentence. Acknowledgments (1–2 lines, `ack`) if any | ~0.4 pg |
| p5+ | **References** (`\small` allowed, unlimited), then **Appendix**: (A) counterfactual-DB generation details, (B) reward hacking examples (SQL + DB snippets), (C) hyperparameters, prompts and compute, (D) extra results and ablations, per-seed numbers. No NeurIPS checklist | unlimited |

Hard rules to carry into the writing-rules file:
- `\usepackage[preprint]{neurips_2025}`; no margin, font or spacing hacks; US Letter; pdflatex; **0 Type 3 fonts** (install `cm-super`).
- The abstract is **one paragraph** (template rule), but it must still cover intro, methods, results and conclusion (Amazon rule).
- Content ends on **page 4**: the references heading may start on p5. Ack counts as content; keep it tiny.
- Table captions go above, figure captions below; booktabs with no vertical rules; size figures with `\linewidth`; keep text
  legible in B/W and the table font at least `\footnotesize`.
- Use natbib consistently (`\citet` in running text). Number every equation you reference. Use `\[ \]`, never `$$`.
- Use exactly one main results table; that is enough for 7 of the 8 reference papers. Do not put a teaser on page 1.

### Files
- Template test builds: `research_notes/template_test/` (`v_preprint.pdf`, `v_main_final.pdf`, `v_sglblindworkshop_final.pdf`,
  `v_dblblindworkshop.pdf`, `v_final.log` showing the `\@trackname` error, `shims/` used only for testing).
- Workshop PDFs: `research_notes/pdfs/workshop_4page/<arxiv-id>.pdf` (37 files); 60-dpi page renders in `research_notes/pdfs/renders/`.
