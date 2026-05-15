"""Print pipeline failure modes to understand what went wrong."""

import json
from collections import Counter
from pathlib import Path

p = Path("../results/pipeline_predictions.jsonl")
rows = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]

print(f"Total: {len(rows)}")
print("Gold dist:", Counter(r["gold_label"] for r in rows))
print("Pred dist:", Counter(r["pred_label"] for r in rows))
print("z3_error count:", sum(1 for r in rows if r.get("z3_error")))
print()

print("=== Sample SOLVABLE that got mislabeled ===")
for r in [x for x in rows if x["gold_label"] == "solvable" and x["pred_label"] != "solvable"][:3]:
    print("Problem:", r["problem"][:200])
    print("Gold ans:", r["gold_answer"], " Pred label:", r["pred_label"])
    print("SMT-LIB:")
    print(r["pred_smtlib"][:500])
    print("---")

print("\n=== Sample CONTRA that got mislabeled ===")
for r in [x for x in rows if x["gold_label"] == "contra" and x["pred_label"] != "contra"][:3]:
    print("Problem:", r["problem"][:200])
    print("Pred label:", r["pred_label"])
    print("SMT-LIB:")
    print(r["pred_smtlib"][:500])
    print("---")

print("\n=== Sample MISSING (most should be REJECT_MISSING) ===")
for r in [x for x in rows if x["gold_label"] == "missing"][:2]:
    print("Problem:", r["problem"][:200])
    print("Pred label:", r["pred_label"])
    print("SMT-LIB:")
    print(r["pred_smtlib"][:500])
    print("---")
