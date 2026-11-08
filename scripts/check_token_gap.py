"""CPU check of the AgentTune multi-turn patch (patches/agenttune-multiturn-ids.patch):
_rerender_stream must give prompt_ids == the turn-0 prompt and loss-mask spans that decode to
exactly the assistant turns, on real SFT trajectories in rollout form.
  HF_HOME=.cache/hf PYTHONPATH=. .venv-train/bin/python scripts/check_token_gap.py
"""
import json

from agenttune.agentic.rollout_engines.rollout_factory import DEFAULT_TOOL_RESULT_FORMAT, _rerender_stream
from transformers import AutoTokenizer

from train import MODEL, to_rollout_form

tok = AutoTokenizer.from_pretrained(MODEL)
for n, line in enumerate(open("data/sft.jsonl")):
    if n == 20:
        break
    conv = to_rollout_form(json.loads(line)["messages"])
    p0, ids, mask = _rerender_stream(tok, conv, [], False, DEFAULT_TOOL_RESULT_FORMAT)
    spans, cur = [], []
    for t, m in zip(ids, mask):
        if m:
            cur.append(t)
        elif cur:
            spans.append(cur); cur = []
    spans += [cur] if cur else []
    want = [m["content"] for m in conv if m["role"] == "assistant"]
    got = [tok.decode(s) for s in spans]
    assert len(got) == len(want), (n, len(got), len(want))
    for g, w in zip(got, want):
        assert g.startswith(w) and g[len(w):] in ("<|END_RESPONSE|><|END_OF_TURN_TOKEN|>", "<|END_RESPONSE|>"), (n, g[-80:], w[-80:])
    assert tok.decode(p0).count("<BOS_TOKEN>") == 1
if n == 0:
    raise SystemExit("no data")
print(f"ok: {n} trajectories, e.g. {len(p0)} prompt + {len(ids)} completion tokens, {sum(mask)} trained; span end {got[-1][-40:]!r}")
