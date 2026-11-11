"""Push the demo to the static HF Space sqlcf-lexsi/counterfactual-sql-demo: demo/index.html runs sqlcf/demo.py
in the visitor's browser (Pyodide 0.27.7: Python + SQLite in WebAssembly), so hosting is free and serverless.
HF bills Gradio/Docker Spaces (402 for free orgs and free personal accounts, Nov 9); Gradio-Lite is stale
(last release Sep 2025, fails on current deps). Private until --public.

  source .secrets.env && .venv-train/bin/python scripts/push_space.py [--models base sft_ho B C] [--public]
Test locally: --stage-only, then python3 -m http.server -d runs/space_stage 8000
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from hf_links import LINKS

ROOT = Path(__file__).resolve().parent.parent
REPO = "sqlcf-lexsi/counterfactual-sql-demo"
CARD = """---
title: Counterfactual SQL Rewards
emoji: 🧮
colorFrom: indigo
colorTo: green
sdk: static
app_file: index.html
license: cc-by-nc-4.0
short_description: Check SQL on counterfactual DBs the agent never saw
tags: [text-to-sql, reward-hacking, lexsi-hackathon]
---
A SQL query can match the answer on the one database an agent explored and still be wrong.
Pick a test question and a recorded run (Tiny Aya Global base, SFT, GRPO-B single-DB reward, GRPO-C
counterfactual reward, or Command A), or type your own SQL, and see it checked on the original DB plus
counterfactual DBs the agent never saw, with the score each reward function gives. Runs in your browser
(Pyodide); the first load takes 20-60 s.

@@LINKS@@""".replace("@@LINKS@@", LINKS)

ap = argparse.ArgumentParser()
ap.add_argument("--models", nargs="+", default=["base", "sft_ho", "B", "C", "command_a"], help="results/traj_<model>.jsonl to ship")
ap.add_argument("--public", action="store_true")
ap.add_argument("--stage-only", action="store_true", help="build runs/space_stage, do not upload")
a = ap.parse_args()

stage = ROOT / "runs/space_stage"
shutil.rmtree(stage, ignore_errors=True)
files = ["sqlcf/demo.py", "sqlcf/rewards.py", "sqlcf/compare.py", "data/test/items.jsonl",
         *[f"results/traj_{m}.jsonl" for m in a.models],
         *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "data/test/dbs").rglob("*.db"))]
for rel in files:
    (stage / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / rel, stage / rel)
shutil.copy(ROOT / "demo/index.html", stage / "index.html")
(stage / "files.json").write_text(json.dumps(files))
(stage / "README.md").write_text(CARD)
print(f"staged {len(files)} files in {stage}")
if a.stage_only:
    sys.exit(0)

from huggingface_hub import HfApi  # noqa: E402

token = os.environ.get("HF_TOKEN_HACK") or sys.exit("HF_TOKEN_HACK not set: source .secrets.env")
api = HfApi(token=token)  # explicit hackathon token; never the cached default
api.create_repo(REPO, repo_type="space", space_sdk="static", private=not a.public, exist_ok=True)
api.upload_folder(repo_id=REPO, repo_type="space", folder_path=str(stage), commit_message="demo update",
                  delete_patterns=["*.py", "*.html", "*.json", "sqlcf/*", "results/*", "data/**"])  # drop stale files
print(f"https://huggingface.co/spaces/{REPO}")
