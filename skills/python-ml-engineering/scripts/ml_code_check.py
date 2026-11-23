#!/usr/bin/env python3
"""AST-based static checker for common Python & ML research code footguns."""

import argparse
import ast
import re
import sys
from pathlib import Path

HARDCODED_PATH_RE = re.compile(r"['\"](?:/" + r"Users/|/home/[a-zA-Z0-9_]+/|C:\\Users\\)")


def check_file(py_path: Path) -> list[str]:
    findings: list[str] = []
    source = py_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = compile(
            source,
            str(py_path),
            "exec",
            flags=ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
    except SyntaxError as exc:
        return [f"{py_path}:L{exc.lineno}: [SYNTAX ERROR] {exc.msg}"]

    lines = source.splitlines()
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if HARDCODED_PATH_RE.search(line):
            findings.append(f"{py_path.name}:L{lineno}: [PORTABILITY] Hardcoded user home path.")

    has_eval_call = False
    has_no_grad = "no_grad" in source or "inference_mode" in source

    for node in ast.walk(tree):
        # 1. Mutable default arguments
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
            for d in defaults:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    findings.append(
                        f"{py_path.name}:L{node.lineno}: [BUG RISK] Mutable default argument in `{node.name}()` — use `None` and initialize inside body."
                    )
                    break

        # 2. Bare except:
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(
                f"{py_path.name}:L{node.lineno}: [HYGIENE] Bare `except:` catches KeyboardInterrupt/SystemExit — use `except Exception:`."
            )

        # 3. breakpoint() / pdb.set_trace()
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "breakpoint":
                findings.append(f"{py_path.name}:L{node.lineno}: [DEBUG] Leftover `breakpoint()`.")
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "set_trace":
                findings.append(f"{py_path.name}:L{node.lineno}: [DEBUG] Leftover `set_trace()`.")
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "eval":
                has_eval_call = True

    if has_eval_call and ("torch" in source) and not has_no_grad:
        findings.append(
            f"{py_path.name}: [ML PERF] Calls `.eval()` in a PyTorch file without `torch.no_grad()` / `torch.inference_mode()`."
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Python/ML files for common footguns.")
    parser.add_argument("--path", nargs="+", required=True, help="Files or directories to scan.")
    args = parser.parse_args()

    py_files: list[Path] = []
    for raw in args.path:
        p = Path(raw).resolve()
        if p.is_file() and p.suffix == ".py":
            py_files.append(p)
        elif p.is_dir():
            py_files.extend(
                sorted(
                    f for f in p.rglob("*.py")
                    if not any(
                        part.startswith(".") or part == "__pycache__"
                        for part in f.relative_to(p).parts
                    )
                )
            )

    all_findings: list[str] = []
    for f in py_files:
        all_findings.extend(check_file(f))

    print(f"=== Python & ML Code Audit ({len(py_files)} file(s) scanned) ===")
    if not all_findings:
        print("[OK] Zero issues detected.")
        return 0

    print(f"Found {len(all_findings)} item(s):")
    for item in all_findings[:40]:
        print(f"  - {item}")
    if len(all_findings) > 40:
        print(f"  ... and {len(all_findings) - 40} more.")
    return 1 if any("[SYNTAX ERROR]" in x for x in all_findings) else 0


if __name__ == "__main__":
    sys.exit(main())
