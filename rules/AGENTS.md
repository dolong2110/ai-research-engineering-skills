# AI Research & Software Engineering — Plugin Rules

This plugin equips Antigravity with 27 modular skills and 5 specialized subagents spanning scientific research, domain AI (Finance, LLMs/NLP, Chemistry, Learned Algorithms), academic writing & publication, PaperOrchestra orchestration, algorithms & data structures, software engineering, and GitHub CI/CD.

## Universal Integrity & Engineering Guardrails

1. **Zero Fabricated Metrics or Citations**: Never invent experimental numbers, smooth negative results, or hallucinate BibTeX entries. Every quantitative claim must trace to measured logs, CSVs, or verified literature.
2. **Credential & Secret Safety**: Never print, log, or commit API keys, tokens, or `.env` secrets. Refer to credentials by environment variable name only.
3. **Verify Before Declaring Done**: Run the matching validation CLI (stats, prose/citation/LaTeX linter, differential oracle fuzzer, code/security/git hygiene check) after substantive changes.

## Skill Routing Guide

### Core Research, Writing & Publication
- `scientific-research` — Falsifiable hypotheses, MVE gates, fair baselines, ablations & multi-seed stats (`analyze_experiment_stats.py`)
- `writing-papers` — Top-conference section blueprints, math notation, LaTeX micro-typography & AI-slop linting (`manuscript_prose_lint.py`)
- `research-paper-writer` — Formal IEEE (`IEEEtran`) and ACM (`acmart`) survey & experimental paper drafting workflow and formatting specs
- `academic-publication` — Double-blind compliance, NeurIPS/ICLR/ACL checklists, clean arXiv `.tar.gz` packaging & OpenReview rebuttals (`package_arxiv_and_audit.py`)

### Domain-Specialized AI Research
- `quant-finance-ml` — Purged/embargoed walk-forward CV, point-in-time & cutoff guards, IC/Rank IC & Net Sharpe/PSR (`backtest_and_leakage_audit.py`)
- `llm-and-nlp-research` — SFT/DPO/GRPO, LoRA/QLoRA, RAG, prompt variance, debiased LLM-as-a-Judge & unbiased `pass@k` (`nlp_llm_eval_metrics.py`)
- `ai-for-chemistry` — SMILES/RDKit hygiene, Murcko scaffold/cluster splits, $E(3)$/$SE(3)$ symmetries & PMO metrics (`chem_dataset_audit.py`)
- `learned-algorithms-and-combinatorial-ai` — Algorithms with predictions (consistency/robustness), learned data structures & neural/LLM combinatorial optimization

### Algorithms, Data Structures & Software Engineering
- `algorithms-and-data-structures` — Paradigm selection, invariant/exchange proofs, differential fuzzing & Big-O fitting (`benchmark_and_complexity.py`)
- `system-design-and-architecture` — Capacity sizing, modular boundaries, distributed reliability & ADR/RFC design docs
- `api-and-database-engineering` — REST/gRPC contracts, composite SQL indexing, `EXPLAIN ANALYZE`, $N+1$ fixes & zero-downtime migrations
- `performance-and-concurrency` — Measure-first profiling (`profile_hotspot.py`), async/thread/process concurrency & backpressure
- `security-and-production-ops` — OWASP/injection/SSRF static scanning (`security_static_scan.py`) & production observability
- `python-ml-engineering` — Typed configs, tensor shape contracts, seeding, leakage guards & AST ML audit (`ml_code_check.py`)
- `testing-and-verification` — Offline API mock tests & 4-check ML sanity suite (shapes, gradients, batch independence, single-batch overfit)
- `systematic-debugging` — Root-cause debugging for Python, concurrency, LLM parsers & ML training pathologies
- `git-and-code-review` — Conventional commits, severity-ranked reviews & pre-commit secret/binary gate (`pre_commit_hygiene.py`)
- `github-repo-and-collaboration` — GitHub repo setup, `.github/` PR/issue forms, Dependabot, CODEOWNERS, branch protection & `gh` workflows (`init_github_repo.py`)
- `github-actions-cicd` — Fast cached CI/CD pipelines, OIDC releases, workflow linting & Actions security hardening (`lint_workflows.py`)

### PaperOrchestra Automation (`google-research/paper-orchestra`)
- `paper-orchestra-setup`, `research-ideation-and-prep`, `paper-orchestra-run`, `literature-and-citations`, `scientific-plotting-and-diagrams`, `latex-template-and-build`, `paper-peer-review-and-eval`, `end-to-end-research-workflow`

## Custom Subagents
Delegate specialized roles via `invoke_subagent`: `literature-scout`, `experiment-analyst`, `scientific-writer`, `conference-reviewer`, and `staff-software-engineer`.
