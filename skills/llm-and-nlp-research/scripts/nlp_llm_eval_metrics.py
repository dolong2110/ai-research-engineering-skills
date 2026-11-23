#!/usr/bin/env python3
"""Compute unbiased pass@k (Chen et al., 2021), position-debiased pairwise judge win rates, and Cohen's kappa."""

import argparse
import json
import math
import sys
from pathlib import Path


def unbiased_pass_at_k(n: int, c: int, k: int) -> float:
    """1 - comb(n - c, k) / comb(n, k) computed stably without large integer overflow."""
    if n < k:
        raise ValueError(f"Total samples n={n} is smaller than k={k}.")
    if n - c < k:
        return 1.0
    prod = 1.0
    for i in range(n - c - k + 1, n - c + 1):
        prod *= i / (i + c)
    return 1.0 - prod


def cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    assert len(labels_a) == len(labels_b) and len(labels_a) > 0
    n = len(labels_a)
    cats = sorted(set(labels_a) | set(labels_b))
    p_o = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    p_e = sum(
        (labels_a.count(c) / n) * (labels_b.count(c) / n)
        for c in cats
    )
    if abs(1.0 - p_e) < 1e-12:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def cmd_pass_at_k(args: argparse.Namespace) -> int:
    """Input JSONL format: {"id": "prob_1", "n": 16, "c": 4}"""
    path = Path(args.input).resolve()
    ks = [int(x.strip()) for x in args.ks.split(",") if x.strip()]
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        print("[FAIL] Empty JSONL input.")
        return 1

    print(f"=== Unbiased pass@k ({len(rows)} problem(s)) ===")
    for k in ks:
        scores = [unbiased_pass_at_k(int(r["n"]), int(r["c"]), k) for r in rows]
        avg = sum(scores) / len(scores)
        print(f"  pass@{k:<3d} : {avg * 100:6.2f}%")
    return 0


def cmd_pairwise(args: argparse.Namespace) -> int:
    """Input JSONL format:
    {"id": "1", "ab_winner": "A", "ba_winner": "A", "len_a": 210, "len_b": 195, "human_winner": "A"}
    where `ab_winner` / `ba_winner` are mapped to model identity ("A", "B", or "tie").
    """
    path = Path(args.input).resolve()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        print("[FAIL] Empty JSONL input.")
        return 1

    consistent_a = 0
    consistent_b = 0
    ties_or_flips = 0
    flips = 0
    longer_wins = 0
    length_compared = 0
    judge_calls: list[str] = []
    human_calls: list[str] = []

    for r in rows:
        w1 = str(r["ab_winner"]).strip()
        w2 = str(r["ba_winner"]).strip()
        if w1 == "A" and w2 == "A":
            verdict = "A"
            consistent_a += 1
        elif w1 == "B" and w2 == "B":
            verdict = "B"
            consistent_b += 1
        else:
            verdict = "tie"
            ties_or_flips += 1
            if {w1, w2} == {"A", "B"}:
                flips += 1

        if "len_a" in r and "len_b" in r and verdict in {"A", "B"} and r["len_a"] != r["len_b"]:
            length_compared += 1
            if (verdict == "A" and r["len_a"] > r["len_b"]) or (verdict == "B" and r["len_b"] > r["len_a"]):
                longer_wins += 1

        if "human_winner" in r and r["human_winner"] is not None:
            judge_calls.append(verdict)
            human_calls.append(str(r["human_winner"]).strip())

    n = len(rows)
    # Standard debiased win rate: wins + 0.5 * ties
    debiased_wr_a = (consistent_a + 0.5 * ties_or_flips) / n

    print(f"=== Position-Debiased Pairwise Judge Report ({n} items) ===")
    print(f"  Strict A Wins (both orders) : {consistent_a} ({consistent_a / n * 100:.1f}%)")
    print(f"  Strict B Wins (both orders) : {consistent_b} ({consistent_b / n * 100:.1f}%)")
    print(f"  Ties / Order-Inconsistent   : {ties_or_flips} ({ties_or_flips / n * 100:.1f}%) [Order-Flip Bias Rate: {flips / n * 100:.1f}%]")
    print(f"  Debiased Win Rate (Model A) : {debiased_wr_a * 100:.2f}%")
    if length_compared > 0:
        len_rate = longer_wins / length_compared
        print(f"  Longer-Response Win Share   : {len_rate * 100:.1f}% (50% = length-neutral; >65% indicates verbosity bias!)")
    if human_calls:
        kappa = cohens_kappa(judge_calls, human_calls)
        print(f"  Judge-Human Cohen's kappa   : {kappa:.3f} (n={len(human_calls)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM & NLP evaluation metrics (pass@k, debiased judge, kappa).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pk = sub.add_parser("pass-at-k", help="Compute unbiased pass@k from JSONL {id, n, c}.")
    p_pk.add_argument("--input", required=True)
    p_pk.add_argument("--ks", default="1,5,10")
    p_pk.set_defaults(func=cmd_pass_at_k)

    p_pw = sub.add_parser("pairwise-judge", help="Analyze position-swapped LLM-as-a-Judge JSONL.")
    p_pw.add_argument("--input", required=True)
    p_pw.set_defaults(func=cmd_pairwise)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
