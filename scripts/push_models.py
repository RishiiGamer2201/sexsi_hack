"""Push the LoRA adapters (SFT, GRPO-B, GRPO-C) to sqlcf-lexsi model repos, with the base model's licence, and
gather demo + data + models in one HF collection. Private until --public; --gated makes the repos gated with
automatic approval (organisers, Nov 9: public or auto-approved gating is fine; include the base model's licence).

  source .secrets.env && .venv-train/bin/python scripts/push_models.py [--public [--gated]] [--stage-only]
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from hf_links import LINKS

ROOT = Path(__file__).resolve().parent.parent
ORG = "sqlcf-lexsi"
E4 = json.loads((ROOT / "results/e4_eval.json").read_text())
MODELS = {  # repo suffix: (local run dir, results key, one-line role, G3 label)
    "tiny-aya-global-sqlcf-sft": ("runs/sft", "sft_ho", "SFT warm start on scripted oracle trajectories (3 train templates held out for GRPO); the init of GRPO-B and GRPO-C", "baseline"),
    "tiny-aya-global-sqlcf-grpo-b": ("runs/grpo_B", "B", "GRPO, 60 steps, single-DB strict execution reward `R_exec_rex` (condition B)", "improved: beats SFT on verified accuracy, McNemar p = 0.006"),
    "tiny-aya-global-sqlcf-grpo-c": ("runs/grpo_C", "C", "GRPO, 60 steps, counterfactual-DB reward `R_cf_mean` (condition C)", "null: no gain over SFT (p = 0.21) and below GRPO-B; reported as a null"),
}
NOTICE = """This adapter is a derivative of CohereLabs/tiny-aya-global and is released under the same terms:
- CC-BY-NC-4.0 (full text in LICENSE) with Cohere's acceptable-use addendum: https://cohere.com/c4ai-cc-by-nc-license
- Cohere Labs Acceptable Use Policy: https://docs.cohere.com/docs/c4ai-acceptable-use-policy
Non-commercial use only. You also need access to the gated base model to use it.
"""


def card(repo, role, key, label):
    v = E4[key]
    pct = lambda x: f"{100 * x[0]:.1f}% [{100 * x[1]:.1f}, {100 * x[2]:.1f}]"
    return f"""---
base_model: CohereLabs/tiny-aya-global
library_name: peft
license: cc-by-nc-4.0
license_link: https://cohere.com/c4ai-cc-by-nc-license
tags: [text-to-sql, grpo, lora, agenttune, counterfactual-rewards, lexsi-hackathon]
datasets: [{ORG}/counterfactual-sql-data]
---
# {repo}

LoRA adapter (r=16) for [CohereLabs/tiny-aya-global](https://huggingface.co/CohereLabs/tiny-aya-global): {role}.

{LINKS}
**Status (gate G3): {label}.**

Test set: 331 items x 8 samples, T=0.7, fresh databases from a different generator; "verified" = correct on the
original and all 4 counterfactual DBs.

| Metric | Value (95% CI) |
|---|---|
| Verified accuracy | {pct(v['verified'])} |
| Single-DB accuracy | {pct(v['single'])} |
| Silent-error rate | {pct(v['silent_error'])} |
| Held-out family F4, verified | {pct(v['verified_by_family']['F4'])} |

## Use

Accept the [base model's licence](https://huggingface.co/CohereLabs/tiny-aya-global) first, then:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base = AutoModelForCausalLM.from_pretrained("CohereLabs/tiny-aya-global", dtype="bfloat16", device_map="auto")
model = PeftModel.from_pretrained(base, "{ORG}/{repo}")
tok = AutoTokenizer.from_pretrained("{ORG}/{repo}")
```

It is a multi-turn SQL agent with one `run_sql` tool, prompted and parsed the way AgentTune renders Tiny Aya
(see `sqlcf/agent.py` and `evaluate.py gen` in the repo). vLLM LoRA fails on Tiny Aya's tied embeddings, so for vLLM
merge first: `python train.py merge --init <this adapter> --out merged` (fp32 merge, saved fp16).

## Licence
{NOTICE}"""


ap = argparse.ArgumentParser()
ap.add_argument("--public", action="store_true")
ap.add_argument("--gated", action="store_true", help="with --public: gated, automatic approval")
ap.add_argument("--stage-only", action="store_true")
a = ap.parse_args()

stage = ROOT / "runs/models_stage"
shutil.rmtree(stage, ignore_errors=True)
for repo, (run, key, role, label) in MODELS.items():
    d = stage / repo
    d.mkdir(parents=True)
    src = ROOT / run / "adapter"
    for f in ("adapter_config.json", "adapter_model.safetensors", "tokenizer.json", "tokenizer_config.json",
              "chat_template.jinja", "special_tokens_map.json"):  # not ref/ (reference copy) or training_args.bin (pickle)
        if (src / f).exists():
            shutil.copy(src / f, d / f)
    for f in ("lexsi_provenance.json", "grpo_training_config.yaml", "training_stats.json"):
        if (ROOT / run / f).exists():
            shutil.copy(ROOT / run / f, d / f)
    shutil.copy(ROOT / "docs/LICENSE-CC-BY-NC-4.0.txt", d / "LICENSE")
    (d / "NOTICE").write_text(NOTICE)
    (d / "README.md").write_text(card(repo, role, key, label))
    assert json.loads((d / "adapter_config.json").read_text())["base_model_name_or_path"] == "CohereLabs/tiny-aya-global"
    print(f"staged {repo}: {sorted(p.name for p in d.iterdir())}")
if a.stage_only:
    sys.exit(0)

from huggingface_hub import HfApi  # noqa: E402

token = os.environ.get("HF_TOKEN_HACK") or sys.exit("HF_TOKEN_HACK not set: source .secrets.env")
api = HfApi(token=token)  # explicit hackathon token; never the cached default
for repo in MODELS:
    rid = f"{ORG}/{repo}"
    api.create_repo(rid, private=not a.public, exist_ok=True)
    api.upload_folder(repo_id=rid, folder_path=str(stage / repo), commit_message="adapter + card + licence")
    if a.public:
        api.update_repo_settings(rid, private=False, gated="auto" if a.gated else False)
    print(f"https://huggingface.co/{rid}")

title = "Counterfactual-DB rewards for a small SQL agent"
coll = next((c for c in api.list_collections(owner=ORG) if c.title == title), None) \
    or api.create_collection(title, namespace=ORG, private=not a.public,
                             description="Lexsi hackathon Track 3: demo, data and adapters")
have = {i.item_id for i in api.get_collection(coll.slug).items}
for item, kind in [(f"{ORG}/counterfactual-sql-demo", "space"), (f"{ORG}/counterfactual-sql-data", "dataset"),
                   *[(f"{ORG}/{r}", "model") for r in MODELS]]:
    if item not in have:
        api.add_collection_item(coll.slug, item_id=item, item_type=kind)
if a.public:
    api.update_collection_metadata(coll.slug, private=False)
print(f"https://huggingface.co/collections/{coll.slug}")
