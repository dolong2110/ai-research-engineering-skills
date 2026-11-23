---
name: quant-finance-ml
description: >-
  Conduct rigorous AI, deep learning, time-series, and LLM research in Quantitative
  Finance (alpha forecasting, limit order books, portfolio optimization, risk modeling,
  and financial NLP). Enforces point-in-time data integrity, purged/embargoed
  walk-forward validation, survivorship-bias & LLM knowledge-cutoff controls,
  transaction-cost-adjusted backtesting, and IC/Sharpe/Deflated-Sharpe metrics.
  Use this skill whenever working on financial ML, market time series, trading
  backtests, or financial LLM research.
---

# Quantitative Finance & Financial AI Research

Financial ML papers face intense reviewer scrutiny (ICAIF, KDD, NeurIPS/ICML Time-Series, Journal of Financial Data Science, Quantitative Finance) because tiny temporal or pretraining leaks create illusory Sharpe ratios of `4.0+` that collapse out-of-sample. Always enforce the rules below.

## 1. Zero Temporal, Point-in-Time & Pretraining Leakage

Read [finml_pitfalls_and_venues.md](./references/finml_pitfalls_and_venues.md) before designing splits or features. Non-negotiable invariants:

1. **Never Use Random K-Fold on Market Data**:
   - Use **Expanding/Rolling Walk-Forward Validation** or **Purged & Embargoed K-Fold CV**: when labels span $[t, t+h]$, purge any training sample whose label horizon overlaps the validation window $[t_{\text{val\_start}}, t_{\text{val\_end}}]$, and add an embargo buffer after $t_{\text{val\_end}}$ for autocorrelated features.
2. **Point-in-Time (PiT) Timestamps Only**:
   - Index earnings, macro releases, fundamentals (Compustat/SEC 10-K/10-Q), and news by **actual public release / filing timestamp** (`acceptance_datetime`), never fiscal quarter-end date (`datadate`).
   - Fit rolling z-score / winsorization statistics strictly on a trailing lookback window $[t-W, t]$—never `StandardScaler().fit(full_df)`.
3. **Survivorship-Free Universe**:
   - Include delisted, bankrupt, and acquired tickers using historical point-in-time index constituents.
4. **LLM Knowledge-Cutoff Guard (Critical for Financial NLP / LLMs)**:
   - Pretrained LLMs know which companies surged or went bankrupt prior to their pretraining cutoff!
   - Always evaluate Financial LLM forecasting/sentiment on a **strictly post-cutoff out-of-time test window** (or anonymized entity-masked transcripts verified for memorization).

## 2. Required Signal & Portfolio Evaluation Metrics

Never report MSE or raw accuracy alone—small MSE improvements often concentrate on illiquid micro-caps or vanish under 5–10 bps turnover costs:
- **Signal Predictive Power**: Daily cross-sectional **IC** (Pearson) and **Rank IC** (Spearman), **ICIR** ($\mu_{\text{IC}} / \sigma_{\text{IC}}$), and $t$-statistic with Newey–West HAC standard errors.
- **Portfolio Economics (Gross AND Net of Transaction Costs)**: Annualized Return, Volatility, **Sharpe Ratio**, **Sortino Ratio**, **Calmar Ratio**, **Maximum Drawdown (MDD)**, **One-Way Turnover**, **Break-Even Cost (bps)**, and **Probabilistic / Deflated Sharpe Ratio (PSR / DSR)** accounting for non-normal fat tails and multiple backtest trials.
- **Regime Stratification**: Slice performance across bull, bear/crisis, and high-volatility VIX regimes.

## 3. Automated Leakage & Net-of-Cost Backtest CLI

Run [backtest_and_leakage_audit.py](./scripts/backtest_and_leakage_audit.py) on prediction CSVs (`timestamp,asset,signal,realized_return`) to verify temporal ordering and compute cross-sectional IC, Rank IC, ICIR, long-short quantile Sharpe (gross & net of bps), Turnover, Max Drawdown, and PSR:

```bash
python3 skills/quant-finance-ml/scripts/backtest_and_leakage_audit.py \
  --input runs/predictions.csv \
  --cost-bps 10 \
  --periods-per-year 252
```
