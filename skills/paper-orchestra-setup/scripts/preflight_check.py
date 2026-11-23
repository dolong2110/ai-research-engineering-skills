#!/usr/bin/env python3
"""Non-destructive preflight diagnostic for PaperOrchestra."""

import argparse
import importlib.util
import os
import shutil
import sys
from pathlib import Path


def resolve_repo_root(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    cwd = Path.cwd().resolve()
    for p in (cwd, *cwd.parents):
        if (p / "paper_writing_cli.py").exists():
            return p
    script_parents = Path(__file__).resolve().parents
    if len(script_parents) > 4 and (script_parents[4] / "paper_writing_cli.py").exists():
        return script_parents[4]
    return cwd

REQUIRED_MODULES = [
    ("google.genai", "google-genai"),
    ("joblib", "joblib"),
    ("json_repair", "json_repair"),
    ("matplotlib", "matplotlib"),
    ("numpy", "numpy"),
    ("openai", "openai"),
    ("cv2", "opencv-python"),
    ("pydantic", "pydantic"),
    ("pymupdf", "PyMuPDF"),
    ("pymupdf4llm", "pymupdf4llm"),
    ("OpenSSL", "pyOpenSSL"),
    ("pypdf", "pypdf"),
    ("dotenv", "python-dotenv"),
    ("requests", "requests"),
    ("rich", "rich"),
    ("streamlit", "streamlit"),
    ("thefuzz", "thefuzz"),
    ("tqdm", "tqdm"),
]


def parse_env_keys(env_path: Path) -> dict[str, bool]:
    """Check which keys are non-empty in .env or environment without reading values aloud."""
    present: dict[str, bool] = {}
    file_vals: dict[str, str] = {}
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            file_vals[k] = v

    watched = [
        "GEMINI_API_KEY",
        "VERTEX_AI_PROJECT",
        "VERTEX_AI_LOCATION",
        "SEMANTIC_SCHOLAR_API_KEY",
        "OPENAI_API_KEY",
    ]
    for key in watched:
        val = os.environ.get(key) or file_vals.get(key, "")
        placeholder = val.lower().startswith("your_")
        present[key] = bool(val) and not placeholder
    return present


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-destructive preflight diagnostic for PaperOrchestra.")
    parser.add_argument("--repo", default=None, help="Path to paper-orchestra repository (defaults to CWD).")
    args = parser.parse_args()
    repo_root = resolve_repo_root(args.repo)

    print(f"=== PaperOrchestra Preflight Check ({repo_root}) ===\n")
    hard_issues: list[str] = []
    warnings: list[str] = []

    # 1. Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if (sys.version_info.major, sys.version_info.minor) >= (3, 10):
        print(f"[OK] Python interpreter: {py_ver} ({sys.executable})")
    else:
        print(f"[FAIL] Python {py_ver} detected; Python 3.11+ recommended.")
        hard_issues.append("Upgrade Python or run inside `conda run -n paper_orchestra`.")

    # 2. Required Python packages
    missing_pkgs = []
    for mod_name, pip_name in REQUIRED_MODULES:
        try:
            found = importlib.util.find_spec(mod_name) is not None
        except (ModuleNotFoundError, ValueError):
            found = False
        if not found:
            missing_pkgs.append(pip_name)

    if not missing_pkgs:
        print(f"[OK] All {len(REQUIRED_MODULES)} Python packages from requirements.txt are importable.")
    else:
        print(f"[FAIL] Missing {len(missing_pkgs)} Python package(s): {', '.join(missing_pkgs)}")
        hard_issues.append("Install dependencies: `pip install -r requirements.txt`")

    # 3. .env & LLM Credentials (masked)
    env_path = repo_root / ".env"
    keys = parse_env_keys(env_path)
    if env_path.exists():
        print("[OK] Found `.env` file at repository root.")
    else:
        print("[WARN] No `.env` file at repository root (checking process environment).")

    has_vertex = keys["VERTEX_AI_PROJECT"] and keys["VERTEX_AI_LOCATION"]
    has_gemini_key = keys["GEMINI_API_KEY"]
    has_openai = keys["OPENAI_API_KEY"]

    if has_vertex:
        print("[OK] Gemini auth: VERTEX_AI_PROJECT + VERTEX_AI_LOCATION configured (takes precedence).")
    elif has_gemini_key:
        print("[OK] Gemini auth: GEMINI_API_KEY configured.")
    elif has_openai:
        print("[WARN] Only OPENAI_API_KEY configured (note: HybridLiteratureAgent & PlottingAgent call Gemini APIs directly).")
        warnings.append("Configure GEMINI_API_KEY or VERTEX_AI_PROJECT/VERTEX_AI_LOCATION for full pipeline support.")
    else:
        print("[FAIL] No LLM credentials configured (set GEMINI_API_KEY or VERTEX_AI_PROJECT + VERTEX_AI_LOCATION in `.env`).")
        hard_issues.append("Create `.env` from `.agents/skills/paper-orchestra-setup/resources/env.example` and set Gemini credentials.")

    if keys["SEMANTIC_SCHOLAR_API_KEY"]:
        print("[OK] SEMANTIC_SCHOLAR_API_KEY configured.")
    else:
        print("[WARN] SEMANTIC_SCHOLAR_API_KEY not set (unauthenticated Semantic Scholar rate limits apply).")
        warnings.append("Optional: set SEMANTIC_SCHOLAR_API_KEY to avoid 429 throttling in literature search.")

    # 4. LaTeX binaries
    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if pdflatex and bibtex:
        print(f"[OK] LaTeX toolchain found: pdflatex ({pdflatex}), bibtex ({bibtex})")
    else:
        missing_tex = [b for b, p in [("pdflatex", pdflatex), ("bibtex", bibtex)] if not p]
        print(f"[FAIL] Missing LaTeX binaries on PATH: {', '.join(missing_tex)}")
        hard_issues.append("Install MacTeX/BasicTeX or `conda install -c conda-forge texlive-core` so Stage 4 can compile PDFs.")

    # 5. Conference templates check
    templates_dir = repo_root / "templates"
    valid_templates = []
    if templates_dir.is_dir():
        for child in sorted(templates_dir.iterdir()):
            if child.is_dir():
                req = ["template.tex", "guidelines.md", "references.bib"]
                if all((child / r).exists() for r in req):
                    valid_templates.append(child.name)
    if valid_templates:
        print(f"[OK] Valid conference templates: {', '.join(valid_templates)}")
    else:
        print("[FAIL] No valid conference templates found under `templates/`.")
        hard_issues.append("Ensure `templates/<venue>/` contains template.tex, guidelines.md, and references.bib.")

    # 6. Optional PaperBanana sibling check
    pb_dir = repo_root.parent / "PaperBanana"
    if pb_dir.is_dir():
        print(f"[OK] Optional PaperBanana sibling directory detected at {pb_dir}")
    else:
        print("[INFO] Optional `../PaperBanana` sibling directory not present (PlottingAgent will use zero-shot styling fallback).")

    print("\n--- Summary ---")
    if not hard_issues:
        print("STATUS: READY FOR FULL PIPELINE")
        if warnings:
            for w in warnings:
                print(f"  Note: {w}")
        return 0
    else:
        print(f"STATUS: ACTION NEEDED ({len(hard_issues)} blocking item(s))")
        for idx, issue in enumerate(hard_issues, 1):
            print(f"  {idx}. {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
