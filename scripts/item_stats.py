"""Print a summary of built item sets: python scripts/item_stats.py data/audit data/train"""
import collections as C
import json
import sys

for d in sys.argv[1:]:
    r = json.load(open(f"{d}/build_report.json"))
    it = [json.loads(l) for l in open(f"{d}/items.jsonl")]
    print(f"== {d}: {r['items']} items, drops={r['drops']}, errors={r['n_errors']}")
    print("  per template:", dict(C.Counter(x["template"] for x in it)))
    print("  per family:", dict(C.Counter(x["family"] for x in it)))
    ms = [(m, x) for x in it for m in x["mutants"]]
    blind = [(m, x) for m, x in ms if x["mutant_blind"][m]]
    print(f"  mutants={len(ms)} blind_on_original={len(blind)} "
          f"blind_and_caught_by_selected_cfs={sum(x['mutant_caught'][m] for m, x in blind)} "
          f"blind_and_catchable_by_pool={sum(x['mutant_catchable'][m] for m, x in blind)}")
    print("  K:", dict(C.Counter(len(x["cf_edits"]) for x in it)), " edits:", dict(C.Counter(e for x in it for e in x["cf_edits"])))
