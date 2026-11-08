"""Agent interface shared by SFT, GRPO and eval: system prompt, the one tool, dataset rows.

The agent sees only the ORIGINAL database of an item (by id, e.g. "S_s101"); counterfactual
DBs are reachable only by the reward. Tool output is truncated (20 rows / 1500 chars).
"""
import os
import re
from pathlib import Path

from .compare import SQLError, run
from .db import GLOSSARY, SCHEMA

DATA = Path(os.environ.get("SQLCF_DATA", Path(__file__).resolve().parent.parent / "data"))
MAX_ROWS, MAX_CHARS = 20, 1500
_DB_ID = re.compile(r"^[SML]_s\d+$")

SYSTEM = f"""You are a careful data analyst working with a retail SQLite database.

Schema:
{SCHEMA.strip()}

Business definitions:
{GLOSSARY}

Use the run_sql tool to explore the data and check your query before answering. Watch for
duplicate rows, joins that multiply rows, missing business filters and superseded records.
When you are done, reply with one short sentence and your final query in a ```sql block.
The final query must compute the answer from the tables; do not hard-code values."""


def db_path(database: str) -> Path:
    if not _DB_ID.match(database or ""):
        raise ValueError(f"unknown database id {database!r}")
    hits = sorted(DATA.glob(f"*/dbs/{database}/base.db"))
    if not hits:
        raise ValueError(f"unknown database id {database!r}")
    return hits[0]


def format_rows(rows: list[tuple]) -> str:
    head = "\n".join(" | ".join("NULL" if v is None else str(v) for v in r) for r in rows[:MAX_ROWS])
    more = f"\n... ({len(rows)} rows total)" if len(rows) > MAX_ROWS else f"\n({len(rows)} rows)"
    text = head + more
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS] + "\n... (truncated)"


def run_sql(database: str, sql_command: str) -> str:
    """Run one read-only SQLite query on a retail database.

    Args:
        database: the database id given in the question, for example "S_s101".
        sql_command: a single SELECT statement.

    Returns:
        Up to 20 result rows as text, or an error message.
    """
    try:
        return format_rows(run(str(db_path(database)), sql_command))
    except (SQLError, ValueError) as e:
        return f"ERROR: {e}"


def user_message(item: dict) -> str:
    return f"Database: {item['dbs'][0].split('/')[-2]}\nQuestion: {item['question']}"


def dataset_row(item: dict) -> dict:
    """One GRPO/eval row: prompt + the columns the rewards read."""
    return {"prompt": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_message(item)}],
            "dbs": item["dbs"], "gold": item["gold"], "ordered": item["ordered"],
            "id": item["id"], "family": item["family"]}
