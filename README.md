# Mitigating Reasoning Hallucinations in LLMs via Neuro-Symbolic Integration

NLP final project — CSAC 224, Camarines Sur Polytechnic Colleges.
Authors: Jave Bacsain, Ivy Pauline Muit.

A few-shot prompted neuro-symbolic pipeline that translates math word
problems into SMT-LIB v2 and uses Z3 to decide whether the problem is
solvable, contradictory, or under-determined.

## Headline result

| System (Qwen2.5-7B-Instruct) | Accuracy | Macro F1 | Hallucination rate on ill-defined inputs |
|---|---|---|---|
| Vanilla | 0.587 | 0.474 | 19.25% |
| Chain-of-Thought | 0.600 | 0.482 | 21.00% |
| **Ours (Few-shot + Z3)** | 0.347 | 0.210 | **2.00%** |

Pipeline reduces confident wrong answers on ill-defined inputs ~10×.

## Repository layout

```
.
├── NLP_midterm_paper/    # original proposal (ACM format)
├── NLP_final_paper/      # final paper (ACM format) + poster plan
└── final_project/        # code, seed examples, run scripts
```

## Final paper

See [NLP_final_paper/main.pdf](NLP_final_paper/main.pdf).
Source: [NLP_final_paper/main.tex](NLP_final_paper/main.tex).

## Code

See [final_project/README.md](final_project/README.md) for end-to-end
run instructions (PMC + GSM8K download, inference on Qwen2.5-7B, Z3
evaluation, baselines).

## Poster

Layout plan: [NLP_final_paper/POSTER_PLAN.md](NLP_final_paper/POSTER_PLAN.md).

## Datasets

- PMC (ill-defined problems): `kevin715/PMC` on Hugging Face,
  introduced in VCSearch (Tian et al., 2024,
  [arXiv:2406.05055](https://arxiv.org/abs/2406.05055)).
- GSM8K (solvable problems): `openai/gsm8k` on Hugging Face
  (Cobbe et al., 2021, [arXiv:2110.14168](https://arxiv.org/abs/2110.14168)).

## Compute

Experiments ran on the AI Research Center for Community Development
HPC at CSPC (4× NVIDIA RTX A5000, 32-core Xeon Silver 4309Y).
