"""ARTICLE.md -> Nerfies-style project page (Bulma hero + link buttons, KaTeX math) as the static HF Space
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
    btn = lambda url, icon, label: (f'<a class="button is-dark is-rounded" href="{url}" target="_blank" rel="noopener">'
                                    f'<span class="icon"><i class="{icon}"></i></span><span>{label}</span></a>')
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
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.4/css/bulma.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<style>
body {{ font-family: 'Noto Sans', sans-serif; background: #fff; }}
.hero .title {{ font-size: 2.6rem; }}
.subtitle.meta {{ font-size: 1.05rem; color: #555; }}
.links .button {{ margin: .25rem; }}
.page {{ max-width: 960px; margin: 0 auto; padding: 0 16px 4rem; }}
.page h2 {{ text-align: center; font-size: 1.9rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; }}
.page h3 {{ font-size: 1.35rem; margin-top: 2rem; }}
.page img {{ display: block; margin: 1.5rem auto; max-width: 100%; }}
.page .tw {{ overflow-x: auto; margin-bottom: 1.5rem; }}
.page table {{ font-size: .88rem; }}
.page blockquote {{ background: #f6f8fa; border-left-color: #485fc7; }}
.katex-display {{ overflow-x: auto; overflow-y: hidden; padding: .3rem 0; }}
pre.bib {{ font-size: .8rem; white-space: pre-wrap; }}
.page code {{ overflow-wrap: anywhere; }}
@media (max-width: 600px) {{ .hero .title {{ font-size: 1.7rem; }} .hero-body {{ padding: 2rem 16px; }} .page h2 {{ font-size: 1.4rem; }} }}
</style></head>
<body>
<section class="hero"><div class="hero-body"><div class="container has-text-centered" style="max-width: 960px">
<h1 class="title is-1 publication-title">{title}</h1>
<p class="subtitle meta">{sub}</p>
<div class="links">{buttons}</div>
<p class="is-size-7 has-text-grey mt-3">Every number comes from stored runs in <code>results/</code>; <code>python verify_all.py</code> re-derives them.</p>
</div></div></section>
<div id="body" class="page content"><noscript>This page needs JavaScript; the plain version is <a href="{GITHUB}/blob/main/ARTICLE.md">ARTICLE.md</a>.</noscript></div>
<div class="page content"><h2>BibTeX</h2><pre class="bib">@misc{{teenkhapeetars2026counterfactual,
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
