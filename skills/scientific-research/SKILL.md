---
name: scientific-research
description: >-
  Conduct rigorous scientific and AI/ML research: problem scoping, literature gap
  taxonomy, falsifiable hypothesis formulation, minimal viable experiments (MVEs),
  fair baseline & ablation study design, multi-seed statistical significance testing,
  error analysis, and reproducibility protocols. Use this skill whenever planning,
  executing, or analyzing research investigations and experiments.
---

# Scientific Research Methodology

Use this skill to enforce top-tier empirical and theoretical research rigor across problem formulation, experimental design, statistical analysis, and failure-mode investigation.

## 1. Problem Scoping & Falsifiable Hypothesis Design

Before writing training or benchmark code, establish a crisp research protocol using [research_protocol_template.md](./resources/research_protocol_template.md):

1. **Identify the Exact Research Gap** (avoid "nobody combined X and Y yet" without a bottleneck):
   - ** Bottleneck / Failure-Mode Gap**: Existing methods degrade sharply under a specific regime (long horizon, low data, distribution shift, high resolution, memory ceiling).
   - **Assumption Flaw**: Prior theory or objectives rely on an assumption violated in practice.
   - **Evaluation / Confounder Gap**: Apparent SOTA gains stem from leaked data, mismatched compute/tuning, or flawed metrics.
2. **Apply the Heilmeier Gate**:
   - What is the concrete problem, why do current approaches fail, what is the specific mechanism of your new insight, and **what single diagnostic experiment could falsify your hypothesis fastest?**
3. **Run a Minimal Viable Experiment (MVE) First**:
   - Design a toy/small-scale diagnostic (<10% of full compute budget) that directly tests the core mechanism (e.g., measuring gradient conflict, attention entropy, or latent alignment) *before* launching full benchmark sweeps.

## 2. Fair Baselines & Systematic Ablations

Read [experimental_design_and_stats.md](./references/experimental_design_and_stats.md) when constructing comparison tables and ablation matrices.

Core rules:
- **Resource Parity**: Match backbone capacity, training data, augmentation, token/epoch budget, and hyperparameter tuning effort across your method and baselines. State explicitly when numbers are copied from prior papers vs. re-run under unified settings.
- **Four Mandatory Ablation Dimensions**:
  1. *Leave-One-Out / Build-Up*: Isolate marginal contribution and synergy of every proposed module/loss term.
  2. *Mechanism Swap*: Replace your novel module with a simpler parameter-matched baseline (e.g., MLP/linear adapter) to prove gains come from *structure*, not extra parameters.
  3. *Sensitivity*: Sweep key hyperparameters (`k`, depth, loss weight $\lambda$, temperature $\tau$) across $\ge 3$ values to demonstrate stability.
  4. *Compute / Latency Overhead*: Report parameter count, FLOPs, peak VRAM, and wall-clock throughput alongside accuracy metrics.

## 3. Multi-Seed Statistical Significance & Table Generation

Never claim an improvement is "statistically significant" without multi-seed variance and a paired test. Run [analyze_experiment_stats.py](./scripts/analyze_experiment_stats.py) on multi-seed CSV or JSON results to compute `mean ± std`, 95% bootstrap confidence intervals, paired $t$-test & Wilcoxon $p$-values, Cohen's $d$, and ready-to-paste Markdown + LaTeX `booktabs` rows:

```bash
python3 skills/scientific-research/scripts/analyze_experiment_stats.py \
  --input runs/multi_seed_results.csv \
  --baseline "Baseline_SOTA" \
  --metrics "Seen_J:max,Unseen_J:max,Null_S:min"
```

## 4. Error Analysis & Honest Negative Results

- Stratify evaluation metrics by difficulty slice (object size, sequence length, rare/unseen classes, SNR).
- Inspect the worst-performing 5% of test examples qualitatively to identify concrete failure modes—these directly strengthen both the next research iteration and the paper's Limitations section.
