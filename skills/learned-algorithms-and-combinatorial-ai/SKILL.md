---
name: learned-algorithms-and-combinatorial-ai
description: >-
  Conduct research at the intersection of ML/DL/LLMs and Algorithms & Data
  Structures: Learning-Augmented Algorithms (Algorithms with Predictions:
  consistency vs. robustness proofs), Learned Data Structures (learned indexes,
  learned Bloom filters, LSH/HNSW), Neural Algorithmic Reasoning (CLRS/GNNs),
  LLM-driven algorithm discovery (FunSearch / MCTS over code), and neural
  combinatorial optimization. Use this skill whenever combining machine learning or
  LLMs with algorithms, data structures, or discrete optimization.
---

# Learned Algorithms, Data Structures & Combinatorial AI

This skill bridges **ML / DL / LLMs** and **Classical Algorithms & Data Structures**—covering the core theoretical and empirical standards expected at ICML, NeurIPS, ICLR, SODA, STOC/FOCS, and KDD.

## 1. Learning-Augmented Algorithms ("Algorithms with Predictions")

When augmenting online/streaming/classic algorithms (caching/paging, ski-rental, scheduling, matching, binary search, primal-dual LP) with untrusted ML predictions $\hat{y}$ of error $\eta = \|\hat{y} - y\|$:

1. **Prove the Three Canonical Theoretical Properties**:
   - **Consistency ($\eta = 0$)**: Competitive ratio approaches the offline optimum ($1 + o(1)$ or controllable $1 + \lambda$) when predictions are accurate.
   - **Robustness ($\eta \to \infty$)**: Competitive ratio remains bounded by $O(\gamma_{\text{classic}})$ (e.g., $O(1/\lambda)$ or $O(\log k)$) **even under adversarial / arbitrarily corrupted ML predictions**.
   - **Smoothness (Graceful Degradation)**: Performance degrades continuously as a function $f(\eta)$ of prediction error—never assuming calibrated or unbiased errors!
2. **Required Empirical Plots**:
   - Plot competitive ratio / cost on the $y$-axis against **synthetic corruption level $\eta$** on the $x$-axis (sweeping from oracle $\eta=0$ through real trained ML predictor error up to adversarial noise), comparing classical worst-case baseline, pure-ML trust-blind baseline, and your $\lambda$-interpolated algorithm.

## 2. Learned Data Structures (Indexes, Filters, Sketches & ANN)

When replacing or hybridizing B-trees, hash tables, Bloom filters, Count-Min sketches, or k-NN indexes with neural/learned models:
- **Account for Total Memory Footprint**: Include **model weights + auxiliary backup filter + overflow buffers** in the exact byte budget when comparing against standard C++/Rust B-tree,Xor/Cuckoo/Bloom filter, or HNSW baselines!
- **Benchmark Build + Dynamic Update Cost**: Report lookup latency (`ns/op`), throughput, **insertion/deletion amortization**, cache-miss behavior, and distribution-shift degradation (when query or key distribution drifts after training).

## 3. Neural Combinatorial Optimization & LLM Algorithm Discovery

When applying GNNs, RL, Diffusion, or LLMs (FunSearch / AlphaEvolve / MCTS-over-heuristics) to NP-hard problems (TSP, VRP, MIS, Max-Cut, Bin Packing, Job-Shop, Molecular/Portfolio Combinatorics):

1. **Mandatory Classical OR Baselines**:
   - Always compare against exact/metaheuristic solvers (**Gurobi / CPLEX / SCIP / OR-Tools / LKH-3 / Concorde**) under **matched wall-clock time budgets** on identical hardware, reporting **Optimality Gap (%)**:
     $$\text{Gap (\%)} = \frac{\text{Obj}_{\text{method}} - \text{Obj}_{\text{BKS}}}{\lvert \text{Obj}_{\text{BKS}} \rvert} \times 100$$
2. **Scale & Out-of-Distribution Generalization**:
   - Train on small instances (e.g., $N=50..100$) and test zero-shot generalization on **10×–100× larger instances** ($N=500, 1{,}000, 10{,}000$) and non-uniform clustered distributions where learned heuristics either shine or collapse.
3. **Verifiable Evaluators (Zero Reward Hacking)**:
   - In LLM-guided heuristic search, run generated candidate functions inside an isolated, deterministic evaluator that verifies **hard feasibility constraints** independently of the objective score (and fuzz-test with `algorithms-and-data-structures/scripts/benchmark_and_complexity.py`).
