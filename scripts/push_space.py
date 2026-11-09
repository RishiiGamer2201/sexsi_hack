"""Push the demo (app.py) to the static HF Space sqlcf-lexsi/counterfactual-sql-demo. It runs in the visitor's
browser via Gradio-Lite (Pyodide: Python + SQLite in WebAssembly), so it is free to host and needs no server.
HF bills Gradio/Docker Spaces (402 for free orgs and free personal accounts, Nov 9); static Spaces are free.
Ships app.py, sqlcf/{rewards,compare}.py, data/test (2 MB) and the chosen trajectories. Private until --public.

  source .secrets.env && .venv-train/bin/python scripts/push_space.py [--models base sft_ho ...] [--public]
Test locally: python -m http.server -d runs/space_stage 8000, open http://localhost:8000
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "sqlcf-lexsi/counterfactual-sql-demo"
LITE = "https://cdn.jsdelivr.net/npm/@gradio/lite@5.45.0/dist"
CARD = """---
title: Counterfactual SQL Rewards
emoji: 🧮
colorFrom: indigo
colorTo: green
sdk: static
app_file: index.html
license: cc-by-nc-4.0
---
A SQL query can match the answer on the one database an agent explored and still be wrong.
Pick a test question and a recorded run of Tiny Aya Global (base / SFT / GRPO), or type your own SQL,
and see it checked on the original DB plus counterfactual DBs the agent never saw, with the score
each reward function gives. Runs in your browser (Gradio-Lite); the first load takes about a minute.
"""
PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Counterfactual SQL Rewards</title>
<script type="module" crossorigin src="{lite}/lite.js"></script>
<link rel="stylesheet" href="{lite}/lite.css">
</head><body>
<gradio-lite>
{files}
</gradio-lite>
</body></html>
"""

ap = argparse.ArgumentParser()
ap.add_argument("--models", nargs="+", default=["base", "sft", "sft_ho"], help="results/traj_<model>.jsonl to ship")
ap.add_argument("--public", action="store_true")
ap.add_argument("--stage-only", action="store_true", help="build runs/space_stage, do not upload")
a = ap.parse_args()

stage = ROOT / "runs/space_stage"
shutil.rmtree(stage, ignore_errors=True)
files = ["app.py", "sqlcf/rewards.py", "sqlcf/compare.py", "data/test/items.jsonl",
         *[f"results/traj_{m}.jsonl" for m in a.models],
         *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "data/test/dbs").rglob("*.db"))]
for rel in files:
    (stage / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / rel, stage / rel)
tags = "\n".join(f'<gradio-file name="{f}" url="{f}"{" entrypoint" if f == "app.py" else ""}></gradio-file>' for f in files)
(stage / "index.html").write_text(PAGE.format(lite=LITE, files=tags))
(stage / "README.md").write_text(CARD)
print(f"staged {len(files)} files in {stage}")
if a.stage_only:
    sys.exit(0)

from huggingface_hub import HfApi  # noqa: E402

token = os.environ.get("HF_TOKEN_HACK") or sys.exit("HF_TOKEN_HACK not set: source .secrets.env")
api = HfApi(token=token)  # explicit hackathon token; never the cached default
api.create_repo(REPO, repo_type="space", space_sdk="static", private=not a.public, exist_ok=True)
api.upload_folder(repo_id=REPO, repo_type="space", folder_path=str(stage), commit_message="demo update",
                  delete_patterns=["results/*", "data/**"])
print(f"https://huggingface.co/spaces/{REPO}")
