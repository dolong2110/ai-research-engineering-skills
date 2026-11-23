#!/usr/bin/env python3
"""Audit prediction CSVs for timestamp anomalies and compute IC, Rank IC, Turnover, MDD, and Net Sharpe/PSR.

Expected CSV columns:
  timestamp,asset,signal,realized_return
"""

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den > 1e-15 else 0.0


def ranks(xs: list[float]) -> list[float]:
    indexed = sorted(enumerate(xs), key=lambda t: t[1])
    out = [0.0] * len(xs)
    i = 0
    n = len(xs)
    while i < n:
        j = i
        while j + 1 < n and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            out[indexed[k][0]] = avg_rank
        i = j + 1
    return out


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(ranks(xs), ranks(ys))


def norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def probabilistic_sharpe_ratio(rets: list[float], sr_benchmark: float = 0.0) -> float:
    """Bailey & Lopez de Prado (2012) Probabilistic Sharpe Ratio adjusting for skew & kurtosis."""
    n = len(rets)
    if n < 5:
        return float("nan")
    mu = mean(rets)
    sd = std(rets)
    if sd <= 1e-15:
        return 0.0
    sr = mu / sd
    z_scores = [(r - mu) / sd for r in rets]
    skew = sum(z ** 3 for z in z_scores) / n
    kurt = sum(z ** 4 for z in z_scores) / n
    denom_sq = 1.0 - skew * sr + ((kurt - 1.0) / 4.0) * (sr ** 2)
    if denom_sq <= 1e-12:
        return float("nan")
    stat = (sr - sr_benchmark) * math.sqrt(n - 1) / math.sqrt(denom_sq)
    return norm_cdf(stat)


def max_drawdown(period_rets: list[float]) -> float:
    wealth = 1.0
    peak = 1.0
    mdd = 0.0
    for r in period_rets:
        wealth *= 1.0 + r
        if wealth > peak:
            peak = wealth
        dd = (peak - wealth) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    return mdd


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute Financial ML IC, Rank IC, Turnover, and Net Sharpe.")
    parser.add_argument("--input", required=True, help="CSV with timestamp,asset,signal,realized_return")
    parser.add_argument("--cost-bps", type=float, default=10.0, help="One-way transaction cost in basis points (default: 10).")
    parser.add_argument("--quantile", type=float, default=0.2, help="Top/bottom fraction for long-short portfolio (default: 0.2).")
    parser.add_argument("--periods-per-year", type=int, default=252, help="Annualization factor (252 daily, 52 weekly, 12 monthly).")
    args = parser.parse_args()

    path = Path(args.input).resolve()
    if not path.exists():
        print(f"[FAIL] CSV not found: {path}")
        return 1

    by_ts: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    duplicate_pairs = 0
    seen_pairs: set[tuple[str, str]] = set()
    non_monotonic_rows = 0
    prev_ts = ""

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row["timestamp"].strip()
            asset = row["asset"].strip()
            sig = float(row["signal"])
            ret = float(row["realized_return"])
            if prev_ts and ts < prev_ts:
                non_monotonic_rows += 1
            prev_ts = ts
            if (ts, asset) in seen_pairs:
                duplicate_pairs += 1
            seen_pairs.add((ts, asset))
            by_ts[ts].append((asset, sig, ret))

    sorted_ts = sorted(by_ts.keys())
    ics: list[float] = []
    rank_ics: list[float] = []
    gross_rets: list[float] = []
    net_rets: list[float] = []
    turnovers: list[float] = []
    prev_weights: dict[str, float] = {}
    cost_rate = args.cost_bps / 10000.0

    for ts in sorted_ts:
        cross = by_ts[ts]
        if len(cross) >= 3:
            sigs = [x[1] for x in cross]
            rets = [x[2] for x in cross]
            ic_v = pearson(sigs, rets)
            ric_v = spearman(sigs, rets)
            if not math.isnan(ic_v):
                ics.append(ic_v)
            if not math.isnan(ric_v):
                rank_ics.append(ric_v)

        # Dollar-neutral Top-Q Long / Bottom-Q Short portfolio
        ranked = sorted(cross, key=lambda x: x[1])
        k = max(1, int(len(ranked) * args.quantile))
        shorts = ranked[:k]
        longs = ranked[-k:]

        weights: dict[str, float] = {}
        for a, _, _ in longs:
            weights[a] = weights.get(a, 0.0) + 0.5 / len(longs)
        for a, _, _ in shorts:
            weights[a] = weights.get(a, 0.0) - 0.5 / len(shorts)

        ret_map = {a: r for a, _, r in cross}
        g_ret = sum(w * ret_map[a] for a, w in weights.items())

        all_assets = set(prev_weights) | set(weights)
        one_way_turnover = 0.5 * sum(abs(weights.get(a, 0.0) - prev_weights.get(a, 0.0)) for a in all_assets)
        n_ret = g_ret - (2.0 * one_way_turnover * cost_rate)

        gross_rets.append(g_ret)
        net_rets.append(n_ret)
        turnovers.append(one_way_turnover)
        prev_weights = weights

    ann = args.periods_per_year
    sqrt_ann = math.sqrt(ann)

    gross_sr = (mean(gross_rets) / std(gross_rets)) * sqrt_ann if std(gross_rets) > 0 else 0.0
    net_sr = (mean(net_rets) / std(net_rets)) * sqrt_ann if std(net_rets) > 0 else 0.0
    downside = [min(0.0, r) for r in net_rets]
    down_sd = math.sqrt(mean([d * d for d in downside]))
    sortino = (mean(net_rets) / down_sd) * sqrt_ann if down_sd > 0 else 0.0
    mdd = max_drawdown(net_rets)
    psr = probabilistic_sharpe_ratio(net_rets, 0.0)
    avg_to = mean(turnovers)
    breakeven_bps = (mean(gross_rets) / (2.0 * avg_to)) * 10000.0 if avg_to > 0 else 0.0

    print(f"=== Quantitative Finance Signal & Backtest Audit ({len(sorted_ts)} periods) ===")
    if duplicate_pairs:
        print(f"[FAIL] Found {duplicate_pairs} duplicate (timestamp, asset) row(s) — check point-in-time join!")
    if non_monotonic_rows:
        print(f"[INFO] Input CSV was not sorted chronologically ({non_monotonic_rows} out-of-order row transitions; sorted prior to backtest).")

    if ics:
        ic_mu, ic_sd = mean(ics), std(ics)
        ric_mu, ric_sd = mean(rank_ics), std(rank_ics)
        icir = ic_mu / ic_sd if ic_sd > 0 else 0.0
        ricir = ric_mu / ric_sd if ric_sd > 0 else 0.0
        print(f"Signal Quality : IC = {ic_mu:.4f} (ICIR = {icir:.2f}) | Rank IC = {ric_mu:.4f} (Rank ICIR = {ricir:.2f})")

    print(f"Gross Sharpe   : {gross_sr:.2f} (Ann. Return = {mean(gross_rets) * ann * 100:.2f}%)")
    print(f"Net Sharpe     : {net_sr:.2f} @ {args.cost_bps:.1f} bps (Ann. Net Return = {mean(net_rets) * ann * 100:.2f}%, Sortino = {sortino:.2f})")
    print(f"Risk & Cost    : Max Drawdown = {mdd * 100:.2f}% | Avg Turnover = {avg_to * 100:.1f}% | Break-Even Cost = {breakeven_bps:.1f} bps")
    print(f"Stat Rigor     : Probabilistic Sharpe Ratio PSR(SR > 0) = {psr * 100:.1f}%")
    if gross_sr > 3.5:
        print("[WARN] Gross Sharpe > 3.5 detected — audit carefully for look-ahead bias, close-price execution illusion, or survivorship bias!")

    return 1 if duplicate_pairs else 0


if __name__ == "__main__":
    sys.exit(main())
