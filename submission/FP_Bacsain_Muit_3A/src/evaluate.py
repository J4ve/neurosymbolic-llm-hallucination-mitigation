"""Score predictions vs gold labels.

Reports overall accuracy, per-class F1, macro F1, and answer accuracy on
the solvable subset. Also emits a small LaTeX table to paste into the paper.

Usage:
    python evaluate.py \
        --pred ../results/pipeline_predictions.jsonl \
        --name "Ours (LoRA + Z3)" \
        --out ../results/pipeline_metrics.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from sklearn.metrics import classification_report, confusion_matrix, f1_score


CLASSES = ["solvable", "missing", "contra"]


def numeric_match(pred, gold) -> bool:
    if pred is None or gold is None:
        return False
    try:
        return abs(float(pred) - float(gold)) < 1e-3
    except (TypeError, ValueError):
        return False


def score(rows: list[dict]) -> dict:
    gold = [r["gold_label"] for r in rows]
    pred = [r["pred_label"] for r in rows]

    # Per-class F1
    f1_per_class = f1_score(gold, pred, labels=CLASSES, average=None, zero_division=0)
    f1_macro = f1_score(gold, pred, labels=CLASSES, average="macro", zero_division=0)
    accuracy = sum(int(g == p) for g, p in zip(gold, pred)) / max(1, len(rows))

    # Answer accuracy on rows where BOTH gold and pred say solvable
    both_solv = [r for r in rows if r["gold_label"] == "solvable" and r["pred_label"] == "solvable"]
    if both_solv:
        ans_acc = sum(int(numeric_match(r["pred_answer"], r["gold_answer"])) for r in both_solv) / len(both_solv)
    else:
        ans_acc = 0.0

    # Rejection-vs-solve binary view (collapse missing+contra)
    binary_gold = ["reject" if g != "solvable" else "solvable" for g in gold]
    binary_pred = ["reject" if p != "solvable" else "solvable" for p in pred]
    binary_f1_reject = f1_score(binary_gold, binary_pred, pos_label="reject", zero_division=0)
    binary_f1_solv = f1_score(binary_gold, binary_pred, pos_label="solvable", zero_division=0)

    return {
        "n": len(rows),
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "f1_per_class": dict(zip(CLASSES, [float(x) for x in f1_per_class])),
        "binary_f1_reject": binary_f1_reject,
        "binary_f1_solvable": binary_f1_solv,
        "answer_accuracy_on_correctly_solved": ans_acc,
        "n_solvable_both": len(both_solv),
        "gold_distribution": dict(Counter(gold)),
        "pred_distribution": dict(Counter(pred)),
        "classification_report": classification_report(gold, pred, labels=CLASSES, zero_division=0),
        "confusion_matrix": confusion_matrix(gold, pred, labels=CLASSES).tolist(),
    }


def latex_table_row(name: str, m: dict) -> str:
    f = m["f1_per_class"]
    return (
        f"{name} & {m['accuracy']:.3f} & {m['f1_macro']:.3f} & "
        f"{f['solvable']:.3f} & {f['missing']:.3f} & {f['contra']:.3f} & "
        f"{m['answer_accuracy_on_correctly_solved']:.3f} \\\\"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--name", default="System")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.pred, encoding="utf-8") if l.strip()]
    m = score(rows)

    print(f"\n=== {args.name} (n={m['n']}) ===")
    print(f"Accuracy:           {m['accuracy']:.4f}")
    print(f"Macro F1:           {m['f1_macro']:.4f}")
    print(f"F1 solvable:        {m['f1_per_class']['solvable']:.4f}")
    print(f"F1 missing:         {m['f1_per_class']['missing']:.4f}")
    print(f"F1 contra:          {m['f1_per_class']['contra']:.4f}")
    print(f"Binary F1 (reject): {m['binary_f1_reject']:.4f}")
    print(f"Binary F1 (solv):   {m['binary_f1_solvable']:.4f}")
    print(f"Answer acc (on solved-correct): "
          f"{m['answer_accuracy_on_correctly_solved']:.4f} "
          f"({m['n_solvable_both']} rows)")
    print(f"\nGold dist: {m['gold_distribution']}")
    print(f"Pred dist: {m['pred_distribution']}")
    print("\nClassification report:")
    print(m["classification_report"])
    print(f"Confusion matrix (rows=gold, cols=pred, order={CLASSES}):")
    for r in m["confusion_matrix"]:
        print(" ", r)

    print("\nLaTeX row (paste into results table):")
    print(latex_table_row(args.name, m))

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"name": args.name, **m}, f, indent=2)
        print(f"\nMetrics saved to {args.out}")


if __name__ == "__main__":
    main()
