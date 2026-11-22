# Citations to verify before submission

Nov 22: every arXiv-backed entry in `refs.bib` was checked against the arXiv API (title, authors, year, journal_ref/comment).

## Fixed on Nov 22

| Key | Fix |
|---|---|
| `zhu2026revisql` | Full author names (Yuxuan Zhu, Tengjun Jin, Yoojin Choi, Daniel Kang); title capitalisation. |
| `habibollah2026` | Title was wrong. Now "SynSQL: Synthesizing Relational Databases for Robust Evaluation of Text-to-SQL Systems"; full names. |
| `he2025hardtests` | Renamed on arXiv to HardTestGen, published at ICLR 2026. Updated to ICLR 2026 (the paper text cites only by key). |
| `liu2025bugs` | Full author list (5); SIGKDD 2025 confirmed by journal_ref. |
| `lyngkhoi2026agenttune` | Full author list (6). |
| `salamanca2026tinyaya` | Full first three names, title confirmed (26 authors, "and others"). |
| `esmp` | Now cites the ESM+ paper: Ascoli, Kandikonda, Choi, arXiv 2407.07313 (2024; later versions retitled "ETM"). The repo bossben/ESMp is that paper's code (its README); the commit stays in the note. |

## Confirmed, no change

`chandra2014` (arXiv 1411.6704, 6 authors; VLDB Journal 2015, the year in the entry, key name is cosmetic), `cohere2025commanda` (2504.00698), `ma2025sqlr1` (arXiv comment: NeurIPS 2025), skalse2022, amodei2016, gao2023, shao2024, hu2022, yu2018, zhong2020, pasupat2016, pourreza2025, yao2025arctic.

## Still open (low priority)

- `skyrl2025`: SkyRL-SQL was released as a blog post plus code, not a paper. The closest paper is SkyRL-Agent (arXiv 2511.16108), which is a different system, so the entry keeps citing the GitHub commit we used (d870046).
- `chandra2014`: volume and pages of the VLDB Journal version not added (not on arXiv); add if an author has the DOI.
- `li2023bird` is in `refs.bib` but not cited. plainnat prints only cited entries, so it is harmless.
