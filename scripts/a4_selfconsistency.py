"""A4: gold-free answer selection and a "shaky answer" flag from the stored test samples (CPU only).

For each test item and model we have 8 sampled trajectories. Each final SQL is executed on the original DB and the
4 counterfactual copies; its *result vector* is the tuple of (canonicalised) results on the 5 DBs. No gold is used
to select or to flag; gold is used only to score.

Selection rules (verified accuracy of the one answer delivered per item):
  first        sample 0
  vote_single  largest cluster of samples by result on the original DB   (classic execution self-consistency)
  vote_multi   largest cluster by result vector across all 5 DBs
  oracle       any of the 8 samples verified (pass@8, upper bound)
Flag: agreement share of the delivered (first) answer = fraction of the item's samples with the same result
(single-DB or multi-DB). Flag "shaky" if share < 0.5; report precision / recall for wrong answers and AUROC.

Caveat: our copies are generated per item from the template's bug families (which know the gold query), so this
is an analysis of the signal, not yet a deployable verifier; a deployable one needs copies built from the schema.

  .venv/bin/python scripts/a4_selfconsistency.py [--models sft_ho B C base]  ->  results/a4_selfconsistency.json
"""
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sqlcf.rewards import _exec, checks, final_sql  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--models", nargs="+", default=["base", "sft_ho", "B", "C"])
a = ap.parse_args()

items = {json.loads(line)["id"]: json.loads(line) for line in open(ROOT / "data/test/items.jsonl")}


def canon(res, ordered):
    if res is None:
        return None
    return tuple(res) if ordered else tuple(sorted(res, key=repr))


def auroc(scores, labels):  # P(score of a correct answer > score of a wrong one); ties count 1/2
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def boot_diff(x, y, n=2000, seed=0):  # paired bootstrap over items of mean(x - y)
    rng = random.Random(seed)
    d = [xi - yi for xi, yi in zip(x, y)]
    means = sorted(sum(d[rng.randrange(len(d))] for _ in d) / len(d) for _ in range(n))
    return [sum(d) / len(d), means[int(0.025 * n)], means[int(0.975 * n) - 1]]


def vote(samples, key):
    """Largest cluster among samples with a result (ties: earliest sample); None if no sample ran."""
    ran = [s for s in samples if key(s) is not None]
    if not ran:
        return samples[0]
    counts = Counter(key(s) for s in ran)
    best = max(counts.values())
    return next(s for s in ran if counts[key(s)] == best)


out = {}
for m in a.models:
    by_item = defaultdict(list)
    for line in open(ROOT / f"results/traj_{m}.jsonl"):
        r = json.loads(line)
        by_item[r["id"]].append(r)
    rules = defaultdict(list)
    flag = {"single": [], "multi": []}
    labels = []
    for iid, rs in by_item.items():
        it = items[iid]
        rs.sort(key=lambda r: r["sample"])
        samples = []
        for r in rs:
            sql = final_sql(r["messages"])
            vec = tuple(canon(_exec(d, sql), it["ordered"]) if sql else None for d in it["dbs"])
            ok = all(checks(sql, it["dbs"], it["gold"], it["ordered"])) if sql else False
            samples.append({"vec": vec, "single": vec[0], "multi": vec if vec[0] is not None else None, "ok": ok})
        rules["first"].append(samples[0]["ok"])
        rules["vote_single"].append(vote(samples, lambda s: s["single"])["ok"])
        rules["vote_multi"].append(vote(samples, lambda s: s["multi"])["ok"])
        rules["oracle"].append(any(s["ok"] for s in samples))
        d = samples[0]
        labels.append(d["ok"])
        for kind in ("single", "multi"):
            share = 0.0 if d[kind] is None else sum(s[kind] == d[kind] for s in samples) / len(samples)
            flag[kind].append(share)
    n = len(labels)
    res = {"items": n, "samples_per_item": len(next(iter(by_item.values())))}
    res["selection_verified"] = {k: sum(v) / n for k, v in rules.items()}
    res["vote_multi_minus_first_ci95"] = boot_diff(rules["vote_multi"], rules["first"])
    res["vote_multi_minus_vote_single_ci95"] = boot_diff(rules["vote_multi"], rules["vote_single"])
    res["flag"] = {}
    wrong = [not y for y in labels]
    for kind, shares in flag.items():
        flagged = [s < 0.5 for s in shares]
        tp = sum(f and w for f, w in zip(flagged, wrong))
        res["flag"][kind] = {"flag_rate": sum(flagged) / n,
                             "precision_wrong": tp / max(1, sum(flagged)),
                             "recall_wrong": tp / max(1, sum(wrong)),
                             "verified_if_unflagged": sum(y for f, y in zip(flagged, labels) if not f) / max(1, n - sum(flagged)),
                             "auroc_share_vs_correct": auroc(shares, labels)}
    out[m] = res
    s = res["selection_verified"]
    print(f"{m:7} first {s['first']:.3f}  vote_single {s['vote_single']:.3f}  vote_multi {s['vote_multi']:.3f}  "
          f"oracle {s['oracle']:.3f}  multi-first {res['vote_multi_minus_first_ci95'][0]:+.3f} "
          f"[{res['vote_multi_minus_first_ci95'][1]:+.3f}, {res['vote_multi_minus_first_ci95'][2]:+.3f}]")
    for kind, f in res["flag"].items():
        print(f"        flag[{kind:6}] rate {f['flag_rate']:.2f} precision(wrong) {f['precision_wrong']:.2f} "
              f"recall(wrong) {f['recall_wrong']:.2f} verified-if-unflagged {f['verified_if_unflagged']:.3f} "
              f"AUROC {f['auroc_share_vs_correct']:.3f}")
(ROOT / "results/a4_selfconsistency.json").write_text(json.dumps(out, indent=1))
