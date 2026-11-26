# AI Research & Engineering Skills (Antigravity Plugin)

A complete, batteries-included **Google Antigravity** plugin bundling **41 modular skills**, **5 specialized subagents**, **27 runnable Python audit/benchmark/scaffolding CLIs**, and always-on scientific & software engineering rules.

Built for interdisciplinary AI/ML/DL/LLM research across **Quantitative Finance**, **LLMs & NLP**, **AI for Chemistry**, **Algorithms & Data Structures**, **ML Systems & Serving**, **Software Engineering & GitHub CI/CD**, and automated paper drafting with **[PaperOrchestra](https://github.com/google-research/paper-orchestra)**.

---

## Quick Install (Share with Friends)

### Option 1: Install Globally as an Antigravity Plugin (Recommended)
Makes all 41 skills, 5 subagents, and rules available automatically across **every** workspace:

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

## Included Skills (41)

### 1. Core Research, Theory, Writing, Presentations & Publication (8)
| Skill | Purpose | Included Helper CLI / Assets |
| :--- | :--- | :--- |
| `scientific-research` | Falsifiable hypotheses, Heilmeier/MVE gates, fair baselines, 4-axis ablations & multi-seed stats | `analyze_experiment_stats.py` (mean ± std, 95% bootstrap CI, paired $t$-test $p$-values, Cohen's $d$, Markdown + LaTeX `booktabs`) |
| `paper-reading-and-reproduction` | 3-pass paper deconstruction, appendix hyperparameter mining & Table 1 baseline reproduction | `reproduction_matrix_template.md` |
| `math-proofs-and-theoretical-analysis` | Formal proofs, explicit assumption audits, complexity/convergence/equivariance bounds | `verify_math_numerically.py` (central-difference gradient checker & randomized inequality counterexample hunter) |
| `writing-papers` | Top-conference section blueprints, math notation, captions, LaTeX typography & anti-AI-slop rules | `manuscript_prose_lint.py` (flags buzzwords, unquantified claims, unreferenced `\label`s, vertical rules, math operator bugs) |
| `research-paper-writer` | Formal IEEE (`IEEEtran`) and ACM (`acmart`) survey & experimental paper drafting workflow | `ieee_formatting_specs.md`, `acm_formatting_specs.md`, `writing_style_guide.md` |
| `academic-publication` | Double-blind compliance, NeurIPS/ICLR/ACL checklists, clean arXiv packaging & OpenReview rebuttals | `package_arxiv_and_audit.py` (double-blind + PDF metadata audit & comment-stripped `arxiv_submission.tar.gz` packager) |
| `research-presentations-and-posters` | 5-min spotlight / 15-min oral talks (Beamer/Slides), A0 posters & GitHub Pages project sites | `talk_and_poster_blueprint.md` |
| `grant-and-research-proposals` | Specific Aims, modular research pitches, risk/mitigation tables & compute budgets | `research_proposal_template.md` |

### 2. Domain & Advanced AI Research (7)
| Skill | Purpose | Included Helper CLI |
| :--- | :--- | :--- |
| `quant-finance-ml` | Purged/embargoed walk-forward CV, point-in-time timestamps, survivorship & LLM cutoff guards | `backtest_and_leakage_audit.py` (IC, Rank IC, ICIR, Gross/Net Sharpe, Sortino, MDD, Turnover, Break-Even bps, PSR) |
| `llm-and-nlp-research` | SFT/DPO/GRPO, LoRA/QLoRA, RAG, matched token budgets, prompt variance & contamination checks | `nlp_llm_eval_metrics.py` (unbiased `pass@k`, position-debiased pairwise LLM-judge, verbosity bias & Cohen's $\kappa$) |
| `ai-for-chemistry` | SMILES/SELFIES/RDKit hygiene, Murcko scaffold/cluster splits, $E(3)$/$SE(3)$ symmetries & PMO | `chem_dataset_audit.py` (invalid SMILES, salt stripping, canonical cross-split leakage & scaffold overlap) |
| `learned-algorithms-and-combinatorial-ai` | Algorithms with predictions (consistency/robustness/smoothness), learned indexes/filters & neural/LLM CO | — |
| `causal-inference-and-econometrics` | Causal DAGs, DiD/staggered DiD, 2SLS IV, RDD, DML cross-fitting & HAC/clustered SEs | `causal_diagnostics.py` (covariate balance SMD, 2×2 DiD ATE & Newey–West HAC mean tests) |
| `reinforcement-learning-and-decision-making` | PPO/GRPO/SAC/Offline RL, truncation vs. termination, reward-hacking audits & rliable evaluation | `rliable_eval.py` (IQM, stratified bootstrap 95% CIs & Probability of Improvement) |
| `bayesian-uncertainty-and-active-learning` | Probability calibration, Split/Adaptive Conformal Prediction & GP/BoTorch active learning | `calibration_and_conformal.py` (ECE, MCE, Brier, NLL & distribution-free conformal coverage) |

### 3. ML Infrastructure, Data, Serving, Evals & Interactive Demos (5)
| Skill | Purpose | Included Helper CLI |
| :--- | :--- | :--- |
| `distributed-training-and-gpu-ops` | PyTorch DDP/FSDP/ZeRO, bf16/fp8, activation checkpointing, DataLoader & Slurm preemption safety | `estimate_gpu_vram.py` (per-GPU weights/grads/optimizer/activations VRAM & GPU tier estimator) |
| `data-engineering-and-eda` | Parquet/DuckDB/Polars out-of-core pipelines, corpus dedup & Dataset Cards | `audit_tabular_or_jsonl.py` (schema, nulls, quantiles, exact duplicates & cross-split overlap profiler) |
| `model-serving-and-inference-optimization` | vLLM/SGLang/ONNX/TensorRT, KV-cache sizing, FP8/AWQ/INT4 quantization & load testing | `benchmark_inference_latency.py` (TTFT, TPOT, E2E p50/p95/p99, tok/s & SLA gate) |
| `prompt-and-agent-eval-engineering` | Golden test sets, tool-call trajectory grading, failure taxonomies & merge regression gates | `compare_eval_runs.py` (baseline vs. candidate slice diffs, regressed IDs & exact McNemar's test) |
| `interactive-ml-demos-and-apps` | Cached, streaming Streamlit/Gradio/FastAPI model & research dashboards | — |

### 4. Algorithms, Systems, Software Engineering, Docker & GitHub CI/CD (13)
| Skill | Purpose | Included Helper CLI / Assets |
| :--- | :--- | :--- |
| `algorithms-and-data-structures` | Big-O sizing, paradigm selection matrix, exchange/invariant proofs & oracle fuzzing | `benchmark_and_complexity.py` (differential brute-force oracle fuzzing + empirical Big-O & peak memory fitter) |
| `systems-cpp-rust-triton-kernels` | Low-latency C++20/Rust (SoA, SIMD, lock-free, PyBind11/PyO3) & Triton/CUDA GPU kernels | `roofline_analyzer.py` (arithmetic intensity, ridge point, memory-vs-compute diagnosis & utilization) |
| `system-design-and-architecture` | Capacity sizing, deep modules, Ports & Adapters, idempotency, retries, backpressure & ADRs | `adr_and_rfc_template.md` |
| `api-and-database-engineering` | REST/gRPC contracts, cursor pagination, composite SQL indexes, `EXPLAIN ANALYZE` & zero-downtime migrations | — |
| `performance-and-concurrency` | Amdahl's Law profiling, `asyncio` vs. threads vs. processes vs. vectorization & lock safety | `profile_hotspot.py` (`cProfile` + `tracemalloc` top CPU/heap hotspot summary) |
| `security-and-production-ops` | OWASP hardening, subprocess/SQL/SSRF/deserialization safety & production observability | `security_static_scan.py` (AST security scanner for Python) |
| `containers-docker-and-packaging` | Multi-stage PyTorch/CUDA/RDKit/TeX Dockerfiles, non-root hardening & `uv`/`pyproject.toml` packaging | `lint_dockerfile.py` (unpinned base tags, root user, cache hygiene, secret-in-`ENV` & `.dockerignore` linter) |
| `python-ml-engineering` | Typed configs, tensor shape contracts, deterministic seeding, `eval()`/`no_grad` hygiene | `ml_code_check.py` (AST ML/Python footgun checker) |
| `testing-and-verification` | Offline API mocks & 4-check ML sanity suite (shapes, gradients, batch independence, 1-batch overfit) | — |
| `systematic-debugging` | Root-cause loop + playbooks for LLM JSON truncation, ThreadPool hangs & training `NaN`s | — |
| `git-and-code-review` | Conventional commits, severity-ranked reviews & pre-commit safety gate | `pre_commit_hygiene.py` (secrets, `>5 MB` checkpoints, conflict markers & syntax checks) |
| `github-repo-and-collaboration` | GitHub repo setup, PR/issue forms, Dependabot, CODEOWNERS, `SECURITY.md`, branch protection & `gh` workflows | `init_github_repo.py` (`init` scaffolder for Python/Node/Plugin/LaTeX + `audit` readiness scorer) |
| `github-actions-cicd` | Fast cached CI/CD pipelines, matrix tests, OIDC releases, LaTeX/Docker builds & Actions security hardening | `lint_workflows.py` (audits `permissions`, `concurrency`, `timeout-minutes`, script injection & pinned actions) |

### 5. PaperOrchestra Automation (8)
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

For live database, workspace, and browser tooling integrations alongside these 37 custom skills:
- **Chemistry** (`antigravity-plugins-official/plugin/chemistry`) — RDKit, ChEMBL, PubChem, QSAR, docking & co-folding.
- **Scientific Literature** (`antigravity-plugins-official/plugin/scientific-literature`) — arXiv, bioRxiv, Europe PMC, OpenAlex, PubMed, ClinicalTrials & openFDA.
- **Science Overview** (`antigravity-plugins-official/plugin/science-overview`) — Overview of Antigravity's official science plugins.
- **Google Slides / Docs / Drive / Sheets / Gmail** — Official Google Workspace plugins for talk decks, docs, and trackers.
- **Chrome DevTools** (`antigravity-plugins-official/plugin/chrome-devtools-plugin`) — Browser debugging, performance & accessibility profiling for ML demos.
- **Gemini API** & **Google Antigravity SDK** — Gemini CLI/SDK, Deep Research & multi-agent orchestration.
- **Context7** (`antigravity-plugins-partners/plugin/context7`), **CodeRabbit** (`antigravity-plugins-partners/plugin/coderabbit`), **Arize AX** (`antigravity-plugins-partners/plugin/arize-skills`).

---

## Local Verification (CI Suite)

Run all plugin manifest, skill YAML, security, workflow lint, and self-test checks locally in seconds:

```bash
./scripts/run_ci.sh
```

---

## License

MIT — see [LICENSE](LICENSE).
