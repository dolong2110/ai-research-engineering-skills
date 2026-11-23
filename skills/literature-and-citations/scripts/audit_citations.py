#!/usr/bin/env python3
"""Audit LaTeX citations against a BibTeX file, with optional Semantic Scholar verification."""

import argparse
import re
import sys
from pathlib import Path

def _add_paper_orchestra_to_path() -> None:
    for base in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (base / "utils" / "scholar_utils.py").exists():
            if str(base) not in sys.path:
                sys.path.insert(0, str(base))
            return
    parents = Path(__file__).resolve().parents
    if len(parents) > 4 and (parents[4] / "utils" / "scholar_utils.py").exists():
        if str(parents[4]) not in sys.path:
            sys.path.insert(0, str(parents[4]))


_add_paper_orchestra_to_path()

CITE_CMD_RE = re.compile(
    r"\\(?:cite|citet|citep|citealp|citealt|citeauthor|citeyear|nocite)\*?(?:\[[^\]]*\])*\{([^}]+)\}"
)
BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
BIB_TITLE_RE = re.compile(
    r"\btitle\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|\"([^\"]*)\")",
    re.IGNORECASE | re.DOTALL,
)
BIB_YEAR_RE = re.compile(r"\byear\s*=\s*[\{\"]?(\d{4})[\}\"]?", re.IGNORECASE)


def extract_tex_citations(tex_text: str) -> list[str]:
    # Strip LaTeX comments first
    uncommented = "\n".join(
        re.sub(r"(?<!\\)%.*$", "", line) for line in tex_text.splitlines()
    )
    keys: list[str] = []
    for match in CITE_CMD_RE.finditer(uncommented):
        for raw_key in match.group(1).split(","):
            k = raw_key.strip()
            if k and k != "*":
                keys.append(k)
    return keys


def parse_bib_entries(bib_text: str) -> tuple[dict[str, dict], list[str]]:
    entries: dict[str, dict] = {}
    duplicates: list[str] = []
    matches = list(BIB_ENTRY_RE.finditer(bib_text))
    for idx, m in enumerate(matches):
        key = m.group(1).strip()
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(bib_text)
        block = bib_text[start:end]
        if key in entries:
            duplicates.append(key)
        title_m = BIB_TITLE_RE.search(block)
        raw_title = (title_m.group(1) or title_m.group(2) or "").strip() if title_m else ""
        clean_title = re.sub(r"\s+", " ", raw_title.replace("{", "").replace("}", "")).strip()
        year_m = BIB_YEAR_RE.search(block)
        year = int(year_m.group(1)) if year_m else None
        entries[key] = {"title": clean_title, "year": year}
    return entries, duplicates


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit .tex citations and .bib entries.")
    parser.add_argument("--tex", required=True, help="Path to .tex manuscript file.")
    parser.add_argument("--bib", required=True, help="Path to .bib bibliography file.")
    parser.add_argument("--cutoff", default=None, help="Optional YYYY-MM cutoff for S2 verification.")
    parser.add_argument("--verify-s2", action="store_true", help="Verify BibTeX titles via Semantic Scholar API.")
    args = parser.parse_args()

    tex_path = Path(args.tex).resolve()
    bib_path = Path(args.bib).resolve()
    if not tex_path.exists():
        print(f"[FAIL] TeX file not found: {tex_path}")
        return 1
    if not bib_path.exists():
        print(f"[FAIL] Bib file not found: {bib_path}")
        return 1

    cited_list = extract_tex_citations(tex_path.read_text(encoding="utf-8", errors="ignore"))
    cited_set = set(cited_list)
    bib_entries, duplicates = parse_bib_entries(bib_path.read_text(encoding="utf-8", errors="ignore"))
    bib_keys = set(bib_entries.keys())

    missing_in_bib = sorted(cited_set - bib_keys)
    unused_in_tex = sorted(bib_keys - cited_set)
    missing_titles = sorted(k for k, v in bib_entries.items() if not v["title"])

    print(f"=== Citation Audit: {tex_path.name} + {bib_path.name} ===")
    print(f"Total citation occurrences in TeX : {len(cited_list)} ({len(cited_set)} unique keys)")
    print(f"Total entries in BibTeX           : {len(bib_entries)}")

    exit_code = 0
    if missing_in_bib:
        print(f"[FAIL] {len(missing_in_bib)} undefined citation key(s) in TeX: {', '.join(missing_in_bib)}")
        exit_code = 1
    else:
        print("[OK] Every \\cite key in TeX resolves to an entry in BibTeX.")

    if duplicates:
        print(f"[WARN] Duplicate BibTeX key(s): {', '.join(sorted(set(duplicates)))}")

    if missing_titles:
        print(f"[WARN] BibTeX entries missing a title field: {', '.join(missing_titles)}")

    if unused_in_tex:
        print(f"[INFO] {len(unused_in_tex)} uncited BibTeX entry/entries: {', '.join(unused_in_tex[:10])}" + (" ..." if len(unused_in_tex) > 10 else ""))

    if args.verify_s2:
        from utils.scholar_utils import s2_title_search

        unverified = []
        keys_to_check = sorted(cited_set & bib_keys)
        print(f"\nVerifying {len(keys_to_check)} cited BibTeX entry/entries against Semantic Scholar...")
        for key in keys_to_check:
            meta = bib_entries[key]
            if not meta["title"]:
                unverified.append((key, "Empty title"))
                continue
            match = s2_title_search(meta["title"], year_hint=meta["year"], cutoff_date=args.cutoff)
            if match is None:
                unverified.append((key, meta["title"]))
        if unverified:
            print(f"[WARN] {len(unverified)} cited entry/entries could not be matched on Semantic Scholar:")
            for k, t in unverified:
                print(f"  - {k}: {t}")
        else:
            print("[OK] All cited entries verified on Semantic Scholar.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
