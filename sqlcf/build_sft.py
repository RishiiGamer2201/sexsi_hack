"""E2 oracle SFT trajectories from train items (standard chat messages with tool_calls).

Trajectory: one family-appropriate check query -> the final query -> short answer + ```sql.
Final query is the gold or a validated paraphrase (variety). Rendering to Tiny Aya's text
format happens at train time with AgentTune's own chat-template code, so SFT text matches
what GRPO rollouts produce.

python -m sqlcf.build_sft --items data/train/items.jsonl --out data/sft.jsonl  (bases S_s101-103)
"""
import argparse
import json
import random
from pathlib import Path

from .agent import SYSTEM, run_sql, user_message

CHECKS = {
    "F1": ["SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id HAVING n > 1 LIMIT 5",
           "SELECT order_id, product_id, COUNT(*) FROM order_items GROUP BY order_id, product_id HAVING COUNT(*) > 1 LIMIT 5"],
    "F2": ["SELECT order_id, COUNT(*) AS n FROM payments GROUP BY order_id HAVING n > 1 LIMIT 5",
           "SELECT order_id, COUNT(*) AS lines FROM order_items GROUP BY order_id HAVING lines > 1 LIMIT 5"],
    "F3": ["SELECT status, COUNT(*) FROM orders GROUP BY status",
           "SELECT COUNT(*) AS refunds, SUM(amount) FROM refunds"],
}


def _call(i, db, sql):
    return {"role": "assistant", "content": "",
            "tool_calls": [{"id": f"call_{i}", "type": "function",
                            "function": {"name": "run_sql", "arguments": {"database": db, "sql_command": sql}}}]}


def trajectory(item: dict, rng: random.Random) -> list[dict]:
    db = item["dbs"][0].split("/")[-2]
    final = rng.choice([item["gold_sql"]] * 2 + item["paraphrases"])
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_message(item)}]
    for i, sql in enumerate([rng.choice(CHECKS[item["family"]]), final]):
        msgs.append(_call(i, db, sql))
        msgs.append({"role": "tool", "name": "run_sql", "tool_call_id": f"call_{i}", "content": run_sql(db, sql)})
    msgs.append({"role": "assistant", "content": f"Here is the query that answers the question.\n```sql\n{final}\n```"})
    return msgs


# GRPO-only train templates (Nov 9): a template SFT has seen is solved deterministically (0 rollouts where R_exec
# and R_cf disagree), so B and C would train identically. Unseen compositions draw silent errors, as on test.
GRPO_ONLY = ("F1_paying_customers", "F2_refunded_category", "F3_net_revenue")


def main(items_path: Path, out: Path, bases: list[str], seed: int = 0, exclude=GRPO_ONLY):
    """bases: base-DB ids reserved for SFT; GRPO uses the other bases (no shared prompts).
    exclude: templates kept out of SFT entirely (GRPO still trains on them)."""
    rng = random.Random(seed)
    items = [json.loads(l) for l in open(items_path)]
    rows = [{"id": it["id"], "messages": trajectory(it, rng)} for it in items
            if it["family"] in CHECKS and it["dbs"][0].split("/")[-2] in bases and it["template"] not in exclude]
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"{len(rows)} SFT trajectories -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--bases", nargs="+", default=["S_s101", "S_s102", "S_s103"])
    ap.add_argument("--exclude", nargs="*", default=list(GRPO_ONLY), help="templates kept out of SFT (GRPO-only)")
    a = ap.parse_args()
    main(a.items, a.out, a.bases, exclude=a.exclude)
