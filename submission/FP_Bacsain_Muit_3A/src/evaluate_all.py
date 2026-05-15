"""Run evaluate.py on all 3 systems, build a combined LaTeX results table.

Usage:
    python evaluate_all.py --results_dir ../results --out ../results/all_metrics.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluate import score, latex_table_row, CLASSES


SYSTEMS = [
    ("vanilla_predictions.jsonl",  "Vanilla Qwen2.5-7B"),
    ("cot_predictions.jsonl",      "CoT Qwen2.5-7B"),
    ("pipeline_predictions.jsonl", "Ours (Few-shot + Z3)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    d = Path(args.results_dir)
    all_metrics = {}
    table_rows = []

    for fname, name in SYSTEMS:
        path = d / fname
        if not path.exists():
            print(f"[skip] {path} not found")
            continue
        rows = [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]
        if not rows:
            print(f"[skip] {path} is empty")
            continue
        m = score(rows)
        all_metrics[name] = m
        table_rows.append(latex_table_row(name, m))

        print(f"\n=== {name} (n={m['n']}) ===")
        print(f"  Acc        : {m['accuracy']:.4f}")
        print(f"  Macro F1   : {m['f1_macro']:.4f}")
        print(f"  F1 solvable: {m['f1_per_class']['solvable']:.4f}")
        print(f"  F1 missing : {m['f1_per_class']['missing']:.4f}")
        print(f"  F1 contra  : {m['f1_per_class']['contra']:.4f}")
        print(f"  AnsAcc     : {m['answer_accuracy_on_correctly_solved']:.4f} "
              f"({m['n_solvable_both']} rows)")
        print(f"  Gold dist  : {m['gold_distribution']}")
        print(f"  Pred dist  : {m['pred_distribution']}")

    print("\n\n=== Combined LaTeX table ===\n")
    header = (
        "\\begin{tabular}{lcccccc}\n"
        "\\toprule\n"
        "System & Acc & Macro F1 & S & M & C & AnsAcc \\\\\n"
        "\\midrule\n"
    )
    body = "\n".join(table_rows)
    footer = "\n\\bottomrule\n\\end{tabular}"
    print(header + body + footer)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(all_metrics, f, indent=2)
        print(f"\nMetrics saved to {args.out}")
        tex_path = Path(args.out).with_suffix(".tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(header + body + footer)
        print(f"LaTeX table saved to {tex_path}")


if __name__ == "__main__":
    main()
