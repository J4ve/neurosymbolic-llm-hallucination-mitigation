"""Download PMC + GSM8K, mix into balanced 3-class test set.

PMC (kevin715/PMC on HF) is test-only ill-defined problems with two splits:
  - missing_test: id, Question
  - contra_test:  id, Question, Reason

GSM8K (openai/gsm8k on HF) provides solvable problems with answers:
  - test split: question, answer (with #### final-number marker)

We build a balanced test set:
  - N solvable from GSM8K test
  - N missing from PMC missing_test
  - N contra from PMC contra_test

Each row written to data/test.jsonl with fields:
  id, problem, label, answer (None for missing/contra)

Usage:
    python fetch_data.py --outdir ../data --per_class 200 --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from datasets import load_dataset


GSM8K_ANSWER_RE = re.compile(r"####\s*([-+]?[\d,]+(?:\.\d+)?)")


def extract_gsm8k_answer(answer_text: str):
    """Extract the final numeric answer from GSM8K's chain-of-thought style."""
    m = GSM8K_ANSWER_RE.search(answer_text)
    if not m:
        return None
    raw = m.group(1).replace(",", "")
    try:
        v = float(raw)
        return int(v) if v.is_integer() else v
    except ValueError:
        return None


def fetch_pmc():
    """Load each PMC split separately to avoid column-schema merge errors."""
    missing_ds = load_dataset(
        "kevin715/PMC",
        data_files={"missing_test": "merge_missing.jsonl"},
        split="missing_test",
    )
    contra_ds = load_dataset(
        "kevin715/PMC",
        data_files={"contra_test": "merge_contra.jsonl"},
        split="contra_test",
    )
    missing = [{"id": r["id"], "problem": r["Question"], "label": "missing", "answer": None}
               for r in missing_ds]
    contra = [{"id": r["id"], "problem": r["Question"], "label": "contra", "answer": None}
              for r in contra_ds]
    return missing, contra


def fetch_gsm8k_solvable():
    ds = load_dataset("openai/gsm8k", "main")
    rows = []
    for i, r in enumerate(ds["test"]):
        ans = extract_gsm8k_answer(r["answer"])
        if ans is None:
            continue
        rows.append({
            "id": f"gsm8k_test_{i:05d}",
            "problem": r["question"],
            "label": "solvable",
            "answer": ans,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--per_class", type=int, default=200,
                    help="rows per class in the final test set")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print("Downloading PMC ...")
    missing, contra = fetch_pmc()
    print(f"  missing: {len(missing)}   contra: {len(contra)}")

    print("Downloading GSM8K test ...")
    solvable = fetch_gsm8k_solvable()
    print(f"  solvable: {len(solvable)}")

    n = args.per_class
    random.shuffle(missing)
    random.shuffle(contra)
    random.shuffle(solvable)

    def take(rows, k, name):
        if len(rows) < k:
            print(f"  warn: only {len(rows)} {name} rows, requested {k}; using all")
            return rows
        return rows[:k]

    test = take(solvable, n, "solvable") + take(missing, n, "missing") + take(contra, n, "contra")
    random.shuffle(test)

    out = outdir / "test.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in test:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(test)} test rows to {out}")
    from collections import Counter
    print("Distribution:", Counter(r["label"] for r in test))

    # Also save full PMC + GSM8K test pools for future use
    with (outdir / "pmc_missing_full.jsonl").open("w", encoding="utf-8") as f:
        for r in missing:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (outdir / "pmc_contra_full.jsonl").open("w", encoding="utf-8") as f:
        for r in contra:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (outdir / "gsm8k_test_full.jsonl").open("w", encoding="utf-8") as f:
        for r in solvable:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Also saved full pools to {outdir}/")


if __name__ == "__main__":
    main()
