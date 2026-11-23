#!/usr/bin/env python3
"""Differential oracle testing and empirical Big-O time/memory complexity fitter.

Usage:
  1. Built-in self-demo:
     python3 benchmark_and_complexity.py --self-test
  2. Custom module:
     python3 benchmark_and_complexity.py --module my_mod.py --func solve --gen make_input --oracle slow_solve
     where `make_input(n: int, seed: int)` returns a tuple of args `(*args,)` (or single arg).
"""

import argparse
import gc
import importlib.util
import math
import statistics
import sys
import time
import tracemalloc
from pathlib import Path


def _as_args(inp):
    return inp if isinstance(inp, tuple) else (inp,)


def fit_complexity_class(ns: list[int], times_sec: list[float]) -> tuple[str, float]:
    """Fit candidate complexity curves c * f(n) in log space and pick lowest RMSE."""
    valid = [(n, t) for n, t in zip(ns, times_sec) if n > 1 and t > 0]
    if len(valid) < 3:
        return ("Insufficient points", 0.0)

    candidates = [
        ("O(1)", lambda n: 1.0),
        ("O(log N)", lambda n: math.log2(n)),
        ("O(N)", lambda n: float(n)),
        ("O(N log N)", lambda n: float(n) * math.log2(n)),
        ("O(N^2)", lambda n: float(n) ** 2),
        ("O(N^3)", lambda n: float(n) ** 3),
    ]

    best_label = "Unknown"
    best_rmse = float("inf")
    log_ts = [math.log(t) for _, t in valid]

    for label, fn in candidates:
        log_fs = [math.log(fn(n)) for n, _ in valid]
        # Optimal scale constant log(c) = mean(log(t) - log(f(n)))
        log_c = sum(lt - lf for lt, lf in zip(log_ts, log_fs)) / len(valid)
        mse = sum((lt - (log_c + lf)) ** 2 for lt, lf in zip(log_ts, log_fs)) / len(valid)
        rmse = math.sqrt(mse)
        if rmse < best_rmse:
            best_rmse = rmse
            best_label = label

    # Also compute empirical power-law slope d(log t)/d(log n)
    log_ns = [math.log(n) for n, _ in valid]
    mean_x = statistics.mean(log_ns)
    mean_y = statistics.mean(log_ts)
    denom = sum((x - mean_x) ** 2 for x in log_ns)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_ns, log_ts)) / denom if denom > 0 else 0.0
    return best_label, slope


def load_module_from_path(mod_path: Path):
    spec = importlib.util.spec_from_file_location(mod_path.stem, str(mod_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


def run_suite(func, gen, oracle, sizes: list[int], repeats: int, oracle_trials: int, oracle_max_n: int) -> int:
    # 1. Differential Oracle Fuzzing
    if oracle is not None:
        print(f"=== Differential Oracle Fuzzing ({oracle_trials} randomized trials, N <= {oracle_max_n}) ===")
        for trial in range(oracle_trials):
            n = (trial * 17) % (oracle_max_n + 1)
            args1 = _as_args(gen(n, trial))
            args2 = _as_args(gen(n, trial))
            got = func(*args1)
            expected = oracle(*args2)
            if got != expected:
                print(f"[FAIL] Mismatch on trial={trial}, N={n}!")
                print(f"  Expected: {expected!r}")
                print(f"  Got     : {got!r}")
                return 1
        print(f"[OK] All {oracle_trials} randomized oracle checks matched identically.\n")

    # 2. Scaling Benchmark
    print("=== Empirical Time & Peak Memory Scaling ===")
    print(f"{'N':>10} | {'Median Time (ms)':>16} | {'Time Ratio':>10} | {'Peak Alloc (KB)':>15}")
    print("-" * 60)

    medians_sec: list[float] = []
    for idx, n in enumerate(sizes):
        samples: list[float] = []
        gc_was_enabled = gc.isenabled()
        gc.disable()
        try:
            for r in range(repeats):
                call_args = _as_args(gen(n, 1000 + r))
                t0 = time.perf_counter_ns()
                func(*call_args)
                t1 = time.perf_counter_ns()
                samples.append((t1 - t0) / 1e9)
        finally:
            if gc_was_enabled:
                gc.enable()

        # Single memory trace pass
        mem_args = _as_args(gen(n, 9999))
        tracemalloc.start()
        func(*mem_args)
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        med = statistics.median(samples)
        medians_sec.append(med)
        ratio_str = f"{med / medians_sec[idx - 1]:.2f}x" if idx > 0 and medians_sec[idx - 1] > 0 else "—"
        print(f"{n:>10} | {med * 1000:>16.3f} | {ratio_str:>10} | {peak_bytes / 1024.0:>15.1f}")

    best_fit, slope = fit_complexity_class(sizes, medians_sec)
    print(f"\nEstimated Time Complexity: {best_fit} (empirical log-log slope ≈ N^{slope:.2f})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Differential oracle fuzzer & empirical Big-O fitter.")
    parser.add_argument("--module", help="Path to Python file defining target functions.")
    parser.add_argument("--func", help="Name of fast function to test/benchmark.")
    parser.add_argument("--gen", help="Name of input generator `gen(n: int, seed: int)`.")
    parser.add_argument("--oracle", default=None, help="Optional reference oracle function name.")
    parser.add_argument("--sizes", default="250,500,1000,2000,4000,8000", help="Comma-separated N values.")
    parser.add_argument("--repeats", type=int, default=5, help="Timing repeats per N.")
    parser.add_argument("--oracle-trials", type=int, default=100, help="Randomized fuzz trials against oracle.")
    parser.add_argument("--oracle-max-n", type=int, default=60, help="Max N for slow oracle fuzzing.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in Kadane O(N) vs O(N^2) demo.")
    args = parser.parse_args()

    sizes = [int(x.strip()) for x in args.sizes.split(",") if x.strip()]

    if args.self_test:
        import random

        def demo_gen(n: int, seed: int):
            rng = random.Random(seed)
            return ([rng.randint(-50, 50) for _ in range(n)],)

        def kadane_fast(arr: list[int]) -> int:
            best = 0
            cur = 0
            for x in arr:
                cur = max(0, cur + x)
                best = max(best, cur)
            return best

        def max_subarray_brute(arr: list[int]) -> int:
            best = 0
            for i in range(len(arr)):
                s = 0
                for j in range(i, len(arr)):
                    s += arr[j]
                    if s > best:
                        best = s
            return best

        return run_suite(kadane_fast, demo_gen, max_subarray_brute, sizes, args.repeats, 80, 50)

    if not (args.module and args.func and args.gen):
        parser.error("Provide --module, --func, and --gen (or run --self-test).")

    mod = load_module_from_path(Path(args.module).resolve())
    func = getattr(mod, args.func)
    gen = getattr(mod, args.gen)
    oracle = getattr(mod, args.oracle) if args.oracle else None
    return run_suite(func, gen, oracle, sizes, args.repeats, args.oracle_trials, args.oracle_max_n)


if __name__ == "__main__":
    sys.exit(main())
