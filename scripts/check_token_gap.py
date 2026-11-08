"""CPU check: does AgentTune's multi-turn completion_ids match what vLLM actually conditioned on?
AgentTune builds  prompt_ids(turn0) + gen_0 + raw_tool_text + gen_1 ...  but each turn is generated
from the full chat-template rendering. Print where the two token streams diverge.
  HF_HOME=.cache/hf .venv-train/bin/python scripts/check_token_gap.py
"""
import json

from agenttune.agentic.rollout_engines.rollout_factory import (
    DEFAULT_TOOL_RESULT_FORMAT, _render_chat_template, fold_tool_messages_into_user)
from transformers import AutoTokenizer

from train import MODEL, to_rollout_form

tok = AutoTokenizer.from_pretrained(MODEL)
msgs = json.loads(open("data/sft.jsonl").readline())["messages"]
conv = to_rollout_form(msgs)  # system, user, assistant(call), user(folded tool), assistant, ...
asst = [i for i, m in enumerate(conv) if m["role"] == "assistant"]


def ids(c, gen_prompt=True):
    out = _render_chat_template(tok, c, [], tokenize=True, return_tensors=None)
    return list(out["input_ids"] if hasattr(out, "keys") else out)


p0 = ids(conv[:asst[0]])
agent = list(p0)  # AgentTune's stream
for k, i in enumerate(asst):
    gen = tok.encode(conv[i]["content"], add_special_tokens=False) + [tok.convert_tokens_to_ids("<|END_RESPONSE|>")]
    real_prompt = ids(conv[:i])
    n = next((j for j, (a, b) in enumerate(zip(agent, real_prompt)) if a != b), min(len(agent), len(real_prompt)))
    print(f"turn {k}: real prompt {len(real_prompt)} tok, AgentTune stream {len(agent)} tok, agree on first {n}")
    if n < len(real_prompt):
        print("   real  :", repr(tok.decode(real_prompt[n:n + 40])))
        print("   agent :", repr(tok.decode(agent[n:n + 40])))
    agent += gen
    if i + 1 < len(conv) and conv[i + 1]["role"] == "user":  # folded tool result: AgentTune appends raw tool text
        raw = conv[i + 1]["content"]
        agent += tok.encode(raw, add_special_tokens=False)
