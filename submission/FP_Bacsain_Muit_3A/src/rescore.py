"""Re-score saved pipeline predictions by re-running Z3 on stored SMT-LIB.

Useful after improving z3_runner (e.g. adding SMT-LIB repair) without
redoing GPU inference.

Usage:
    python rescore.py --in ../results/pipeline_predictions.jsonl \
        --out ../results/pipeline_predictions_v2.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tqdm import tqdm

from z3_runner import run_smtlib


VERDICT_TO_LABEL = {
    "SOLVED": "solvable",
    "REJECT_CONTRA": "contra",
    "REJECT_MISSING": "missing",
    "ERROR": "missing",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, dest="input_file")
    ap.add_argument("--output", required=True, dest="output_file")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.input_file, encoding="utf-8") if l.strip()]

    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        for r in tqdm(rows):
            smt = r.get("pred_smtlib", "")
            z3 = run_smtlib(smt, timeout_s=5)
            pred_label = VERDICT_TO_LABEL.get(z3.verdict, "missing")
            pred_answer = z3.value if pred_label == "solvable" else None
            r["pred_label"] = pred_label
            r["pred_answer"] = pred_answer
            r["z3_error"] = z3.error
            r["z3_verdict"] = z3.verdict
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote rescored predictions to {args.output_file}")


if __name__ == "__main__":
    main()
