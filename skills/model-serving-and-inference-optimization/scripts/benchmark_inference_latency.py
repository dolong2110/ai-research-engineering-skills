#!/usr/bin/env python3
"""Analyze inference serving traces (TTFT, TPOT, E2E p50/p95/p99, tok/s, SLA check).

Input JSONL row format:
  {"ttft_ms": 120.4, "e2e_ms": 1450.0, "prompt_tokens": 512, "output_tokens": 64, "ok": true}
"""

import argparse
import json
import math
import random
import sys
from pathlib import Path


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = (p / 100.0) * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo])


def summarize_rows(rows: list[dict], wall_sec: float | None, sla_ttft: float | None, sla_tpot: float | None) -> int:
    total = len(rows)
    ok_rows = [r for r in rows if r.get("ok", True)]
    err_count = total - len(ok_rows)
    if not ok_rows:
        print(f"[FAIL] 0/{total} requests succeeded.")
        return 1

    ttfts = sorted(float(r["ttft_ms"]) for r in ok_rows if "ttft_ms" in r)
    e2es = sorted(float(r["e2e_ms"]) for r in ok_rows if "e2e_ms" in r)
    tpots = []
    total_out_toks = 0
    total_prompt_toks = 0
    for r in ok_rows:
        out_t = int(r.get("output_tokens", 0))
        in_t = int(r.get("prompt_tokens", 0))
        total_out_toks += out_t
        total_prompt_toks += in_t
        if out_t > 1 and "e2e_ms" in r and "ttft_ms" in r:
            decode_ms = max(0.0, float(r["e2e_ms"]) - float(r["ttft_ms"]))
            tpots.append(decode_ms / (out_t - 1))
    tpots.sort()

    eff_wall = wall_sec if (wall_sec and wall_sec > 0) else (sum(e2es) / 1000.0 if e2es else 1.0)
    print(f"=== Inference Serving Latency Report ({len(ok_rows)}/{total} succeeded, {err_count} failed) ===")
    if ttfts:
        print(
            f"  TTFT (ms)      : p50={percentile(ttfts, 50):7.1f} | p95={percentile(ttfts, 95):7.1f} | p99={percentile(ttfts, 99):7.1f}"
        )
    if tpots:
        print(
            f"  TPOT (ms/tok)  : p50={percentile(tpots, 50):7.2f} | p95={percentile(tpots, 95):7.2f} | p99={percentile(tpots, 99):7.2f} "
            f"(~{1000.0 / max(1e-6, percentile(tpots, 50)):.1f} tok/s per stream)"
        )
    if e2es:
        print(
            f"  E2E (ms)       : p50={percentile(e2es, 50):7.1f} | p95={percentile(e2es, 95):7.1f} | p99={percentile(e2es, 99):7.1f}"
        )
    if total_out_toks > 0:
        print(
            f"  Throughput     : {len(ok_rows) / eff_wall:.2f} req/s | {total_out_toks / eff_wall:.1f} output tok/s "
            f"(prompt_toks={total_prompt_toks}, out_toks={total_out_toks})"
        )

    exit_code = 0
    if sla_ttft is not None and ttfts and percentile(ttfts, 99) > sla_ttft:
        print(f"  [FAIL] SLA breach: TTFT p99 ({percentile(ttfts, 99):.1f} ms) > limit ({sla_ttft:.1f} ms)")
        exit_code = 1
    if sla_tpot is not None and tpots and percentile(tpots, 99) > sla_tpot:
        print(f"  [FAIL] SLA breach: TPOT p99 ({percentile(tpots, 99):.2f} ms) > limit ({sla_tpot:.2f} ms)")
        exit_code = 1
    if exit_code == 0 and (sla_ttft is not None or sla_tpot is not None):
        print("  [OK] All latency SLAs met.")
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute TTFT/TPOT/E2E tail latencies and SLA checks.")
    parser.add_argument("--input", help="Path to JSONL trace file.")
    parser.add_argument("--wall-sec", type=float, default=None, help="Total load-test wall time in seconds (for concurrent throughput).")
    parser.add_argument("--sla-ttft-p99-ms", type=float, default=None)
    parser.add_argument("--sla-tpot-p99-ms", type=float, default=None)
    parser.add_argument("--self-test", action="store_true", help="Run built-in synthetic trace benchmark.")
    args = parser.parse_args()

    if args.self_test:
        rng = random.Random(42)
        rows = []
        for _ in range(100):
            out_t = rng.randint(40, 120)
            ttft = rng.lognormvariate(math.log(120.0), 0.25)
            tpot = rng.lognormvariate(math.log(18.0), 0.15)
            rows.append({
                "ttft_ms": ttft,
                "e2e_ms": ttft + tpot * (out_t - 1),
                "prompt_tokens": rng.randint(256, 1024),
                "output_tokens": out_t,
                "ok": True,
            })
        return summarize_rows(rows, wall_sec=12.0, sla_ttft=400.0, sla_tpot=40.0)

    if not args.input:
        parser.error("Provide --input <traces.jsonl> or --self-test.")

    path = Path(args.input).resolve()
    if not path.exists():
        print(f"[FAIL] Trace file not found: {path}")
        return 1

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return summarize_rows(rows, args.wall_sec, args.sla_ttft_p99_ms, args.sla_tpot_p99_ms)


if __name__ == "__main__":
    sys.exit(main())
