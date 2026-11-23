---
name: algorithms-and-data-structures
description: >-
  Design, analyze, prove, and benchmark optimal algorithms and data structures.
  Covers constraint-driven complexity sizing, paradigm selection (graphs, dynamic
  programming, greedy exchange arguments, trees/tries/segment trees, streaming
  sketches, ANN), loop-invariant/induction proofs, cache-friendly memory layouts,
  and differential oracle fuzzing. Use this skill whenever solving algorithmic
  problems, choosing data structures, proving time/space bounds, or replacing slow
  O(N^2) bottlenecks.
---

# Algorithms & Data Structures

Use this skill to select optimal data structures, design provably correct algorithms, verify edge cases against brute-force oracles, and empirically validate asymptotic time and memory scaling.

## 1. The 5-Step Algorithmic Design Protocol

1. **Formalize Input, Output & Constraints**:
   - State exact domains, invariants (sorted? DAG? non-negative weights? unique keys?), and scale $N, M, Q$.
   - **Size target complexity from $N$** (~$10^8$ elementary C ops/sec, ~$10^7$ Python ops/sec):
     - $N \le 20 \implies O(2^N \cdot N)$ (bitmask DP, branch-and-bound)
     - $N \le 400 \implies O(N^3)$ (Floyd–Warshall, interval DP, dense Gaussian elimination)
     - $N \le 5{,}000 \implies O(N^2)$ (quadratic DP, all-pairs on small graphs)
     - $N \le 2 \times 10^5 \implies O(N \log N)$ or $O(N \log^2 N)$ (sorting, heap, segment/Fenwick tree, divide & conquer)
     - $N \ge 10^6 \implies O(N)$ or $O(1)$ amortized (hash table, monotonic deque, two pointers, streaming sketch)
2. **Reduce to a Canonical Paradigm**:
   - Consult [paradigm_and_ds_selection.md](./references/paradigm_and_ds_selection.md) to map problem structure to the cleanest known abstraction before inventing ad-hoc logic.
3. **Prove Correctness Before Coding**:
   - **Greedy**: Prove the *greedy choice property* (via an **exchange argument** transforming an optimal solution $O$ into greedy choice $G$ without worsening cost) + *optimal substructure*. If an exchange fails on a 4-element counterexample, switch to DP or flow!
   - **Dynamic Programming**: Define exact state semantics `dp[...]`, base cases, acyclic transition topological order, and whether space can roll from $O(N \cdot K) \to O(K)$.
   - **Iterative / Graph / Pointer Loops**: State the **loop invariant** (true at initialization, preserved per step, implies postcondition at termination) and strictly decreasing **termination variant**.
4. **Engineer for Real Hardware Constants**:
   - Prefer contiguous arrays (`list`, `array`, `numpy.ndarray`) over pointer-heavy node objects for cache locality; use `collections.deque` (never `list.pop(0)` which is $O(N)$!), `heapq`, `bisect`, and iterative DFS when Python recursion depth ($10^3$) can overflow.
5. **Differential Oracle Fuzzing & Empirical Scaling**:
   - Write a dead-simple $O(N^2)$ / brute-force reference oracle and fuzz-test your fast implementation on hundreds of small random + adversarial inputs ($N=0, 1$, all-equal, sorted, reverse-sorted, disconnected, overflow boundaries).

## 2. Empirical Complexity & Differential Oracle Tool

Run [benchmark_and_complexity.py](./scripts/benchmark_and_complexity.py) to verify your fast function against a reference oracle and fit its empirical Big-O time & memory scaling across doubling input sizes:

```bash
python3 skills/algorithms-and-data-structures/scripts/benchmark_and_complexity.py \
  --module path/to/my_algo.py \
  --func fast_solve \
  --gen gen_input \
  --oracle brute_solve \
  --sizes 250,500,1000,2000,4000,8000
```
