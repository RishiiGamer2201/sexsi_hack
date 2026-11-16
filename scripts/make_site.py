"""ARTICLE.md -> paper-style project page (one serif column, booktabs tables, KaTeX math) as the static HF Space
sqlcf-lexsi/counterfactual-sql-article. Math is cut out before Markdown parsing (so `_` and `\\` survive) and
typeset by KaTeX in the browser; figures are copied into the Space. Private until go_public.py.

  .venv/bin/python scripts/make_site.py --stage-only      # build runs/site_stage
  python3 -m http.server -d runs/site_stage 8000           # look at it
  source .secrets.env && .venv-train/bin/python scripts/make_site.py   # build + upload (private)
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

from hf_links import COLLECTION, DATA_COLLECTION, GITHUB, ORG
from make_hf_article import RAW, absolutize

ROOT = Path(__file__).resolve().parent.parent
REPO = f"{ORG}/counterfactual-sql-article"
# code spans/blocks pass through untouched; $$display$$; $inline$ must not start with a digit or space ($0.57 is money)
MATH = re.compile(r"(```[\s\S]*?```|`[^`\n]*`)|\$\$([\s\S]+?)\$\$|\$(?=[^\s\d])([^$\n]+?)(?<=\S)\$")
CARD = f"""---
title: When Execution Success Lies
emoji: 📄
colorFrom: indigo
colorTo: green
sdk: static
app_file: index.html
license: cc-by-nc-4.0
short_description: Write-up - counterfactual-database rewards for a SQL agent
tags: [text-to-sql, reward-hacking, lexsi-hackathon]
---
Project page for the Lexsi hackathon Track 3 entry. Source: [{GITHUB}]({GITHUB}) (ARTICLE.md).
"""


def cut_math(md):
    """Replace math by MATHPH<i>END tokens; returns (markdown, [(tex, display), ...])."""
    out = []

    def sub(m):
        if m[1]:
            return m[1]
        out.append((m[2] if m[2] is not None else m[3], m[2] is not None))
        return f"MATHPH{len(out) - 1}END"
    return MATH.sub(sub, md), out


def page(md):
    lines = md.split("\n")
    title, sub = lines[0].lstrip("# ").strip(), lines[2].strip()
    body = "\n".join(l for l in lines[3:] if not l.startswith("> **Links:**"))
    body = absolutize(body).replace(f"]({RAW}/", "](")  # links -> GitHub, figures stay local (copied in)
    body, maths = cut_math(body)
    js = lambda x: json.dumps(x).replace("</", "<\\/")
    authors, _, venue = sub.partition(" · ")  # "names (team) · Lexsi ... · PS ..." -> author line + venue line
    btn = lambda url, icon, label: (f'<a class="btn" href="{url}" target="_blank" rel="noopener">'
                                    f'<i class="{icon}"></i> {label}</a>')
    buttons = "\n".join([
        btn(GITHUB, "fab fa-github", "Code"),
        btn(f"https://huggingface.co/spaces/{ORG}/counterfactual-sql-demo", "fas fa-play", "Demo"),
        btn(f"https://huggingface.co/datasets/{ORG}/counterfactual-sql-data", "fas fa-database", "Dataset"),
        btn(COLLECTION, "fas fa-cubes", "Models"),
        btn(DATA_COLLECTION, "fas fa-layer-group", "Data collection")])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>When Execution Success Lies</title>
<meta name="description" content="Counterfactual-database rewards for a small SQL agent (Lexsi hackathon, Track 3)">
<link href="https://fonts.googleapis.com/css2?family=Tinos:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<style>
/* paper look: one narrow serif column, justified, booktabs tables. Tinos is metric-compatible with Times New Roman. */
html {{ background: #fff; }}
body {{ margin: 0; background: #fff; color: #111; font: 18px/1.5 "Times New Roman", Tinos, Times, serif; }}
.page {{ max-width: 740px; margin: 0 auto; padding: 0 16px; }}
header.page {{ text-align: center; padding-top: 3rem; }}
header h1 {{ font-size: 1.75rem; line-height: 1.25; margin: 0 0 1rem; }}
.authors {{ font-size: 1.1rem; margin: 0; }}
.venue {{ font-style: italic; color: #333; margin: .3rem 0 1rem; }}
.btn {{ display: inline-block; margin: .2rem; padding: .15rem .6rem; border: 1px solid #555; border-radius: 3px;
        color: #111; font-size: .85rem; text-decoration: none; }}
.btn:hover {{ background: #f0f0f0; }}
.note {{ font-size: .8rem; color: #555; margin-top: .6rem; }}
#body {{ text-align: justify; hyphens: auto; padding-bottom: 2rem; }}
#body p, #body li {{ text-align: justify; }}
h2 {{ font-size: 1.25rem; margin: 2.2rem 0 .6rem; }}
h3 {{ font-size: 1.05rem; margin: 1.5rem 0 .4rem; }}
.abstract {{ margin: 1.5rem 2.5rem 2rem; font-size: .95rem; }}
.abstract h2 {{ text-align: center; font-size: 1rem; font-variant: small-caps; letter-spacing: .05em; margin: 0 0 .5rem; }}
a {{ color: #1a4d8f; }}
ul, ol {{ padding-left: 1.6rem; }}
li {{ margin: .15rem 0; }}
figure {{ margin: 1.5rem 0; text-align: center; }}
figure img {{ max-width: 100%; }}
figcaption {{ font-size: .85rem; text-align: justify; margin-top: .4rem; }}
.tw {{ overflow-x: auto; margin: .6rem 0 1.4rem; }}
table {{ border-collapse: collapse; margin: 0 auto; font-size: .85rem; border-top: 2px solid #000; border-bottom: 2px solid #000; }}
thead th {{ border-bottom: 1px solid #000; }}
th, td {{ padding: .25rem .55rem; text-align: left; vertical-align: top; }}
code {{ font: .85em/1.3 ui-monospace, Menlo, Consolas, monospace; background: #f4f4f4; padding: 0 .15em; overflow-wrap: anywhere; }}
pre {{ background: #f7f7f7; padding: .7rem; overflow-x: auto; }}
pre code {{ background: none; }}
.katex {{ font-size: 1.05em; }}
.katex-display {{ overflow-x: auto; overflow-y: hidden; padding: .3rem 0; }}
pre.bib {{ font-size: .78rem; white-space: pre-wrap; text-align: left; }}
@media (max-width: 600px) {{
  body {{ font-size: 17px; }} header h1 {{ font-size: 1.4rem; }}
  #body p, #body li {{ text-align: left; }} .abstract {{ margin: 1rem 0 1.5rem; }}
}}
</style></head>
<body>
<header class="page">
<h1>{title}</h1>
<p class="authors">{authors}</p>
<p class="venue">{venue}</p>
<div class="links">{buttons}</div>
</header>
<main id="body" class="page"><noscript>This page needs JavaScript; the plain version is <a href="{GITHUB}/blob/main/ARTICLE.md">ARTICLE.md</a>.</noscript></main>
<div class="page"><h2>BibTeX</h2><pre class="bib">@misc{{teenkhapeetars2026counterfactual,
  title  = {{When Execution Success Lies: Counterfactual-Database Rewards for a Small SQL Agent}},
  author = {{Rai, Shreshth and Singh, Rishii Kumar and Aggarwal, Aksh}},
  year   = {{2026}},
  note   = {{Lexsi Labs AI Safety and Alignment Hackathon, Track 3}},
  url    = {{{GITHUB}}}
}}</pre></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script>
const MD = {js(body)}, MATH = {js(maths)};
let html = marked.parse(MD, {{gfm: true}}).replace(/MATHPH(\\d+)END/g, (_, i) =>
  katex.renderToString(MATH[i][0], {{displayMode: MATH[i][1], throwOnError: false}}));
const el = document.getElementById("body");
el.innerHTML = html;
el.querySelectorAll("table").forEach(t => {{ const w = document.createElement("div"); w.className = "tw"; t.before(w); w.append(t); }});
// figure + caption from the image alt text
el.querySelectorAll("p > img:only-child").forEach(img => {{
  const f = document.createElement("figure"), c = document.createElement("figcaption");
  c.textContent = img.alt; img.parentElement.replaceWith(f); f.append(img, c); }});
// clickable citations: "Zhu et al., 2026", "Zhong, Yu & Klein (2020)", "Ai, 2026" -> #ref-<surname><year> in References
const rh = [...el.querySelectorAll("h2")].find(h => h.textContent.trim() === "References");
const refs = rh && rh.nextElementSibling, keys = new Set();
if (refs) refs.querySelectorAll("li").forEach(li => {{
  const m = li.textContent.match(/^(.+?)(?:,.*?)? \\((\\d{{4}}[ab]?)\\)/);
  if (m) {{ const k = m[1].trim().replace(/\\W/g, "") + m[2]; li.id = "ref-" + k; keys.add(k); }} }});
const CITE = /\\b(Team Cohere|Lexsi Labs|[A-Z][A-Za-z'-]+)((?: et al\\.)|(?:,? [A-Z][a-z]+)*(?: & [A-Z][A-Za-z]+)?),? (?:\\((\\d{{4}}[ab]?)\\)|(\\d{{4}}[ab]?)\\b)/g;
const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {{ acceptNode: n =>
  n.parentElement.closest("a, code, pre, .katex") || (refs && refs.contains(n)) ? 2 : 1 }});
const texts = []; while (tw.nextNode()) texts.push(tw.currentNode);
texts.forEach(n => {{
  const s = n.nodeValue; let last = 0, frag = null;
  for (const m of s.matchAll(CITE)) {{
    const k = m[1].replace(/\\W/g, "") + (m[3] || m[4]); if (!keys.has(k)) continue;
    frag = frag || document.createDocumentFragment();
    frag.append(s.slice(last, m.index));
    const a = document.createElement("a"); a.href = "#ref-" + k; a.className = "cite"; a.textContent = m[0];
    frag.append(a); last = m.index + m[0].length; }}
  if (frag) {{ frag.append(s.slice(last)); n.replaceWith(frag); }} }});
// abstract block: the "Abstract" heading and its paragraphs, up to the next h2
const ah = [...el.querySelectorAll("h2")].find(h => h.textContent.trim() === "Abstract");
if (ah) {{ const box = document.createElement("section"); box.className = "abstract"; ah.before(box);
  let n = ah; while (n && !(n !== ah && n.tagName === "H2")) {{ const nx = n.nextElementSibling; box.append(n); n = nx; }} }}
el.querySelectorAll('a[href^="http"]').forEach(a => {{ a.target = "_blank"; a.rel = "noopener"; }});
</script>
</body></html>
""", maths


if __name__ == "__main__":
    t, m = cut_math("price $0.57 and $D_0$, `$x$` code, $$a_1$$")
    assert t == "price $0.57 and MATHPH0END, `$x$` code, MATHPH1END" and m == [("D_0", False), ("a_1", True)], (t, m)
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage-only", action="store_true", help="build runs/site_stage, do not upload")
    a = ap.parse_args()
    html, maths = page((ROOT / "ARTICLE.md").read_text())
    assert "$\\" not in html and "MATHPH" not in html.split("const MD")[0], "math left unprotected"
    stage = ROOT / "runs/site_stage"
    shutil.rmtree(stage, ignore_errors=True)
    (stage / "results").mkdir(parents=True)
    figs = re.findall(r"!\[[^\]]*\]\((results/[^)\s]+)\)", (ROOT / "ARTICLE.md").read_text())
    for f in figs:
        shutil.copy(ROOT / f, stage / f)
    (stage / "index.html").write_text(html)
    (stage / "README.md").write_text(CARD)
    print(f"staged {stage}: {len(maths)} formulas, {len(figs)} figures")
    if a.stage_only:
        sys.exit(0)
    from huggingface_hub import HfApi
    token = os.environ.get("HF_TOKEN_HACK") or sys.exit("HF_TOKEN_HACK not set: source .secrets.env")
    api = HfApi(token=token)  # explicit hackathon token; never the cached default
    api.create_repo(REPO, repo_type="space", space_sdk="static", private=True, exist_ok=True)
    api.upload_folder(repo_id=REPO, repo_type="space", folder_path=str(stage), commit_message="article page update")
    print(f"https://huggingface.co/spaces/{REPO}")
