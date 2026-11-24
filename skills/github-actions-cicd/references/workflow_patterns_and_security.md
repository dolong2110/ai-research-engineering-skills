# GitHub Actions Patterns & Security Hardening Matrix

## 1. Fast Python + `uv` + `ruff` + `mypy` + `pytest` Workflow Pattern

```yaml
name: Python CI

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
  quality:
    name: Lint & Typecheck
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - run: uv sync --frozen --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src

  test:
    name: Pytest (${{ matrix.python-version }})
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          python-version: ${{ matrix.python-version }}
          enable-cache: true
      - run: uv sync --frozen --dev
      - run: uv run pytest -q --tb=short --cov=src
```

## 2. Tag-Triggered Release + PyPI OIDC Trusted Publishing

```yaml
name: Release

on:
  push:
    tags: ["v*.*.*"]

permissions:
  contents: write
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment: release
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv build
      - name: Publish to PyPI via OIDC (no static API token!)
        uses: pypa/gh-action-pypi-publish@release/v1
      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release create "${GITHUB_REF_NAME}" dist/* --generate-notes
```

## 3. Common CI Pitfalls & Fixes

| Pitfall | Risk / Cost | Fix |
| :--- | :--- | :--- |
| `${{ github.event.pull_request.title }}` inside `run:` | **Remote Code Execution** via crafted PR title (`$(curl ...)`) | Pass via `env: PR_TITLE: ${{ ... }}` and quote `"$PR_TITLE"` |
| Missing `permissions:` block | Default `GITHUB_TOKEN` may inherit broad write scopes | Always declare `permissions: { contents: read }` at workflow root |
| Missing `timeout-minutes:` | Hung test/subprocess burns 360 min of Actions quota | Set `timeout-minutes: 10..20` per job |
| Missing `concurrency:` on PRs | Rapid pushes stack duplicate slow CI jobs | Add `cancel-in-progress: true` grouped by workflow + ref |
| Unpinned `uses: foo/bar@main` | Upstream compromise silently injects code into CI | Pin to `@vX` or full 40-char commit SHA (`@<sha> # vX.Y.Z`) |
| Self-hosted GPU runner on public repos | Fork PRs execute arbitrary code on your lab GPU box! | Never attach self-hosted runners directly to public `pull_request` triggers |
