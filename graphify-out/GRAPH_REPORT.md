# Graph Report - neurosymbolic-llm-hallucination-mitigation  (2026-10-23)

## Corpus Check
- Large corpus: 500 files · ~680,437 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 266 nodes · 504 edges · 24 communities (16 shown, 8 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Mitigating Reasoning Hallucinations in
- run_smtlib()
- run_smtlib()
- Submission README (identical copy
- final_project/src/inference.py
- FP_Bacsain_Muit_3A/src/inference.py
- final_project/src/baselines.py
- final_project/src/data_loader.py
- final_project/src/evaluate.py
- FP_Bacsain_Muit_3A/src/baselines.py
- FP_Bacsain_Muit_3A/src/evaluate.py
- final_project/src/fetch_data.py
- FP_Bacsain_Muit_3A/src/fetch_data.py
- final_project/src/plots.py
- final_project/src/train_lora.py
- FP_Bacsain_Muit_3A/src/plots.py
- final_project/src/inspect_failures.py
- final_project/src/print_binary.py
- final_project/src/run_all.sh
- final_project/src/run_smoke.sh
- FP_Bacsain_Muit_3A/src/inspect_failures.py
- FP_Bacsain_Muit_3A/src/print_binary.py
- FP_Bacsain_Muit_3A/src/run_all.sh
- FP_Bacsain_Muit_3A/src/run_smoke.sh

## God Nodes (most connected - your core abstractions)
1. `Mitigating Reasoning Hallucinations in LLMs via Neuro-Symbolic Integration (Final Paper)` - 50 edges
2. `Neuro-Symbolic Hallucination Mitigation Midterm Proposal` - 33 edges
3. `Poster Plan (CSPC NLP format, A1 portrait)` - 21 edges
4. `Neuro-Symbolic Math Reasoning Pipeline README (final_project)` - 21 edges
5. `run_smtlib()` - 18 edges
6. `run_smtlib()` - 18 edges
7. `Two-Stage Neuro-Symbolic Pipeline (LLM translator + Z3 judge)` - 16 edges
8. `Final Project Poster PDF (FP_Poster_Bacsain_Muit_3A)` - 15 edges
9. `Neuro-Symbolic LLM Hallucination Mitigation README` - 13 edges
10. `Few-Shot Prompted LLM Translator (Stage 1: problem -> SMT-LIB v2)` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Final Project Poster PDF (FP_Poster_Bacsain_Muit_3A)` --conceptually_related_to--> `CSAC 224 Natural Language Processing (course)`  [AMBIGUOUS]
  submission/FP_Poster_Bacsain_Muit_3A.pdf → README.md
- `Neuro-Symbolic Math Reasoning Pipeline README (final_project)` --conceptually_related_to--> `Few-Shot Prompted LLM Translator (Stage 1: problem -> SMT-LIB v2)`  [AMBIGUOUS]
  final_project/README.md → NLP_final_paper/main.pdf
- `Submission README (identical copy of final_project README)` --semantically_similar_to--> `Neuro-Symbolic Math Reasoning Pipeline README (final_project)`  [INFERRED] [semantically similar]
  submission/FP_Bacsain_Muit_3A/README.md → final_project/README.md
- `Submission requirements.txt (identical copy of final_project requirements)` --semantically_similar_to--> `final_project requirements.txt (z3-solver, groq, transformers, peft, trl, bitsandbytes)`  [INFERRED] [semantically similar]
  submission/FP_Bacsain_Muit_3A/requirements.txt → final_project/requirements.txt
- `4-bit nf4 Quantization` --conceptually_related_to--> `AI Research Center for Community Development HPC at CSPC (4x RTX A5000)`  [INFERRED]
  NLP_final_paper/main.pdf → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Neuro-symbolic decision flow: translator -> SMT-LIB (+auto-repair) -> Z3 uniqueness check -> answer or REJECT** — neurosymbolic_llm_hallucination_mitigation_nlp_final_paper_main_llm_translator, neurosymbolic_llm_hallucination_mitigation_nlp_final_paper_main_smt_lib_v2, neurosymbolic_llm_hallucination_mitigation_nlp_final_paper_main_smt_lib_auto_repair, neurosymbolic_llm_hallucination_mitigation_nlp_final_paper_main_z3_smt_solver, neurosymbolic_llm_hallucination_mitigation_nlp_final_paper_main_z3_decision_procedure [EXTRACTED 1.00]

## Communities (24 total, 8 thin omitted)

### Community 0 - "Mitigating Reasoning Hallucinations in"
Cohesion: 0.10
Nodes (64): Neuro-Symbolic Math Reasoning Pipeline README (final_project), Groq API (SMT-LIB label generation), final_project requirements.txt (z3-solver, groq, transformers, peft, trl, bitsandbytes), Per-Class F1 by System Bar Chart (Solvable/Missing/Contra; not embedded in final paper), Mitigating Reasoning Hallucinations in LLMs via Neuro-Symbolic Integration (Final Paper), Balanced 600-Problem Test Set (200 solvable GSM8K / 200 PMC missing / 200 PMC contra), Binary Reject-vs-Solve View (Reject F1 0.799 vs best 0.880), Language Models are Few-Shot Learners (Brown et al., 2020) (+56 more)

### Community 1 - "run_smtlib()"
Cohesion: 0.09
Nodes (28): Debug: try repair on a known-broken SMT-LIB and see what happens., build_prompt(), call_groq(), _format_example(), main(), Groq, Generate SMT-LIB labels for PMC problems via Groq API. Pipeline per problem: 1.…, Remove ```...``` fences if Groq added them despite instruction. (+20 more)

### Community 2 - "run_smtlib()"
Cohesion: 0.09
Nodes (28): Debug: try repair on a known-broken SMT-LIB and see what happens., build_prompt(), call_groq(), _format_example(), main(), Groq, Generate SMT-LIB labels for PMC problems via Groq API. Pipeline per problem: 1.…, Remove ```...``` fences if Groq added them despite instruction. (+20 more)

### Community 3 - "Submission README (identical copy"
Cohesion: 0.17
Nodes (15): Submission README (identical copy of final_project README), Submission requirements.txt (identical copy of final_project requirements), load_raw(), main(), normalize_row(), Path, PMC dataset loader + train/val/test splitter. PMC dataset (Tian et al. 2024,…, Map PMC raw row to canonical schema. Return None if unparseable. (+7 more)

### Community 4 - "final_project/src/inference.py"
Cohesion: 0.29
Nodes (10): build_user_message(), _format_example(), generate_smtlib(), load_model(), main(), predict_label_and_answer(), no_grad, End-to-end pipeline: problem -> fine-tuned model -> SMT-LIB -> Z3 -> verdict.… (+2 more)

### Community 5 - "FP_Bacsain_Muit_3A/src/inference.py"
Cohesion: 0.29
Nodes (10): build_user_message(), _format_example(), generate_smtlib(), load_model(), main(), predict_label_and_answer(), no_grad, End-to-end pipeline: problem -> fine-tuned model -> SMT-LIB -> Z3 -> verdict.… (+2 more)

### Community 6 - "final_project/src/baselines.py"
Cohesion: 0.33
Nodes (8): generate(), load_model(), main(), parse_response(), no_grad, Baseline systems for comparison: 1. vanilla: base model, zero-shot, direct…, Heuristic parser. Returns (label, answer_or_None). label in {"solvable",…, _to_float()

### Community 7 - "final_project/src/data_loader.py"
Cohesion: 0.36
Nodes (8): load_raw(), main(), normalize_row(), Path, PMC dataset loader + train/val/test splitter. PMC dataset (Tian et al. 2024,…, Map PMC raw row to canonical schema. Return None if unparseable., Try .json (list) and .jsonl (one per line)., write_jsonl()

### Community 8 - "final_project/src/evaluate.py"
Cohesion: 0.39
Nodes (7): main(), Run evaluate.py on all 3 systems, build a combined LaTeX results table. Usage:…, latex_table_row(), main(), numeric_match(), Score predictions vs gold labels. Reports overall accuracy, per-class F1, macro…, score()

### Community 9 - "FP_Bacsain_Muit_3A/src/baselines.py"
Cohesion: 0.33
Nodes (8): generate(), load_model(), main(), parse_response(), no_grad, Baseline systems for comparison: 1. vanilla: base model, zero-shot, direct…, Heuristic parser. Returns (label, answer_or_None). label in {"solvable",…, _to_float()

### Community 10 - "FP_Bacsain_Muit_3A/src/evaluate.py"
Cohesion: 0.39
Nodes (7): main(), Run evaluate.py on all 3 systems, build a combined LaTeX results table. Usage:…, latex_table_row(), main(), numeric_match(), Score predictions vs gold labels. Reports overall accuracy, per-class F1, macro…, score()

### Community 11 - "final_project/src/fetch_data.py"
Cohesion: 0.36
Nodes (7): extract_gsm8k_answer(), fetch_gsm8k_solvable(), fetch_pmc(), main(), Download PMC + GSM8K, mix into balanced 3-class test set. PMC (kevin715/PMC on…, Extract the final numeric answer from GSM8K's chain-of-thought style., Load each PMC split separately to avoid column-schema merge errors.

### Community 12 - "FP_Bacsain_Muit_3A/src/fetch_data.py"
Cohesion: 0.36
Nodes (7): extract_gsm8k_answer(), fetch_gsm8k_solvable(), fetch_pmc(), main(), Download PMC + GSM8K, mix into balanced 3-class test set. PMC (kevin715/PMC on…, Extract the final numeric answer from GSM8K's chain-of-thought style., Load each PMC split separately to avoid column-schema merge errors.

### Community 13 - "final_project/src/plots.py"
Cohesion: 0.53
Nodes (5): fig_confusion(), fig_hallucination(), fig_perclass_f1(), main(), Generate figures for the final paper and poster. Outputs (in ../figures/):…

### Community 14 - "final_project/src/train_lora.py"
Cohesion: 0.47
Nodes (5): format_example(), load_jsonl(), main(), Supervised fine-tune a 7-8B base model on (problem -> SMT-LIB) pairs. LoRA via…, Build a chat-template-formatted training string. Loss is computed over the full…

### Community 15 - "FP_Bacsain_Muit_3A/src/plots.py"
Cohesion: 0.53
Nodes (5): fig_confusion(), fig_hallucination(), fig_perclass_f1(), main(), Generate figures for the final paper and poster. Outputs (in ../figures/):…

## Ambiguous Edges - Review These
- `CSAC 224 Natural Language Processing (course)` → `Final Project Poster PDF (FP_Poster_Bacsain_Muit_3A)`  [AMBIGUOUS]
  submission/FP_Poster_Bacsain_Muit_3A.pdf · relation: conceptually_related_to
- `Few-Shot Prompted LLM Translator (Stage 1: problem -> SMT-LIB v2)` → `Neuro-Symbolic Math Reasoning Pipeline README (final_project)`  [AMBIGUOUS]
  final_project/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **6 isolated node(s):** `run_all.sh script`, `run_smoke.sh script`, `run_all.sh script`, `run_smoke.sh script`, `The Neuro-Symbolic Concept Learner (Mao et al., 2019)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 76 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `CSAC 224 Natural Language Processing (course)` and `Final Project Poster PDF (FP_Poster_Bacsain_Muit_3A)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Few-Shot Prompted LLM Translator (Stage 1: problem -> SMT-LIB v2)` and `Neuro-Symbolic Math Reasoning Pipeline README (final_project)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Submission README (identical copy of final_project README)` connect `Submission README (identical copy` to `Mitigating Reasoning Hallucinations in`, `run_smtlib()`, `FP_Bacsain_Muit_3A/src/inference.py`, `FP_Bacsain_Muit_3A/src/baselines.py`, `FP_Bacsain_Muit_3A/src/evaluate.py`?**
  _High betweenness centrality (0.354) - this node is a cross-community bridge._
- **Why does `Neuro-Symbolic Math Reasoning Pipeline README (final_project)` connect `Mitigating Reasoning Hallucinations in` to `run_smtlib()`, `Submission README (identical copy`, `final_project/src/inference.py`, `final_project/src/baselines.py`, `final_project/src/data_loader.py`, `final_project/src/evaluate.py`, `final_project/src/train_lora.py`?**
  _High betweenness centrality (0.278) - this node is a cross-community bridge._
- **Why does `Two-Stage Neuro-Symbolic Pipeline (LLM translator + Z3 judge)` connect `Mitigating Reasoning Hallucinations in` to `Submission README (identical copy`, `final_project/src/inference.py`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **What connects `run_all.sh script`, `run_smoke.sh script`, `run_all.sh script` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Mitigating Reasoning Hallucinations in` be split into smaller, more focused modules?**
  _Cohesion score 0.0992063492063492 - nodes in this community are weakly interconnected._