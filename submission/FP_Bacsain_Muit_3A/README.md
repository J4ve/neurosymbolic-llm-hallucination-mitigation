# Neuro-Symbolic Math Reasoning Pipeline

Code for: *Mitigating Reasoning Hallucinations in LLMs via Neuro-Symbolic Integration for Ill-Defined Mathematical Problems* (Bacsain & Muit).

## Pipeline

```
Math problem (English)
        |
        v
  Fine-tuned 7B LLM (Qwen2.5-7B-Instruct + LoRA)
        |
        v
  SMT-LIB v2 code
        |
        v
  Z3 solver
        |
        v
  SOLVED (return number) | REJECT_CONTRA | REJECT_MISSING
```

## Setup

```powershell
# Create env (Python 3.10+)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env with API key
"GROQ_API_KEY=gsk_xxx" | Out-File -Encoding utf8 .env
```

On HPC (Linux):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "GROQ_API_KEY=gsk_xxx" > .env
```

## End-to-end run

```bash
# 1. Prepare PMC splits (run once, after downloading PMC raw file)
cd src
python data_loader.py --raw ../data/pmc_raw.json --outdir ../data \
    --train 4000 --val 500 --test 500

# 2. Generate SMT-LIB labels for training set (uses Groq API)
python label_gen.py --input ../data/train.jsonl \
    --output ../data/labeled_train.jsonl \
    --rejected ../data/labeled_train_rejected.jsonl

# Smoke test first (10 examples)
python label_gen.py --input ../data/train.jsonl \
    --output ../data/labeled_train_smoke.jsonl --limit 10

# 3. LoRA fine-tune (HPC; ~2-3h single A5000)
python train_lora.py \
    --train ../data/labeled_train.jsonl \
    --val ../data/labeled_train.jsonl \
    --out ../models/qwen25-smtlib-lora \
    --epochs 3 --batch 4 --grad_accum 4

# 4. Inference on test set (our system)
python inference.py \
    --base Qwen/Qwen2.5-7B-Instruct \
    --adapter ../models/qwen25-smtlib-lora \
    --input ../data/test.jsonl \
    --output ../results/pipeline_predictions.jsonl

# 5. Baselines
python baselines.py --mode vanilla --base Qwen/Qwen2.5-7B-Instruct \
    --input ../data/test.jsonl \
    --output ../results/vanilla_predictions.jsonl
python baselines.py --mode cot --base Qwen/Qwen2.5-7B-Instruct \
    --input ../data/test.jsonl \
    --output ../results/cot_predictions.jsonl

# 6. Score
python evaluate.py --pred ../results/pipeline_predictions.jsonl \
    --name "Ours (LoRA + Z3)" --out ../results/pipeline_metrics.json
python evaluate.py --pred ../results/vanilla_predictions.jsonl \
    --name "Vanilla Qwen2.5-7B" --out ../results/vanilla_metrics.json
python evaluate.py --pred ../results/cot_predictions.jsonl \
    --name "CoT Qwen2.5-7B" --out ../results/cot_metrics.json
```

## Notes

- Default base model is `Qwen/Qwen2.5-7B-Instruct` (ungated). To use LLaMA-3:
  request access at https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
  then pass `--base meta-llama/Meta-Llama-3-8B-Instruct` in steps 3-5.
- `label_gen.py` is resumable via `--resume`. Drops mismatches; ~70% keep rate
  expected on first pass.
- For multi-GPU training: `accelerate launch train_lora.py [args]`.
- Z3 timeouts default to 5s per problem; tunable in `z3_runner.py`.

## File map

```
src/
  z3_runner.py     # SMT-LIB -> verdict (SOLVED/REJECT_CONTRA/REJECT_MISSING)
  label_gen.py     # Groq translator + Z3 verification filter
  data_loader.py   # PMC raw -> train/val/test jsonl splits
  train_lora.py    # 4-bit base + LoRA SFT via TRL
  inference.py     # base+adapter -> SMT-LIB -> Z3 pipeline
  baselines.py     # vanilla + CoT prompted baselines
  evaluate.py      # F1 per class + LaTeX table row
examples/
  seed_examples.json   # 10 hand-written (problem, SMT-LIB) seeds
data/        # not committed; populate via data_loader.py + label_gen.py
models/      # LoRA adapters, not committed
results/     # predictions + metrics, not committed
```
