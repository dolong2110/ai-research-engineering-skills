# Financial ML Pitfalls, Baselines & Venue Guide

## 1. Mandatory Baselines by Subfield

Reviewers reject deep/LLM architectures in finance if simple domain baselines are omitted:
- **Cross-Sectional Return / Alpha Prediction**: Linear Ridge/Lasso, **LightGBM / XGBoost / CatBoost** (often stronger than deep tabular/time-series nets!), Fama–French / Momentum / Reversal factors, plus modern TS models (PatchTST, iTransformer, Mamba/Transformer).
- **Limit Order Book (LOB) Microstructure**: Linear OFI (Order Flow Imbalance), DeepLOB, TLOB / Axial-Attention baselines; evaluate across multiple prediction horizons ($k \in \{10, 50, 100\}$ ticks) and explicitly account for bid-ask spread crossing + queue-position latency.
- **Volatility & Risk Forecasting**: HAR-RV (Corsi), GARCH(1,1) / EGARCH, Quantile Regression (evaluating Pinball Loss + Kupiec/Christoffersen VaR coverage tests).
- **Financial NLP / Agentic Analysts**: FinBERT / DeBERTa fine-tuned baseline, BM25 + lexical Loughran–McDonald dictionary baseline, zero-shot vs. RAG-grounded frontier LLM, evaluated strictly post-knowledge-cutoff.

## 2. Common Subtle Leaks Checklist

- [ ] **Adjusted-Price Split Leak**: Using split/dividend backward-adjusted prices to compute nominal dollar-volume or tick-size features at time $t$ leaks future stock splits! Use *unadjusted* prices for price-level filters and point-in-time total-return factors for returns.
- [ ] **Intraday Close-to-Close Execution Illusion**: Using day-$t$ closing price both to compute the signal *and* as the entry fill price without slippage. Lag execution to $t+1$ open/VWAP or apply realistic half-spread + market-impact bps.
- [ ] **Cross-Asset Synchronous Contamination**: In GNN / cross-attention asset graphs across international markets, ensure Tokyo/London/NY closing timestamps are aligned in UTC without using same-date US close to predict earlier Asian close!

## 3. Target Venues

- **AI/CS Conferences**: ACM ICAIF, KDD (Applied Data Science), NeurIPS / ICML / ICLR (Time-Series, Decision Making, Benchmarks), AAAI, WWW.
- **Journals**: *Journal of Financial Data Science*, *Quantitative Finance*, *Management Science*, *Operations Research*, *Journal of Financial Economics* (for empirical asset pricing).
