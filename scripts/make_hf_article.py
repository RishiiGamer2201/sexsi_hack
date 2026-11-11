"""ARTICLE.md -> runs/hf_article.md for pasting into the Hugging Face Article editor: images load from the HF
dataset (results/ is mirrored there), other repo-relative links become absolute GitHub URLs. Also writes
runs/abstract.txt (ABSTRACT.md as plain text for the form).

  python scripts/make_hf_article.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = "https://github.com/RishiiGamer2201/sexsi_hack"
RAW = "https://huggingface.co/datasets/sqlcf-lexsi/counterfactual-sql-data/resolve/main"


def absolutize(md):
    rel = r"\]\((?!https?://|#|mailto:)([^)\s]+)\)"
    md = re.sub(r"(!\[[^\]]*)" + rel, lambda m: f"{m[1]}]({RAW}/{m[2]})", md)  # images
    return re.sub(r"(?<!!)(\[[^\]]*)" + rel, lambda m: f"{m[1]}]({GH}/blob/main/{m[2]})", md)  # links


if __name__ == "__main__":
    t = absolutize("![f](results/a.png) [p](patches/x.patch) [u](https://x.org) [s](#sec)")
    assert t == f"![f]({RAW}/results/a.png) [p]({GH}/blob/main/patches/x.patch) [u](https://x.org) [s](#sec)", t
    out = absolutize((ROOT / "ARTICLE.md").read_text())
    assert not re.search(r"\]\((?!https?://|#|mailto:)", out), "relative link left"
    (ROOT / "runs").mkdir(exist_ok=True)
    (ROOT / "runs/hf_article.md").write_text(out)
    print(f"wrote runs/hf_article.md ({len(out.split())} words)")
    # plain-text abstract for the form's Abstract box: drop the title + track lines, strip ** and `
    ab = re.sub(r"\*\*|`", "", (ROOT / "ABSTRACT.md").read_text().split("\n", 3)[3]).strip() + "\n"
    assert len(ab.split()) < 500, len(ab.split())
    (ROOT / "runs/abstract.txt").write_text(ab)
    print(f"wrote runs/abstract.txt ({len(ab.split())} words)")
