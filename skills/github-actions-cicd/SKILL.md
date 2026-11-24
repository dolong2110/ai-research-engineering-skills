---
name: github-actions-cicd
description: >-
  Author, optimize, harden, and audit GitHub Actions CI/CD workflows (`.github/workflows/*.yml`)
  for linting, type-checking, matrix testing, caching, security scanning, LaTeX PDF
  builds, Docker/GHCR containers, and OIDC tag-driven releases. Use this skill
  whenever writing, debugging, speeding up, or security-reviewing GitHub Actions
  pipelines.
---

# GitHub Actions CI/CD Engineering & Hardening

Use this skill to build fast, reliable, secure GitHub Actions workflows that prevent broken merges without wasting runner minutes or exposing repository secrets.

## 1. Core CI/CD Design Principles

Read [workflow_patterns_and_security.md](./references/workflow_patterns_and_security.md) for reusable templates (Python/`uv`/`ruff`/`pytest`, PyPI Trusted Publishing, Docker/GHCR, LaTeX PDF compilation, and security scanning).

Always include these 5 engineering defaults in every workflow:
1. **Least-Privilege `permissions:`**: Set top-level `permissions: { contents: read }` explicitly, elevating per-job only where needed (`packages: write`, `id-token: write`, `pull-requests: write`).
2. **Cancel Redundant Runs (`concurrency:`)**: On `push`/`pull_request` workflows, cancel obsolete in-flight runs when a new commit pushes to the same PR branch:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```
3. **Explicit `timeout-minutes:`**: Set `timeout-minutes: 10`–`30` on every job (default is 360 minutes—a hung test or API call can burn 6 hours of runner quota!).
4. **Dependency Caching**: Enable built-in caching on `actions/setup-python` (`cache: "pip"`), `astral-sh/setup-uv` (`enable-cache: true`), or `actions/setup-node` (`cache: "npm"`).
5. **Fast Fail-Order Separation**: Run fast checks (<60s: lint, format, static security, type-check) in parallel or ahead of slow multi-version test matrices or builds.

## 2. Critical GitHub Actions Security Rules

- **Prevent Script Injection**: Never interpolate untrusted event strings (`${{ github.event.issue.title }}`, `${{ github.event.pull_request.title }}`, `${{ github.event.comment.body }}`, `${{ github.head_ref }}`) directly inside `run:` shell commands! Pass them through an intermediate `env:` variable and quote `"$VAR"` in shell.
- **Avoid `pull_request_target` + Untrusted Checkout**: Never check out `github.event.pull_request.head.sha` and execute code inside a `pull_request_target` workflow (gives untrusted fork code access to write tokens & secrets!).
- **Pin Action Versions**: Avoid floating `@main` or `@master` refs on third-party actions; use pinned release tags (`@v4`) or full 40-char commit SHAs for security-sensitive/release workflows.
- **Prefer OIDC (`id-token: write`)**: Authenticate to PyPI, AWS, GCP, and Azure via short-lived OIDC federation instead of static long-lived secrets whenever supported.

## 3. Automated Workflow Linter & Security Auditor

Always run [lint_workflows.py](./scripts/lint_workflows.py) after creating or editing `.github/workflows/*.yml`:

```bash
python3 skills/github-actions-cicd/scripts/lint_workflows.py --repo .
```
