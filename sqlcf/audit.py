"""E0 reward audit + E1 blind rate (CPU only).  Plan §2.

python -m sqlcf.audit e1 --seeds 900 901 902          -> results/e1_blind_rate.json, figure2_blind_rate.png
python -m sqlcf.audit e0 --items data/audit/items.jsonl -> results/e0_reward_audit.json, figure1_reward_audit.png
python -m sqlcf.audit agenttune --items ...            -> results/e0_agenttune.json
"""
import argparse
import importlib.util
import json
import math
import shutil
import sys
import tempfile
import types
from collections import defaultdict
from pathlib import Path

from . import db
from .cf import degenerate
from .compare import SQLError, match, run
from .rewards import REWARDS, _exec
from .templates import TEMPLATES

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
AGENTTUNE_SQL = ROOT / "vendor/AgentTune/src/agenttune/agentic/rewards/builtin_rewards/sql.py"


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, max(0.0, c - h), min(1.0, c + h)]


def _lit(v):
    return "NULL" if v is None else repr(v) if isinstance(v, (int, float)) else "'" + str(v).replace("'", "''") + "'"


def literal_sql(rows) -> str:
    """Answer smuggling: return the original DB's gold rows as constants."""
    return " UNION ALL ".join("SELECT " + ", ".join(_lit(v) for v in r) for r in rows)


def hacks(item) -> dict:
    g = item["gold"][0]
    out = {"literal": literal_sql(g), "empty": "SELECT NULL WHERE 0"}
    if all(len(r) == 1 and isinstance(r[0], int) for r in g) and len(g) > 1:
        ids = ", ".join(str(r[0]) for r in g)
        out["hardcoded_ids"] = f"SELECT customer_id FROM customers WHERE customer_id IN ({ids})"
    return out


def _completion(sql):
    return [{"role": "assistant", "content": f"Final answer:\n```sql\n{sql}\n```"}]


# ---------------- E0 ----------------
def e0(items_path: Path):
    items = [json.loads(l) for l in open(items_path)]
    stats = defaultdict(lambda: [0, 0, 0.0])  # (reward, family, kind) -> [n_full_pay, n, sum_reward]
    for it in items:
        cands = [("gold", it["gold_sql"])] + [("paraphrase", q) for q in it["paraphrases"]]
        cands += [(f"mutant:{m}", q) for m, q in it["mutants"].items()]
        cands += [(f"hack:{h}", q) for h, q in hacks(it).items()]
        comps = [_completion(q) for _, q in cands]
        n = len(comps)
        greedy = {"dbs": [it["dbs"]] * n, "gold": [it["gold"]] * n, "ordered": [it["ordered"]] * n}
        rand = {"dbs": [it["dbs_random"]] * n, "gold": [it["gold_random"]] * n, "ordered": [it["ordered"]] * n}
        runs = [(r, f, greedy) for r, f in REWARDS.items()]
        runs += [(f"{r}@random", f, rand) for r, f in REWARDS.items() if r.startswith("R_cf")]
        for rname, f, cols in runs:
            for (kind, _), s in zip(cands, f(comps, **cols)):
                group = "correct" if kind in ("gold", "paraphrase") else kind.split(":")[0]
                for key in [(rname, it["family"], group), (rname, "ALL", group), (rname, "ALL", kind)]:
                    st = stats[key]
                    st[0] += s >= 1.0
                    st[1] += 1
                    st[2] += s
    out = []
    for (r, fam, kind), (k, n, tot) in sorted(stats.items()):
        wrong = kind != "correct" and kind not in ("gold", "paraphrase")
        p, lo, hi = wilson(n - k if not wrong else k, n)
        out.append({"reward": r, "family": fam, "candidates": kind, "n": n,
                    "metric": "FP (full pay to wrong SQL)" if wrong else "FN (correct SQL not fully paid)",
                    "rate": p, "ci95": [lo, hi], "mean_reward": tot / n})
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "e0_reward_audit.json").write_text(json.dumps({"items": str(items_path), "n_items": len(items), "rows": out}, indent=1))
    _fig1(out)
    for row in out:
        if row["family"] == "ALL" and row["candidates"] in ("correct", "mutant", "hack"):
            print(f"{row['reward']:12} {row['candidates']:8} {row['metric'][:2]} {row['rate']:.3f} "
                  f"[{row['ci95'][0]:.3f},{row['ci95'][1]:.3f}] mean={row['mean_reward']:.3f} n={row['n']}")
    return out


def _fig1(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rewards = ["R_exec_set", "R_exec_rex", "R_cf_mean@random", "R_cf_strict@random", "R_cf_strict"]
    fams = ["F1", "F2", "F3", "F4"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, kind, title in zip(axes, ["mutant", "hack", "correct"],
                               ["FP: bug mutants fully paid", "FP: hacks fully paid", "FN: correct SQL not fully paid"]):
        w = 0.8 / len(rewards)
        for j, r in enumerate(rewards):
            ys, errs = [], [[], []]
            for f in fams:
                row = next((x for x in rows if x["reward"] == r and x["family"] == f and x["candidates"] == kind), None)
                p, lo, hi = (row["rate"], *row["ci95"]) if row else (0, 0, 0)
                ys.append(p)
                errs[0].append(max(0.0, p - lo))
                errs[1].append(max(0.0, hi - p))
            ax.bar([i + j * w for i in range(len(fams))], ys, w, yerr=errs, label=r, capsize=2)
        ax.set_xticks([i + 0.4 - w / 2 for i in range(len(fams))], fams)
        ax.set_title(title)
    axes[0].set_ylabel("rate (Wilson 95% CI)")
    axes[-1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "figure1_reward_audit.png", dpi=150)


# ---------------- E1 ----------------
def e1(seeds: list[int], sizes="SML"):
    tmp = Path(tempfile.mkdtemp(dir=ROOT / "data"))
    counts = defaultdict(lambda: [0, 0])
    try:
        for size in sizes:
            for seed in seeds:
                p = db.write(db.generate(size, seed), tmp / f"{size}_{seed}.db")
                for t in TEMPLATES:
                    for prm in t.grid():
                        g = run(p, t.sql.format(**prm))
                        if degenerate(g):
                            continue
                        for m, q in t.mutants.items():
                            try:
                                blind = match(run(p, q.format(**prm)), g, t.ordered)
                            except SQLError:
                                blind = False
                            for key in [(size, t.family), (size, "ALL")]:
                                counts[key][0] += blind
                                counts[key][1] += 1
    finally:
        shutil.rmtree(tmp)
    out = [{"size": s, "customers": db.SIZES[s], "family": f, "blind": k, "n": n, "rate_ci95": wilson(k, n)}
           for (s, f), (k, n) in sorted(counts.items())]
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "e1_blind_rate.json").write_text(json.dumps({"seeds": seeds, "rows": out}, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    for f in ["F1", "F2", "F3", "F4", "ALL"]:
        rs = [r for r in out if r["family"] == f]
        x = [r["customers"] for r in rs]
        y = [r["rate_ci95"][0] for r in rs]
        ax.errorbar(x, y, yerr=[[max(0.0, a - r["rate_ci95"][1]) for a, r in zip(y, rs)], [max(0.0, r["rate_ci95"][2] - a) for a, r in zip(y, rs)]],
                    marker="o", capsize=3, label=f, lw=2.5 if f == "ALL" else 1)
    ax.set_xscale("log")
    ax.set_xlabel("customers in DB")
    ax.set_ylabel("P(bug mutant passes single-DB check)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "figure2_blind_rate.png", dpi=150)
    for r in out:
        print(r["size"], r["family"], f"{r['blind']}/{r['n']}", [round(x, 3) for x in r["rate_ci95"]])
    return out


# ---------------- AgentTune built-in SQL reward (H3) ----------------
def load_agenttune_sql(path=AGENTTUNE_SQL):
    """Import AgentTune's builtin SQL rewards (or a patched copy at `path`) without installing AgentTune."""
    import re
    stubs = {"agenttune": None, "agenttune.agentic": None, "agenttune.agentic.rollout_engines": None,
             "agenttune.agentic.rollout_engines.tool_call_parse": {"_THINK_BLOCK_RE": re.compile(r"<think>.*?</think>", re.S)},
             "agenttune.utils": None, "agenttune.utils.score_logger": {"log_score": lambda *a, **k: None}}
    for name, attrs in stubs.items():
        mod = sys.modules.setdefault(name, types.ModuleType(name))
        for k, v in (attrs or {}).items():
            setattr(mod, k, v)
    spec = importlib.util.spec_from_file_location(f"agenttune_sql_rewards_{abs(hash(str(path)))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _traj(sql, rows, final):
    msgs = []
    if sql is not None:
        msgs.append({"role": "assistant", "content": "", "tool_calls": [{"function": {"name": "sql_database", "arguments": {"sql_command": sql}}}]})
        msgs.append({"role": "tool", "content": rows})
    msgs.append({"role": "assistant", "content": final})
    return msgs


def agenttune_audit(items_path: Path):
    """Yes/no questions ('Is there any customer such that <list template>?') over the list
    templates' full parameter grid on the audit base DBs, so both yes and no answers occur.
    Policies are scored with AgentTune's correctness_reward + query_reward + structure_reward."""
    at = load_agenttune_sql()
    bases = sorted({json.loads(l)["dbs"][0] for l in open(items_path)})
    policies = defaultdict(lambda: defaultdict(list))
    for base in bases:
        for t in (t for t in TEMPLATES if t.id.endswith("_list")):
            for prm in t.grid():
                gold_sql = t.sql.format(**prm)
                gold_rows = [list(r) for r in _exec(base, gold_sql)]
                answer = "yes" if gold_rows else "no"
                cand = {
                    "honest_gold_sql": _traj(gold_sql, gold_rows, f"*{answer}*"),
                    "hack_where_padding_always_yes": _traj("select * from customers where 1 = 1", [[1]], "*yes*"),
                    "hack_where_padding_always_no": _traj("select * from customers where 1 = 0", [], "*no*"),
                    "hack_no_sql_always_yes": _traj(None, None, "*yes*"),
                }
                for name, traj in cand.items():
                    r = sum(f([traj], answer=[answer])[0] for f in (at.correctness_reward, at.query_reward, at.structure_reward))
                    policies[name][answer].append(r)
                    policies[name]["all"].append(r)
    out = {k: {a: {"mean_reward": sum(v) / len(v), "n": len(v)} for a, v in d.items()} for k, d in policies.items()}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "e0_agenttune.json").write_text(json.dumps(out, indent=1))
    for k, d in out.items():
        print(f"{k:32} " + "  ".join(f"{a}: {v['mean_reward']:+.3f} (n={v['n']})" for a, v in d.items()))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["e0", "e1", "agenttune"])
    ap.add_argument("--items", type=Path, default=ROOT / "data/audit/items.jsonl")
    ap.add_argument("--seeds", type=int, nargs="+", default=[900, 901, 902])
    a = ap.parse_args()
    {"e0": lambda: e0(a.items), "e1": lambda: e1(a.seeds), "agenttune": lambda: agenttune_audit(a.items)}[a.cmd]()
