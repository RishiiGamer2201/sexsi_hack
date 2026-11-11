"""ARTICLE.md -> runs/hf_article.md for pasting into the Hugging Face Article editor: repo-relative links and images
become absolute GitHub URLs (images render once the repo is public).

  python scripts/make_hf_article.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = "https://github.com/RishiiGamer2201/sexsi_hack"
RAW = "https://raw.githubusercontent.com/RishiiGamer2201/sexsi_hack/main"


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
