"""Verify seed examples produce expected Z3 verdicts.

Run before trusting label_gen.py. Any seed that disagrees with its declared
label is a bug in seed_examples.json and must be fixed.
"""

import json
from pathlib import Path

from z3_runner import run_smtlib


LABEL_TO_VERDICT = {
    "solvable": "SOLVED",
    "contra": "REJECT_CONTRA",
    "missing": "REJECT_MISSING",
}


def main():
    seeds = json.loads(Path("../examples/seed_examples.json").read_text(encoding="utf-8"))
    bad = 0
    for i, s in enumerate(seeds):
        r = run_smtlib(s["smtlib"])
        expected = LABEL_TO_VERDICT[s["label"]]
        ok = r.verdict == expected
        if s["label"] == "solvable" and ok:
            if s["answer"] is not None and r.value is not None:
                ok = abs(r.value - float(s["answer"])) < 1e-3
        status = "OK " if ok else "BAD"
        line = (
            f"[{status}] seed {i:2d} label={s['label']:<8} verdict={r.verdict:<14}"
            f" value={r.value}  expected_answer={s['answer']}"
        )
        print(line)
        if not ok:
            bad += 1
            print(f"   problem: {s['problem']}")
    print(f"\n{len(seeds) - bad}/{len(seeds)} seeds OK")


if __name__ == "__main__":
    main()
