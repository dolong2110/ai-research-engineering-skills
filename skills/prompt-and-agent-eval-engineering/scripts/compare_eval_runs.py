#!/usr/bin/env python3
"""Compare baseline vs. candidate LLM/agent eval JSONL runs with slice breakdowns & McNemar's test.

Input JSONL format:
  {"id": "case_01", "category": "rag", "passed": true, "latency_ms": 950, "cost_usd": 0.003}
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def mcnemar_exact_pvalue(b: int, c: int) -> float:
    """Two-sided exact binomial McNemar p-value on discordant pairs (b=fixed, c=regressed)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # Sum_{i=0..k} comb(n, i) * 0.5^n * 2
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)


def load_by_id(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        out[str(obj["id"])] = obj
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline vs. candidate eval JSONL runs.")
    parser.add_argument("--baseline", required=True, help="Baseline eval JSONL.")
    parser.add_argument("--candidate", required=True, help="Candidate eval JSONL.")
    parser.add_argument("--max-regressions", type=int, default=None, help="Optional CI gate: exit 1 if regressed items exceed this count.")
    args = parser.parse_args()

    base = load_by_id(Path(args.baseline).resolve())
    cand = load_by_id(Path(args.candidate).resolve())
    common = sorted(set(base) & set(cand))
    if not common:
        print("[FAIL] Zero overlapping item IDs between baseline and candidate.")
        return 1

    base_pass = 0
    cand_pass = 0
    improved: list[str] = []
    regressed: list[str] = []
    slice_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])  # [n, base_pass, cand_pass]
    base_lat, cand_lat = [], []
    base_cost, cand_cost = 0.0, 0.0

    for cid in common:
        b = base[cid]
        c = cand[cid]
        bp = bool(b.get("passed"))
        cp = bool(c.get("passed"))
        cat = str(c.get("category") or b.get("category") or "default")
        base_pass += int(bp)
        cand_pass += int(cp)
        slice_stats[cat][0] += 1
        slice_stats[cat][1] += int(bp)
        slice_stats[cat][2] += int(cp)
        if not bp and cp:
            improved.append(cid)
        elif bp and not cp:
            regressed.append(cid)
        if "latency_ms" in b and "latency_ms" in c:
            base_lat.append(float(b["latency_ms"]))
            cand_lat.append(float(c["latency_ms"]))
        base_cost += float(b.get("cost_usd", 0.0))
        cand_cost += float(c.get("cost_usd", 0.0))

    n = len(common)
    b_rate = base_pass / n * 100.0
    c_rate = cand_pass / n * 100.0
    pval = mcnemar_exact_pvalue(len(improved), len(regressed))

    print(f"=== Paired Eval Regression Diff ({n} shared cases) ===")
    print(f"  Overall Pass Rate : {b_rate:5.1f}% -> {c_rate:5.1f}% (Delta: {c_rate - b_rate:+5.1f}%)")
    print(f"  Discordant Pairs  : +{len(improved)} improved, -{len(regressed)} regressed (exact McNemar p={pval:.4f})")
    if base_lat:
        bl = sum(base_lat) / len(base_lat)
        cl = sum(cand_lat) / len(cand_lat)
        print(f"  Mean Latency      : {bl:.1f} ms -> {cl:.1f} ms ({(cl - bl) / max(1e-6, bl) * 100:+.1f}%)")
    if base_cost > 0 or cand_cost > 0:
        print(f"  Total Cost        : ${base_cost:.4f} -> ${cand_cost:.4f}")

    print("\n--- Per-Category Slice Breakdown ---")
    for cat in sorted(slice_stats):
        sn, sbp, scp = slice_stats[cat]
        br, cr = sbp / sn * 100.0, scp / sn * 100.0
        flag = " [REGRESSION]" if cr < br else ""
        print(f"  {cat:<20} (n={sn:>3}): {br:5.1f}% -> {cr:5.1f}% ({cr - br:+5.1f}%){flag}")

    if regressed:
        print(f"\nRegressed IDs ({len(regressed)}): {', '.join(regressed[:20])}")
    if improved:
        print(f"Improved IDs  ({len(improved)}): {', '.join(improved[:20])}")

    if args.max_regressions is not None and len(regressed) > args.max_regressions:
        print(f"\n[FAIL] Gate failed: {len(regressed)} regressions > max allowed ({args.max_regressions}).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
