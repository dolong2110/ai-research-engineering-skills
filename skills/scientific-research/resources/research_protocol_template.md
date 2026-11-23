# Research Protocol: [Working Project Title]

## 1. Problem & Bottleneck
- **Target Task / Domain:**
- **Concrete Failure Mode of Current SOTA:**
- **Quantitative Evidence of Bottleneck:**

## 2. Falsifiable Hypothesis
- **Primary Hypothesis ($H_1$):** By introducing [mechanism], [metric] on [regime] will improve by at least [threshold] at matched compute because [causal intuition].
- **Null / Alternative Explanation ($H_0$):** Any gain comes purely from [extra parameters / regularization / data scaling] rather than [mechanism].
- **Fastest Falsification Test (MVE):**
  - *Setup (<10% full budget):*
  - *Pass / Kill Criterion:*

## 3. Experimental Matrix
- **Datasets & Splits (Train / Val / Test):**
- **Primary & Trade-off Metrics (`↑` / `↓`):**
- **Baselines (with Resource-Parity Controls):**
  1. Standard Baseline:
  2. Strongest Recent SOTA:
  3. Parameter/Compute-Matched Control:
- **Planned Ablations:**
  - [ ] Full Proposed Model ($N \ge 3$ seeds)
  - [ ] w/o Component A
  - [ ] w/o Component B
  - [ ] Parameter-matched vanilla replacement for Component A
  - [ ] Hyperparameter sweep: [param] $\in \{v_1, v_2, v_3\}$
  - [ ] Efficiency profile: Params (M), FLOPs (G), Peak VRAM (GB), Latency (ms)

## 4. Threats to Validity & Negative Results Log
- *Document unexpected degradations, unstable regimes, and boundary conditions here.*
