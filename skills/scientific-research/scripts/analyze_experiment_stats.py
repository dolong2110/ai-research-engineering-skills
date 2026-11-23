#!/usr/bin/env python3
"""Compute multi-seed mean ± std, 95% bootstrap CI, paired p-values, and Markdown/LaTeX tables.

Input CSV format example:
  method,seed,Seen_J,Unseen_J,Null_S
  Baseline_SOTA,0,34.10,49.40,0.008
  Baseline_SOTA,1,34.30,49.68,0.006
  Ours,0,43.25,54.40,0.017
  Ours,1,43.61,54.76,0.017
"""

import argparse
import csv
import math
import random
import sys
from collections import defaultdict
from pathlib import Path


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def sample_std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def bootstrap_ci95(xs: list[float], n_boot: int = 2000, rng_seed: int = 42) -> tuple[float, float]:
    if len(xs) < 2:
        v = xs[0] if xs else float("nan")
        return (v, v)
    rng = random.Random(rng_seed)
    n = len(xs)
    means = sorted(mean([xs[rng.randrange(n)] for _ in range(n)]) for _ in range(n_boot))
    lo = means[int(0.025 * n_boot)]
    hi = means[int(0.975 * n_boot)]
    return (lo, hi)


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for incomplete beta function (Numerical Recipes)."""
    max_it = 200
    eps = 3e-12
    fpmin = 1e-30
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_it + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betainc_reg(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def paired_ttest_pvalue(diffs: list[float]) -> float:
    """Exact two-sided paired Student's t-test p-value (stdlib only, matches scipy.stats.ttest_rel)."""
    n = len(diffs)
    if n < 2:
        return float("nan")
    mu = mean(diffs)
    sd = sample_std(diffs)
    if sd == 0.0:
        return 0.0 if mu != 0.0 else 1.0
    t_stat = abs(mu) / (sd / math.sqrt(n))
    df = n - 1
    x = df / (df + t_stat * t_stat)
    return _betainc_reg(0.5 * df, 0.5, x)


def cohens_d_paired(diffs: list[float]) -> float:
    sd = sample_std(diffs)
    if sd == 0.0:
        return float("inf") if mean(diffs) != 0 else 0.0
    return mean(diffs) / sd


def parse_metrics_arg(spec: str) -> list[tuple[str, str]]:
    out = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            name, direction = item.split(":", 1)
            direction = direction.strip().lower()
            if direction not in {"max", "min"}:
                raise ValueError(f"Direction for {name} must be 'max' or 'min', got '{direction}'")
            out.append((name.strip(), direction))
        else:
            out.append((item, "max"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze multi-seed experimental results.")
    parser.add_argument("--input", required=True, help="CSV file with columns: method, seed, <metric1>, ...")
    parser.add_argument("--baseline", default=None, help="Baseline method name for paired significance tests.")
    parser.add_argument(
        "--metrics",
        required=True,
        help="Comma-separated metric specs, e.g. 'Acc:max,F1:max,Loss:min'.",
    )
    parser.add_argument("--precision", type=int, default=2, help="Decimal places in formatted tables.")
    args = parser.parse_args()

    csv_path = Path(args.input).resolve()
    if not csv_path.exists():
        print(f"[FAIL] Input CSV not found: {csv_path}")
        return 1

    metric_specs = parse_metrics_arg(args.metrics)
    data: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    method_order: list[str] = []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m_name = row["method"].strip()
            seed = row.get("seed", str(len(data[m_name]))).strip()
            if m_name not in method_order:
                method_order.append(m_name)
            for m_col, _ in metric_specs:
                if m_col in row and row[m_col] != "":
                    data[m_name][m_col][seed] = float(row[m_col])

    baseline = args.baseline or (method_order[0] if method_order else None)
    prec = args.precision

    # Compute summary stats and rankings per metric
    stats: dict[tuple[str, str], dict] = {}
    best_method: dict[str, str] = {}
    second_method: dict[str, str] = {}

    for m_col, direction in metric_specs:
        scored = []
        for m_name in method_order:
            seed_map = data[m_name][m_col]
            vals = [seed_map[s] for s in sorted(seed_map)]
            mu = mean(vals)
            sd = sample_std(vals)
            ci_lo, ci_hi = bootstrap_ci95(vals)
            pval = float("nan")
            d_val = float("nan")
            if baseline and baseline in data and m_name != baseline:
                base_map = data[baseline][m_col]
                common_seeds = sorted(set(seed_map) & set(base_map))
                if len(common_seeds) >= 2:
                    diffs = [
                        (seed_map[s] - base_map[s]) if direction == "max" else (base_map[s] - seed_map[s])
                        for s in common_seeds
                    ]
                    pval = paired_ttest_pvalue(diffs)
                    d_val = cohens_d_paired(diffs)
            stats[(m_name, m_col)] = {
                "n": len(vals),
                "mean": mu,
                "std": sd,
                "ci95": (ci_lo, ci_hi),
                "pval": pval,
                "cohens_d": d_val,
            }
            scored.append((mu if direction == "max" else -mu, m_name))
        scored.sort(reverse=True)
        if scored:
            best_method[m_col] = scored[0][1]
        if len(scored) > 1:
            second_method[m_col] = scored[1][1]

    # 1. Markdown Table
    headers = ["Method"] + [f"{m} ({'↑' if d == 'max' else '↓'})" for m, d in metric_specs]
    print("### Markdown Summary Table (`mean ± std`)\n")
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join([":---"] * len(headers)) + " |")
    for m_name in method_order:
        cells = [f"**{m_name}**" if m_name != baseline else m_name]
        for m_col, _ in metric_specs:
            st = stats[(m_name, m_col)]
            cell = f"{st['mean']:.{prec}f} ± {st['std']:.{prec}f}"
            if not math.isnan(st["pval"]) and st["pval"] < 0.05 and st["cohens_d"] > 0:
                cell += "†"
            if best_method.get(m_col) == m_name:
                cell = f"**{cell}**"
            cells.append(cell)
        print("| " + " | ".join(cells) + " |")

    # 2. LaTeX booktabs Table
    col_spec = "l" + "c" * len(metric_specs)
    tex_headers = ["Method"] + [
        f"{m.replace('_', ' ')} ($\\{'uparrow' if d == 'max' else 'downarrow'}$)"
        for m, d in metric_specs
    ]
    print("\n### LaTeX `booktabs` Snippet (`\\dagger` denotes paired $p < 0.05$ vs. baseline)\n")
    print("\\begin{tabular}{@{}" + col_spec + "@{}}")
    print("  \\toprule")
    print("  " + " & ".join(tex_headers) + " \\\\")
    print("  \\midrule")
    for m_name in method_order:
        row_cells = [m_name.replace("_", "\\_")]
        for m_col, _ in metric_specs:
            st = stats[(m_name, m_col)]
            sig = "^\\dagger" if (not math.isnan(st["pval"]) and st["pval"] < 0.05 and st["cohens_d"] > 0) else ""
            val_str = f"{st['mean']:.{prec}f} \\pm {st['std']:.{prec}f}{sig}"
            if best_method.get(m_col) == m_name:
                cell = f"$\\mathbf{{{val_str}}}$"
            elif second_method.get(m_col) == m_name:
                cell = f"\\underline{{${val_str}$}}"
            else:
                cell = f"${val_str}$"
            row_cells.append(cell)
        print("  " + " & ".join(row_cells) + " \\\\")
    print("  \\bottomrule")
    print("\\end{tabular}")

    # 3. Detailed Diagnostics
    if baseline:
        print(f"\n### Paired Significance Diagnostics (vs. `{baseline}`)")
        for m_name in method_order:
            if m_name == baseline:
                continue
            for m_col, _ in metric_specs:
                st = stats[(m_name, m_col)]
                lo, hi = st["ci95"]
                print(
                    f"- {m_name} [{m_col}] (n={st['n']}): mean={st['mean']:.{prec}f}, 95% CI=[{lo:.{prec}f}, {hi:.{prec}f}], paired p={st['pval']:.4f}, Cohen's d={st['cohens_d']:.2f}"
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
