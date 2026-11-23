#!/usr/bin/env python3
"""Pre-commit hygiene check: secrets, large binaries, conflict markers, and Python syntax."""

import argparse
import ast
import py_compile
import re
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for p in (cur, *cur.parents):
        if (p / ".git").exists():
            return p
    return cur


MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB

SECRET_PATTERNS = [
    (r"AIza[0-9A-Za-z\-_]{35}", "Possible Google / Gemini API key (`AIza...`)"),
    (r"sk-[A-Za-z0-9\-_]{20,}", "Possible OpenAI API key (`sk-...`)"),
    (r"ghp_[A-Za-z0-9]{36}", "Possible GitHub personal access token (`ghp_...`)"),
    (r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----", "Private key block"),
]

CONFLICT_RE = re.compile(r"^(?:<{7}\s|={7}$|>{7}\s)", re.MULTILINE)
FORBIDDEN_FILENAMES = {".env", ".env.local", ".env.production", "credentials.json"}
HEAVY_EXTS = {".pt", ".pth", ".ckpt", ".safetensors", ".onnx", ".h5", ".zip", ".tar.gz"}


def candidate_files(repo_root: Path) -> list[Path]:
    res = subprocess.run(
        ["git", "-C", str(repo_root), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    paths: list[Path] = []
    for raw in res.stdout.splitlines():
        if len(raw) < 4:
            continue
        status = raw[:2]
        if "D" in status:
            continue
        rel = raw[3:].strip().split(" -> ")[-1].strip('"')
        full = (repo_root / rel).resolve()
        if full.is_file():
            paths.append(full)
        elif full.is_dir():
            paths.extend(f for f in full.rglob("*") if f.is_file())
    return sorted(set(paths))


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-commit git hygiene check.")
    parser.add_argument("--repo", default=None, help="Repository path (defaults to current git root).")
    args = parser.parse_args()
    repo_root = find_repo_root(Path(args.repo) if args.repo else None)

    files = candidate_files(repo_root)
    print(f"=== Git Pre-Commit Hygiene Check ({len(files)} modified/untracked file(s) in {repo_root.name}) ===")
    issues: list[str] = []
    warnings: list[str] = []

    for f in files:
        rel = f.relative_to(repo_root)
        if f.name in FORBIDDEN_FILENAMES:
            issues.append(f"[SECRET] Forbidden credential file staged/untracked: `{rel}`")
            continue

        size = f.stat().st_size
        if size > MAX_FILE_BYTES:
            issues.append(f"[SIZE] `{rel}` is {size / (1024 * 1024):.1f} MB (>5 MB limit).")
        elif any(str(rel).lower().endswith(ext) for ext in HEAVY_EXTS):
            warnings.append(f"[ARTIFACT] Binary/checkpoint file `{rel}` detected — verify it belongs in git.")

        if f.suffix == ".py":
            try:
                py_compile.compile(str(f), doraise=True)
            except py_compile.PyCompileError as exc:
                # Antigravity run_workflow scripts allow top-level `await`
                is_workflow_ok = False
                if "workflow" in f.name:
                    try:
                        compile(
                            f.read_text(encoding="utf-8"),
                            str(f),
                            "exec",
                            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
                        )
                        is_workflow_ok = True
                    except SyntaxError:
                        pass
                if not is_workflow_ok:
                    issues.append(f"[SYNTAX] `{rel}` failed py_compile: {exc.msg}")

        # Scan text files <= 1 MB for secrets & conflict markers
        if size <= 1024 * 1024:
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if CONFLICT_RE.search(text):
                issues.append(f"[CONFLICT] Unresolved merge conflict marker in `{rel}`.")
            for pat, desc in SECRET_PATTERNS:
                if re.search(pat, text):
                    issues.append(f"[SECRET] {desc} pattern matched in `{rel}`.")

    for w in warnings:
        print(f"  {w}")
    if issues:
        print(f"[FAIL] {len(issues)} blocking issue(s):")
        for i in issues:
            print(f"  - {i}")
        return 1

    print("[OK] All modified/untracked files passed secret, size, conflict, and syntax checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
