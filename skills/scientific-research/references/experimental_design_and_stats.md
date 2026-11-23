# Experimental Design, Controls & Statistical Rigor Reference

## 1. Preventing Common Confounders in AI/ML Experiments

| Confounder | Symptom | Required Control |
| :--- | :--- | :--- |
| **Parameter / Compute Inflation** | Adding an auxiliary module increases params/FLOPs by 15% and improves accuracy by 1%. | Include a **parameter-matched vanilla baseline** (wider/deeper backbone or standard MLP adapter). |
| **Unequal Hyperparameter Tuning** | Proposed method tuned over 30 runs; baselines run with default repo LR. | Tune LR and regularization on validation split using identical grid/budget for top baselines. |
| **Test-Set Leakage / Over-Selection** | Selecting checkpoint or hyperparameters based on test metrics. | Lock hyperparameters on `val`; evaluate `test` strictly once per seed after model selection. |
| **Single-Seed Luck** | Delta is +0.4% while run-to-run standard deviation is ±0.6%. | Run $N \ge 3$ (ideally $N = 5$) independent random seeds (`data shuffle + init`). |
| **Metric Gaming** | High precision via ultra-conservative predictions, or improvement on Seen at heavy cost to Null/OOD. | Report complementary trade-off metrics (Precision + Recall / F1, Seen + Unseen + Null, Accuracy + Calibration/ECE). |

## 2. Choosing the Right Statistical Test

- **Paired $t$-test (or Paired Permutation / Bootstrap Test)**: Use when comparing two models evaluated on the **same** set of random seeds, cross-validation folds, or per-instance test items ($N$ paired observations).
- **Wilcoxon Signed-Rank Test**: Non-parametric alternative to the paired $t$-test when per-slice/per-dataset deltas are skewed or contain outliers (standard across multi-dataset benchmarks like GLUE, VTAB, or MTEB).
- **McNemar's Test**: Comparing binary classification accuracy of two models on the exact same test set when only 1 training run is feasible (e.g., frontier LLM evaluation).
- **Holm-Bonferroni Correction**: Apply whenever testing multiple hypotheses/metrics simultaneously to control family-wise error rate ($\alpha = 0.05$).

## 3. Reproducibility Artifacts Checklist

Record for every experiment run:
1. Exact git commit hash (and dirty diff if any).
2. Python, CUDA/ROCm, and framework (`torch`, `jax`, `transformers`) versions.
3. Exact training/eval CLI command and config YAML/JSON.
4. Random seeds (`python`, `numpy`, `torch`, dataloader worker seeds).
5. Hardware model, GPU count, precision (`fp32`, `bf16`, `fp16`), wall-clock training hours, and peak GPU memory.
