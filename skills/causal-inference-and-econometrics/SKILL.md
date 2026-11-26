---
name: causal-inference-and-econometrics
description: >-
  Design and audit causal identification studies and econometric analyses across
  Finance, Healthcare/Chemistry, Policy, and A/B experiments. Covers causal DAGs
  (confounders vs. colliders/mediators), Difference-in-Differences (DiD / staggered),
  Instrumental Variables (2SLS), Regression Discontinuity, Synthetic Controls,
  Double Machine Learning (DML), covariate balance, and clustered / Newey-West HAC
  standard errors. Use this skill whenever estimating treatment effects rather than
  pure correlations.
---

# Causal Inference & Econometrics

Prediction models optimize $\mathbb{E}[Y \mid X]$; causal studies estimate $\mathbb{E}[Y \mid \operatorname{do}(T=1)] - \mathbb{E}[Y \mid \operatorname{do}(T=0)]$. Adding more predictive features or a deeper neural net **worsens** bias if you condition on a collider or post-treatment mediator!

## 1. Identification Before Estimation

1. **Draw the Causal DAG First**:
   - **Confounders** ($X \to T$ and $X \to Y$): **Must adjust** to close backdoor paths.
   - **Mediators** ($T \to M \to Y$): **Do not adjust** when estimating total treatment effect.
   - **Colliders** ($T \to C \leftarrow Y$): **Never adjust**—conditioning on a collider opens a spurious correlation (selection/Berkson bias)!
2. **Choose the Matching Quasi-Experimental Design**:
   - **Difference-in-Differences (DiD)**: Verify **parallel pre-trends** via an event-study plot; for staggered adoption across cohorts, use Callaway–Sant'Anna or Sun–Abraham estimators rather than naive Two-Way Fixed Effects (TWFE suffers negative weighting!).
   - **Instrumental Variables (2SLS)**: Prove relevance (first-stage $F > 10$, Stock–Yogo) AND defend exclusion restriction ($Z$ affects $Y$ *only* through $T$).
   - **Regression Discontinuity (RDD)**: Run McCrary running-variable density manipulation check and local-linear bandwidth sensitivity checks.
   - **Double / Debiased Machine Learning (DML)**: Always use **$K$-fold cross-fitting** when plugging ML nuisance models ($\hat{m}(X), \hat{e}(X)$) into Neyman-orthogonal scores so regularization bias vanishes at $\sqrt{N}$ rate!
3. **Econometric Standard Errors & Falsification**:
   - Never report naive i.i.d. OLS standard errors on panel/time-series financial data: use **Newey–West HAC** (autocorrelation) or **two-way entity + time clustered SEs** (Petersen / Cameron–Gelbach–Miller).
   - Run **placebo tests** (fake treatment date, unaffected outcome, or permutation randomization inference) to confirm effects aren't spurious trends.

## 2. Covariate Balance, DiD & Newey–West HAC CLI

Run [causal_diagnostics.py](./scripts/causal_diagnostics.py) to check treated/control covariate balance (Standardized Mean Differences, flagging $|\text{SMD}| > 0.1$), compute 2×2 DiD ATE with robust SEs, or run OLS with Newey–West HAC standard errors:

```bash
python3 skills/causal-inference-and-econometrics/scripts/causal_diagnostics.py --self-test
```
