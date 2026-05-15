# Poster Plan

**Title:** Mitigating Reasoning Hallucinations in LLMs via Neuro-Symbolic Integration for Ill-Defined Mathematical Problems
**Authors:** Jave Bacsain, Ivy Pauline Muit — CSAC 224 NLP, CSPC

## Recommended physical size

A1 (594 × 841 mm) portrait, or 36" × 48" landscape if your school uses
US sizes. Portrait reads better when judges walk a hallway.

## Tool

PowerPoint (single 33.1" × 46.8" slide) or LaTeX `tikzposter` / `beamerposter`.
PowerPoint is faster for first iteration; export to PDF for printing.

## Header band (full width, ~10% of height)

- Title (60--72 pt, bold)
- Authors + emails (24--28 pt)
- CSPC logo left, CSAC 224 -- NLP label right
- Thin separator below

## 3-column layout (rest of poster)

### Column 1 — Problem & Approach

**Box 1.1: The Problem**
- 1 sentence: LLMs hallucinate confident answers when math problems
  are missing info or contradictory.
- Real-world quote / example of a missing-info word problem
- Bullet: "20% of ill-defined inputs answered confidently wrong by
  vanilla / CoT Qwen-7B"

**Box 1.2: Our Idea**
- 1 sentence: separate language understanding from logical evaluation.
- Pipeline diagram (use `pipeline.png` from paper)
- Caption: "LLM translates problem → SMT-LIB. Z3 decides solvable /
  contradictory / under-determined."

**Box 1.3: Why It Matters**
- Bullet list: applications where wrong-answer >> abstention
  - Medical dosing
  - Financial calculation
  - Automated grading

### Column 2 — Method & Data

**Box 2.1: Two-Stage Pipeline**
- Diagram: Problem → LLM (Qwen2.5-7B) → SMT-LIB → Z3 →
  {SOLVED / UNSAT / multi-model} → answer or REJECT

**Box 2.2: How Z3 Decides**
- `SAT` + unique model → numeric answer (Solvable)
- `UNSAT` → REJECT (Contra)
- `SAT` + multiple models → REJECT (Missing)
- Uniqueness check: assert "var != first value", re-check

**Box 2.3: Data**
- Test set: 600 problems, balanced 200 / 200 / 200
  - 200 from PMC `missing_test` split
  - 200 from PMC `contra_test` split
  - 200 from GSM8K `test` split
- Few-shot: 10 hand-crafted (problem, SMT-LIB) demos

**Box 2.4: Setup**
- Qwen2.5-7B-Instruct, 4-bit nf4
- Single RTX A5000 per system
- 5 s Z3 timeout, greedy decoding, seed 42
- SMT-LIB auto-repair pass

### Column 3 — Results & Takeaways

**Box 3.1: Main Table**
| System | Acc | Macro F1 | F1_C | AnsAcc |
|---|---|---|---|---|
| Vanilla | 0.587 | 0.474 | 0.000 | 0.761 |
| CoT     | 0.600 | 0.482 | 0.000 | 0.904 |
| **Ours**| 0.347 | 0.210 | **0.029** | 0.636 |

**Box 3.2: HEADLINE — Hallucination Rate** (largest visual element)
- Big bar chart, three bars:
  - Vanilla: 19.25%
  - CoT: 21.00%
  - **Ours: 2.00%** (highlight in different color)
- Subtitle: "10× fewer confident wrong answers on ill-defined inputs"

**Box 3.3: What the Pipeline Buys vs Pays**
- BUYS: structural immunity to hallucination on ill-defined problems;
  only system that detects any contradictions explicitly.
- PAYS: 7B model under-constrains SMT-LIB → over-rejects 95% of
  solvable inputs.

**Box 3.4: Conclusion + Future Work**
- Few-shot prompted neuro-symbolic = safer (lower hallucination) but
  not yet competitive on aggregate F1 at 7B.
- Future: fine-tune translator via Z3-verified auto-labels; add
  unit-typed SMT-LIB; hybridize with VCSearch.

## Footer band (~5% height)

- QR code → GitHub repo (https://github.com/J4ve/NLP_FP)
- "CSAC 224 Final Project, NLP, 2026"
- Acknowledgements: AI Research Center for Community Development
  (HPC compute)

## Color palette

- Primary: deep blue (#1F3A5F) for boxes' headers
- Accent: amber (#E8A33D) for hallucination chart "Ours" bar
- Background: white
- Text: dark gray (#222)

## Typography

- Headers: bold sans-serif (Inter / Helvetica), 36 pt
- Body: 22--24 pt sans-serif
- Code / SMT-LIB snippets: monospace 18 pt

## Pre-print checklist

- [ ] All tables and figures readable from 1 m away
- [ ] Headline (hallucination rate) visible from 3 m
- [ ] No text below 18 pt
- [ ] QR code resolves
- [ ] Author emails legible
- [ ] PDF export at 300 DPI
- [ ] Test print on letter size, hold at arm's length to check
      readability scaling
