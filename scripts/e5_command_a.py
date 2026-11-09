"""E5: Cohere Command A on the E4 test set, single-turn (schema + business definitions in the prompt,
no tool). Writes results/traj_command_a.jsonl in evaluate.py's trajectory format (score it with
`evaluate.py score`), plus per-call latency and billed tokens. Resumes: ids already written are skipped,
so a crash never spends trial quota twice.

  source .secrets.env && .venv-train/bin/python scripts/e5_command_a.py [--limit N]
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.agent import SYSTEM, user_message  # noqa: E402

MODEL = "command-a-03-2025"
TOOL_LINE = "Use the run_sql tool to explore the data and check your query before answering. "
assert TOOL_LINE in SYSTEM
SYS = SYSTEM.replace(TOOL_LINE, "You cannot run queries; answer from the schema and definitions. ")


def chat(key, user, temperature, retries=6):
    body = json.dumps({"model": MODEL, "temperature": temperature,
                       "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": user}]}).encode()
    for i in range(retries):
        req = urllib.request.Request("https://api.cohere.com/v2/chat", body, method="POST", headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"})
        t = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            return "".join(c.get("text", "") for c in d["message"]["content"]), time.time() - t, d.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or i == retries - 1:
                raise SystemExit(f"HTTP {e.code}: {e.read()[:300]!r}")
            time.sleep(15 * (i + 1))  # trial keys are rate-limited per minute


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=Path, default=ROOT / "data/test/items.jsonl")
    ap.add_argument("--out", type=Path, default=ROOT / "results/traj_command_a.jsonl")
    ap.add_argument("--temperature", type=float, default=0.7, help="same as E4")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--gap", type=float, default=3.2, help="seconds between calls (trial: ~20 calls/min)")
    a = ap.parse_args()
    key = os.environ.get("CO_API_KEY") or sys.exit("CO_API_KEY not set: source .secrets.env")
    items = [json.loads(l) for l in open(a.items)][: a.limit or None]
    done = {json.loads(l)["id"] for l in open(a.out)} if a.out.exists() else set()
    todo = [it for it in items if it["id"] not in done]
    print(f"{len(done)} done, {len(todo)} to go", flush=True)
    with open(a.out, "a") as f:
        for n, it in enumerate(todo, 1):
            text, lat, usage = chat(key, user_message(it), a.temperature)
            f.write(json.dumps({"model": "command_a", "id": it["id"], "sample": 0, "latency_s": round(lat, 3),
                                "billed": usage.get("billed_units", {}),
                                "messages": [{"role": "assistant", "content": text}]}) + "\n")
            f.flush()
            if n % 25 == 0:
                print(f"{n}/{len(todo)}", flush=True)
            time.sleep(a.gap)
