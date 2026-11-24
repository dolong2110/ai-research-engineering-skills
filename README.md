# AI Research & Engineering Skills (Antigravity Plugin)

[![CI](https://github.com/dolong2110/ai-research-engineering-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/dolong2110/ai-research-engineering-skills/actions/workflows/ci.yml)

A complete, batteries-included **Google Antigravity** plugin bundling **27 modular skills**, **5 specialized subagents**, **17 runnable Python audit/benchmark/scaffolding CLIs**, and always-on scientific & software engineering rules.

Built for interdisciplinary AI/ML/DL/LLM research across **Quantitative Finance**, **LLMs & NLP**, **AI for Chemistry**, **Algorithms & Data Structures**, **Software Engineering**, and automated paper drafting with **[PaperOrchestra](https://github.com/google-research/paper-orchestra)**.

---

## Quick Install (Share with Friends)

### Option 1: Install Globally as an Antigravity Plugin (Recommended)
Makes all 27 skills, 5 subagents, and rules available automatically across **every** workspace:

```bash
git clone https://github.com/dolong2110/ai-research-engineering-skills.git \
  ~/.gemini/config/plugins/ai-research-engineering-skills
```

Antigravity auto-discovers `plugin.json` on the next turn (you can toggle it anytime in **Customizations**).

### Option 2: Install into a Single Project Workspace
Copy `skills/`, `agents/`, and `rules/AGENTS.md` into your repository's `.agents/` folder:

```bash
git clone https://github.com/dolong2110/ai-research-engineering-skills.git /tmp/ai-skills
mkdir -p .agents
cp -R /tmp/ai-skills/skills /tmp/ai-skills/agents .agents/
cp /tmp/ai-skills/rules/AGENTS.md ./AGENTS.md
```

---

## Included Skills (27)

### 1. Core Research, Writing & Publication (4)
| Skill | Purpose | Included Helper CLI / Assets |
| :--- | :--- | :--- |
| `scientific-research` | Falsifiable hypotheses, Heilmeier/MVE gates, fair baselines, 4-axis ablations & multi-seed stats | `analyze_experiment_stats.py` (mean ± std, 95% bootstrap CI, paired $t$-test $p$-values, Cohen's $d$, Markdown + LaTeX `booktabs`) |
| `writing-papers` | Top-conference section blueprints, math notation, captions, LaTeX typography & anti-AI-slop rules | `manuscript_prose_lint.py` (flags buzzwords, unquantified claims, unreferenced `\label`s, vertical rules, math operator bugs) |
| `research-paper-writer` | Formal IEEE (`IEEEtran`) and ACM (`acmart`) survey & experimental paper drafting workflow | `ieee_formatting_specs.md`, `acm_formatting_specs.md`, `writing_style_guide.md` |
| `academic-publication` | Double-blind compliance, NeurIPS/ICLR/ACL checklists, clean arXiv packaging & OpenReview rebuttals | `package_arxiv_and_audit.py` (double-blind + PDF metadata audit & comment-stripped `arxiv_submission.tar.gz` packager) |

### 2. Domain-Specialized AI Research (4)
| Skill | Purpose | Included Helper CLI |
| :--- | :--- | :--- |
| `quant-finance-ml` | Purged/embargoed walk-forward CV, point-in-time timestamps, survivorship & LLM cutoff guards | `backtest_and_leakage_audit.py` (IC, Rank IC, ICIR, Gross/Net Sharpe, Sortino, MDD, Turnover, Break-Even bps, PSR) |
| `llm-and-nlp-research` | SFT/DPO/GRPO, LoRA/QLoRA, RAG, matched token budgets, prompt variance & contamination checks | `nlp_llm_eval_metrics.py` (unbiased `pass@k`, position-debiased pairwise LLM-judge, verbosity bias & Cohen's $\kappa$) |
| `ai-for-chemistry` | SMILES/SELFIES/RDKit hygiene, Murcko scaffold/cluster splits, $E(3)$/$SE(3)$ symmetries & PMO | `chem_dataset_audit.py` (invalid SMILES, salt stripping, canonical cross-split leakage & scaffold overlap) |
| `learned-algorithms-and-combinatorial-ai` | Algorithms with predictions (consistency/robustness/smoothness), learned indexes/filters & neural/LLM CO | — |

### 3. Algorithms, Data Structures, Software Engineering & GitHub CI/CD (11)
| Skill | Purpose | Included Helper CLI / Assets |
| :--- | :--- | :--- |
| `algorithms-and-data-structures` | Big-O sizing, paradigm selection matrix, exchange/invariant proofs & oracle fuzzing | `benchmark_and_complexity.py` (differential brute-force oracle fuzzing + empirical Big-O & peak memory fitter) |
| `system-design-and-architecture` | Capacity sizing, deep modules, Ports & Adapters, idempotency, retries, backpressure & ADRs | `adr_and_rfc_template.md` |
| `api-and-database-engineering` | REST/gRPC contracts, cursor pagination, composite SQL indexes, `EXPLAIN ANALYZE` & zero-downtime migrations | — |
| `performance-and-concurrency` | Amdahl's Law profiling, `asyncio` vs. threads vs. processes vs. vectorization & lock safety | `profile_hotspot.py` (`cProfile` + `tracemalloc` top CPU/heap hotspot summary) |
| `security-and-production-ops` | OWASP hardening, subprocess/SQL/SSRF/deserialization safety & production observability | `security_static_scan.py` (AST security scanner for Python) |
| `python-ml-engineering` | Typed configs, tensor shape contracts, deterministic seeding, `eval()`/`no_grad` hygiene | `ml_code_check.py` (AST ML/Python footgun checker) |
| `testing-and-verification` | Offline API mocks & 4-check ML sanity suite (shapes, gradients, batch independence, 1-batch overfit) | — |
| `systematic-debugging` | Root-cause loop + playbooks for LLM JSON truncation, ThreadPool hangs & training `NaN`s | — |
| `git-and-code-review` | Conventional commits, severity-ranked reviews & pre-commit safety gate | `pre_commit_hygiene.py` (secrets, `>5 MB` checkpoints, conflict markers & syntax checks) |
| `github-repo-and-collaboration` | GitHub repo setup, PR/issue forms, Dependabot, CODEOWNERS, `SECURITY.md`, branch protection & `gh` workflows | `init_github_repo.py` (`init` scaffolder for Python/Node/Plugin/LaTeX + `audit` readiness scorer) |
| `github-actions-cicd` | Fast cached CI/CD pipelines, matrix tests, OIDC releases, LaTeX/Docker builds & Actions security hardening | `lint_workflows.py` (audits `permissions`, `concurrency`, `timeout-minutes`, script injection & pinned actions) |

### 4. PaperOrchestra Automation (8)
Designed to pair with [`google-research/paper-orchestra`](https://github.com/google-research/paper-orchestra):
- `paper-orchestra-setup` (`preflight_check.py`, `env.example`)
- `research-ideation-and-prep` (`prepare_raw_materials.py`, idea & experimental log templates)
- `paper-orchestra-run` (`pipeline_artifacts.md` stage map & selective reruns)
- `literature-and-citations` (`audit_citations.py` offline + Semantic Scholar verifier)
- `scientific-plotting-and-diagrams` (`sync_figures_info.py`)
- `latex-template-and-build` (`compile_and_check_latex.py` static lint + 4-pass compile + 2×2 page grids)
- `paper-peer-review-and-eval` (`run_review_cli.py` wrapper for `AgentReview` + SxS PDF eval)
- `end-to-end-research-workflow` (`research_to_paper_workflow.py` Antigravity `run_workflow` template)

---

## Included Custom Subagents (5)

- `literature-scout` — Prior-work surveys, P0/P1 citation scoping, and hypothesis framing.
- `experiment-analyst` — Baseline/ablation execution and zero-hallucination `experimental_log.md` synthesis.
- `scientific-writer` — Top-conference academic drafting, LaTeX editing, and rebuttal preparation.
- `conference-reviewer` — Double-blind CVPR/ICLR/NeurIPS rubric auditing and claims-to-evidence checks.
- `staff-software-engineer` — System architecture, optimal algorithms/DS, profiling, and security reviews.

---

## Recommended Companion Plugins from the Antigravity Marketplace

For live database and external tooling integrations alongside these 25 custom skills, install these official / partner plugins directly from the Antigravity Marketplace:
- **Chemistry** (`antigravity-plugins-official/plugin/chemistry`) — RDKit, ChEMBL, PubChem, QSAR, docking & co-folding.
- **Scientific Literature** (`antigravity-plugins-official/plugin/scientific-literature`) — arXiv, bioRxiv, Europe PMC, OpenAlex, PubMed, ClinicalTrials & openFDA.
- **Science Overview** (`antigravity-plugins-official/plugin/science-overview`) — Overview of Antigravity's official science plugins.
- **Gemini API** (`gemini-api`) & **Google Antigravity SDK** (`antigravity-plugins-official/plugin/google-antigravity-sdk`) — Gemini CLI/SDK, Deep Research & multi-agent orchestration.
- **Context7** (`antigravity-plugins-partners/plugin/context7`) — Version-exact library documentation lookup.
- **CodeRabbit** (`antigravity-plugins-partners/plugin/coderabbit`) — AI pull-request reviews.
- **Arize AX** (`antigravity-plugins-partners/plugin/arize-skills`) — Agent tracing, evals & prompt optimization.

---

## License

MIT — see [LICENSE](LICENSE).
