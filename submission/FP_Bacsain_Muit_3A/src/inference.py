"""End-to-end pipeline: problem -> fine-tuned model -> SMT-LIB -> Z3 -> verdict.

Loads base model + LoRA adapter, generates SMT-LIB for each problem,
runs Z3, and emits final prediction in canonical form.

Predictions format:
    {"id", "problem", "gold_label", "gold_answer",
     "pred_smtlib", "pred_label", "pred_answer", "z3_error"}

Usage:
    python inference.py \
        --base Qwen/Qwen2.5-7B-Instruct \
        --adapter ../models/qwen25-smtlib-lora \
        --input ../data/test.jsonl \
        --output ../results/pipeline_predictions.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from peft import PeftModel
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from z3_runner import run_smtlib


def strip_fences(text: str) -> str:
    """Remove ```...``` fences if model added them despite instruction."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


SYSTEM_PROMPT = (
    "You are a translator from English math word problems to SMT-LIB v2 (Z3 input format).\n"
    "Strict rules:\n"
    "1. Declare every variable BEFORE using it: (declare-const <name> Int) or Real.\n"
    "2. For every unknown that represents a count, money, distance, time, age, or "
    "any other natural quantity, ALSO add (assert (>= <name> 0)). Real-world "
    "quantities cannot be negative; without this, Z3 will fail to detect "
    "contradictions like 'subtract more than you have'.\n"
    "3. Encode every stated relationship as an (assert ...). Include all "
    "constraints, including ones implied by ordering (e.g. if A is the total "
    "and B is a part, then B <= A).\n"
    "4. End with (check-sat) and (get-value (<target>)) where <target> is the "
    "specific variable the problem asks about.\n"
    "5. For SOLVABLE problems, the asserts together with the non-negativity "
    "constraints must uniquely determine <target>.\n"
    "6. For CONTRADICTORY problems, include ALL stated facts so they conflict; "
    "Z3 will return UNSAT.\n"
    "7. For MISSING-INFO problems, do NOT invent values; leave them as free "
    "variables so Z3 finds multiple models.\n"
    "8. Output ONLY SMT-LIB code, no markdown fences, no commentary, no prose."
)


def _format_example(ex: dict) -> str:
    return f"Problem: {ex['problem']}\nSMT-LIB:\n{ex['smtlib']}"


def build_user_message(problem: str, seeds: list[dict] | None) -> str:
    if seeds:
        examples = "\n\n".join(_format_example(s) for s in seeds)
        return (f"Here are translation examples:\n\n{examples}\n\n"
                f"Now translate the following problem to SMT-LIB v2. "
                f"Output ONLY SMT-LIB code.\n\n"
                f"Problem: {problem}\nSMT-LIB:\n")
    return f"Problem: {problem}"


VERDICT_TO_LABEL = {
    "SOLVED": "solvable",
    "REJECT_CONTRA": "contra",
    "REJECT_MISSING": "missing",
    "ERROR": "missing",  # default to REJECT on parse/timeout errors
}


def load_model(base: str, adapter: str | None, four_bit: bool = True):
    tok = AutoTokenizer.from_pretrained(base, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    if four_bit:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            base, quantization_config=bnb, device_map="auto",
            torch_dtype=torch.bfloat16, trust_remote_code=True,
        )
    else:
        base_model = AutoModelForCausalLM.from_pretrained(
            base, device_map="auto", torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

    if adapter:
        model = PeftModel.from_pretrained(base_model, adapter)
    else:
        model = base_model
    model.eval()
    return tok, model


@torch.no_grad()
def generate_smtlib(tok, model, problem: str, seeds: list[dict] | None = None,
                    max_new: int = 768) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(problem, seeds)},
    ]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(
        **inputs,
        max_new_tokens=max_new,
        do_sample=False,
        pad_token_id=tok.pad_token_id,
    )
    raw = tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return strip_fences(raw)


def predict_label_and_answer(smtlib: str):
    r = run_smtlib(smtlib, timeout_s=5)
    label = VERDICT_TO_LABEL.get(r.verdict, "missing")
    answer = r.value if label == "solvable" else None
    return label, answer, r.error


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--adapter", default=None, help="path to LoRA adapter dir")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no_4bit", action="store_true")
    ap.add_argument("--seeds", default=None,
                    help="path to seed_examples.json for few-shot prompting")
    args = ap.parse_args()

    tok, model = load_model(args.base, args.adapter, four_bit=not args.no_4bit)

    seeds = None
    if args.seeds:
        seeds = json.loads(Path(args.seeds).read_text(encoding="utf-8"))
        print(f"Loaded {len(seeds)} seed examples for few-shot prompting")

    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    if args.limit:
        rows = rows[: args.limit]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out_f = open(args.output, "w", encoding="utf-8")

    for row in tqdm(rows):
        smt = generate_smtlib(tok, model, row["problem"], seeds=seeds)
        pred_label, pred_answer, z3_err = predict_label_and_answer(smt)
        rec = {
            "id": row["id"],
            "problem": row["problem"],
            "gold_label": row["label"],
            "gold_answer": row.get("answer"),
            "pred_smtlib": smt,
            "pred_label": pred_label,
            "pred_answer": pred_answer,
            "z3_error": z3_err,
        }
        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out_f.flush()

    out_f.close()
    print(f"Wrote predictions to {args.output}")


if __name__ == "__main__":
    main()
