"""D1/D2: distil Command A into Tiny Aya, with the counterfactual copies as the data filter.

The teacher (Command A, single-turn, plan + SQL, T=0.3) answers the same 353 train items that `sft_ho` learned from
(data/sft.jsonl). D1 grades each answer on the item's original DB and its train counterfactual copies: a single-DB
filter keeps every answer that is right on the original, the counterfactual filter only the verified ones; the gap
is lucky teacher answers that would leak into distillation data. D2 rebuilds data/sft.jsonl's trajectories
(same items, same check queries, same seed) with the teacher's verified SQL and its plan in the final turn.

  python scripts/distil.py items                     # -> runs/distil/items.jsonl (the 353 sft_ho items)
  source .secrets.env && python scripts/e5_command_a.py --items runs/distil/items.jsonl \
      --out results/teacher_command_a.jsonl --plan --temperature 0.3
  python scripts/distil.py score                     # D1 -> results/d1_teacher_filter.json
  python scripts/distil.py build                     # D2 data -> data/sft_distil.jsonl
  D3, int4 local teacher (scripts/teacher_local.py): same commands with --teacher <file> --tag int4
  -> results/d1_teacher_filter_int4.json, data/sft_distil_int4.jsonl
  D4, logit distillation: build --raw-final keeps the teacher's exact text as the final turn (its saved log-probs
  are for that text) -> data/sft_distil_int4_raw.jsonl, rows marked "teacher_final"; scripts/logit_distil.py trains on it
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluate import grade  # noqa: E402
from sqlcf.agent import run_sql  # noqa: E402
from sqlcf.audit import wilson  # noqa: E402
from sqlcf.build_sft import CHECKS, GRPO_ONLY, trajectory  # noqa: E402
from sqlcf.rewards import final_sql  # noqa: E402

ITEMS = ROOT / "data/train/items.jsonl"
SFT = ROOT / "data/sft.jsonl"
SUB = ROOT / "runs/distil/items.jsonl"
TEACHER = ROOT / "results/teacher_command_a.jsonl"  # not traj_*: those are test trajectories (verify_all)
TAG = ""
RAW = False
BASES = ["S_s101", "S_s102", "S_s103"]  # build_sft defaults


def sft_items():
    """The train items behind data/sft.jsonl, in build_sft's order (its rng depends on the order)."""
    items = [json.loads(l) for l in open(ITEMS)]
    keep = [it for it in items if it["family"] in CHECKS and it["dbs"][0].split("/")[-2] in BASES
            and it["template"] not in GRPO_ONLY]
    assert [it["id"] for it in keep] == [json.loads(l)["id"] for l in open(SFT)], "build_sft selection changed"
    return keep


def teacher():
    return {r["id"]: r["messages"][-1]["content"] for r in map(json.loads, open(TEACHER))}


def tagged(path: Path) -> Path:
    return path.with_name(f"{path.stem}_{TAG}{path.suffix}") if TAG else path


def score():
    items, t = sft_items(), teacher()
    g = {it["id"]: grade(it, [{"role": "assistant", "content": t[it["id"]]}]) for it in items if it["id"] in t}
    n = len(g)
    single = [i for i, x in g.items() if x["single"]]
    verified = [i for i, x in g.items() if x["verified"]]
    fam = {}
    for it in items:
        if it["id"] in g:
            f = fam.setdefault(it["family"], [0, 0, 0])
            f[0] += 1
            f[1] += g[it["id"]]["single"]
            f[2] += g[it["id"]]["verified"]
    res = {"what": "D1: Command A teacher answers (plan + SQL, T=0.3) on the 353 sft_ho train items, graded on the "
                   "original train DB and its train counterfactual copies",
           "teacher": str(TEACHER.relative_to(ROOT)) if TEACHER.is_relative_to(ROOT) else str(TEACHER),
           "n": n, "has_sql": wilson(sum(x["has_sql"] for x in g.values()), n),
           "kept_by_single_db_filter": wilson(len(single), n), "kept_by_counterfactual_filter": wilson(len(verified), n),
           "lucky_kept_only_by_single_db": len(single) - len(verified),
           "lucky_share_of_single_db_kept": (len(single) - len(verified)) / len(single) if single else None,
           "smuggled": sum(x["smuggled"] for x in g.values()),
           "by_family_n_single_verified": fam,
           "lucky_ids": sorted(set(single) - set(verified))}
    out = tagged(ROOT / "results/d1_teacher_filter.json")
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "lucky_ids"}, indent=1))


def build():
    items, t = sft_items(), teacher()
    rng = random.Random(0)  # build_sft.main's seed: same check queries as data/sft.jsonl
    rows, n_teacher = [], 0
    for it in items:
        msgs = trajectory(it, rng)  # consumes rng exactly as build_sft did
        text = t.get(it["id"])
        # counterfactual filter: verified teacher answers replace the gold ending; the rest keep sft_ho's
        # trajectory, so D2 has the same 353 rows as sft_ho and differs only in the teacher's plan + SQL
        if text and grade(it, [{"role": "assistant", "content": text}])["verified"]:
            sql = final_sql([{"role": "assistant", "content": text}])
            plan = text.split("```")[0].strip()
            db = it["dbs"][0].split("/")[-2]
            msgs[-3]["tool_calls"][0]["function"]["arguments"]["sql_command"] = sql
            msgs[-2]["content"] = run_sql(db, sql)
            msgs[-1]["content"] = text if RAW else f"{plan}\n```sql\n{sql}\n```"
            n_teacher += 1
            rows.append({"id": it["id"], "messages": msgs} | ({"teacher_final": True} if RAW else {}))
            continue
        rows.append({"id": it["id"], "messages": msgs})
    assert [r["id"] for r in rows] == [json.loads(l)["id"] for l in open(SFT)]
    out = tagged(ROOT / "data/sft_distil.jsonl")
    out = out.with_name(out.stem + "_raw.jsonl") if RAW else out
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"{n_teacher} of {len(items)} trajectories end with the teacher's verified plan + SQL -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("cmd", nargs="?", default="")
    ap.add_argument("--teacher", type=Path, default=TEACHER)
    ap.add_argument("--tag", default="", help="suffix for the output files, e.g. int4")
    ap.add_argument("--raw-final", action="store_true", help="build: the teacher's exact text as the final turn (D4)")
    a = ap.parse_args()
    cmd, TEACHER, TAG, RAW = a.cmd, a.teacher, a.tag, a.raw_final
    if cmd == "items":
        SUB.parent.mkdir(parents=True, exist_ok=True)
        SUB.write_text("".join(json.dumps(it) + "\n" for it in sft_items()))
        print(f"{len(sft_items())} items -> {SUB}")
    elif cmd in ("score", "build"):
        {"score": score, "build": build}[cmd]()
    else:
        sys.exit(__doc__)
