---
name: bayesian-uncertainty-and-active-learning
description: >-
  Quantify predictive uncertainty, calibrate probabilities (ECE, Brier, NLL,
  temperature scaling), construct distribution-free Conformal Prediction intervals,
  and run sample-efficient Bayesian Optimization / Active Learning (Gaussian
  Processes, BoTorch, Optuna, EI/UCB/Thompson). Use this skill for chemistry
  active learning, financial risk intervals, LLM abstention calibration, or
  expensive black-box hyperparameter optimization.
---

# Uncertainty Quantification, Conformal Prediction & Bayesian Optimization

High accuracy without calibrated uncertainty causes catastrophic failures in molecular wet-lab selection, financial position sizing, and LLM selective abstention.

## 1. Probability Calibration Discipline

1. **Always Report Proper Scoring Rules Alongside AUROC/Accuracy**:
   - **Expected Calibration Error (ECE)**, **Maximum Calibration Error (MCE)**, **Brier Score**, and **Negative Log-Likelihood (NLL)**.
2. **Post-Hoc Calibration Without Leakage**:
   - Fit temperature scaling $p_i = \operatorname{softmax}(z_i / T)$ (or isotonic/Platt scaling) strictly on a held-out **validation/calibration split**—never on test labels!

## 2. Split & Adaptive Conformal Prediction (Distribution-Free Coverage)

When you need rigorous $(1-\alpha)$ prediction intervals or sets with finite-sample guarantees (assuming exchangeability—or using Adaptive Conformal Inference `ACI` for non-stationary financial time series!):
1. Split data into `train`, `cal` ($n_{\text{cal}} \ge 200$ recommended), and `test`.
2. Compute nonconformity scores $s_i = |y_i - \hat{y}_i|$ (or normalized $|y_i - \hat{y}_i| / \hat{\sigma}_i$ for heteroscedastic intervals!) on `cal`.
3. Take the $\lceil (n_{\text{cal}} + 1)(1 - \alpha) \rceil / n_{\text{cal}}$ empirical quantile $\hat{q}$ -> guarantees $\mathbb{P}(Y_{\text{test}} \in [\hat{y} - \hat{q}, \hat{y} + \hat{q}]) \ge 1 - \alpha$.
4. Report **both Empirical Coverage AND Mean Interval Width** (trivial infinite intervals give 100% coverage with zero utility!).

## 3. Bayesian Optimization & Active Learning Loops

- **Surrogate Choice**:
  - Continuous low-D ($D \le 20$): **Gaussian Process (Matérn-5/2 ARD)** via BoTorch/GPyTorch.
  - Molecular / Discrete Graphs: **Tanimoto-kernel GP on ECFP4**, **Deep Ensembles (5 members)**, or **Evidential/Laplace last-layer neural surrogate**.
- **Acquisition & Batch Diversity**: Use **qLogEI / qNEI** or **Thompson Sampling** for parallel batches (`q > 1`) so experiments explore diverse scaffolds/regions rather than selecting 10 identical near-duplicates!

## 4. Calibration & Split Conformal Prediction CLI

Run [calibration_and_conformal.py](./scripts/calibration_and_conformal.py) to compute ECE, MCE, Brier, NLL, and validate Split Conformal coverage & interval width:

```bash
python3 skills/bayesian-uncertainty-and-active-learning/scripts/calibration_and_conformal.py --self-test
```
