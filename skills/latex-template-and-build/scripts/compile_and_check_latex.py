#!/usr/bin/env python3
"""Static lint, 4-pass LaTeX compile, log diagnostics, and 2x2 page grid renderer."""

import argparse
import re
import shutil
import sys
from pathlib import Path

def _add_paper_orchestra_to_path() -> None:
    for base in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (base / "utils" / "pdf_utils.py").exists():
            if str(base) not in sys.path:
                sys.path.insert(0, str(base))
            return
    parents = Path(__file__).resolve().parents
    if len(parents) > 4 and (parents[4] / "utils" / "pdf_utils.py").exists():
        if str(parents[4]) not in sys.path:
            sys.path.insert(0, str(parents[4]))


_add_paper_orchestra_to_path()

INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
OVERFULL_RE = re.compile(r"^(Overfull \\[hv]box .+)$", re.MULTILINE)
UNDEF_REF_RE = re.compile(r"^LaTeX Warning: (?:Reference|Citation) `([^']+)' .* undefined", re.MULTILINE)
LATEX_ERR_RE = re.compile(r"^! (.+)$", re.MULTILINE)


def static_lint(workdir: Path, tex_path: Path) -> list[str]:
    issues: list[str] = []
    raw = tex_path.read_text(encoding="utf-8", errors="ignore")
    uncommented = "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in raw.splitlines())

    if "cleverref" in uncommented:
        issues.append("[FAIL] Found typo `cleverref` — must be `cleveref`.")

    if "\\begin{center}" in uncommented and "\\includegraphics" in uncommented:
        issues.append("[WARN] Found `\\begin{center}` — conference guidelines prefer `\\centering` inside figures/tables.")

    for m in INCLUDEGRAPHICS_RE.finditer(uncommented):
        img_ref = m.group(1).strip()
        if not img_ref.startswith("figures/"):
            issues.append(f"[WARN] `\\includegraphics{{{img_ref}}}` is missing the mandatory `figures/` prefix.")
        candidate = workdir / img_ref
        candidates_with_ext = [
            candidate,
            candidate.with_suffix(".pdf"),
            candidate.with_suffix(".png"),
            candidate.with_suffix(".jpg"),
        ]
        if not any(c.exists() for c in candidates_with_ext):
            issues.append(f"[FAIL] Referenced figure not found on disk: {img_ref} (searched under {workdir})")

    if re.search(r"https?://github\.com/(?!anonymous)", uncommented, re.IGNORECASE):
        issues.append("[WARN] Non-anonymized GitHub URL detected — double-blind submissions require anonymous links.")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint, compile, and visually inspect a PaperOrchestra LaTeX folder.")
    parser.add_argument("--workdir", required=True, help="Directory containing the .tex file, .sty/.bst, and figures/.")
    parser.add_argument("--tex", default="template.tex", help="Filename of the .tex file inside --workdir.")
    parser.add_argument("--out-pdf", default=None, help="Output PDF path (defaults to <workdir>/<tex_stem>.pdf).")
    parser.add_argument("--grid-dir", default=None, help="Optional directory to render 2x2 page grid PNGs.")
    parser.add_argument("--lint-only", action="store_true", help="Run static .tex checks without invoking pdflatex.")
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    tex_path = workdir / Path(args.tex).name
    if not tex_path.exists():
        print(f"[FAIL] TeX file not found: {tex_path}")
        return 1

    print(f"=== Static Lint: {tex_path} ===")
    lint_issues = static_lint(workdir, tex_path)
    if lint_issues:
        for item in lint_issues:
            print(f"  {item}")
    else:
        print("  [OK] Static LaTeX checks passed.")

    if args.lint_only:
        return 1 if any(i.startswith("[FAIL]") for i in lint_issues) else 0

    if not shutil.which("pdflatex") or not shutil.which("bibtex"):
        print("[FAIL] `pdflatex` or `bibtex` not found on PATH. Run with `--lint-only` or install TeX Live (see `paper-orchestra-setup`).")
        return 1

    from utils.pdf_utils import compile_latex, pdf_to_grid_images
    import pymupdf

    stem = tex_path.stem
    out_pdf = Path(args.out_pdf).resolve() if args.out_pdf else (workdir / f"{stem}_compiled.pdf")
    compile_latex(cwd=str(workdir), pdf_file=str(out_pdf), texfile_name=stem, timeout=60)

    log_file = workdir / f"{stem}.log"
    if log_file.exists():
        log_text = log_file.read_text(encoding="utf-8", errors="ignore")
        errs = LATEX_ERR_RE.findall(log_text)
        undefs = sorted(set(UNDEF_REF_RE.findall(log_text)))
        overfulls = OVERFULL_RE.findall(log_text)
        if errs:
            print(f"[WARN] {len(errs)} LaTeX `!` error(s) in {log_file.name}: {errs[:5]}")
        if undefs:
            print(f"[WARN] Undefined references/citations ({len(undefs)}): {', '.join(undefs[:10])}")
        if overfulls:
            print(f"[INFO] {len(overfulls)} overfull box warning(s) in {log_file.name}.")

    if not out_pdf.exists():
        print("[FAIL] Compilation did not produce an output PDF.")
        return 1

    doc = pymupdf.open(str(out_pdf))
    print(f"[OK] Compiled PDF saved to {out_pdf} ({len(doc)} page(s)).")

    if args.grid_dir:
        grids = pdf_to_grid_images(str(out_pdf), str(Path(args.grid_dir).resolve()))
        print(f"[OK] Rendered {len(grids)} 2x2 page inspection grid(s): {', '.join(grids)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
