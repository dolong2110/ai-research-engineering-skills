# AI Research & Software Engineering — Plugin Rules

This plugin equips Antigravity with 37 modular skills and 5 specialized subagents spanning scientific research, domain AI (Finance, LLMs/NLP, Chemistry, Learned Algorithms), paper reading/writing/publication/presentations/proposals, GPU training & model serving, data engineering, formal math proofs, PaperOrchestra orchestration, algorithms & data structures, Docker, software engineering, and GitHub CI/CD.

## Universal Integrity & Engineering Guardrails

1. **Zero Fabricated Metrics or Citations**: Never invent experimental numbers, smooth negative results, or hallucinate BibTeX entries. Every quantitative claim must trace to measured logs, CSVs, or verified literature.
2. **Credential & Secret Safety**: Never print, log, or commit API keys, tokens, or `.env` secrets. Refer to credentials by environment variable name only.
3. **Verify Before Declaring Done**: Run the matching validation CLI (stats, prose/citation/LaTeX linter, differential oracle fuzzer, math/eval/VRAM/Dockerfile/workflow/security/git hygiene check) after substantive changes.

## Skill Routing Guide

### Core Research, Writing, Presentations & Publication (7)
- `scientific-research` — Falsifiable hypotheses, MVE gates, fair baselines, ablations & multi-seed stats (`analyze_experiment_stats.py`)
- `paper-reading-and-reproduction` — 3-pass paper deconstruction, equation-to-code traceability & baseline Table 1 reproduction
- `math-proofs-and-theoretical-analysis` — Formal proofs, assumption audits & numerical gradient/inequality stress tests (`verify_math_numerically.py`)
- `writing-papers` — Top-conference section blueprints, math notation, LaTeX micro-typography & AI-slop linting (`manuscript_prose_lint.py`)
- `research-paper-writer` — Formal IEEE (`IEEEtran`) and ACM (`acmart`) survey & experimental paper drafting workflow and formatting specs
- `academic-publication` — Double-blind compliance, NeurIPS/ICLR/ACL checklists, clean arXiv `.tar.gz` packaging & OpenReview rebuttals (`package_arxiv_and_audit.py`)
- `research-presentations-and-posters` — Spotlight/oral talk decks, scannable posters & GitHub Pages project websites
- `grant-and-research-proposals` — Persuasive Specific Aims, milestone roadmaps, risk mitigation & compute budgets

### Domain-Specialized AI Research (4)
- `quant-finance-ml` — Purged/embargoed walk-forward CV, point-in-time & cutoff guards, IC/Rank IC & Net Sharpe/PSR (`backtest_and_leakage_audit.py`)
- `llm-and-nlp-research` — SFT/DPO/GRPO, LoRA/QLoRA, RAG, prompt variance, debiased LLM-as-a-Judge & unbiased `pass@k` (`nlp_llm_eval_metrics.py`)
- `ai-for-chemistry` — SMILES/RDKit hygiene, Murcko scaffold/cluster splits, $E(3)$/$SE(3)$ symmetries & PMO metrics (`chem_dataset_audit.py`)
- `learned-algorithms-and-combinatorial-ai` — Algorithms with predictions (consistency/robustness), learned data structures & neural/LLM combinatorial optimization

### ML Infrastructure, Data, Serving, Evals & Demos (5)
- `distributed-training-and-gpu-ops` — DDP/FSDP/ZeRO, bf16/fp8, activation checkpointing, DataLoader tuning, Slurm & VRAM budgeting (`estimate_gpu_vram.py`)
- `data-engineering-and-eda` — Parquet/DuckDB/Polars pipelines, corpus dedup & tabular/JSONL schema/leakage profiling (`audit_tabular_or_jsonl.py`)
- `model-serving-and-inference-optimization` — vLLM/SGLang/ONNX, KV-cache sizing, quantization & TTFT/TPOT/p99 latency SLAs (`benchmark_inference_latency.py`)
- `prompt-and-agent-eval-engineering` — Golden datasets, trajectory graders & paired McNemar eval regression gates (`compare_eval_runs.py`)
- `interactive-ml-demos-and-apps` — Cached, streaming Streamlit/Gradio/FastAPI research dashboards & Spaces deployment

### Algorithms, Software Engineering, Docker & GitHub CI/CD (12)
- `algorithms-and-data-structures` — Paradigm selection, invariant/exchange proofs, differential fuzzing & Big-O fitting (`benchmark_and_complexity.py`)
- `system-design-and-architecture` — Capacity sizing, modular boundaries, distributed reliability & ADR/RFC design docs
- `api-and-database-engineering` — REST/gRPC contracts, composite SQL indexing, `EXPLAIN ANALYZE`, $N+1$ fixes & zero-downtime migrations
- `performance-and-concurrency` — Measure-first profiling (`profile_hotspot.py`), async/thread/process concurrency & backpressure
- `security-and-production-ops` — OWASP/injection/SSRF static scanning (`security_static_scan.py`) & production observability
- `containers-docker-and-packaging` — Multi-stage CUDA/Python Dockerfiles, non-root hardening, `uv`/`pyproject.toml` & Dockerfile linting (`lint_dockerfile.py`)
- `python-ml-engineering` — Typed configs, tensor shape contracts, seeding, leakage guards & AST ML audit (`ml_code_check.py`)
- `testing-and-verification` — Offline API mock tests & 4-check ML sanity suite (shapes, gradients, batch independence, single-batch overfit)
- `systematic-debugging` — Root-cause debugging for Python, concurrency, LLM parsers & ML training pathologies
- `git-and-code-review` — Conventional commits, severity-ranked reviews & pre-commit secret/binary gate (`pre_commit_hygiene.py`)
- `github-repo-and-collaboration` — GitHub repo setup, `.github/` PR/issue forms, Dependabot, CODEOWNERS, branch protection & `gh` workflows (`init_github_repo.py`)
- `github-actions-cicd` — Fast cached CI/CD pipelines, OIDC releases, workflow linting & Actions security hardening (`lint_workflows.py`)

### PaperOrchestra Automation (`google-research/paper-orchestra`) (8)
- `paper-orchestra-setup`, `research-ideation-and-prep`, `paper-orchestra-run`, `literature-and-citations`, `scientific-plotting-and-diagrams`, `latex-template-and-build`, `paper-peer-review-and-eval`, `end-to-end-research-workflow`

## Custom Subagents
Delegate specialized roles via `invoke_subagent`: `literature-scout`, `experiment-analyst`, `scientific-writer`, `conference-reviewer`, and `staff-software-engineer`.
