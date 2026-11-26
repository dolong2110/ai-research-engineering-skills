#!/usr/bin/env python3
"""Evaluate probability calibration (ECE, MCE, Brier, NLL) and Split Conformal Prediction intervals."""

import argparse
import csv
import math
import random
import sys
from pathlib import Path


def eval_calibration(probs: list[float], labels: list[int], n_bins: int = 10) -> None:
    n = len(probs)
    eps = 1e-12
    brier = sum((p - y) ** 2 for p, y in zip(probs, labels)) / n
    nll = -sum(y * math.log(max(eps, p)) + (1 - y) * math.log(max(eps, 1.0 - p)) for p, y in zip(probs, labels)) / n

    ece = 0.0
    mce = 0.0
    for b in range(n_bins):
        lo = b / n_bins
        hi = (b + 1) / n_bins
        idxs = [i for i, p in enumerate(probs) if (lo <= p < hi) or (b == n_bins - 1 and p == 1.0)]
        if not idxs:
            continue
        avg_conf = sum(probs[i] for i in idxs) / len(idxs)
        avg_acc = sum(labels[i] for i in idxs) / len(idxs)
        gap = abs(avg_acc - avg_conf)
        ece += (len(idxs) / n) * gap
        if gap > mce:
            mce = gap

    print(f"=== Calibration Metrics (n={n}, bins={n_bins}) ===")
    print(f"  ECE (↓)    : {ece:.4f}")
    print(f"  MCE (↓)    : {mce:.4f}")
    print(f"  Brier (↓)  : {brier:.4f}")
    print(f"  NLL (↓)    : {nll:.4f}")


def eval_split_conformal(cal_res: list[float], test_res: list[float], alpha: float = 0.1) -> None:
    n_cal = len(cal_res)
    sorted_cal = sorted(abs(r) for r in cal_res)
    k = min(n_cal, int(math.ceil((n_cal + 1) * (1.0 - alpha))))
    q_hat = sorted_cal[k - 1]
    covered = sum(1 for r in test_res if abs(r) <= q_hat)
    cov_rate = covered / len(test_res)
    print(f"=== Split Conformal Prediction (target >= {(1.0 - alpha) * 100:.1f}%, n_cal={n_cal}, n_test={len(test_res)}) ===")
    print(f"  Conformal Radius q_hat : {q_hat:.4f} (Mean Interval Width = {2.0 * q_hat:.4f})")
    print(f"  Empirical Coverage     : {cov_rate * 100:.2f}% ({covered}/{len(test_res)})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibration (ECE/Brier/NLL) and Split Conformal Prediction CLI.")
    sub = parser.add_subparsers(dest="cmd")

    p_cal = sub.add_parser("calibrate", help="Compute ECE, MCE, Brier, NLL from CSV (prob,label).")
    p_cal.add_argument("--input", required=True)
    p_cal.add_argument("--prob-col", default="prob")
    p_cal.add_argument("--label-col", default="label")
    p_cal.add_argument("--bins", type=int, default=10)

    p_conf = sub.add_parser("conformal", help="Evaluate Split Conformal intervals from CSV (split,y_true,y_pred).")
    p_conf.add_argument("--input", required=True)
    p_conf.add_argument("--alpha", type=float, default=0.1)

    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        rng = random.Random(42)
        probs, labels = [], []
        for _ in range(500):
            p = rng.random()
            probs.append(p)
            labels.append(1 if rng.random() < p else 0)
        eval_calibration(probs, labels)

        cal_res = [abs(rng.gauss(0.0, 1.0)) for _ in range(300)]
        test_res = [abs(rng.gauss(0.0, 1.0)) for _ in range(500)]
        eval_split_conformal(cal_res, test_res, alpha=0.1)
        return 0

    if args.cmd == "calibrate":
        probs, labels = [], []
        with Path(args.input).resolve().open("r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                probs.append(float(r[args.prob_col]))
                labels.append(int(float(r[args.label_col]) > 0.5))
        eval_calibration(probs, labels, args.bins)
        return 0

    if args.cmd == "conformal":
        cal_res, test_res = [], []
        with Path(args.input).resolve().open("r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                res = abs(float(r["y_true"]) - float(r["y_pred"]))
                sp = r["split"].strip().lower()
                if sp in {"cal", "val", "calibration"}:
                    cal_res.append(res)
                elif sp == "test":
                    test_res.append(res)
        eval_split_conformal(cal_res, test_res, args.alpha)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
