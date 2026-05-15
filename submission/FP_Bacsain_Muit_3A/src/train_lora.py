"""Supervised fine-tune a 7-8B base model on (problem -> SMT-LIB) pairs.

LoRA via PEFT, 4-bit base via bitsandbytes, SFTTrainer from TRL.

Default model: Qwen/Qwen2.5-7B-Instruct (ungated; swap to meta-llama if access).

Usage on HPC (single GPU):
    python train_lora.py \
        --train ../data/labeled_train.jsonl \
        --val ../data/val.jsonl \
        --out ../models/qwen25-smtlib-lora \
        --epochs 3 --batch 4 --grad_accum 4

For multi-GPU DDP (4x A5000):
    accelerate launch train_lora.py [same args]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer, SFTConfig


SYSTEM_PROMPT = (
    "Translate the math word problem into SMT-LIB v2 code. "
    "Declare variables, encode every constraint as an assert. "
    "End with (check-sat) and (get-value (<target>)) when applicable. "
    "Output only SMT-LIB code."
)


def format_example(row: dict, tokenizer) -> str:
    """Build a chat-template-formatted training string.

    Loss is computed over the full string; for cleanest results, you may want
    to mask the prompt tokens. SFTTrainer's `dataset_text_field` mode trains
    on the whole string, which is fine for first iteration.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Problem: {row['problem']}"},
        {"role": "assistant", "content": row["smtlib"]},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


def load_jsonl(path: str) -> list[dict]:
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--train", required=True)
    ap.add_argument("--val", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--grad_accum", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--lora_r", type=int, default=16)
    ap.add_argument("--lora_alpha", type=int, default=32)
    ap.add_argument("--max_seq_len", type=int, default=1024)
    args = ap.parse_args()

    print(f"Loading tokenizer + model: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    train_rows = load_jsonl(args.train)
    print(f"Train rows: {len(train_rows)}")

    train_texts = [format_example(r, tokenizer) for r in train_rows]
    train_ds = Dataset.from_dict({"text": train_texts})

    eval_ds = None
    if args.val:
        val_rows = load_jsonl(args.val)
        # Only rows with smtlib labels are useful for SFT loss; skip if val is unlabeled
        val_labeled = [r for r in val_rows if r.get("smtlib")]
        if val_labeled:
            val_texts = [format_example(r, tokenizer) for r in val_labeled]
            eval_ds = Dataset.from_dict({"text": val_texts})
            print(f"Eval rows: {len(val_labeled)}")

    sft_config = SFTConfig(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch" if eval_ds else "no",
        bf16=True,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        report_to="none",
        max_seq_length=args.max_seq_len,
        dataset_text_field="text",
        packing=False,
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"Saved LoRA adapter to {args.out}")


if __name__ == "__main__":
    main()
