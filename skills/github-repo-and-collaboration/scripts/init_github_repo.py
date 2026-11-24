#!/usr/bin/env python3
"""Scaffold and audit standard GitHub repository governance files and starter CI."""

import argparse
import sys
from pathlib import Path

PR_TEMPLATE = """## Summary
<!-- Briefly describe what changed and why. Link related issues: Closes #123 -->

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature / skill / experiment
- [ ] Refactor / performance / documentation
- [ ] Breaking change

## Verification
<!-- List exact commands, tests, linters, or benchmarks run -->
- [ ] Tests / validation scripts pass locally
- [ ] Linting, security scan, and pre-commit hygiene checks pass
- [ ] Documentation / README updated if behavior changed
"""

BUG_ISSUE_FORM = """name: Bug Report
description: Report a bug, failing script, or unexpected behavior
labels: ["bug"]
body:
  - type: textarea
    id: summary
    attributes:
      label: What happened?
      description: Clear description of the bug and expected behavior.
    validations:
      required: true
  - type: textarea
    id: repro
    attributes:
      label: Reproduction Steps
      placeholder: |
        1. Run `...`
        2. Observe error `...`
    validations:
      required: true
  - type: input
    id: env
    attributes:
      label: Environment
      placeholder: "OS, Python/Node version, commit SHA"
"""

FEATURE_ISSUE_FORM = """name: Feature / Skill Request
description: Propose a new feature, skill, template, or enhancement
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem or Goal
      description: What workflow or research/engineering problem does this solve?
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposed Solution
      description: Describe the desired behavior, CLI interface, or skill scope.
"""

ISSUE_CONFIG = """blank_issues_enabled: true
"""

CONTRIBUTING_MD = """# Contributing

Contributions, bug fixes, and new improvements are welcome!

## Workflow
1. Fork the repository and create a topic branch from `main`:
   ```bash
   git switch -c feat/short-description
   ```
2. Keep commits focused and follow Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
3. Run all local checks and CI validators before opening a Pull Request.
4. Open a PR against `main` filling out the PR template and confirming all GitHub Actions checks are green.
"""

SECURITY_MD = """# Security Policy

## Reporting a Vulnerability
Please **do not** open a public GitHub issue for security vulnerabilities, leaked credentials, or unsafe code execution bugs.

Instead, report vulnerabilities privately via GitHub **Security Advisories** (Security tab -> *Report a vulnerability*) or contact the repository maintainer directly. Include reproduction steps and affected commit/version so we can patch and disclose responsibly.
"""


def make_dependabot(project_type: str) -> str:
    updates = [
        """  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      github-actions:
        patterns: ["*"]"""
    ]
    if project_type == "python":
        updates.append(
            """  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly\""""
        )
    elif project_type == "node":
        updates.append(
            """  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly\""""
        )
    return "version: 2\nupdates:\n" + "\n\n".join(updates) + "\n"


def make_starter_ci(project_type: str) -> str:
    if project_type == "plugin":
        return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    name: Validate Plugin, Skills & Scripts
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install PyYAML
        run: python -m pip install --upgrade pip pyyaml

      - name: Validate plugin.json, skills, and subagents
        run: |
          python - <<'PY'
          import json, pathlib, yaml
          root = pathlib.Path(".")
          manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
          allowed = {"name", "displayName", "version", "description", "logo", "suggestedPrompts", "author", "homepage", "repository", "disabled"}
          unknown = set(manifest.keys()) - allowed
          assert not unknown, f"Unknown plugin.json fields: {unknown}"

          skills = sorted((root / "skills").glob("*/SKILL.md"))
          assert skills, "No skills found"
          for s in skills:
              parts = s.read_text(encoding="utf-8").split("---", 2)
              assert len(parts) >= 3, f"Missing YAML frontmatter: {s}"
              meta = yaml.safe_load(parts[1])
              assert meta["name"] == s.parent.name, f"Name mismatch in {s}"
              assert len(meta["description"]) > 20, f"Short description in {s}"

          agents = sorted((root / "agents").glob("*.md"))
          for a in agents:
              parts = a.read_text(encoding="utf-8").split("---", 2)
              meta = yaml.safe_load(parts[1])
              assert meta["name"] == a.stem, f"Agent name mismatch: {a}"
              assert meta["subagent"] is True and meta["mainAgent"] is False
          print(f"Validated {len(skills)} skills and {len(agents)} subagents.")
          PY

      - name: Static code, security & workflow lint
        run: |
          python skills/python-ml-engineering/scripts/ml_code_check.py --path skills
          python skills/security-and-production-ops/scripts/security_static_scan.py --path skills
          python skills/github-actions-cicd/scripts/lint_workflows.py --repo .
          python skills/algorithms-and-data-structures/scripts/benchmark_and_complexity.py --self-test --sizes 200,400,800
"""
    if project_type == "node":
        return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:
    name: Lint, Typecheck & Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test --if-present
"""
    if project_type == "latex":
        return """name: Build LaTeX PDF

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build_pdf:
    name: Compile Manuscript
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Compile LaTeX document
        uses: xu-cheng/latex-action@v3
        with:
          root_file: main.tex
      - name: Upload compiled PDF artifact
        uses: actions/upload-artifact@v4
        with:
          name: manuscript-pdf
          path: main.pdf
"""
    # Default: python
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:
    name: Lint & Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip ruff pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Lint with ruff
        run: ruff check .
      - name: Run tests
        run: pytest -q --tb=short
"""


def write_if_needed(path: Path, content: str, overwrite: bool) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return f"[SKIP] {path.name} already exists ({path})"
    path.write_text(content, encoding="utf-8")
    return f"[OK]   Wrote {path}"


def cmd_init(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"[FAIL] Repository path does not exist: {repo}")
        return 1

    owner = args.owner.lstrip("@")
    targets = [
        (repo / ".github/PULL_REQUEST_TEMPLATE.md", PR_TEMPLATE),
        (repo / ".github/ISSUE_TEMPLATE/bug_report.yml", BUG_ISSUE_FORM),
        (repo / ".github/ISSUE_TEMPLATE/feature_request.yml", FEATURE_ISSUE_FORM),
        (repo / ".github/ISSUE_TEMPLATE/config.yml", ISSUE_CONFIG),
        (repo / ".github/dependabot.yml", make_dependabot(args.project_type)),
        (repo / ".github/CODEOWNERS", f"* @{owner}\n"),
        (repo / ".github/workflows/ci.yml", make_starter_ci(args.project_type)),
        (repo / "CONTRIBUTING.md", CONTRIBUTING_MD),
        (repo / "SECURITY.md", SECURITY_MD),
    ]

    print(f"=== Scaffolding GitHub Repo Files ({args.project_type}) in {repo} ===")
    for p, content in targets:
        print(write_if_needed(p, content, args.overwrite))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    checks = [
        ("README.md", (repo / "README.md").exists()),
        ("LICENSE", (repo / "LICENSE").exists() or (repo / "LICENSE.md").exists()),
        (".gitignore", (repo / ".gitignore").exists()),
        ("CONTRIBUTING.md", (repo / "CONTRIBUTING.md").exists()),
        ("SECURITY.md", (repo / "SECURITY.md").exists()),
        (".github/PULL_REQUEST_TEMPLATE.md", (repo / ".github/PULL_REQUEST_TEMPLATE.md").exists()),
        (".github/ISSUE_TEMPLATE/", (repo / ".github/ISSUE_TEMPLATE").is_dir()),
        (".github/dependabot.yml", (repo / ".github/dependabot.yml").exists()),
        (".github/CODEOWNERS", (repo / ".github/CODEOWNERS").exists()),
        (
            ".github/workflows/*.yml",
            (repo / ".github/workflows").is_dir()
            and any((repo / ".github/workflows").glob("*.y*ml")),
        ),
    ]
    print(f"=== GitHub Repository Readiness Audit ({repo.name}) ===")
    present = 0
    for label, ok in checks:
        status = "[OK]  " if ok else "[MISS]"
        if ok:
            present += 1
        print(f"  {status} {label}")
    print(f"\nScore: {present}/{len(checks)} standard GitHub governance & CI checks present.")
    return 0 if present == len(checks) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold or audit GitHub repository governance & CI files.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create .github/ templates, Dependabot, CODEOWNERS, docs & starter CI.")
    p_init.add_argument("--repo", default=".", help="Target repository directory.")
    p_init.add_argument("--owner", required=True, help="GitHub username or @org/team for CODEOWNERS.")
    p_init.add_argument("--project-type", choices=["python", "node", "plugin", "latex"], default="python")
    p_init.add_argument("--overwrite", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_aud = sub.add_parser("audit", help="Check repository for standard GitHub governance & CI files.")
    p_aud.add_argument("--repo", default=".", help="Target repository directory.")
    p_aud.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
