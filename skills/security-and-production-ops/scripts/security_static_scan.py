#!/usr/bin/env python3
"""AST + pattern static security scanner for Python codebases."""

import argparse
import ast
import re
import sys
from pathlib import Path

SQL_FSTRING_RE = re.compile(
    r"f['\"][^'\"]*\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b[^'\"]*\{",
    re.IGNORECASE,
)


def _dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def scan_py_file(py_path: Path) -> list[str]:
    findings: list[str] = []
    source = py_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = compile(
            source,
            str(py_path),
            "exec",
            flags=ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
    except SyntaxError:
        return findings

    for lineno, line in enumerate(source.splitlines(), 1):
        if not line.lstrip().startswith("#") and SQL_FSTRING_RE.search(line):
            findings.append(f"{py_path}:L{lineno}: [HIGH] Possible SQL injection via f-string — use parameterized placeholders.")

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = _dotted_name(node.func)
        kw_map = {kw.arg: kw.value for kw in node.keywords if kw.arg}

        # 1. Dangerous eval/exec/os.system
        if fn in {"eval", "exec", "os.system", "os.popen"}:
            findings.append(f"{py_path}:L{node.lineno}: [HIGH] Dynamic code/shell execution `{fn}(...)` — verify strict sandboxing/input trust.")

        # 2. subprocess(..., shell=True)
        if fn.startswith("subprocess.") and isinstance(kw_map.get("shell"), ast.Constant) and kw_map["shell"].value is True:
            findings.append(f"{py_path}:L{node.lineno}: [HIGH] `{fn}(..., shell=True)` — pass argv list with `shell=False`.")

        # 3. Unsafe deserialization
        if fn in {"pickle.load", "pickle.loads", "marshal.loads"}:
            findings.append(f"{py_path}:L{node.lineno}: [HIGH] Unsafe deserialization `{fn}(...)`.")
        if fn == "yaml.load" and "Loader" not in kw_map:
            findings.append(f"{py_path}:L{node.lineno}: [HIGH] `yaml.load()` without `SafeLoader` — use `yaml.safe_load()`.")

        # 4. TLS verify=False or missing timeout in requests.*
        if fn in {"requests.get", "requests.post", "requests.put", "requests.delete", "requests.request"}:
            if isinstance(kw_map.get("verify"), ast.Constant) and kw_map["verify"].value is False:
                findings.append(f"{py_path}:L{node.lineno}: [HIGH] `{fn}(..., verify=False)` disables TLS certificate validation.")
            if "timeout" not in kw_map:
                findings.append(f"{py_path}:L{node.lineno}: [MEDIUM] `{fn}(...)` called without explicit `timeout=...` (can hang indefinitely).")

        # 5. tempfile.mktemp race condition
        if fn == "tempfile.mktemp":
            findings.append(f"{py_path}:L{node.lineno}: [MEDIUM] `tempfile.mktemp()` is vulnerable to symlink races — use `NamedTemporaryFile` or `mkstemp`.")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Static security scanner for Python files.")
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
                        part in {".git", "__pycache__", ".venv", "venv"}
                        for part in f.relative_to(p).parts
                    )
                )
            )

    findings: list[str] = []
    for f in py_files:
        findings.extend(scan_py_file(f))

    print(f"=== Security & Production Readiness Scan ({len(py_files)} Python file(s)) ===")
    if not findings:
        print("[OK] Zero security or reliability findings.")
        return 0

    print(f"Found {len(findings)} item(s) to review:")
    for item in findings[:30]:
        print(f"  - {item}")
    if len(findings) > 30:
        print(f"  ... and {len(findings) - 30} additional item(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
