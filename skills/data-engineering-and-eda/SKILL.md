---
name: data-engineering-and-eda
description: >-
  Curate, profile, clean, deduplicate, and audit structured and text datasets
  (CSV, JSONL, Parquet, DuckDB, Polars) across Quantitative Finance, LLM/NLP
  corpora, and Chemistry. Enforces schema validation, missingness/outlier audits,
  exact & near-duplicate detection, train/test split-leakage checks, and Dataset
  Cards. Use this skill before training models or building ETL pipelines.
---

# Data Engineering, Dataset Curation & Exploratory Data Analysis

Garbage data silently invalidates every downstream experiment. Always audit schemas, duplicates, missingness, outliers, and split overlap *before* writing training loops.

## 1. Automated Schema, Quality & Split-Overlap Profiler

Run [audit_tabular_or_jsonl.py](./scripts/audit_tabular_or_jsonl.py) on any CSV, TSV, or JSONL dataset to profile column types, null rates, numeric quantiles (`p01/p50/p99`), exact duplicate rows, text length distributions, and cross-split key overlap:

```bash
python3 skills/data-engineering-and-eda/scripts/audit_tabular_or_jsonl.py \
  --input data/dataset.csv \
  --split-col split \
  --id-col text
```

## 2. Out-of-Core Pipelines for Large Datasets

- **Stop loading multi-GB CSVs into pandas**: Convert raw exports once to compressed **Apache Parquet** (`zstd` / `snappy`) and query/transform out-of-core with **DuckDB** or **Polars** (`scan_parquet` lazy execution -> `sink_parquet`) to stay within laptop/node RAM and run 10×–50× faster.
- **Immutable Raw Layer**: Keep `data/raw/` strictly read-only; emit versioned, deterministic transformations into `data/processed/<version>/` with SHA-256 checksums and row-count assertions at every join (catch accidental many-to-many fan-out joins!).

## 3. Domain-Specific Data Hygiene Checklists

- **LLM / NLP Pretraining & SFT Corpora (JSONL)**:
  - Deduplicate exact strings AND near-duplicates (MinHash LSH on 5-grams / 13-grams) *across* train and eval benchmarks to prevent contamination.
  - Inspect `p01`/`p50`/`p99` character/token lengths, empty completions, mojibake encoding errors, and template-formatting leaks.
- **Quantitative Finance Panels (Parquet/CSV)**:
  - Verify primary key uniqueness on `(timestamp, asset_id)`, timezone alignment (UTC), missing-bar forward-fill limits (never backfill!), and survivorship/delisting coverage.
- **Chemistry / Scientific Tables**:
  - Pair with `ai-for-chemistry` (`chem_dataset_audit.py`) to check SMILES canonicalization, counter-ion salts, assay unit consistency (`nM` vs `uM`), and conflicting replicate measurements on identical compounds.

## 4. Documenting Curated Datasets

Record a concise `DATASET_CARD.md` alongside `data/processed/`: source URL/version, license, collection window, filtering/dedup drops at each stage (funnel counts), split methodology, and known biases/caveats.
