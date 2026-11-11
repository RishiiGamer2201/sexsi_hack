"""Flip every submission artifact to public in one go: 3 adapters (gated, automatic approval), dataset, Space,
both HF collections, and the GitHub repo. Dry run by default (prints current visibility); --go makes the changes.
Run only after the Lexsi submission form is sent (team rule).

  source .secrets.env && .venv-train/bin/python scripts/go_public.py [--go]
"""
import argparse
import os
import subprocess
import sys

from huggingface_hub import HfApi

ORG = "sqlcf-lexsi"
REPOS = [(f"{ORG}/tiny-aya-global-sqlcf-{m}", "model") for m in ("sft", "grpo-b", "grpo-c")] + [
    (f"{ORG}/counterfactual-sql-data", "dataset"), (f"{ORG}/counterfactual-sql-demo", "space")]
COLLECTIONS = [f"{ORG}/counterfactual-db-rewards-for-a-small-sql-agent-6af174f77dbae0bf0a54c3c4",  # models + demo
               f"{ORG}/counterfactual-sql-data-rollouts-and-traces-6af479430243b7731f85d144"]  # dataset
GITHUB = "RishiiGamer2201/sexsi_hack"

ap = argparse.ArgumentParser()
ap.add_argument("--go", action="store_true", help="make the changes (default: dry run)")
a = ap.parse_args()
api = HfApi(token=os.environ.get("HF_TOKEN_HACK") or sys.exit("HF_TOKEN_HACK not set: source .secrets.env"))


def state():
    for rid, kind in REPOS:
        i = api.repo_info(rid, repo_type=kind)
        print(f"{kind:8} {rid:50} private={i.private} gated={getattr(i, 'gated', None)}")
    for c in COLLECTIONS:
        print(f"{'coll':8} {c:50} private={api.get_collection(c).private}")
    gh = subprocess.run(["gh", "repo", "view", GITHUB, "--json", "visibility", "-q", ".visibility"],
                        capture_output=True, text=True)
    print(f"{'github':8} {GITHUB:50} {gh.stdout.strip() or gh.stderr.strip()}")


state()
if not a.go:
    sys.exit("dry run: nothing changed (pass --go)")
for rid, kind in REPOS:
    api.update_repo_settings(rid, repo_type=kind, private=False, **({"gated": "auto"} if kind == "model" else {}))
for c in COLLECTIONS:
    api.update_collection_metadata(c, private=False)
subprocess.run(["gh", "repo", "edit", GITHUB, "--visibility", "public", "--accept-visibility-change-consequences"],
               check=True)
print("--- after")
state()
