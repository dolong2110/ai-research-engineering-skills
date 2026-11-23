#!/usr/bin/env python3
"""Run cProfile + tracemalloc on a Python script and print concise CPU & memory hotspots."""

import argparse
import cProfile
import io
import pstats
import runpy
import sys
import time
import tracemalloc
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profile a Python script's top CPU and memory hotspots."
    )
    parser.add_argument("--script", required=True, help="Path to target .py script.")
    parser.add_argument("--top", type=int, default=15, help="Number of top rows to display.")
    parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed to target script (prefix with `--`).",
    )
    args = parser.parse_args()

    script_path = Path(args.script).resolve()
    if not script_path.exists():
        print(f"[FAIL] Script not found: {script_path}")
        return 1

    forwarded = list(args.script_args)
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]

    sys.path.insert(0, str(script_path.parent))
    orig_argv = sys.argv[:]
    sys.argv = [str(script_path)] + forwarded

    profiler = cProfile.Profile()
    tracemalloc.start()
    t0 = time.perf_counter()
    exit_note = "0"
    try:
        profiler.enable()
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit as exc:
        exit_note = str(exc.code)
    finally:
        profiler.disable()
        elapsed = time.perf_counter() - t0
        snapshot = tracemalloc.take_snapshot()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.argv = orig_argv

    print(f"\n=== Hotspot Profile: {script_path.name} (exit={exit_note}) ===")
    print(f"Wall Time: {elapsed * 1000:.2f} ms | Peak Python Heap: {peak_mem / (1024 * 1024):.2f} MB (Current: {current_mem / (1024 * 1024):.2f} MB)\n")

    for sort_key, label in [("cumtime", "Top Cumulative Time"), ("tottime", "Top Self (Internal) Time")]:
        buf = io.StringIO()
        stats = pstats.Stats(profiler, stream=buf).strip_dirs().sort_stats(sort_key)
        stats.print_stats(args.top)
        print(f"--- {label} ---")
        for line in buf.getvalue().splitlines():
            if line.strip():
                print(line)
        print()

    top_allocs = snapshot.statistics("lineno")[: min(args.top, 10)]
    if top_allocs:
        print("--- Top Memory Allocations by Line ---")
        for stat in top_allocs:
            print(f"  {stat}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
