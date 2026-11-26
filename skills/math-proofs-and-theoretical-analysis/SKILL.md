---
name: math-proofs-and-theoretical-analysis
description: >-
  Formulate, verify, and debug mathematical proofs, derivations, convergence/generalization
  bounds, algorithmic competitive ratios, convex/stochastic optimization analysis,
  and physical group-equivariance proofs. Enforces explicit assumption tracking,
  counterexample probing, and numerical/symbolic sanity checks. Use this skill
  whenever proving theorems, deriving gradients/losses, or checking theoretical
  claims in research papers.
---

# Mathematical Proofs & Theoretical Analysis

Use this skill whenever deriving equations, proving theorems/lemmas, checking competitive ratios or convergence rates, or auditing theoretical claims in ML, Quantitative Finance, Chemistry, or Algorithms.

## 1. Proof & Derivation Audit Protocol

1. **List Every Assumption Explicitly**:
   - Never hide silent requirements (e.g., convexity, $L$-smoothness, bounded variance, i.i.d. vs. martingale difference, full rank, compact support, strict positivity, non-negative weights).
   - Check whether each assumption actually holds in your empirical setup—if not, flag the gap transparently in the paper.
2. **Verify Dimensional & Boundary Consistency**:
   - Check matrix/tensor dimensions at every step of linear-algebra derivations.
   - Plug in extreme/degenerate values ($N=1$, $\lambda \to 0$, $\lambda \to \infty$, $\eta = 0$, orthogonal rotation $\mathbf{Q} \in O(3)$ vs. $SO(3)$ with $\det \mathbf{Q} = -1$) to catch missing constants, sign flips, or broken edge cases immediately.
3. **Attempt to Falsify Before Claiming Q.E.D.**:
   - Actively construct small counterexamples (2D vectors, 3-node graphs, 2-step random walks, skewed discrete distributions) to try to break every inequality step before accepting it.
4. **Canonical Proof Toolkits by Domain**:
   - **Algorithms & Online Optimization**: Greedy exchange arguments, amortized potential functions $\Phi(D_i) \ge \Phi(D_0)$, primal-dual fitting, Yao's minimax principle, Chernoff/Hoeffding/Azuma–Hoeffding concentration bounds.
   - **ML & Convex Optimization**: Descent lemma ($f(y) \le f(x) + \langle \nabla f(x), y-x \rangle + \frac{L}{2}\|y-x\|^2$), Polyak–Łojasiewicz (PL) condition, KKT stationarity/duality, Jensen/Cauchy–Schwarz/Hölder inequalities.
   - **Physics / Chemistry**: Exact $E(3)$ vs. $SE(3)$ transformation check $f(\mathbf{Q}\mathbf{x} + \mathbf{t}) = \mathbf{Q} f(\mathbf{x})$ and conservative curl-free force check ($\nabla \times \mathbf{F} = \mathbf{0}$).

## 2. Numerical Gradient & Inequality Counterexample Verifier

Before finalizing any derived gradient, loss derivative, or algebraic inequality in a paper or codebase, test it numerically with [verify_math_numerically.py](./scripts/verify_math_numerically.py):

```bash
# Built-in self-test verifying central-difference gradients & Cauchy-Schwarz stress test
python3 skills/math-proofs-and-theoretical-analysis/scripts/verify_math_numerically.py --self-test

# Check analytic gradient `grad_f(x)` against central finite differences of `f(x)`
python3 skills/math-proofs-and-theoretical-analysis/scripts/verify_math_numerically.py grad-check \
  --module my_derivations.py --fn loss_fn --grad grad_loss_fn --dim 8
```
