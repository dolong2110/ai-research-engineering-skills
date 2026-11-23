# Section-by-Section Blueprints & Reviewer Expectations

## 1. Introduction (The 5-Paragraph Funnel)

1. **Paragraph 1 — Motivation & Stakes**: Define the task and why solving it matters practically or scientifically. Keep broad throat-clearing ("Deep learning has revolutionized...") to zero sentences.
2. **Paragraph 2 — The Concrete Bottleneck**: Pinpoint the exact technical limitation of existing paradigms (e.g., *static encoders discard cross-frame object permanence, while manual point prompts require human-in-the-loop clicks*). Reference `\cref{fig:teaser}` (left) showing the failure mode visually.
3. **Paragraph 3 — Key Insight**: State your core hypothesis in one bold/italicized or crystal-clear sentence (*"Our key insight is that aligned audio-text correlations can be projected directly into SAM's native geometric prompt space..."*).
4. **Paragraph 4 — Technical Realization & Empirical Headline**: Briefly explain how your modules instantiate that insight (`\cref{fig:teaser}`, right) and summarize headline gains across primary benchmarks (e.g., `+9.2% Seen J and +5.0% Unseen J over prior SOTA at 1.08× inference cost`).
5. **Paragraph 5 — Verifiable Contributions**:
   - **Contribution 1 (Formulation/Theory):** Specific architectural/algorithmic contribution (`\cref{sec:method}`).
   - **Contribution 2 (Component/Mechanism):** Specific technical module solving the bottleneck (`\cref{sec:module_b}`).
   - **Contribution 3 (Empirical/Analytical):** Comprehensive validation, ablations, and new insights across [X] benchmarks (`\cref{sec:experiments}`).

## 2. Methodology (Top-Down Clarity)

- **Preliminaries / Problem Formulation (`3.1`)**: Define input domain $\mathcal{X}$, output space $\mathcal{Y}$, tensor shapes (e.g., $\mathbf{V} \in \mathbb{R}^{T \times H \times W \times 3}$), and base model equations *once* so subsequent subsections stay uncluttered.
- **System Overview (`3.2` + Figure 2)**: Walk left-to-right through the architecture diagram in 1 paragraph using the **exact same module names and math symbols** drawn in Figure 2.
- **Module Subsections (`3.3`, `3.4`, ...)**:
  1. *Design Goal*: One sentence stating what sub-problem this module solves.
  2. *Formulation*: Numbered equations (`\begin{equation} ... \label{eq:...} \end{equation}`) integrated grammatically into sentences with trailing commas/periods.
  3. *Why This Form?*: Explain why this operator/loss works better than naive alternatives (anticipation of reviewer "Why not just concatenate?" questions).
- **Training & Inference Summary (`3.5`)**: Unified objective $\mathcal{L} = \mathcal{L}_{\text{task}} + \lambda \mathcal{L}_{\text{aux}}$ and inference complexity.

## 3. Experiments (Driven by Research Questions)

Structure the section so reviewers never wonder *why* a table exists:
- **4.1 Experimental Setup**: Datasets & splits, evaluation metrics (`↑`/`↓`), baselines grouped by family, and key implementation details (full hyperparams in Appendix).
- **4.2 Main Comparison (`RQ1: Does [Method] outperform SOTA on Seen and Unseen regimes?`)**: Lead each paragraph with a bold takeaway sentence, cite `\cref{tab:main}`, highlight gains on the hardest split, and honestly explain any metric where a baseline wins (e.g., Null-set behavior).
- **4.3 Ablation Study (`RQ2: Which components drive the gains?`)**: Reference `\cref{tab:ablation}`; analyze single-component drops *and* multi-component interactions.
- **4.4 Sensitivity & Efficiency (`RQ3: How sensitive is [Method] to hyperparameters and compute?`)**: Trade-off curves/tables for $k$, depth $M$, latency, and memory.
- **4.5 Qualitative & Failure-Mode Analysis (`RQ4: Where does [Method] succeed and still fail?`)**: Multi-column visual comparison + honest failure case visualization.
