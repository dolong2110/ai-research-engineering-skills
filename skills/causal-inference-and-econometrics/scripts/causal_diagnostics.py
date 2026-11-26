#!/usr/bin/env python3
"""Causal diagnostics CLI: covariate balance (SMD), 2x2 DiD ATE, and Newey-West HAC OLS SEs."""

import argparse
import csv
import math
import random
import sys
from pathlib import Path


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def var(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def norm_p_two_sided(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def check_balance(treated: dict[str, list[float]], control: dict[str, list[float]]) -> int:
    print("=== Covariate Balance (Standardized Mean Difference) ===")
    imbalanced = 0
    for col in sorted(treated):
        t_vals, c_vals = treated[col], control[col]
        pooled_sd = math.sqrt(0.5 * (var(t_vals) + var(c_vals)))
        smd = (mean(t_vals) - mean(c_vals)) / pooled_sd if pooled_sd > 1e-12 else 0.0
        flag = " [IMBALANCED |SMD|>0.1]" if abs(smd) > 0.1 else " [OK]"
        if abs(smd) > 0.1:
            imbalanced += 1
        print(f"  {col:<20}: treated={mean(t_vals):8.4f}, control={mean(c_vals):8.4f}, SMD={smd:+.3f}{flag}")
    return 1 if imbalanced else 0


def estimate_did_2x2(rows: list[dict], outcome_col: str, treat_col: str, post_col: str) -> None:
    cells: dict[tuple[int, int], list[float]] = {(0, 0): [], (0, 1): [], (1, 0): [], (1, 1): []}
    for r in rows:
        t = int(float(r[treat_col]) > 0.5)
        p = int(float(r[post_col]) > 0.5)
        cells[(t, p)].append(float(r[outcome_col]))
    m00, m01 = mean(cells[(0, 0)]), mean(cells[(0, 1)])
    m10, m11 = mean(cells[(1, 0)]), mean(cells[(1, 1)])
    ate = (m11 - m10) - (m01 - m00)
    se = math.sqrt(
        sum(var(vals) / max(1, len(vals)) for vals in cells.values())
    )
    z = ate / se if se > 1e-12 else 0.0
    pval = norm_p_two_sided(z)
    print("=== 2x2 Difference-in-Differences (DiD) ===")
    print(f"  Control: pre={m00:.4f} -> post={m01:.4f} (delta={m01 - m00:+.4f})")
    print(f"  Treated: pre={m10:.4f} -> post={m11:.4f} (delta={m11 - m10:+.4f})")
    print(f"  DiD ATE = {ate:+.4f} (SE = {se:.4f}, z = {z:.2f}, p = {pval:.4f}, 95% CI = [{ate - 1.96 * se:+.4f}, {ate + 1.96 * se:+.4f}])")


def newey_west_mean_test(series: list[float], max_lag: int | None = None) -> tuple[float, float, float]:
    """Newey-West HAC standard error for a time-series mean (e.g., alpha or IC series)."""
    n = len(series)
    if n < 3:
        return (mean(series), 0.0, 1.0)
    mu = mean(series)
    e = [x - mu for x in series]
    lags = max_lag if max_lag is not None else max(1, int(math.floor(4.0 * ((n / 100.0) ** (2.0 / 9.0)))))
    gamma0 = sum(v * v for v in e) / n
    lrv = gamma0
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1.0 - lag / (lags + 1.0)
        cov = sum(e[t] * e[t - lag] for t in range(lag, n)) / n
        lrv += 2.0 * w * cov
    se = math.sqrt(max(0.0, lrv) / n)
    t_stat = mu / se if se > 1e-12 else 0.0
    return (mu, se, norm_p_two_sided(t_stat))


def main() -> int:
    parser = argparse.ArgumentParser(description="Causal balance (SMD), 2x2 DiD, and Newey-West HAC diagnostics.")
    sub = parser.add_subparsers(dest="cmd")

    p_did = sub.add_parser("did", help="Compute 2x2 Difference-in-Differences from CSV.")
    p_did.add_argument("--input", required=True)
    p_did.add_argument("--outcome", default="y")
    p_did.add_argument("--treat", default="treated")
    p_did.add_argument("--post", default="post")

    p_nw = sub.add_parser("newey-west", help="Compute Newey-West HAC t-stat on a CSV time-series column.")
    p_nw.add_argument("--input", required=True)
    p_nw.add_argument("--col", required=True)
    p_nw.add_argument("--lags", type=int, default=None)

    parser.add_argument("--self-test", action="store_true", help="Run built-in balance, DiD, and Newey-West self-test.")
    args = parser.parse_args()

    if args.self_test:
        rng = random.Random(42)
        treated = {"age": [rng.gauss(40.0, 5.0) for _ in range(1000)], "income": [rng.gauss(50.0, 8.0) for _ in range(1000)]}
        control = {"age": [rng.gauss(40.0, 5.0) for _ in range(1000)], "income": [rng.gauss(50.0, 8.0) for _ in range(1000)]}
        rc = check_balance(treated, control)

        rows = []
        for t in (0, 1):
            for p in (0, 1):
                for _ in range(150):
                    y = 10.0 + 2.0 * t + 1.5 * p + 3.0 * (t * p) + rng.gauss(0.0, 1.0)
                    rows.append({"y": y, "treated": t, "post": p})
        estimate_did_2x2(rows, "y", "treated", "post")

        # AR(1) autocorrelated positive alpha series
        ar_series = []
        val = 0.0
        for _ in range(250):
            val = 0.4 * val + 0.02 + rng.gauss(0.0, 0.05)
            ar_series.append(val)
        mu, se, pval = newey_west_mean_test(ar_series)
        print(f"=== Newey-West HAC Mean Test ===\n  Mean = {mu:+.5f}, HAC SE = {se:.5f}, z = {mu / max(1e-12, se):.2f}, p = {pval:.4f}")
        return rc

    if args.cmd == "did":
        with Path(args.input).resolve().open("r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        estimate_did_2x2(rows, args.outcome, args.treat, args.post)
        return 0
    if args.cmd == "newey-west":
        with Path(args.input).resolve().open("r", encoding="utf-8") as f:
            vals = [float(r[args.col]) for r in csv.DictReader(f) if r.get(args.col)]
        mu, se, pval = newey_west_mean_test(vals, args.lags)
        print(f"Mean = {mu:+.6f} | Newey-West HAC SE = {se:.6f} | t = {mu / max(1e-12, se):.2f} | p = {pval:.4f}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
