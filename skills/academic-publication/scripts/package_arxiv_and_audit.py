#!/usr/bin/env python3
"""Audit manuscripts for double-blind leaks & build clean, comment-stripped arXiv .tar.gz bundles."""

import argparse
import os
import re
import tarfile
import tempfile
import sys
from pathlib import Path

LEAK_PATTERNS = [
    (r"\\thanks\{", "Found `\\thanks{...}` (often leaks funding/affiliations in anonymous drafts)."),
    (r"\\section\*?\{Acknowledg", "Found `Acknowledgments` section (must be omitted in double-blind submissions)."),
    (r"https?://github\.com/(?!anonymous)", "Non-anonymized `github.com` URL detected."),
    (r"https?://huggingface\.co/(?!anonymous)", "Non-anonymized `huggingface.co` URL detected."),
    (r"https?://wandb\.ai/", "Non-anonymized `wandb.ai` URL detected."),
    (r"\b(?:in|follow(?:ing)?)\s+our\s+(?:prior|previous|earlier)\s+work\b", "First-person self-citation phrasing ('our prior work') violates double-blind rules."),
    (r"\\(?:iclrfinalcopy|cvprfinalcopy)\b", "Final camera-ready macro active (`\\iclrfinalcopy` / `\\cvprfinalcopy`) — disable for anonymous review!"),
]

SENSITIVE_COMMENT_RE = re.compile(r"(?<!\\)%(?:.*\b(?:todo|fixme|hack|xxx|author|grant|email|@)\b.*)$", re.IGNORECASE)
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")

BUILD_JUNK_EXTS = {
    ".aux", ".log", ".out", ".toc", ".lof", ".lot", ".fls",
    ".fdb_latexmk", ".synctex.gz", ".blg", ".nav", ".snm", ".vrb",
}


def strip_latex_comments_preserving_verbatim(tex_content: str) -> str:
    """Strip LaTeX % comments safely while preserving \\% and verbatim environments."""
    out_lines: list[str] = []
    in_verbatim = False
    for line in tex_content.splitlines():
        if re.search(r"\\begin\{(?:verbatim|lstlisting|minted)\}", line):
            in_verbatim = True
        if in_verbatim:
            out_lines.append(line)
            if re.search(r"\\end\{(?:verbatim|lstlisting|minted)\}", line):
                in_verbatim = False
            continue

        stripped = re.sub(r"(?<!\\)%.*$", "", line)
        # Drop lines that were purely comments so we don't accidentally introduce paragraph breaks!
        if line.lstrip().startswith("%"):
            continue
        out_lines.append(stripped.rstrip())
    return "\n".join(out_lines) + "\n"


def collect_tex_files(workdir: Path, root_tex: Path) -> list[Path]:
    visited: list[Path] = []
    queue = [root_tex]
    seen = set()
    while queue:
        cur = queue.pop(0)
        if cur in seen or not cur.exists():
            continue
        seen.add(cur)
        visited.append(cur)
        uncommented = strip_latex_comments_preserving_verbatim(
            cur.read_text(encoding="utf-8", errors="ignore")
        )
        for m in INPUT_RE.finditer(uncommented):
            rel = m.group(1).strip()
            cand = (workdir / rel) if rel.endswith(".tex") else (workdir / f"{rel}.tex")
            if cand.exists():
                queue.append(cand.resolve())
    return visited


def cmd_audit(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).resolve()
    root_tex = (workdir / args.tex).resolve()
    if not root_tex.exists():
        print(f"[FAIL] TeX file not found: {root_tex}")
        return 1

    tex_files = collect_tex_files(workdir, root_tex)
    issues: list[str] = []
    comment_leaks: list[str] = []

    for tf in tex_files:
        raw_lines = tf.read_text(encoding="utf-8", errors="ignore").splitlines()
        for lineno, line in enumerate(raw_lines, 1):
            cm = SENSITIVE_COMMENT_RE.search(line)
            if cm:
                comment_leaks.append(f"{tf.name}:L{lineno}: {cm.group(0).strip()[:80]}")
            uncommented = re.sub(r"(?<!\\)%.*$", "", line)
            for pat, msg in LEAK_PATTERNS:
                if re.search(pat, uncommented, re.IGNORECASE):
                    issues.append(f"{tf.name}:L{lineno}: {msg}")

    if args.pdf:
        pdf_path = Path(args.pdf).resolve()
        if pdf_path.exists():
            try:
                import pymupdf  # type: ignore

                doc = pymupdf.open(str(pdf_path))
                meta = doc.metadata or {}
                author_meta = (meta.get("author") or "").strip()
                if author_meta and "anonymous" not in author_meta.lower():
                    issues.append(f"PDF metadata `/Author` is non-empty: '{author_meta}'")
            except ImportError:
                try:
                    from pypdf import PdfReader  # type: ignore

                    reader = PdfReader(str(pdf_path))
                    author_meta = str((reader.metadata or {}).get("/Author", "")).strip()
                    if author_meta and "anonymous" not in author_meta.lower():
                        issues.append(f"PDF metadata `/Author` is non-empty: '{author_meta}'")
                except Exception:
                    pass

    print(f"=== Double-Blind & Publication Audit ({len(tex_files)} TeX file(s)) ===")
    if issues:
        print(f"[FAIL] {len(issues)} double-blind / compliance risk(s) detected:")
        for item in issues:
            print(f"  - {item}")
    else:
        print("[OK] Zero double-blind leaks detected in active TeX content.")

    if comment_leaks:
        print(f"[WARN] {len(comment_leaks)} `%` comment(s) contain TODO/author/email notes (strip before arXiv upload!):")
        for c in comment_leaks[:10]:
            print(f"  - {c}")

    return 1 if issues else 0


def cmd_package_arxiv(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).resolve()
    root_tex = (workdir / args.tex).resolve()
    if not root_tex.exists():
        print(f"[FAIL] TeX file not found: {root_tex}")
        return 1

    tex_files = collect_tex_files(workdir, root_tex)
    referenced_figs: set[Path] = set()
    for tf in tex_files:
        clean = strip_latex_comments_preserving_verbatim(
            tf.read_text(encoding="utf-8", errors="ignore")
        )
        for m in GRAPHICS_RE.finditer(clean):
            ref = m.group(1).strip()
            base_cand = workdir / ref
            for cand in [
                base_cand,
                base_cand.with_suffix(".pdf"),
                base_cand.with_suffix(".png"),
                base_cand.with_suffix(".jpg"),
                base_cand.with_suffix(".jpeg"),
            ]:
                if cand.exists():
                    referenced_figs.add(cand.resolve())
                    break

    bbl_path = root_tex.with_suffix(".bbl")
    has_bbl = bbl_path.exists()

    out_tar = Path(args.out).resolve()
    out_tar.parent.mkdir(parents=True, exist_ok=True)

    staged_files: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # 1. Write comment-stripped .tex files
        for tf in tex_files:
            rel = tf.relative_to(workdir)
            dst = tmp_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            cleaned = strip_latex_comments_preserving_verbatim(
                tf.read_text(encoding="utf-8", errors="ignore")
            )
            dst.write_text(cleaned, encoding="utf-8")
            staged_files.append(str(rel))

        # 2. Copy all style/macro/bibliography support files (.sty, .cls, .bst, .bbl, .bib, preamble/math .tex)
        for item in workdir.rglob("*"):
            if not item.is_file():
                continue
            rel = item.relative_to(workdir)
            if any(part.startswith(".") for part in rel.parts):
                continue
            if item.suffix.lower() in BUILD_JUNK_EXTS:
                continue
            if item.suffix.lower() in {".sty", ".cls", ".bst", ".bbl", ".bib", ".def", ".clo"}:
                dst = tmp_dir / rel
                if not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(item.read_bytes())
                    staged_files.append(str(rel))

        # 3. Copy referenced figures
        for fig in sorted(referenced_figs):
            rel = fig.relative_to(workdir)
            dst = tmp_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(fig.read_bytes())
            staged_files.append(str(rel))

        with tarfile.open(out_tar, "w:gz") as tar:
            for item in sorted(tmp_dir.rglob("*")):
                if item.is_file():
                    tar.add(item, arcname=str(item.relative_to(tmp_dir)))

    size_kb = os.path.getsize(out_tar) / 1024.0
    print(f"[OK] Packaged clean arXiv tarball: {out_tar} ({size_kb:.1f} KB, {len(set(staged_files))} file(s))")
    if not has_bbl:
        print(
            f"[WARN] `{bbl_path.name}` was not found in {workdir}! Compile with pdflatex+bibtex first so `{bbl_path.name}` is bundled (arXiv requires pre-compiled `.bbl`)."
        )
    else:
        print(f"[OK] Included compiled bibliography `{bbl_path.name}`.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Double-blind compliance audit & clean arXiv packager.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_aud = sub.add_parser("audit", help="Audit .tex and optional .pdf for double-blind & arXiv comment leaks.")
    p_aud.add_argument("--workdir", required=True, help="LaTeX directory.")
    p_aud.add_argument("--tex", default="template.tex", help="Root .tex filename inside --workdir.")
    p_aud.add_argument("--pdf", default=None, help="Optional compiled PDF to inspect metadata.")
    p_aud.set_defaults(func=cmd_audit)

    p_pkg = sub.add_parser("package-arxiv", help="Create comment-stripped arXiv .tar.gz source archive.")
    p_pkg.add_argument("--workdir", required=True, help="LaTeX directory.")
    p_pkg.add_argument("--tex", default="template.tex", help="Root .tex filename inside --workdir.")
    p_pkg.add_argument("--out", default="./arxiv_submission.tar.gz", help="Output .tar.gz path.")
    p_pkg.set_defaults(func=cmd_package_arxiv)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
