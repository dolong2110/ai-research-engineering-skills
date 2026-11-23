---
name: writing-papers
description: >-
  Author, structure, edit, and polish high-impact academic research papers across
  Abstract, Introduction, Related Work, Methodology, Experiments, Discussion, and
  Limitations. Enforces top-conference rhetorical blueprints, mathematical notation
  consistency, table/figure storytelling, LaTeX micro-typography, and zero AI-slop
  prose. Use this skill whenever drafting, rewriting, or editing scientific
  manuscripts or sections.
---

# Writing High-Impact Academic Papers

Use this skill when drafting new manuscript sections, refining `raw_draft_paper.tex` after PaperOrchestra runs, or editing human-written LaTeX/Markdown papers to top-conference standards (NeurIPS, ICLR, ICML, CVPR, ACL, Nature/IEEE).

## 1. Rhetorical Blueprints by Section

Read [section_blueprints.md](./references/section_blueprints.md) before drafting or restructuring major sections. Core invariants:

- **Title**: Specific and mechanism-driven (`[Name]: [Core Mechanism] for [Problem/Regime]`). Avoid empty hype ("Towards Universal...", "A Novel Framework for...").
- **Abstract (5-Move Arc, 150–220 words)**:
  1. *Context & Task* (1 sentence)
  2. *Concrete Bottleneck in Prior Work* (1 sentence)
  3. *Key Insight & Mechanism* (1–2 sentences)
  4. *Specific Quantitative Gains* (1–2 sentences with exact benchmark deltas, not "state-of-the-art results")
  5. *Takeaway / Generality* (optional 1 sentence). **Never put `\cite{}` or undefined acronyms in the Abstract.**
- **Introduction (1–1.5 pages)**:
  - Open with the *problem and bottleneck*, hook to a **Page-1/2 Teaser Figure** (`\cref{fig:teaser}`) that visually contrasts failure of prior work vs. your insight, summarize your technical approach, and end with **3–4 crisp, verifiable Contribution Bullets**—every bullet must forward-reference the exact section, equation, table, or theorem that proves it!
- **Related Work**:
  - Group into **2–4 conceptual sub-axes**, never chronological "Paper A did X. Paper B did Y." End each paragraph with an explicit contrast sentence explaining *how and why* your formulation differs.
- **Methodology**:
  - Present top-down: Problem Formulation & Notation -> Architecture Overview (`\cref{fig:overview}`) -> Core Modules (each following **Motivation -> Mathematical Formulation -> Intuition & Complexity**). Define every symbol immediately before or after its first equation.
- **Experiments**:
  - Organize subsections around explicit **Research Questions (`RQ1..RQ4`)** or clear analytical takeaways as paragraph lead-ins (e.g., `\textbf{Temporal memory prevents mask drift on unseen classes.}`). Never dump a table and merely repeat its numbers in prose—explain *why* the pattern occurs.
- **Limitations & Conclusion**:
  - State concrete technical boundary conditions (compute trade-offs, failure slices, assumptions), not disguised humblebrags.

## 2. Academic Prose Style & Mathematical Micro-Typography

Read [academic_style_and_anti_patterns.md](./references/academic_style_and_anti_patterns.md) for strict prose, math, and LaTeX rules. Key highlights:
- **Zero LLM Puffery**: Ban words like *delve, tapestry, testament, pivotal, groundbreaking, paradigm shift, intricate, underscore, realm, foster*, and unquantified *dramatically/significantly* (reserve *statistically significant* strictly for $p < \alpha$).
- **Self-Contained Captions**: Readers skim Title -> Abstract -> Figures -> Tables first. Every caption must state **(1) What is shown**, **(2) Setup/metric cue**, and **(3) The 1-sentence takeaway**.
- **Math & LaTeX Hygiene**: Non-breaking space `~` before `\cite`/`\ref` (when not using `\cref`), `--` en-dashes for numeric ranges (`10--15`), `\log`/`\exp`/`\max`/`\operatorname{softmax}` instead of italic math words, punctuation inside displayed equations, and `booktabs` (`\toprule`, `\midrule`, `\bottomrule`) with **zero vertical lines**.

## 3. Automated Prose, Notation & LaTeX Typography Lint

Always run [manuscript_prose_lint.py](./scripts/manuscript_prose_lint.py) after drafting or editing `.tex` / `.md` manuscripts to catch AI-isms, unreferenced `\label`s, citations in the abstract, vertical table rules, and math operator errors:

```bash
python3 skills/writing-papers/scripts/manuscript_prose_lint.py \
  --file paper_output_my_study/latex_writeup/raw_draft_paper.tex
```
