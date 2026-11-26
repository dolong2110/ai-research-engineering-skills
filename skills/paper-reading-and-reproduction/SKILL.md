---
name: paper-reading-and-reproduction
description: >-
  Deconstruct academic papers systematically (3-pass reading, equation-to-code
  mapping, extracting hidden appendix hyperparameters and preprocessing quirks)
  and reproduce baseline results faithfully within tolerance before modifying or
  extending them. Use this skill when reading research papers deeply, implementing
  a method from a PDF, or debugging why a reproduced baseline falls short of Table 1.
---

# Deep Paper Reading & Baseline Reproduction

Before proposing an improvement over a prior method, you must understand its real assumptions and reproduce its reported baseline faithfully.

## 1. The 3-Pass Technical Deconstruction

1. **Pass 1 — Structural Triage (5 min)**:
   - Read Title, Abstract, Section headings, Figure 1/2, Table 1, and Conclusion. Summarize: *What is the exact claim? What dataset/metric/baseline backs it? What assumptions might break?*
2. **Pass 2 — Mechanism & Math Audit (20 min)**:
   - Map every symbol and equation in Methodology to exact tensor shapes (`[B, T, D]`), loss signs, gradient stop operations (`detach`), and inference-time differences (EMA weights, beam search, test-time augmentation).
3. **Pass 3 — Hidden Appendix & Code-Gap Mining (30 min)**:
   - Always check the **Appendix and official GitHub repo** for silent performance drivers that rarely appear in the main text:
     - Data filtering / cleaning rules (dropped NaNs, outlier winsorization, salt stripping, split seed)
     - Optimizer quirks (weight decay exclusions on LayerNorm/bias, cosine warmup steps, gradient clipping, EMA decay)
     - Metric calculation specifics (macro vs. micro F1, exact padding/EOS truncation, evaluation batch size, `eval()` vs `train()` dropout/BN)

## 2. Equation-to-Code Reproduction Protocol

Copy and fill [reproduction_matrix_template.md](./resources/reproduction_matrix_template.md):
1. **Lock Baseline First (No Early "Improvements")**: Implement the paper's exact method first—resist tweaking losses or architectures until your reproduced metric matches Table 1 within multi-seed variance (typically $\pm 0.5\%$–$1\%$).
2. **Run the 4-Check Sanity Suite**: Verify shapes, gradient flow, batch independence, and 2-sample single-batch overfit (`testing-and-verification`) before full runs.
3. **Diagnose Reproduction Gaps Systematically**:
   - If reproduced score trails Table 1 by $>2\%$, audit in order: **(1) Data split & preprocessing**, **(2) Metric implementation** (test on author's released predictions if available), **(3) Initialization & LR schedule**, **(4) Hidden loss weighting / regularization**.
