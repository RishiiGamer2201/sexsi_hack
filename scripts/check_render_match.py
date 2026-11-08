"""CPU check: the prompt text SFT trains on == the prompt text eval/GRPO rollouts feed the model.
For each assistant turn of a real SFT trajectory, compare TRL's SFT rendering
(tok.apply_chat_template(prompt, add_generation_prompt=True)) with evaluate.gen's rendering
(AgentTune _render_chat_template on the same conversation, as eval builds it).
  HF_HOME=.cache/hf PYTHONPATH=. .venv-train/bin/python scripts/check_render_match.py
"""
import difflib
import json

from agenttune.agentic.rollout_engines.rollout_factory import _build_tool_schema, _render_chat_template, fold_tool_messages_into_user
from transformers import AutoTokenizer

from sqlcf.agent import run_sql
from train import MODEL, fallback_system, sft_examples

tok = AutoTokenizer.from_pretrained(MODEL)
schema = [_build_tool_schema(run_sql)]
traj = json.loads(open("data/sft.jsonl").readline())["messages"]
# the conversation as evaluate.gen builds it: fallback system, user, assistant text, raw tool messages
conv = [{"role": "system", "content": fallback_system(traj[0]["content"])}, traj[1]]
for m in traj[2:]:
    if m.get("tool_calls"):
        conv.append({"role": "assistant", "content": json.dumps(
            [{"tool_name": c["function"]["name"], "parameters": c["function"]["arguments"]} for c in m["tool_calls"]])})
    elif m["role"] == "tool":
        conv.append({"role": "tool", "name": m["name"], "content": m["content"]})
    else:
        conv.append(m)
bad = 0
for n, ex in enumerate(sft_examples("data/sft.jsonl")[:3]):
    sft_txt = tok.apply_chat_template(ex["prompt"], tokenize=False, add_generation_prompt=True)
    upto = [i for i, m in enumerate(conv) if m["role"] == "assistant"][n]
    eval_txt = _render_chat_template(tok, fold_tool_messages_into_user(conv[:upto]), schema, tokenize=False)
    if sft_txt != eval_txt:
        bad += 1
        print(f"--- turn {n}: SFT {len(sft_txt)} chars vs eval {len(eval_txt)} chars")
        for d in difflib.unified_diff(sft_txt.splitlines(), eval_txt.splitlines(), "sft", "eval", n=1, lineterm=""):
            print(d[:200])
print("MISMATCH" if bad else "ok: SFT prompt text == eval prompt text for 3 turns")
