#!/usr/bin/env python3
"""Lint academic .tex or .md manuscripts for AI-slop clichés, notation bugs, and LaTeX anti-patterns."""

import argparse
import re
import sys
from pathlib import Path

BANNED_BUZZWORDS = [
    r"\bdelve(?:s|d|ing)?\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bpivotal\b",
    r"\bgroundbreaking\b",
    r"\bparadigm shift\b",
    r"\brealm\b",
    r"\bunderscore(?:s|d|ing)?\b",
    r"\bintricate\b",
    r"\bmeticulous(?:ly)?\b",
    r"\brevolutioniz(?:e|es|ed|ing)\b",
]

ITALIC_MATH_FUNCS_RE = re.compile(
    r"\$[^$]*(?<![\\a-zA-Z])(?:softmax|sigmoid|relu|gelu|argmin|argmax|LayerNorm|CrossAttn)\s*\([^$]*\$"
)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|cref|Cref|eqref|autoref)\{([^}]+)\}")
ABSTRACT_BLOCK_RE = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.DOTALL)
TABULAR_SPEC_RE = re.compile(r"\\begin\{tabular\*?\}(?:\{[^}]*\})?\{([^}]*)\}")
UNESCAPED_SPACE_CITE_RE = re.compile(r"[A-Za-z0-9]\s+\\(?:cite|citep|ref|eqref)\{")
STRAIGHT_QUOTES_RE = re.compile(r'(?<![=\\])"[^"\n]{1,80}"')


def strip_tex_comments(text: str) -> list[str]:
    return [re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint academic .tex / .md prose and LaTeX style.")
    parser.add_argument("--file", required=True, help="Path to .tex or .md manuscript.")
    args = parser.parse_args()

    path = Path(args.file).resolve()
    if not path.exists():
        print(f"[FAIL] File not found: {path}")
        return 1

    raw = path.read_text(encoding="utf-8", errors="ignore")
    is_tex = path.suffix.lower() == ".tex"
    lines = strip_tex_comments(raw) if is_tex else raw.splitlines()
    clean_full = "\n".join(lines)

    warnings: list[str] = []

    # 1. Buzzword / AI-ism scan
    for lineno, line in enumerate(lines, 1):
        for pat in BANNED_BUZZWORDS:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                warnings.append(f"L{lineno} [STYLE] Avoid LLM buzzword '{m.group(0)}': {line.strip()[:90]}")

    # 2. Overuse of 'novel'
    novel_hits = len(re.findall(r"\bnovel\b", clean_full, re.IGNORECASE))
    if novel_hits > 3:
        warnings.append(f"[STYLE] Word 'novel' appears {novel_hits} times (prefer <= 2; demonstrate novelty via concrete deltas).")

    # 3. Unquantified 'significantly' check
    sig_hits = [
        i + 1
        for i, l in enumerate(lines)
        if re.search(r"\bsignificantly\b", l, re.IGNORECASE)
        and not re.search(r"(?:p\s*[<≤=]|statistically|\d+\.?\d*\s*\\?%)", l, re.IGNORECASE)
    ]
    if sig_hits:
        warnings.append(
            f"[RIGOR] 'significantly' used without p-value or percentage on line(s) {sig_hits[:6]} (prefer 'substantially' unless reporting a statistical test)."
        )

    if is_tex:
        # 4. Citations in abstract
        abs_m = ABSTRACT_BLOCK_RE.search(clean_full)
        if abs_m and re.search(r"\\cite", abs_m.group(1)):
            warnings.append("[LATEX] Found `\\cite` inside `\\begin{abstract}` — abstracts should be self-contained.")

        # 5. Unreferenced \label{}
        defined_labels = set(LABEL_RE.findall(clean_full))
        referenced_labels: set[str] = set()
        for m in REF_RE.finditer(clean_full):
            for k in m.group(1).split(","):
                referenced_labels.add(k.strip())
        unused_labels = sorted(defined_labels - referenced_labels)
        if unused_labels:
            warnings.append(f"[LATEX] Unreferenced `\\label`s ({len(unused_labels)}): {', '.join(unused_labels[:10])}")

        # 6. Vertical rules in tabular & \hline
        for lineno, line in enumerate(lines, 1):
            for tm in TABULAR_SPEC_RE.finditer(line):
                if "|" in tm.group(1):
                    warnings.append(f"L{lineno} [TYPOGRAPHY] Vertical rule `|` in tabular spec `{tm.group(1)}` — prefer `booktabs` without vertical lines.")
            if "\\hline" in line:
                warnings.append(f"L{lineno} [TYPOGRAPHY] Found `\\hline` — prefer `\\toprule`, `\\midrule`, `\\bottomrule`.")
            if ITALIC_MATH_FUNCS_RE.search(line):
                warnings.append(f"L{lineno} [MATH] Multi-letter math operator without `\\operatorname{{...}}`: {line.strip()[:80]}")
            if STRAIGHT_QUOTES_RE.search(line) and not line.lstrip().startswith("\\"):
                warnings.append(f"L{lineno} [TYPOGRAPHY] Straight ASCII quotes `\"...\"` in LaTeX — use `` ``...'' ``.")

        space_cite_lines = [i + 1 for i, l in enumerate(lines) if UNESCAPED_SPACE_CITE_RE.search(l)]
        if space_cite_lines:
            warnings.append(
                f"[TYPOGRAPHY] Breakable space before `\\cite`/`\\ref` on {len(space_cite_lines)} line(s) (e.g. L{space_cite_lines[:5]}) — use `~\\cite{{...}}` or `\\cref{{...}}`."
            )

    print(f"=== Manuscript Prose & Style Lint: {path.name} ===")
    if not warnings:
        print("[OK] Zero prose, rigor, or LaTeX typography warnings detected.")
        return 0

    print(f"Found {len(warnings)} item(s) to review:")
    for w in warnings[:30]:
        print(f"  - {w}")
    if len(warnings) > 30:
        print(f"  ... and {len(warnings) - 30} additional item(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
