"""PMC dataset loader + train/val/test splitter.

PMC dataset (Tian et al. 2024, arXiv:2406.05055) is released by the authors of
VCSearch. As of writing, check the VCSearch GitHub repo for the latest
download link:
    https://github.com/lamda-bbo/VCSearch  (placeholder; update if different)

Expected raw format varies. This script normalizes whatever shape the release
ships to a single jsonl with fields:
    id        -- string
    problem   -- problem text (English)
    label     -- "solvable" | "missing" | "contra"
    answer    -- number or None

Usage:
    python data_loader.py --raw path/to/pmc_raw.json --outdir ../data \
        --seed 42 --train 4000 --val 500 --test 500
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Iterable


# Map heuristics for raw labels -> canonical labels.
# Update this dict once you inspect the actual PMC release file.
LABEL_ALIASES = {
    "solvable": "solvable",
    "well_defined": "solvable",
    "well-defined": "solvable",
    "normal": "solvable",
    "missing": "missing",
    "missing_info": "missing",
    "missing-info": "missing",
    "underdetermined": "missing",
    "contra": "contra",
    "contradiction": "contra",
    "contradictory": "contra",
    "unsat": "contra",
}


def normalize_row(raw: dict, idx: int) -> dict | None:
    """Map PMC raw row to canonical schema. Return None if unparseable."""
    # PMC's actual field names not known until you download; cover common keys.
    rid = raw.get("id") or raw.get("uid") or f"pmc_{idx:06d}"
    problem = (
        raw.get("problem")
        or raw.get("question")
        or raw.get("text")
        or raw.get("body")
    )
    if not problem:
        return None

    raw_label = (
        raw.get("label")
        or raw.get("type")
        or raw.get("category")
        or raw.get("class")
    )
    if raw_label is None:
        return None
    label = LABEL_ALIASES.get(str(raw_label).strip().lower())
    if label is None:
        return None

    answer = raw.get("answer") or raw.get("solution") or raw.get("gold")
    if isinstance(answer, str):
        try:
            answer = float(answer)
            if answer.is_integer():
                answer = int(answer)
        except ValueError:
            pass
    if label != "solvable":
        answer = None

    return {"id": str(rid), "problem": str(problem), "label": label, "answer": answer}


def load_raw(path: Path) -> Iterable[dict]:
    """Try .json (list) and .jsonl (one per line)."""
    text = path.read_text(encoding="utf-8")
    text = text.strip()
    if text.startswith("["):
        for r in json.loads(text):
            yield r
        return
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        yield json.loads(line)


def write_jsonl(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="path to raw PMC file (.json or .jsonl)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train", type=int, default=4000)
    ap.add_argument("--val", type=int, default=500)
    ap.add_argument("--test", type=int, default=500)
    args = ap.parse_args()

    raw_path = Path(args.raw)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    skipped = 0
    for i, r in enumerate(load_raw(raw_path)):
        norm = normalize_row(r, i)
        if norm is None:
            skipped += 1
            continue
        rows.append(norm)
    print(f"Loaded {len(rows)} rows; skipped {skipped} unparseable")

    # Class balance summary
    from collections import Counter
    print("Label distribution:", Counter(r["label"] for r in rows))

    random.seed(args.seed)
    random.shuffle(rows)

    total_needed = args.train + args.val + args.test
    if len(rows) < total_needed:
        raise SystemExit(
            f"Need {total_needed} rows but only {len(rows)} available. "
            f"Shrink splits via --train/--val/--test."
        )

    train = rows[: args.train]
    val = rows[args.train : args.train + args.val]
    test = rows[args.train + args.val : args.train + args.val + args.test]

    write_jsonl(train, outdir / "train.jsonl")
    write_jsonl(val, outdir / "val.jsonl")
    write_jsonl(test, outdir / "test.jsonl")
    print(f"Wrote train={len(train)} val={len(val)} test={len(test)} to {outdir}")


if __name__ == "__main__":
    main()
