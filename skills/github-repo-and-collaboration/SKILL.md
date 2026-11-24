---
name: github-repo-and-collaboration
description: >-
  Set up, configure, and manage professional GitHub repositories and collaboration
  workflows using `gh` CLI and standard `.github/` governance files. Covers repo
  bootstrapping, PR/issue templates, Dependabot, CODEOWNERS, SECURITY.md,
  CONTRIBUTING.md, branch protection rulesets, pull-request reviews, issue triage,
  and semantic GitHub Releases. Use this skill whenever creating a GitHub repo,
  adding `.github/` templates, configuring branch protection, managing PRs/issues,
  or publishing releases.
---

# GitHub Repository Setup & Collaboration

Use this skill to bootstrap production-ready GitHub repositories with standard governance files and operate PRs, issues, branch protection, and releases cleanly via `gh`.

## 1. One-Command Repository Scaffolding & Readiness Audit

Run [init_github_repo.py](./scripts/init_github_repo.py) to audit an existing repo or scaffold standard GitHub files without overwriting existing work:

```bash
# Audit any repository for missing GitHub governance & CI files
python3 skills/github-repo-and-collaboration/scripts/init_github_repo.py audit --repo .

# Scaffold .github/ templates, Dependabot, CODEOWNERS, SECURITY.md, CONTRIBUTING.md & starter CI
python3 skills/github-repo-and-collaboration/scripts/init_github_repo.py init \
  --repo . \
  --owner <github-username> \
  --project-type python   # choices: python | node | plugin | latex
```

Files generated on `init`:
- `.github/PULL_REQUEST_TEMPLATE.md` — structured summary, verification checklist, and breaking-change callout.
- `.github/ISSUE_TEMPLATE/bug_report.yml` & `feature_request.yml` + `config.yml` — structured GitHub Issue Forms.
- `.github/dependabot.yml` — weekly automated PRs for `github-actions` + ecosystem packages (`pip`/`npm`).
- `.github/CODEOWNERS` — automatic review routing on PRs.
- `.github/workflows/ci.yml` — hardened starter CI tailored to `--project-type` (then customize with `github-actions-cicd`).
- `CONTRIBUTING.md` & `SECURITY.md` — contributor workflow and private vulnerability disclosure policy.

## 2. Repository Hygiene, Branch Protection & `gh` Workflows

Read [gh_cli_and_branch_protection.md](./references/gh_cli_and_branch_protection.md) for copy-paste `gh` CLI commands covering:
1. **Repo Initialization**: `gh repo create`, setting topics/homepage, enabling **Squash merge** & **Automatically delete head branches** after merge.
2. **Main Branch Protection**: Requiring PR reviews, passing CI status checks, blocking force pushes and direct pushes to `main`.
3. **Pull Request Lifecycle**: Creating linked PRs (`Closes #123`), watching CI (`gh pr checks --watch`), reviewing diffs, and squash-merging cleanly.
4. **Semantic Releases**: Tagging `vX.Y.Z` and generating release notes via `gh release create v1.0.0 --generate-notes`.
5. **Secrets & Variables**: Managing Actions secrets with `gh secret set` (never committing secrets or printing values to logs).

## Validation

After scaffolding or modifying `.github/` files:
1. Re-run `init_github_repo.py audit --repo .` and verify `[OK]` across governance & CI items.
2. Run `skills/github-actions-cicd/scripts/lint_workflows.py --repo .` to validate workflow YAML and security hardening.
3. Run `skills/git-and-code-review/scripts/pre_commit_hygiene.py --repo .` before committing and pushing.
