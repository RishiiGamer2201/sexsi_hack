"""Push the data collection to the HF dataset sqlcf-lexsi/counterfactual-sql-data (private until --public).
Item files, SFT trajectories, results and GRPO rollout logs as-is; each split's SQLite DBs as one dbs.tar.gz
(about 3,900 small files otherwise). Everything here is regenerable with the README commands.

  source .secrets.env && .venv-train/bin/python scripts/push_dataset.py [--stage-only] [--public]
"""
import argparse
import os
import shutil
import sys
import tarfile
from pathlib import Path

from hf_links import LINKS

ROOT = Path(__file__).resolve().parent.parent
REPO = "sqlcf-lexsi/counterfactual-sql-data"
CARD = """---
license: cc-by-nc-4.0
language: [en]
tags: [text-to-sql, reward-modeling, grpo, counterfactual, sqlite, lexsi-hackathon]
pretty_name: Counterfactual-DB rewards for SQL agents
---
# Counterfactual-DB rewards for SQL agents: data, results and rollout logs

@@LINKS@@
Every number in the write-up is re-derived from these files by `python verify_all.py` in the code repo.

```python
import tarfile
from huggingface_hub import snapshot_download

d = snapshot_download("sqlcf-lexsi/counterfactual-sql-data", repo_type="dataset")
for split in ("audit", "train", "test"):
    tarfile.open(f"{d}/{split}/dbs.tar.gz").extractall(f"{d}/{split}")  # SQLite DBs next to items.jsonl
```

| Path | What |
|---|---|
| `{audit,train,test}/items.jsonl` | Questions, gold SQL, per-item DB paths and gold results on the original + counterfactual DBs |
| `{audit,train,test}/dbs.tar.gz` | The SQLite DBs (original and counterfactual copies); extract in place |
| `train/grpo_items.jsonl` | GRPO prompts (SFT pass rate in (0,1); 3 templates held out of SFT) |
| `sft.jsonl`, `sft_all_templates.jsonl` | Scripted oracle trajectories for the SFT warm start |
| `results/e0_*.json`, `results/e1_*.json`, `figure*.png` | Reward audit (FP/FN per reward) and blind rate vs DB size |
| `results/traj_<model>.jsonl` | Test trajectories: base, sft, sft_ho, GRPO B, GRPO C, Command A, sft_distil (E9) |
| `results/e4_eval.json` | Verified / single-DB accuracy, silent error, smuggling, pass^k, McNemar, bootstrap |
| `results/a2_spider_lucky.json` | E6: Spider-dev lucky passes of 8 published systems (question indices only; predictions from bossben/ESMp, DBs from Zhong et al. 2020) |
| `results/a3_skyrl_audit.json` | E7: SkyRL-SQL reward audit on the E0 candidates |
| `results/a4_selfconsistency.json` | E8: gold-free majority vote and shaky-answer flag on the test trajectories |
| `results/teacher_command_a.jsonl`, `results/d1_teacher_filter.json` | E9: Command A plan + SQL on the 353 SFT train items; lucky answers a single-DB filter would keep |
| `sft_distil.jsonl` | E9: the SFT trajectories with the 211 counterfactual-verified teacher endings swapped in (`traj_sft_distil` is the resulting model) |
| `runs/grpo_<B,C>_rewards.jsonl` | Every GRPO rollout: final SQL, reward, per-DB pass vector |
| `runs/grpo_<B,C>/` | `lexsi_provenance.json`, training config and stats |

Synthetic e-commerce data from a seeded generator; no personal data. Rollouts contain outputs of
Tiny Aya Global (CC-BY-NC-4.0) and Cohere Command A, hence the non-commercial licence.
""".replace("@@LINKS@@", LINKS)

ap = argparse.ArgumentParser()
ap.add_argument("--public", action="store_true")
ap.add_argument("--stage-only", action="store_true")
a = ap.parse_args()

stage = ROOT / "runs/dataset_stage"
shutil.rmtree(stage, ignore_errors=True)
stage.mkdir(parents=True)
for split in ("audit", "train", "test"):
    src = ROOT / "data" / split
    for f in src.glob("*.json*"):
        (stage / split).mkdir(exist_ok=True)
        shutil.copy(f, stage / split / f.name)
    with tarfile.open(stage / split / "dbs.tar.gz", "w:gz") as t:
        t.add(src / "dbs", arcname="dbs")
for f in ("sft.jsonl", "sft_all_templates.jsonl", "sft_distil.jsonl"):
    shutil.copy(ROOT / "data" / f, stage / f)
(stage / "results").mkdir()
for f in (ROOT / "results").iterdir():
    if f.is_file() and not f.name.startswith("_"):
        shutil.copy(f, stage / "results" / f.name)
for run in ("B", "C"):
    log = ROOT / f"runs/grpo_{run}_rewards.jsonl"
    if not log.exists():
        print(f"skip GRPO-{run}: no reward log")
        continue
    (stage / f"runs/grpo_{run}").mkdir(parents=True)
    shutil.copy(log, stage / "runs" / log.name)
    for f in ("lexsi_provenance.json", "grpo_training_config.yaml", "training_stats.json"):
        if (ROOT / f"runs/grpo_{run}/{f}").exists():
            shutil.copy(ROOT / f"runs/grpo_{run}/{f}", stage / f"runs/grpo_{run}/{f}")
(stage / "README.md").write_text(CARD)
n = sum(1 for p in stage.rglob("*") if p.is_file())
print(f"staged {n} files, {sum(p.stat().st_size for p in stage.rglob('*') if p.is_file()) / 1e6:.0f} MB in {stage}")
if a.stage_only:
    sys.exit(0)

from huggingface_hub import HfApi  # noqa: E402

token = os.environ.get("HF_TOKEN_HACK") or sys.exit("HF_TOKEN_HACK not set: source .secrets.env")
api = HfApi(token=token)  # explicit hackathon token; never the cached default
api.create_repo(REPO, repo_type="dataset", private=not a.public, exist_ok=True)
api.upload_folder(repo_id=REPO, repo_type="dataset", folder_path=str(stage), commit_message="data update")
print(f"https://huggingface.co/datasets/{REPO}")
