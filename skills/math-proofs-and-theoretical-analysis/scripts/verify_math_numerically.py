#!/usr/bin/env python3
"""Numerically verify analytic gradients (central finite differences) and stress-test inequalities."""

import argparse
import importlib.util
import math
import random
import sys
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


def run_grad_check(fn, grad_fn, dim: int, trials: int = 20, eps: float = 1e-6, tol: float = 1e-5) -> int:
    rng = random.Random(42)
    max_rel_err = 0.0
    for t in range(trials):
        x = [rng.gauss(0.0, 1.0) for _ in range(dim)]
        analytic = list(grad_fn(list(x)))
        numeric = []
        for i in range(dim):
            xp = list(x)
            xm = list(x)
            xp[i] += eps
            xm[i] -= eps
            numeric.append((float(fn(xp)) - float(fn(xm))) / (2.0 * eps))
        for i, (ga, gn) in enumerate(zip(analytic, numeric)):
            denom = max(1.0, abs(ga), abs(gn))
            rel = abs(ga - gn) / denom
            if rel > max_rel_err:
                max_rel_err = rel
            if rel > tol:
                print(
                    f"[FAIL] Gradient mismatch on trial={t}, coord={i}: analytic={ga:.8g}, numeric={gn:.8g}, rel_err={rel:.3e} > tol={tol:.1e}"
                )
                return 1
    print(f"[OK] Gradient check passed across {trials} random points (dim={dim}, max_rel_err={max_rel_err:.2e}).")
    return 0


def run_ineq_check(lhs_fn, rhs_fn, dim: int, trials: int = 5000, tol: float = 1e-9) -> int:
    """Test lhs(x) <= rhs(x) + tol across Gaussian, uniform, sparse, and extreme scales."""
    rng = random.Random(123)
    worst_margin = -float("inf")
    for t in range(trials):
        mode = t % 4
        if mode == 0:
            x = [rng.gauss(0.0, 1.0) for _ in range(dim)]
        elif mode == 1:
            x = [rng.uniform(1e-4, 1e2) for _ in range(dim)]
        elif mode == 2:
            x = [0.0 if rng.random() < 0.5 else rng.gauss(0.0, 10.0) for _ in range(dim)]
        else:
            scale = 10.0 ** rng.uniform(-3, 3)
            x = [rng.uniform(-scale, scale) for _ in range(dim)]
        lv = float(lhs_fn(x))
        rv = float(rhs_fn(x))
        margin = lv - rv
        if margin > worst_margin:
            worst_margin = margin
        if margin > tol:
            print(f"[FAIL] Counterexample found on trial={t}! lhs={lv:.8g} > rhs={rv:.8g} (excess={margin:.3e})")
            print(f"  x = {x[:10]}")
            return 1
    print(f"[OK] Inequality lhs(x) <= rhs(x) held across {trials} stress trials (tightest lhs-rhs={worst_margin:.3e}).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Numerical gradient check & inequality counterexample hunter.")
    sub = parser.add_subparsers(dest="cmd")

    p_g = sub.add_parser("grad-check", help="Check analytic grad_fn(x) against central finite differences of fn(x).")
    p_g.add_argument("--module", required=True)
    p_g.add_argument("--fn", required=True)
    p_g.add_argument("--grad", required=True)
    p_g.add_argument("--dim", type=int, default=6)
    p_g.add_argument("--trials", type=int, default=20)
    p_g.add_argument("--tol", type=float, default=1e-5)

    p_i = sub.add_parser("check-ineq", help="Hunt counterexamples to lhs(x) <= rhs(x).")
    p_i.add_argument("--module", required=True)
    p_i.add_argument("--lhs", required=True)
    p_i.add_argument("--rhs", required=True)
    p_i.add_argument("--dim", type=int, default=6)
    p_i.add_argument("--trials", type=int, default=5000)

    parser.add_argument("--self-test", action="store_true", help="Run built-in LogSumExp grad & Cauchy-Schwarz checks.")
    args = parser.parse_args()

    if args.self_test:
        def lse(x: list[float]) -> float:
            m = max(x)
            return m + math.log(sum(math.exp(v - m) for v in x))

        def grad_lse(x: list[float]) -> list[float]:
            m = max(x)
            exps = [math.exp(v - m) for v in x]
            s = sum(exps)
            return [e / s for e in exps]

        rc1 = run_grad_check(lse, grad_lse, dim=8)

        def cs_lhs(x: list[float]) -> float:
            half = len(x) // 2
            a, b = x[:half], x[half : 2 * half]
            return abs(sum(u * v for u, v in zip(a, b)))

        def cs_rhs(x: list[float]) -> float:
            half = len(x) // 2
            a, b = x[:half], x[half : 2 * half]
            return math.sqrt(sum(u * u for u in a)) * math.sqrt(sum(v * v for v in b))

        rc2 = run_ineq_check(cs_lhs, cs_rhs, dim=8, trials=1000)
        return rc1 or rc2

    if args.cmd == "grad-check":
        mod = load_module(Path(args.module).resolve())
        return run_grad_check(getattr(mod, args.fn), getattr(mod, args.grad), args.dim, args.trials, tol=args.tol)
    if args.cmd == "check-ineq":
        mod = load_module(Path(args.module).resolve())
        return run_ineq_check(getattr(mod, args.lhs), getattr(mod, args.rhs), args.dim, args.trials)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
