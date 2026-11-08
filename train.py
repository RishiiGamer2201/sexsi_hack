"""SFT warm-start and GRPO (conditions B/C) for Tiny Aya Global + LoRA. GPU-side (Vertex L4).

  python train.py sft  --out runs/sft
  python train.py grpo --reward R_exec_rex --init runs/sft/merged --out runs/grpo_B
  python train.py grpo --reward R_cf_mean  --init runs/sft/merged --out runs/grpo_C
  python train.py render                 # CPU check: print one SFT example as the model sees it

Tiny Aya's chat template ignores `tools`, so AgentTune's rollout appends its fallback tool prompt
to the system turn, the model calls tools as a JSON list, and tool results come back folded into
user turns. SFT text is built with AgentTune's own constants/functions so it matches rollouts.
B and C differ ONLY in --reward; everything else is a shared default below.
"""
import argparse
import json
from pathlib import Path

from agenttune.agentic.rollout_engines.rollout_factory import (
    DEFAULT_TOOL_RESULT_FORMAT, DEFAULT_TOOLS_FALLBACK_PROMPT, _build_tool_schema,
    fold_tool_messages_into_user)

from sqlcf.agent import dataset_row, run_sql
from sqlcf.rewards import REWARDS

MODEL = "CohereLabs/tiny-aya-global"
SFT_BASES = {"S_s101", "S_s102", "S_s103"}  # GRPO uses the other train bases (no shared prompts)
LORA = dict(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])


def fallback_system(system: str) -> str:
    tools = json.dumps([_build_tool_schema(run_sql)], indent=2)
    return f"{system}\n\n{DEFAULT_TOOLS_FALLBACK_PROMPT.format(tools=tools)}"


def to_rollout_form(messages: list[dict]) -> list[dict]:
    """Standard tool_calls trajectory -> the plain role/content text a Tiny Aya rollout has."""
    out = []
    for m in messages:
        if m["role"] == "system":
            out.append({"role": "system", "content": fallback_system(m["content"])})
        elif m.get("tool_calls"):
            calls = [{"tool_name": c["function"]["name"], "parameters": c["function"]["arguments"]}
                     for c in m["tool_calls"]]
            out.append({"role": "assistant", "content": json.dumps(calls)})
        else:
            out.append({k: m[k] for k in ("role", "content", "name") if k in m})
    return fold_tool_messages_into_user(out, DEFAULT_TOOL_RESULT_FORMAT)


def sft_examples(path: Path) -> list[dict]:
    """One prompt/completion pair per assistant turn: loss only on what the model must generate."""
    rows = []
    for line in open(path):
        conv = to_rollout_form(json.loads(line)["messages"])
        for i, m in enumerate(conv):
            if m["role"] == "assistant":
                rows.append({"prompt": conv[:i], "completion": [m]})
    return rows


def grpo_rows(items_path: Path) -> list[dict]:
    items = [json.loads(l) for l in open(items_path)]
    return [dataset_row(it) for it in items
            if it["split"] == "train" and it["dbs"][0].split("/")[-2] not in SFT_BASES]


def sft(a):
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    tok = AutoTokenizer.from_pretrained(MODEL)
    trainer = SFTTrainer(
        model=AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16),
        processing_class=tok, train_dataset=Dataset.from_list(sft_examples(a.data)),
        peft_config=LoraConfig(**LORA),
        args=SFTConfig(output_dir=str(a.out), num_train_epochs=a.epochs, learning_rate=1e-4,
                       per_device_train_batch_size=2, gradient_accumulation_steps=8,
                       gradient_checkpointing=True, bf16=True, max_length=4096,
                       logging_steps=5, save_strategy="no", report_to=[], seed=a.seed))
    trainer.train()
    trainer.save_model(str(a.out / "adapter"))
    merged = trainer.model.merge_and_unload()  # GRPO trains a fresh LoRA on the SFT-merged model
    merged.save_pretrained(str(a.out / "merged"))
    tok.save_pretrained(str(a.out / "merged"))


def grpo(a):
    from datasets import Dataset
    from peft import LoraConfig
    from agenttune import create_agentic_trainer

    rows = grpo_rows(a.items)
    print(f"{len(rows)} GRPO prompts, reward={a.reward}")
    trainer = create_agentic_trainer(
        "grpo", backend="trl", model=str(a.init), reward_funcs=[REWARDS[a.reward]],
        tools=[run_sql], train_dataset=Dataset.from_list(rows).shuffle(seed=a.seed),
        output_dir=str(a.out), peft_config=LoraConfig(**LORA),
        remove_unused_columns=False,  # rewards read dbs/gold/ordered (rewards._need fails loudly)
        max_steps=a.steps, num_generations=a.G, per_device_train_batch_size=a.G * a.prompts,
        gradient_accumulation_steps=1, learning_rate=1e-5, beta=0.02, temperature=1.0,
        max_completion_length=2048, max_steps_per_turn=4, gradient_checkpointing=True,
        bf16=True, logging_steps=1, save_steps=20, report_to=[], seed=a.seed,
        use_vllm=a.vllm, vllm_mode="colocate", vllm_gpu_memory_utilization=a.vllm_mem)
    trainer.train()


def render(a):
    ex = sft_examples(a.data)[1]
    for m in ex["prompt"] + ex["completion"]:
        print(f"--- {m['role']}\n{m['content'][-700:]}")
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(MODEL)
        print("=== template\n" + tok.apply_chat_template(ex["prompt"] + ex["completion"], tokenize=False)[-1500:])
    except Exception as e:  # gated tokenizer needs licence + HF token
        print(f"(tokenizer render skipped: {type(e).__name__}: {e})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sft", "grpo", "render"])
    ap.add_argument("--data", type=Path, default=Path("data/sft.jsonl"))
    ap.add_argument("--items", type=Path, default=Path("data/train/items.jsonl"))
    ap.add_argument("--init", type=Path, default=Path("runs/sft/merged"))
    ap.add_argument("--out", type=Path, default=Path("runs/out"))
    ap.add_argument("--reward", choices=sorted(REWARDS), default="R_cf_mean")
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--G", type=int, default=6)
    ap.add_argument("--prompts", type=int, default=4)
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-vllm", dest="vllm", action="store_false")
    ap.add_argument("--vllm-mem", type=float, default=0.45, help="colocated vLLM share of GPU memory (3.35B bf16 weights ~6.7 GB)")
    a = ap.parse_args()
    {"sft": sft, "grpo": grpo, "render": render}[a.cmd](a)
