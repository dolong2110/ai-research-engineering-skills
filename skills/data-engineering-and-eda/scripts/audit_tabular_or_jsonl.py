#!/usr/bin/env python3
"""Profile CSV/TSV/JSONL datasets for schema, nulls, quantiles, duplicates, and cross-split overlap."""

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


def quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo])


def load_rows(path: Path, max_rows: int) -> tuple[list[dict], list[str]]:
    ext = path.suffix.lower()
    rows: list[dict] = []
    cols: list[str] = []
    if ext == ".jsonl":
        seen_cols: list[str] = []
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                if max_rows > 0 and idx >= max_rows:
                    break
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
                    for k in obj.keys():
                        if k not in seen_cols:
                            seen_cols.append(k)
        cols = seen_cols
    else:
        delim = "\t" if ext == ".tsv" else ","
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter=delim)
            cols = list(reader.fieldnames or [])
            for idx, row in enumerate(reader):
                if max_rows > 0 and idx >= max_rows:
                    break
                rows.append(dict(row))
    return rows, cols


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile CSV/TSV/JSONL dataset quality and split overlap.")
    parser.add_argument("--input", required=True, help="Path to .csv, .tsv, or .jsonl file.")
    parser.add_argument("--split-col", default=None, help="Optional split column (train/val/test).")
    parser.add_argument("--id-col", default=None, help="Optional key/text column to check cross-split leakage.")
    parser.add_argument("--max-rows", type=int, default=200000, help="Row cap for fast profiling (0=unlimited).")
    args = parser.parse_args()

    path = Path(args.input).resolve()
    if not path.exists():
        print(f"[FAIL] File not found: {path}")
        return 1

    rows, cols = load_rows(path, args.max_rows)
    n = len(rows)
    if n == 0:
        print(f"[FAIL] Dataset `{path.name}` contains 0 rows.")
        return 1

    row_hashes = Counter()
    split_counts = Counter()
    split_keys: dict[str, set[str]] = defaultdict(set)

    col_nulls = Counter()
    col_nums: dict[str, list[float]] = defaultdict(list)
    col_str_lens: dict[str, list[int]] = defaultdict(list)
    col_uniques: dict[str, set[str]] = defaultdict(set)

    for r in rows:
        canon_row = json.dumps(r, sort_keys=True, default=str)
        row_hashes[hashlib.sha1(canon_row.encode("utf-8")).hexdigest()] += 1
        split_val = str(r.get(args.split_col, "all")).strip().lower() if args.split_col else "all"
        if args.split_col:
            split_counts[split_val] += 1
        if args.id_col and args.id_col in r and r[args.id_col] not in (None, ""):
            key_h = hashlib.sha1(str(r[args.id_col]).strip().encode("utf-8")).hexdigest()
            split_keys[split_val].add(key_h)

        for c in cols:
            val = r.get(c)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                col_nulls[c] += 1
                continue
            s_val = str(val)
            if len(col_uniques[c]) <= 10000:
                col_uniques[c].add(s_val)
            try:
                num = float(val)
                if math.isfinite(num):
                    col_nums[c].append(num)
                else:
                    col_nulls[c] += 1
            except (TypeError, ValueError):
                col_str_lens[c].append(len(s_val))

    dup_rows = sum(cnt - 1 for cnt in row_hashes.values() if cnt > 1)
    print(f"=== Dataset Quality Profile: {path.name} ({n} rows, {len(cols)} cols) ===")
    print(f"Exact Duplicate Rows: {dup_rows} ({dup_rows / n * 100:.2f}%)")
    if split_counts:
        dist = ", ".join(f"{k}={v} ({v / n * 100:.1f}%)" for k, v in sorted(split_counts.items()))
        print(f"Split Distribution  : {dist}")

    print("\n--- Column Summary ---")
    for c in cols:
        null_n = col_nulls[c]
        null_pct = null_n / n * 100.0
        uniq = len(col_uniques[c])
        uniq_lbl = f"{uniq}+" if uniq > 10000 else str(uniq)
        if col_nums[c] and not col_str_lens[c]:
            sv = sorted(col_nums[c])
            print(
                f"  {c:<22} [numeric] null={null_pct:5.1f}% uniq={uniq_lbl:<6} "
                f"p01={quantile(sv, 0.01):.4g} p50={quantile(sv, 0.50):.4g} p99={quantile(sv, 0.99):.4g}"
            )
        else:
            lens = sorted(col_str_lens[c]) if col_str_lens[c] else [0]
            print(
                f"  {c:<22} [text/cat] null={null_pct:5.1f}% uniq={uniq_lbl:<6} "
                f"len_p50={quantile([float(x) for x in lens], 0.50):.0f} len_p99={quantile([float(x) for x in lens], 0.99):.0f}"
            )

    exit_code = 0
    if args.split_col and args.id_col and len(split_keys) > 1:
        print(f"\n--- Cross-Split Overlap on `{args.id_col}` ---")
        splits = sorted(split_keys.keys())
        for i in range(len(splits)):
            for j in range(i + 1, len(splits)):
                s1, s2 = splits[i], splits[j]
                ov = len(split_keys[s1] & split_keys[s2])
                if ov > 0:
                    print(f"  [FAIL] {ov} identical `{args.id_col}` value(s) leaked across `{s1}` and `{s2}`!")
                    exit_code = 1
                else:
                    print(f"  [OK] Zero exact overlap between `{s1}` and `{s2}`.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
