#!/bin/bash
# Smoke test: 5 problems, Qwen2.5-7B, prompted pipeline
set -e
source /home/javebacsain/miniconda3/etc/profile.d/conda.sh
conda activate nlp_final
cd ~/projects/nlp_final/src
nohup python -u inference.py \
    --base Qwen/Qwen2.5-7B-Instruct \
    --input ../data/test.jsonl \
    --output ../results/smoke.jsonl \
    --seeds ../examples/seed_examples.json \
    --limit 5 \
    > ../results/smoke.log 2>&1 &
echo "smoke PID=$!"
