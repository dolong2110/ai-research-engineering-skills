---
name: paper-orchestra-setup
description: >-
  Bootstrap, diagnose, and configure the PaperOrchestra environment. Use this skill
  when setting up the repository for the first time, configuring .env API keys
  (Gemini, Vertex AI, OpenAI, Semantic Scholar), creating the paper_orchestra Conda
  environment, installing pdflatex/bibtex, or troubleshooting missing dependencies.
---

# PaperOrchestra Setup & Preflight

Use this skill to verify or provision all runtime dependencies required by PaperOrchestra before running multi-agent pipelines.

## 1. Run the Non-Destructive Preflight Check

Always run [preflight_check.py](./scripts/preflight_check.py) first to see what is already configured and what is missing (secrets are masked):

```bash
python3 skills/paper-orchestra-setup/scripts/preflight_check.py
```

To check against the `paper_orchestra` Conda environment specifically:

```bash
conda run -n paper_orchestra python skills/paper-orchestra-setup/scripts/preflight_check.py
```

## 2. Python & Conda Environment Setup

PaperOrchestra targets Python 3.11:

```bash
conda create -y -n paper_orchestra python=3.11
conda run -n paper_orchestra pip install -r requirements.txt
```

## 3. Configure `.env` Credentials

If `.env` does not exist at the repository root, copy [env.example](./resources/env.example) to `.env` and ask the user to populate their keys (never echo secret values in chat):

```bash
cp -n skills/paper-orchestra-setup/resources/env.example .env
```

Key resolution rules in `utils/gemini_utils.py` and `utils/scholar_utils.py`:
- **Gemini via Vertex AI** (`VERTEX_AI_PROJECT` + `VERTEX_AI_LOCATION`): Takes precedence over `GEMINI_API_KEY` when both are non-empty. Requires Application Default Credentials (`gcloud auth application-default login`).
- **Gemini Developer API** (`GEMINI_API_KEY`): Used when Vertex AI variables are unset/empty.
- **Semantic Scholar** (`SEMANTIC_SCHOLAR_API_KEY`): Optional; `s2_title_search` works unauthenticated at lower rate limits, but setting an API key prevents 429 throttling during parallel `HybridLiteratureAgent` and `citation_f1.py` runs.
- **OpenAI** (`OPENAI_API_KEY`): Only needed if passing `gpt-*`, `o1*`, or `o3*` to `--writer_model_name` / `--reflection_model_name`.

## 4. LaTeX Toolchain (`pdflatex` + `bibtex`)

`utils/pdf_utils.py:compile_latex` invokes `pdflatex` and `bibtex` directly. Without them, Stages 1–3 still produce `.tex` and `.bib` files, retrieve literature, and generate figures, **but Stage 4 (`ContentRefinementAgent`) cannot compile `final_paper.pdf`**.

Install options if `pdflatex` is missing:
- **macOS (Homebrew BasicTeX)**:
  ```bash
  brew install --cask basictex
  # Ensure /Library/TeX/texbin is on PATH, then install common conference packages:
  sudo /Library/TeX/texbin/tlmgr update --self
  sudo /Library/TeX/texbin/tlmgr install collection-fontsrecommended collection-latexextra algorithms booktabs cleveref subcaption multirow natbib
  ```
- **Conda-scoped TeX (no sudo required)**:
  ```bash
  conda install -y -n paper_orchestra -c conda-forge texlive-core
  ```

## 5. Optional: PaperBanana Few-Shot Assets

`utils/paper_banana_utils.py` checks `../PaperBanana` (sibling directory to `paper-orchestra`) for optional few-shot reference images (`data/PaperBananaBench/`) and style guides (`style_guides/neurips2025_*_style_guide.md`). Plotting still works without it (falling back to zero-shot styling), or you can clone PaperBanana alongside this repo if desired.

## Validation

Re-run `preflight_check.py` and confirm `READY FOR FULL PIPELINE` (or verify that all required Python modules, `.env` credentials, and `pdflatex`/`bibtex` report `[OK]`).
