#!/bin/bash
# Launch all 3 systems in parallel on different GPUs.
# Each writes its own log + jsonl. Use `tail -f` to monitor.
set -e
source /home/javebacsain/miniconda3/etc/profile.d/conda.sh
conda activate nlp_final
cd ~/projects/nlp_final/src

# Pipeline (our system) on GPU 1
CUDA_VISIBLE_DEVICES=1 nohup python -u inference.py \
    --base Qwen/Qwen2.5-7B-Instruct \
    --input ../data/test.jsonl \
    --output ../results/pipeline_predictions.jsonl \
    --seeds ../examples/seed_examples.json \
    > ../results/pipeline.log 2>&1 &
PID_P=$!
echo "pipeline PID=$PID_P (GPU 1)"

# Vanilla baseline on GPU 2
CUDA_VISIBLE_DEVICES=2 nohup python -u baselines.py \
    --mode vanilla \
    --base Qwen/Qwen2.5-7B-Instruct \
    --input ../data/test.jsonl \
    --output ../results/vanilla_predictions.jsonl \
    > ../results/vanilla.log 2>&1 &
PID_V=$!
echo "vanilla  PID=$PID_V (GPU 2)"

# CoT baseline on GPU 3
CUDA_VISIBLE_DEVICES=3 nohup python -u baselines.py \
    --mode cot \
    --base Qwen/Qwen2.5-7B-Instruct \
    --input ../data/test.jsonl \
    --output ../results/cot_predictions.jsonl \
    > ../results/cot.log 2>&1 &
PID_C=$!
echo "cot      PID=$PID_C (GPU 3)"

echo "$PID_P $PID_V $PID_C" > ../results/pids.txt
echo "all launched"
