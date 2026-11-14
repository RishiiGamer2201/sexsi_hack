"""Phase 1 of D3: is the int4 Command A as accurate as the API one on our test set? (CPU, seconds)

Grades both single-sample test runs (same 331 items, same prompt, T=0.7) on the test original and its 4 hidden
copies, then compares them per item: verified and single-DB accuracy with Wilson 95% CIs, the paired difference
(exact McNemar on verified), lucky passes (single but not verified), per bug family, and how often each model
adds a status != 'cancelled' filter (the habit that sank D2).

  python scripts/int4_accuracy.py      # -> results/e5_int4_accuracy.json + a table
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluate import grade, mcnemar_exact  # noqa: E402
from sqlcf.audit import wilson  # noqa: E402
from sqlcf.rewards import final_sql  # noqa: E402


def load(path):
    return {r["id"]: r["messages"] for r in map(json.loads, open(path)) if r.get("sample", 0) == 0}


def main(a):
    items = {it["id"]: it for it in map(json.loads, open(a.items))}
    runs = {"api": load(a.api), "int4": load(a.int4)}
    ids = [i for i in items if all(i in r for r in runs.values())]
    missing = {k: len(items) - len([i for i in items if i in r]) for k, r in runs.items()}
    g = {k: {i: grade(items[i], r[i]) for i in ids} for k, r in runs.items()}
    n = len(ids)
    out = {"n_items": n, "missing": missing, "models": {}, "by_family": {}}
    for k in runs:
        x = g[k]
        out["models"][k] = {
            "verified": wilson(sum(v["verified"] for v in x.values()), n),
            "single": wilson(sum(v["single"] for v in x.values()), n),
            "lucky": sum(v["single"] and not v["verified"] for v in x.values()),
            "has_sql": wilson(sum(v["has_sql"] for v in x.values()), n),
            "cancel_filter": sum("cancel" in (final_sql(runs[k][i]) or "").lower() for i in ids)}
    b = sum(g["api"][i]["verified"] and not g["int4"][i]["verified"] for i in ids)  # API right, int4 wrong
    c = sum(g["int4"][i]["verified"] and not g["api"][i]["verified"] for i in ids)
    diff = out["models"]["int4"]["verified"][0] - out["models"]["api"]["verified"][0]
    out["paired"] = {"api_only": b, "int4_only": c, "verified_diff": diff, "mcnemar_p": mcnemar_exact(b, c)}
    for fam in sorted({items[i]["family"] for i in ids}):
        f = [i for i in ids if items[i]["family"] == fam]
        out["by_family"][fam] = {k: wilson(sum(g[k][i]["verified"] for i in f), len(f)) for k in runs} | {"n": len(f)}
    a.out.write_text(json.dumps(out, indent=1))

    m = out["models"]
    pct = lambda w: f"{100 * w[0]:5.1f}% [{100 * w[1]:4.1f}, {100 * w[2]:4.1f}]"
    print(f"test items graded: {n}   missing answers: {missing}")
    print(f"{'':16} {'API (bf16)':>22} {'int4 AWQ':>22}")
    for k in ("verified", "single", "has_sql"):
        print(f"{k:16} {pct(m['api'][k]):>22} {pct(m['int4'][k]):>22}")
    for k in ("lucky", "cancel_filter"):
        print(f"{k:16} {m['api'][k]:>22} {m['int4'][k]:>22}")
    for fam, v in out["by_family"].items():
        print(f"  {fam} verified (n={v['n']:3}) {pct(v['api']):>18} {pct(v['int4']):>22}")
    p = out["paired"]
    print(f"paired: int4 - API = {100 * diff:+.1f} pts; API-only right {b}, int4-only right {c}; McNemar p = {p['mcnemar_p']:.3f}")
    print("reading: p >= 0.05 and |diff| <= ~3 pts -> no measurable loss from int4 on this test set "
          "(n=331 cannot resolve smaller gaps)" if p["mcnemar_p"] >= 0.05 else
          "reading: the gap is statistically real; look at the families above before using int4 as the teacher")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=Path, default=ROOT / "data/test/items.jsonl")
    ap.add_argument("--api", type=Path, default=ROOT / "results/traj_command_a.jsonl")
    ap.add_argument("--int4", type=Path, default=ROOT / "results/traj_command_a_int4.jsonl")
    ap.add_argument("--out", type=Path, default=ROOT / "results/e5_int4_accuracy.json")
    main(ap.parse_args())
