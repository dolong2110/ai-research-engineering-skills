#!/usr/bin/env python3
"""Lint & security-audit `.github/workflows/*.yml` files."""

import argparse
import re
import sys
from pathlib import Path

import yaml

UNTRUSTED_EXPR_RE = re.compile(
    r"\$\{\{\s*github\.event\.(?:issue|pull_request|comment|review|discussion|head_commit)\."
    r"(?:title|body|message|name)|github\.head_ref\s*\}\}"
)
FLOATING_REF_RE = re.compile(r"@(?:main|master|HEAD|latest)$", re.IGNORECASE)


def audit_workflow(wf_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    raw = wf_path.read_text(encoding="utf-8", errors="ignore")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return [f"{wf_path.name}: [YAML SYNTAX] {exc}"], []

    if not isinstance(data, dict):
        return [f"{wf_path.name}: [SCHEMA] Workflow file must parse to a YAML mapping."], []

    # PyYAML parses bare `on:` as boolean True
    triggers = data.get("on", data.get(True))
    jobs = data.get("jobs", {})
    if not triggers:
        errors.append(f"{wf_path.name}: [SCHEMA] Missing `on:` trigger block.")
    if not isinstance(jobs, dict) or not jobs:
        errors.append(f"{wf_path.name}: [SCHEMA] Missing or empty `jobs:` block.")
        return errors, warnings

    has_top_perms = "permissions" in data
    has_concurrency = "concurrency" in data

    trigger_names = set()
    if isinstance(triggers, str):
        trigger_names.add(triggers)
    elif isinstance(triggers, list):
        trigger_names.update(str(t) for t in triggers)
    elif isinstance(triggers, dict):
        trigger_names.update(str(k) for k in triggers.keys())

    if "pull_request" in trigger_names and not has_concurrency:
        warnings.append(
            f"{wf_path.name}: [EFFICIENCY] Missing `concurrency:` (`cancel-in-progress: true`) on `pull_request` workflow."
        )

    is_prt = "pull_request_target" in trigger_names

    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            continue
        if not has_top_perms and "permissions" not in job:
            warnings.append(
                f"{wf_path.name} ({job_id}): [SECURITY] No explicit `permissions:` block — declare minimal `permissions: {{contents: read}}`."
            )
        if "timeout-minutes" not in job:
            warnings.append(
                f"{wf_path.name} ({job_id}): [RELIABILITY] Missing `timeout-minutes:` (defaults to 360 min)."
            )

        for idx, step in enumerate(job.get("steps", []) or [], 1):
            if not isinstance(step, dict):
                continue
            step_label = step.get("name") or f"step #{idx}"
            uses = str(step.get("uses") or "")
            run_cmd = str(step.get("run") or "")

            if uses and FLOATING_REF_RE.search(uses):
                errors.append(
                    f"{wf_path.name} ({job_id} / {step_label}): [SECURITY] Unpinned floating action ref `{uses}` — pin to `@vX` or commit SHA."
                )

            if run_cmd and UNTRUSTED_EXPR_RE.search(run_cmd):
                errors.append(
                    f"{wf_path.name} ({job_id} / {step_label}): [INJECTION] Untrusted `${{{{ github.event.* }}}}` interpolated directly inside `run:` — pass via `env:` instead."
                )

            if is_prt and uses.startswith("actions/checkout"):
                with_cfg = step.get("with") or {}
                ref = str(with_cfg.get("ref") or "")
                if "pull_request.head" in ref:
                    errors.append(
                        f"{wf_path.name} ({job_id} / {step_label}): [CRITICAL] `pull_request_target` checks out untrusted PR head ref (`{ref}`)."
                    )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint and security-audit GitHub Actions workflows.")
    parser.add_argument("--repo", default=".", help="Repository root directory.")
    args = parser.parse_args()

    wf_dir = Path(args.repo).resolve() / ".github" / "workflows"
    if not wf_dir.is_dir():
        print(f"[INFO] No `.github/workflows/` directory found under {Path(args.repo).resolve()}.")
        return 0

    wf_files = sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")))
    if not wf_files:
        print(f"[INFO] No workflow YAML files found in {wf_dir}.")
        return 0

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for wf in wf_files:
        errs, warns = audit_workflow(wf)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    print(f"=== GitHub Actions CI/CD Audit ({len(wf_files)} workflow(s)) ===")
    for w in all_warnings:
        print(f"  [WARN] {w}")
    for e in all_errors:
        print(f"  [FAIL] {e}")

    if not all_errors and not all_warnings:
        print("[OK] All workflow files passed schema, efficiency, and security checks.")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
