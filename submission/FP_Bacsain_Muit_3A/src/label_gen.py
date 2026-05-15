"""Generate SMT-LIB labels for PMC problems via Groq API.

Pipeline per problem:
  1. Build few-shot prompt with seed examples.
  2. Call Groq (Llama-3.3-70B) to generate SMT-LIB.
  3. Run candidate SMT-LIB through Z3.
  4. Compare Z3 verdict vs PMC ground-truth label.
  5. Keep on match, drop on mismatch.

Inputs:
  data/train.jsonl  -- each line: {"id", "problem", "label", "answer"}
                       label in {"solvable", "missing", "contra"}
                       answer = number or null

Outputs:
  data/labeled_train.jsonl  -- kept rows: {..., "smtlib", "z3_verdict"}
  data/labeled_train_rejected.jsonl  -- mismatched rows for inspection
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from groq import Groq
from tqdm import tqdm

from z3_runner import run_smtlib, Z3Result


# Map PMC labels to Z3 verdicts
LABEL_TO_VERDICT = {
    "solvable": "SOLVED",
    "contra": "REJECT_CONTRA",
    "missing": "REJECT_MISSING",
}


SYSTEM_PROMPT = """You are a translator from English math word problems to SMT-LIB v2 (the standard input format for SMT solvers like Z3).

Rules:
- Declare each unknown as (declare-const <name> Int) or Real as appropriate.
- Encode every stated constraint as an (assert ...) form.
- For SOLVABLE problems, the constraints must uniquely determine the asked quantity. End with (check-sat) and (get-value (<target>)) where <target> is the asked-for variable.
- For CONTRADICTORY problems, include all conflicting constraints so Z3 returns UNSAT.
- For MISSING-INFO problems, do NOT invent values for missing quantities. Leave them as free variables. Z3 will then find multiple models, which our pipeline interprets as REJECT.
- Use integer arithmetic when problem uses whole numbers; use Real when fractions or division could yield non-integer results.
- Output ONLY the SMT-LIB code, no markdown fences, no commentary.
"""


def _format_example(ex: dict) -> str:
    return f"Problem: {ex['problem']}\nSMT-LIB:\n{ex['smtlib']}\n"


def build_prompt(problem: str, seeds: list[dict]) -> list[dict]:
    examples_text = "\n\n".join(_format_example(s) for s in seeds)
    user_msg = (
        f"Here are translation examples:\n\n{examples_text}\n\n"
        f"Now translate the following problem to SMT-LIB v2. "
        f"Output ONLY SMT-LIB code, no fences, no commentary.\n\n"
        f"Problem: {problem}\nSMT-LIB:\n"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]


def strip_fences(text: str) -> str:
    """Remove ```...``` fences if Groq added them despite instruction."""
    text = text.strip()
    if text.startswith("```"):
        # Drop first line (``` or ```smt) and last fence
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def call_groq(client: Groq, messages: list[dict], model: str, retries: int = 3) -> Optional[str]:
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=600,
            )
            return resp.choices[0].message.content
        except Exception as e:
            wait = 2 ** attempt
            print(f"Groq error ({e}); retry in {wait}s")
            time.sleep(wait)
    return None


def verdict_matches(pmc_label: str, z3: Z3Result, gold_answer) -> bool:
    expected = LABEL_TO_VERDICT.get(pmc_label)
    if z3.verdict != expected:
        return False
    if pmc_label == "solvable":
        if z3.value is None or gold_answer is None:
            return False
        return abs(z3.value - float(gold_answer)) < 1e-3
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="path to train.jsonl")
    ap.add_argument("--output", required=True, help="path to labeled_train.jsonl")
    ap.add_argument("--rejected", default=None, help="optional path to dump mismatches")
    ap.add_argument("--seeds", default="../examples/seed_examples.json")
    ap.add_argument("--model", default="llama-3.3-70b-versatile")
    ap.add_argument("--limit", type=int, default=None, help="cap rows for testing")
    ap.add_argument("--resume", action="store_true", help="skip ids already in output")
    args = ap.parse_args()

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("Set GROQ_API_KEY in environment or .env file")
    client = Groq(api_key=api_key)

    seeds = json.loads(Path(args.seeds).read_text(encoding="utf-8"))
    print(f"Loaded {len(seeds)} seed examples")

    done_ids = set()
    if args.resume and Path(args.output).exists():
        with open(args.output, encoding="utf-8") as f:
            for line in f:
                try:
                    done_ids.add(json.loads(line)["id"])
                except Exception:
                    pass
        print(f"Resuming; {len(done_ids)} ids already done")

    out_f = open(args.output, "a", encoding="utf-8")
    rej_f = open(args.rejected, "a", encoding="utf-8") if args.rejected else None

    kept = 0
    dropped = 0
    rows = list(open(args.input, encoding="utf-8"))
    if args.limit:
        rows = rows[: args.limit]

    for line in tqdm(rows):
        row = json.loads(line)
        if row["id"] in done_ids:
            continue

        messages = build_prompt(row["problem"], seeds)
        raw = call_groq(client, messages, args.model)
        if raw is None:
            dropped += 1
            continue
        smtlib = strip_fences(raw)

        z3 = run_smtlib(smtlib, timeout_s=5)
        match = verdict_matches(row["label"], z3, row.get("answer"))

        record = {
            **row,
            "smtlib": smtlib,
            "z3_verdict": z3.verdict,
            "z3_value": z3.value,
            "z3_error": z3.error,
        }
        if match:
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()
            kept += 1
        else:
            if rej_f:
                rej_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                rej_f.flush()
            dropped += 1

    out_f.close()
    if rej_f:
        rej_f.close()
    total = kept + dropped
    rate = 100 * kept / total if total else 0
    print(f"Kept {kept}/{total} ({rate:.1f}%); dropped {dropped}")


if __name__ == "__main__":
    main()
