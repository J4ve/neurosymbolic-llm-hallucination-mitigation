# Poster Plan (layman-friendly)

**Goal:** non-CS person walking past in 30 seconds gets it.

**Title (big, plain):**
> Teaching AI to Say "I Don't Know" When Math Problems Are Broken

**Authors line:** Jave Bacsain, Ivy Pauline Muit — CSAC 224 NLP, CSPC

## Size + tool

A1 portrait (594 × 841 mm) for hallway viewing.
Make in PowerPoint, export PDF for printing.

---

## Layout — 3 columns, top-to-bottom

### Column 1 — The Problem

**Box: "The lying chatbot"**

- Cartoon: chatbot face confidently saying "$15" to broken math problem
- Caption: "AI chatbots make up confident answers — even when problem
  is impossible to solve."

**Box: "Example broken problem"**

> *John spent $10 and has $5 left. He also has $50 left.
>  How much did he start with?*

Below in red: "Contradiction! Can't have both $5 and $50."
Below in red: "Chatbot answer: $15  ← WRONG (made up)"

**Box: "Why this matters"**

Plain icons + 1-line each:
- 💊 Medical dosing — wrong dose = harm
- 💰 Finance — wrong calculation = lost money
- 📝 Grading — wrong score = unfair

### Column 2 — Our Solution

**Big diagram (centerpiece of poster):**

```
   English math problem
            ↓
   [ Chatbot — TRANSLATOR ONLY ]   ← writes problem as logic code
            ↓
       Logic code (SMT-LIB)
            ↓
   [ Z3 logic tool — JUDGE ]        ← proves; cannot lie
            ↓
   ┌────────┴────────┐
   ↓        ↓        ↓
Answer   "REJECT"  "REJECT"
       (contradicts) (missing info)
```

Caption below diagram: "Chatbot translates. Z3 decides. Chatbot can't
sneak in a fake answer because Z3 is the gatekeeper."

**Box: "What is Z3?"**

- Free logic tool from Microsoft Research
- Used in real software (security, hardware design)
- Doesn't guess — it PROVES
- If logic has solution → tells you the number
- If logic contradicts → says UNSAT
- If many solutions → says SAT but with multiple answers

**Box: "Where data came from"**

- 600 math problems, balanced 3 ways:
  - 200 normal (have answer) — from GSM8K (grade-school math)
  - 200 missing info — from PMC benchmark
  - 200 contradictory — from PMC benchmark
- All free + public (HuggingFace)

### Column 3 — Results

**HEADLINE (biggest visual on poster):**

> ## Hallucination rate dropped ~10×

**Bar chart, three bars side by side:**

```
  Plain chatbot          ████████████████████  19%
  Step-by-step chatbot   █████████████████████ 21%
  OUR SYSTEM             ██                    2%  ← in bright color
```

Big caption: "Out of 400 broken problems, plain chatbots faked 80
confident answers. Ours faked only 8."

**Smaller table — full picture:**

| System | Got overall right | Faked wrong answers on broken problems |
|---|---|---|
| Plain chatbot | 59% | 19% |
| Step-by-step | 60% | 21% |
| **Ours** | 35% | **2%** |

**Box: "Honest trade-off"**

✅ Win: 10× fewer fake-confident answers when problem is broken
❌ Cost: Sometimes refuses problems that DO have an answer
   (chatbot wrote incomplete logic, so Z3 found too many solutions)

**Box: "What's next"**

- Train the translator instead of just prompting → better logic code
- Tag units (dollars vs %) in logic → fix unit mistakes
- Combine with VCSearch's smart search

---

## Footer band

- **QR code** linking to GitHub repo (https://github.com/J4ve/NLP_FP)
- "CSAC 224 — Natural Language Processing — Final Project, 2026"
- "Compute: AI Research Center for Community Development HPC, CSPC"

---

## Visual style

- White background, plain dark text
- One **bright accent color** (suggest amber #E8A33D) — ONLY for the
  "Ours = 2%" bar and headline number. Eye goes there first.
- Boxes outlined in dark blue (#1F3A5F) — clean grid feel

## Typography

- Title: 72 pt bold sans-serif (Inter / Calibri / Helvetica)
- Section headers: 36 pt bold
- Body text: 22 pt
- Caption / footer: 18 pt
- Code / math: monospace 18 pt

## Pre-print checklist

- [ ] Walk 1 meter back from screen — headline still readable?
- [ ] Walk 3 meters back — can still tell what poster is about?
- [ ] No text smaller than 18 pt
- [ ] QR code scans on phone
- [ ] All 3 names + emails legible
- [ ] Export at 300 DPI
- [ ] Test print on letter paper at scaled size before final A1 print

---

## Quick elevator pitch (for when judge asks)

> "Chatbots lie when math problems are broken. We made them pass the
> problem to a logic tool first. Logic tool either solves it or says
> 'this is impossible'. Result: ten times fewer lies on broken
> problems."

If judge wants more: "But our chatbot writes imperfect logic, so we
sometimes refuse problems that actually have answers. Trade-off:
safer but more cautious. Good when wrong answer is dangerous, like
medicine or money."
