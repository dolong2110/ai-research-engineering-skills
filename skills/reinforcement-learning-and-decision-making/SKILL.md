---
name: reinforcement-learning-and-decision-making
description: >-
  Design, debug, and rigorously evaluate Reinforcement Learning, sequential
  decision-making, and RL-trained LLM systems (PPO, GRPO/RLVR, SAC, Offline RL
  CQL/IQL, MCTS). Enforces termination vs. truncation correctness, reward-hacking
  audits, KL/entropy monitoring, and rliable IQM + stratified bootstrap evaluation.
  Use this skill for RL agents, optimal execution, RL post-training, de novo
  molecular optimization, or neural combinatorial control.
---

# Reinforcement Learning & Sequential Decision-Making

RL experiments are notoriously sensitive to implementation bugs, reward hacking, and random-seed outliers. Always enforce these engineering and evaluation standards.

## 1. Correctness & Stability Invariants (Before Scaling)

1. **Termination vs. Time-Limit Truncation**:
   - **Never zero out bootstrap value $V(s_{t+1})$ on `truncated=True`!** Only `terminated=True` (true absorbing failure/goal) zeroes future returns; time-limit truncation must still bootstrap $\gamma V(s_{t+1})$ or value estimates bias sharply downward near episode boundaries.
2. **Reward Shaping & Reward-Hacking Audit**:
   - Potential-based shaping $F(s, a, s') = \gamma \Phi(s') - \Phi(s)$ preserves optimal policies; arbitrary bonus terms often invite degenerate looping or length exploitation.
   - For **LLM RLVR / GRPO** and **de novo drug optimization**: monitor **proxy reward vs. held-out gold verifier**, **KL divergence from reference policy** ($\beta \cdot D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})$), response length drift, and entropy collapse!
3. **Offline RL Distribution Shift (Finance Execution / Historical Logs)**:
   - Standard Q-learning extrapolates catastrophically on unseen actions $(s, a_{\text{OOD}})$. Use conservative critics (**CQL** / **IQL** / behavior-cloning regularization) and evaluate via Off-Policy Evaluation (**WIS / Doubly Robust / FQE**) before live deployment.
4. **Core Diagnostics to Log Every Update**:
   - Explained variance of value function ($1 - \operatorname{Var}(y - \hat{V}) / \operatorname{Var}(y)$ — if $\le 0$, critic is broken!), policy entropy, approx KL, clip fraction (PPO target `~0.1–0.2`), and gradient norms.

## 2. Statistically Valid Evaluation (`rliable` Standard)

Never report raw mean return across 3 seeds—one outlier seed or high-scale task dominates the average! Follow Agarwal et al. (*rliable*, NeurIPS):
- Report **Interquartile Mean (IQM)** (25% trimmed mean across runs × tasks), **Median**, **Optimality Gap**, **Stratified Bootstrap 95% CIs**, and **Probability of Improvement** $P(\text{Ours} > \text{Baseline})$.

Run [rliable_eval.py](./scripts/rliable_eval.py) on multi-task, multi-seed CSVs (`method,task,seed,score`):

```bash
python3 skills/reinforcement-learning-and-decision-making/scripts/rliable_eval.py \
  --input runs/rl_scores.csv --baseline PPO
```
