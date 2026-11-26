#!/usr/bin/env python3
"""Compute rliable-style aggregate RL metrics (IQM, Median, Mean, Stratified Bootstrap 95% CI, P(X > Y)).

Input CSV format:
  method,task,seed,score
"""

import argparse
import csv
import math
import random
import sys
from collections import defaultdict
from pathlib import Path


def iqm(vals: list[float]) -> float:
    """Interquartile Mean: mean of middle 50% of values (robust to outlier seeds)."""
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return float("nan")
    if n < 4:
        return sum(s) / n
    lo = int(math.floor(0.25 * n))
    hi = int(math.ceil(0.75 * n))
    mid = s[lo:hi]
    return sum(mid) / len(mid) if mid else sum(s) / n


def median(vals: list[float]) -> float:
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return float("nan")
    m = n // 2
    return s[m] if n % 2 == 1 else 0.5 * (s[m - 1] + s[m])


def stratified_bootstrap_ci(task_scores: dict[str, list[float]], stat_fn, n_boot: int = 2000) -> tuple[float, float]:
    rng = random.Random(42)
    tasks = sorted(task_scores.keys())
    boots = []
    for _ in range(n_boot):
        sample = []
        for t in tasks:
            vals = task_scores[t]
            k = len(vals)
            sample.extend(vals[rng.randrange(k)] for _ in range(k))
        boots.append(stat_fn(sample))
    boots.sort()
    return (boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot)])


def prob_of_improvement(x_tasks: dict[str, list[float]], y_tasks: dict[str, list[float]]) -> float:
    """Average Mann-Whitney U probability P(X > Y) + 0.5 P(X == Y) across shared tasks."""
    shared = sorted(set(x_tasks) & set(y_tasks))
    if not shared:
        return float("nan")
    probs = []
    for t in shared:
        xs, ys = x_tasks[t], y_tasks[t]
        wins = 0.0
        for x in xs:
            for y in ys:
                if x > y:
                    wins += 1.0
                elif x == y:
                    wins += 0.5
        probs.append(wins / (len(xs) * len(ys)))
    return sum(probs) / len(probs)


def run_report(by_method: dict[str, dict[str, list[float]]], baseline: str | None) -> int:
    methods = sorted(by_method.keys())
    base = baseline if (baseline and baseline in by_method) else (methods[0] if methods else None)
    print("=== rliable Multi-Task RL Evaluation Summary ===")
    print(f"{'Method':<18} | {'IQM [95% CI]':<26} | {'Median':>8} | {'Mean':>8} | {'P(>base)':>8}")
    print("-" * 80)
    for m in methods:
        tmap = by_method[m]
        flat = [v for vals in tmap.values() for v in vals]
        m_iqm = iqm(flat)
        lo, hi = stratified_bootstrap_ci(tmap, iqm)
        m_med = median(flat)
        m_mean = sum(flat) / len(flat)
        poi_str = "   —    "
        if base and m != base:
            poi = prob_of_improvement(tmap, by_method[base])
            poi_str = f"{poi * 100:6.1f}% "
        print(f"{m:<18} | {m_iqm:6.3f} [{lo:6.3f}, {hi:6.3f}]   | {m_med:8.3f} | {m_mean:8.3f} | {poi_str}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute rliable IQM, stratified bootstrap CIs, and P(X > Y).")
    parser.add_argument("--input", help="CSV with columns: method,task,seed,score")
    parser.add_argument("--baseline", default=None, help="Baseline method name for probability of improvement.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in synthetic multi-task RL benchmark.")
    args = parser.parse_args()

    if args.self_test:
        rng = random.Random(7)
        by_m: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        for task in ["task_a", "task_b", "task_c", "task_d"]:
            for seed in range(5):
                by_m["PPO"][task].append(rng.gauss(0.65, 0.08))
                by_m["GRPO_Ours"][task].append(rng.gauss(0.81, 0.06))
        return run_report(by_m, "PPO")

    if not args.input:
        parser.error("Provide --input <scores.csv> or --self-test.")

    by_m = defaultdict(lambda: defaultdict(list))
    with Path(args.input).resolve().open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_m[row["method"].strip()][row["task"].strip()].append(float(row["score"]))
    return run_report(by_m, args.baseline)


if __name__ == "__main__":
    sys.exit(main())
