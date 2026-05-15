# Poster Plan — CSPC NLP Format

Layout matches the BuilDense example: dark-navy header band + 2-column
body with dark-navy section header bars and white content boxes.

## Size + tool

A1 portrait (594 × 841 mm). Build in PowerPoint, one slide at custom
size 24" × 36" (60 × 90 cm) or 33.1" × 46.8" (A1). Export PDF for print.

## Color palette (match template)

- **Dark navy** #1F3A5F — header band, section header bars
- **White** — content box background
- **Light blue / muted** #D7E3F0 — secondary accents, icon backgrounds
- **Dark gray** #222 — body text
- **Single accent** (optional, for headline number only) — amber #E8A33D

## Typography

- Title: 70--80 pt bold sans-serif, WHITE on navy, all caps
- Section header (inside navy bar): 32 pt bold WHITE all caps
- Body: 22--24 pt dark gray
- Captions: 18 pt italic
- Citations: 16 pt

---

## Header band (full width, ~12% height)

**Top line (title, white on navy, all caps):**
> NEURO-SYMBOLIC INTEGRATION FOR MITIGATING REASONING
> HALLUCINATIONS IN ILL-DEFINED MATHEMATICAL PROBLEMS

**Author block (left, white text on navy, below title):**

| | |
|---|---|
| **JAVE BACSAIN** | **IVY PAULINE MUIT** |
| Proponent | Proponent |
| javbacsain@my.cspc.edu.ph | ivmuit@my.cspc.edu.ph |

(Add Project Adviser block to the right of authors if your prof
wants — name + email. Fill in adviser's name.)

**Logo (top right corner, white background round/square):** CSPC logo
or a small project mark. If no project logo, use CSPC seal only.

---

## Body — 2 columns

### LEFT COLUMN

#### Box 1 — ABSTRACT
(navy bar "ABSTRACT", white body)

This project studies whether a hybrid neuro-symbolic pipeline can stop
Large Language Models (LLMs) from producing confident wrong answers on
broken math problems. A 7B language model (Qwen2.5-7B-Instruct)
translates each problem into SMT-LIB v2 logic code; the Z3 constraint
solver then decides whether the constraints uniquely determine an
answer, contradict each other, or leave the problem underdetermined,
producing either a numeric answer or a REJECT label. On a balanced
600-problem test set (PMC + GSM8K), the pipeline reduces the rate of
confident wrong answers on ill-defined problems from ~20% to 2% — a
ten-fold reduction — while trading off overall accuracy because the
7B model occasionally under-constrains its logic output.

#### Box 2 — INTRODUCTION
(navy bar "INTRODUCTION")

Modern LLMs answer plain-language questions well but are trained to
produce *plausible* text. On mathematical word problems that are
missing key data or contain contradictory constraints, LLMs still
return a fluent numeric answer with apparent confidence — a behavior
known as *hallucination*. In safety-critical domains (medical dosing,
financial calculation, automated grading), a confident-but-wrong
answer is more harmful than abstention.

This study evaluates whether separating language understanding from
logical evaluation — by routing the LLM's output through a deductive
solver — measurably reduces hallucination on broken problems while
preserving acceptable answer quality on solvable ones.

**Inputs:** English math word problems.
**Outputs:** Numeric answer (Solvable) OR REJECT (Missing-type /
Contra-type ill-defined).

#### Box 3 — RESEARCH QUESTIONS
(navy bar; each question with light-blue circle "?" icon)

❓ **RQ1.** Can a deductive solver, used as a post-hoc filter on a
prompted LLM, lower the rate of confidently-wrong answers on broken
math problems compared to standard prompting and chain-of-thought?

❓ **RQ2.** What is the trade-off between hallucination reduction and
aggregate classification accuracy when the translator is a 7B
prompted model rather than a fine-tuned one?

❓ **RQ3.** Where does the prompted translator's SMT-LIB output fail
most often, and what kind of solver-level repair is feasible without
fine-tuning?

#### Box 4 — REFERENCES
(navy bar; small font 16 pt, numbered)

[1] Tian, S.-Y., et al. (2024). *VCSearch: Bridging the Gap Between
Well-Defined and Ill-Defined Problems in Mathematical Reasoning.*
arXiv:2406.05055.

[2] Cobbe, K., et al. (2021). *Training Verifiers to Solve Math Word
Problems.* arXiv:2110.14168.

[3] de Moura, L., & Bjørner, N. (2008). *Z3: An Efficient SMT Solver.*
TACAS 2008.

[4] Yang, A., et al. (2024). *Qwen2.5 Technical Report.*
arXiv:2412.15115.

[5] Wei, J., et al. (2022). *Chain-of-Thought Prompting Elicits
Reasoning in Large Language Models.* NeurIPS 2022.

(Full 22-reference list in paper.)

---

### RIGHT COLUMN

#### Box 5 — METHODOLOGY
(navy bar "METHODOLOGY")

**Pipeline (insert `pipeline.png`):**

```
Math problem (English)
        ↓
LLM translator (Qwen2.5-7B-Instruct, 10 few-shot examples)
        ↓
SMT-LIB v2 logic code   ← (auto-repair pass adds missing
                           variable declarations)
        ↓
Z3 constraint solver
        ↓
┌──────────────┬──────────────┬──────────────┐
↓              ↓              ↓
UNIQUE        UNSAT          MULTIPLE
MODEL                        MODELS
↓              ↓              ↓
Answer        REJECT         REJECT
              (contra)       (missing)
```

**Setup:** 4-bit nf4 quantization, single RTX A5000 per system,
greedy decoding (max 768 tokens), Z3 timeout 5 s.

**Dataset:** 600 problems balanced 200/200/200 from PMC
(`kevin715/PMC` on HuggingFace) + GSM8K test split.

**Baselines:** Same Qwen2.5-7B-Instruct under (a) vanilla zero-shot
prompt and (b) chain-of-thought "Let's think step by step".

#### Box 6 — EXPERIMENTAL RESULTS
(navy bar "EXPERIMENTAL RESULTS"; embed 1 bar chart + 1 mini-table)

**HEADLINE BAR CHART (large, centerpiece):**

> Hallucination rate — fraction of 400 ill-defined problems for which
> the system returned a confident numeric answer instead of REJECT.

```
Plain (Vanilla)   ████████████████████  19.25%
Step-by-step (CoT) █████████████████████ 21.00%
Ours (Few-shot + Z3) ██                  2.00%
                                            ↑
                                       10× lower
```

**Per-class F1 mini-table:**

| System | Acc | Macro F1 | S | M | C | AnsAcc |
|---|---|---|---|---|---|---|
| Vanilla | 0.587 | 0.474 | 0.798 | 0.623 | 0.000 | 0.761 |
| CoT | 0.600 | 0.482 | 0.822 | 0.625 | 0.000 | 0.904 |
| Ours | 0.347 | 0.210 | 0.100 | 0.500 | **0.029** | 0.636 |

**Key observations:**
- Pipeline cuts confident wrong answers on broken problems ~10×.
- Pipeline is the only system that detects any contradictions
  explicitly (F1$_C$ = 0.029 vs. 0.000 for both baselines).
- Trade-off: pipeline over-rejects solvable problems (11/200 answered)
  because the 7B translator under-constrains SMT-LIB.

#### Box 7 — RECOMMENDATIONS
(navy bar; each item with light-blue 💡 icon)

💡 **Fine-tune the translator.** Auto-generate (problem, SMT-LIB)
training pairs and filter by Z3 verification; would let a smaller
model learn the implicit non-negativity, totality, and ordering
constraints the few-shot prompt misses.

💡 **Add unit annotations to SMT-LIB.** A lightweight type layer
(currency, distance, percentage) would let the pipeline distinguish
right-magnitude / wrong-unit answers from genuine errors.

💡 **Hybrid translation search.** Combine the prompted translator
with VCSearch's variable-constraint search to repair near-miss
SMT-LIB rather than abstaining.

💡 **Deploy in safety-critical settings.** Where wrong-answer cost
is high (medical dosing, finance, grading), the trade-off
(over-rejection for fewer confident lies) becomes favorable.

---

## Footer / corner elements

- **QR code (lower-right corner)** linking to the GitHub repo:
  `https://github.com/J4ve/NLP_FP`
- "CSAC 224 — Natural Language Processing — Final Project, 2026"
- "Compute provided by AI Research Center for Community Development
  HPC, CSPC"

---

## Production checklist

- [ ] Title fits one line at 70 pt (shorten if needed)
- [ ] Adviser name + email inserted (currently placeholder)
- [ ] All section header bars same height + alignment
- [ ] Body text minimum 22 pt
- [ ] Bar chart readable from 3 m
- [ ] Headline number (10× / 2.00%) is the largest non-title element
- [ ] All emails legible at print scale
- [ ] QR code scans on phone
- [ ] Export at 300 DPI
- [ ] Test print on letter paper, hold at arm's length to verify
      readability before printing A1

---

## 30-second elevator pitch (for the judge)

> "Chatbots invent confident wrong numbers when a math problem is
> broken. We made the chatbot pass each problem to a logic tool —
> Z3 — before answering. The logic tool either proves an answer
> exists or formally rejects the problem. Result: ten times fewer
> confident wrong answers on broken problems. The trade-off is that
> our small model writes imperfect logic, so we sometimes refuse
> problems that actually have answers. That trade-off is the right
> one when wrong answers are dangerous — like medicine or money."
