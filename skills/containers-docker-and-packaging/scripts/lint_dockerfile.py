#!/usr/bin/env python3
"""Static best-practice & security linter for Dockerfiles."""

import argparse
import re
import sys
from pathlib import Path

SECRET_NAME_RE = re.compile(r"\b(?:API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY|AWS_SECRET)\b", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a Dockerfile for reproducibility, size, and security.")
    parser.add_argument("--file", default="Dockerfile", help="Path to Dockerfile.")
    args = parser.parse_args()

    df_path = Path(args.file).resolve()
    if not df_path.exists():
        print(f"[FAIL] Dockerfile not found: {df_path}")
        return 1

    raw = df_path.read_text(encoding="utf-8", errors="ignore")
    # Join backslash-continued lines while preserving starting line numbers
    logical_lines: list[tuple[int, str]] = []
    buf = ""
    start_no = 1
    for idx, line in enumerate(raw.splitlines(), 1):
        stripped = line.strip()
        if not buf:
            if not stripped or stripped.startswith("#"):
                continue
            start_no = idx
        if stripped.endswith("\\"):
            buf += stripped[:-1] + " "
        else:
            buf += stripped
            logical_lines.append((start_no, buf.strip()))
            buf = ""
    if buf:
        logical_lines.append((start_no, buf.strip()))

    errors: list[str] = []
    warnings: list[str] = []
    has_non_root_user = False

    for lineno, cmd in logical_lines:
        upper = cmd.upper()
        if upper.startswith("FROM "):
            image = cmd.split()[1]
            if ":latest" in image.lower() or (":" not in image and "@" not in image and image.lower() != "scratch"):
                warnings.append(f"L{lineno} [REPRO] Unpinned base image `{image}` — pin explicit version tag or digest.")
        elif upper.startswith("USER "):
            user_val = cmd.split()[1].strip()
            if user_val not in {"root", "0", "0:0"}:
                has_non_root_user = True
        elif upper.startswith("ADD "):
            if not re.search(r"\.(?:tar|tgz|gz|bz2|xz)\b", cmd, re.IGNORECASE):
                warnings.append(f"L{lineno} [HYGIENE] Prefer `COPY` over `ADD` unless auto-extracting local tarballs.")
        elif upper.startswith(("ENV ", "ARG ")):
            if SECRET_NAME_RE.search(cmd) and "=" in cmd:
                val = cmd.split("=", 1)[1].strip()
                if val and not val.startswith("$"):
                    errors.append(f"L{lineno} [SECRET] Hardcoded secret-like value in `ENV`/`ARG` persists in image layers!")
        elif upper.startswith("RUN "):
            if "apt-get install" in cmd:
                if "--no-install-recommends" not in cmd:
                    warnings.append(f"L{lineno} [SIZE] `apt-get install` without `--no-install-recommends`.")
                if "/var/lib/apt/lists" not in cmd:
                    warnings.append(f"L{lineno} [SIZE] Clean up `/var/lib/apt/lists/*` in the same `RUN` layer.")
            if re.search(r"\bpip3?\s+install\b", cmd) and "--no-cache-dir" not in cmd and "--mount=type=cache" not in cmd:
                warnings.append(f"L{lineno} [SIZE] `pip install` without `--no-cache-dir` (or BuildKit cache mount).")
        elif upper.startswith(("CMD ", "ENTRYPOINT ")):
            rest = cmd.split(None, 1)[1].strip() if len(cmd.split(None, 1)) > 1 else ""
            if rest and not rest.startswith("["):
                warnings.append(f"L{lineno} [SIGNALS] Shell-form `{cmd.split()[0]}` wraps PID 1 in `/bin/sh` — prefer JSON exec form `[\"...\"]` for graceful SIGTERM.")

    if not has_non_root_user:
        warnings.append("[SECURITY] No non-root `USER` instruction found — container runs as root by default.")

    if not (df_path.parent / ".dockerignore").exists():
        warnings.append("[BUILD] No `.dockerignore` found next to Dockerfile (risk of copying `.git`/`.env`/checkpoints into build context).")

    print(f"=== Dockerfile Audit: {df_path.name} ===")
    for w in warnings:
        print(f"  [WARN] {w}")
    for e in errors:
        print(f"  [FAIL] {e}")
    if not errors and not warnings:
        print("[OK] Dockerfile passed reproducibility, size, and security checks.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
