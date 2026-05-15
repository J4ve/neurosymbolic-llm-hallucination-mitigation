"""Print binary F1 + confusion matrices from all_metrics.json."""
import json
m = json.load(open("../results/all_metrics.json"))
for name, d in m.items():
    print(name)
    print("  binary_f1_reject:  ", round(d["binary_f1_reject"], 4))
    print("  binary_f1_solvable:", round(d["binary_f1_solvable"], 4))
    print("  confusion (gold rows x pred cols, classes=[solvable,missing,contra]):")
    cm = d["confusion_matrix"]
    labels = ["solv", "miss", "contr"]
    print("    gold/pred  solv  miss  contr")
    for l, row in zip(labels, cm):
        print(f"    {l:8s}  {row[0]:4d}  {row[1]:4d}  {row[2]:4d}")
    print()
