"""Baseline systems for comparison:

  1. vanilla:  base model, zero-shot, direct answer or REJECT
  2. cot:      base model, zero-shot Chain-of-Thought ("Let's think step by step")

Both parse the model's free-form output back into a (label, answer) prediction
using lightweight regex heuristics. Predictions written in the same schema as
inference.py so evaluate.py can score them uniformly.

Usage:
    python baselines.py --mode vanilla --base Qwen/Qwen2.5-7B-Instruct \
        --input ../data/test.jsonl --output ../results/vanilla_predictions.jsonl
    python baselines.py --mode cot --base Qwen/Qwen2.5-7B-Instruct \
        --input ../data/test.jsonl --output ../results/cot_predictions.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


VANILLA_PROMPT = (
    "Solve the following math word problem. If the problem is missing required "
    "information or contains contradictory conditions, respond with exactly "
    "'REJECT'. Otherwise, give the final numeric answer in the form: "
    "'Answer: <number>'.\n\nProblem: {problem}"
)

COT_PROMPT = (
    "Solve the following math word problem step by step. Let's think step by step. "
    "If the problem is missing required information or contains contradictory "
    "conditions, respond with exactly 'REJECT' at the end. Otherwise, after "
    "your reasoning, give the final numeric answer on a new line in the form: "
    "'Answer: <number>'.\n\nProblem: {problem}"
)


REJECT_WORDS = ("REJECT", "cannot be solved", "no solution", "insufficient",
                "missing information", "contradict")


def parse_response(text: str) -> tuple[str, float | None]:
    """Heuristic parser. Returns (label, answer_or_None).

    label in {"solvable", "missing", "contra", "missing"}.
    Vanilla/CoT can't reliably distinguish missing vs contra, so we collapse
    all REJECT responses to "missing" by default. evaluate.py treats both as
    correct rejections when scoring at the rejection-vs-solve granularity.
    """
    t = text.strip()
    upper = t.upper()
    if any(w.upper() in upper for w in REJECT_WORDS):
        return "missing", None

    # Look for "Answer: X" first
    m = re.search(r"answer[:\s]*([-+]?\d+(?:\.\d+)?(?:/\d+)?)", t, re.IGNORECASE)
    if m:
        return "solvable", _to_float(m.group(1))

    # Fallback: last number in the text
    nums = re.findall(r"-?\d+(?:\.\d+)?", t)
    if nums:
        return "solvable", _to_float(nums[-1])

    return "missing", None


def _to_float(s: str) -> float | None:
    try:
        if "/" in s:
            num, den = s.split("/")
            return float(num) / float(den)
        return float(s)
    except Exception:
        return None


def load_model(base: str, four_bit: bool = True):
    tok = AutoTokenizer.from_pretrained(base, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    if four_bit:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            base, quantization_config=bnb, device_map="auto",
            torch_dtype=torch.bfloat16, trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base, device_map="auto", torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
    model.eval()
    return tok, model


@torch.no_grad()
def generate(tok, model, user_msg: str, max_new: int = 512) -> str:
    messages = [{"role": "user", "content": user_msg}]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(
        **inputs,
        max_new_tokens=max_new,
        do_sample=False,
        pad_token_id=tok.pad_token_id,
    )
    return tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["vanilla", "cot"], required=True)
    ap.add_argument("--base", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no_4bit", action="store_true")
    args = ap.parse_args()

    tok, model = load_model(args.base, four_bit=not args.no_4bit)
    template = VANILLA_PROMPT if args.mode == "vanilla" else COT_PROMPT

    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    if args.limit:
        rows = rows[: args.limit]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out_f = open(args.output, "w", encoding="utf-8")

    for row in tqdm(rows):
        text = generate(tok, model, template.format(problem=row["problem"]))
        pred_label, pred_answer = parse_response(text)
        rec = {
            "id": row["id"],
            "problem": row["problem"],
            "gold_label": row["label"],
            "gold_answer": row.get("answer"),
            "pred_raw": text,
            "pred_label": pred_label,
            "pred_answer": pred_answer,
        }
        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out_f.flush()

    out_f.close()
    print(f"Wrote {args.mode} predictions to {args.output}")


if __name__ == "__main__":
    main()
