---
name: research-paper-writer
description: >-
  Creates formal academic research papers following IEEE and ACM formatting
  standards with structured sections (Abstract, Introduction, Related Work,
  Methodology, Implementation, Evaluation, Discussion, Conclusion, References),
  numbered/ACM citations, and scholarly writing style. Use when the user asks to
  write a formal IEEE or ACM research paper, survey paper, experimental conference
  paper, or journal manuscript on any topic.
---

# Research Paper Writer (IEEE & ACM)

This skill guides the creation of formal academic research papers meeting publication standards for **IEEE** and **ACM** conferences and journals. It covers scope clarification, survey and experimental paper structures, iterative drafting, citation formatting, and venue-specific typography.

## Workflow

### 1. Clarify Topic and Scope (Required Before Drafting)

Always confirm scope with the user before writing:
- **Research question / core contribution**: What specific problem, method, or survey taxonomy is the paper presenting?
- **Paper type**: Experimental/empirical paper, theoretical paper, system paper, or literature survey?
- **Target venue & format**: Conference vs. journal, and **IEEE** (default) vs. **ACM** (`acmart`) formatting standard?
- **Target length**: Page count (e.g., 6–8 pages conference, 10–15 pages journal/survey) or word count?
- **User-supplied research substance**: Gather any notes, experimental logs, datasets, metrics, baselines, or key references (the skill structures and drafts; never invent experimental results or fake citations).

### 2. Standard Academic Paper Structure

1. **Title and Abstract**: Concise contribution-focused title; self-contained 150–250 word abstract (context -> problem/gap -> approach -> quantitative results -> contribution).
2. **Introduction**: Real-world motivation, inverted-pyramid problem framing, explicit research gap, 3–5 concrete contribution bullets, and paper organization roadmap.
3. **Related Work / Background**: Grouped thematically (not chronologically), explicitly contrasting prior limitations against the proposed work.
4. **Methodology / Approach / System Design**: Core formulation, architecture/algorithmic steps, and design rationale.
5. **Implementation** *(if applicable)*: Technical stack, hyperparameters, hardware/runtime details, and engineering challenges solved.
6. **Evaluation / Experiments / Results**: Experimental setup, datasets/scenarios, metrics, baselines, structured tables/figures, and objective quantitative + ablation analysis.
7. **Discussion**: Implications, honest limitations, and threats to validity.
8. **Conclusion and Future Work**: Summary of verified contributions and concrete next directions.
9. **References**: Minimum 15–20 verified references for a full paper, balancing foundational works and recent (last 5 years) publications.

### 3. Iterative Drafting Order

1. **Create a detailed outline** first (section bullets + planned figures/tables) and align with the user.
2. **Draft in high-coherence order**:
   1. Methodology (locks core technical terminology and notation)
   2. Evaluation / Results (grounds quantitative claims)
   3. Introduction (now aligned tightly with actual method and results)
   4. Related Work (positioned directly against finalized contributions)
   5. Discussion & Conclusion
   6. Abstract **last** (so every number and claim matches the completed body)
3. **Verify & Polish**:
   - Check every figure/table/equation is referenced in text.
   - Verify every acronym is defined on first use.
   - Pair with `writing-papers` (`manuscript_prose_lint.py`) and `literature-and-citations` (`audit_citations.py`) to check prose style and BibTeX completeness.

## Detailed Formatting & Style References

Load the matching reference guide as needed:
- **IEEE specifications** (two-column A4/Letter layout, 10pt Times, section numbering, captions, IEEE numbered `[1]` bibliography): [ieee_formatting_specs.md](./references/ieee_formatting_specs.md)
- **ACM specifications** (`acmart` class, CCS Concepts, Keywords, single-column abstract / two-column body, ACM Reference Format): [acm_formatting_specs.md](./references/acm_formatting_specs.md)
- **Academic writing style conventions** (voice, tense, precision, argumentation, survey vs. experimental templates): [writing_style_guide.md](./references/writing_style_guide.md)

## Integrity Notes

- **Never fabricate metrics, baselines, or BibTeX entries.** If technical details or experimental outputs are missing, pause and ask the user for them.
- **Acknowledge limitations honestly** (scope boundaries, assumptions, negative results).
