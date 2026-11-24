# GitHub CLI (`gh`) & Repository Governance Reference

## 1. Repository Creation & Settings Hygiene

```bash
# Check auth identity & scopes
gh auth status

# Create public or private repo from an existing local git repository
gh repo create <repo-name> --public --source=. --remote=origin --push \
  --description "Concise one-line project summary"

# Configure merge hygiene (squash merges + auto-delete merged PR branches + topics)
gh repo edit <owner>/<repo> \
  --enable-squash-merge \
  --delete-branch-on-merge \
  --add-topic ai,research,python
```

## 2. Branch Protection on `main`

Protect `main` so accidental direct pushes or broken merges cannot land (adapt required status check names to match your CI job names in `.github/workflows/ci.yml`):

```bash
gh api --method PUT "repos/<owner>/<repo>/branches/main/protection" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

*(For solo repos, set `"required_pull_request_reviews": null` while keeping `required_status_checks` + `allow_force_pushes: false` so CI must pass before merging PRs without blocking solo merges.)*

## 3. Daily PR, Issue & Release Workflows

```bash
# Create a feature branch, commit, and open a PR with template body
git switch -c feat/my-change
gh pr create --fill --base main

# Monitor CI checks until completion & inspect failed logs if any
gh pr checks --watch
gh run view <run-id> --log-failed

# Merge cleanly with squash + delete remote/local branch
gh pr merge --squash --delete-branch

# Create a semantic GitHub Release with auto-generated changelog
gh release create v1.0.0 --title "v1.0.0" --generate-notes
```

## 4. Secrets & Environment Variables (Never Commit `.env`!)

```bash
# Set an encrypted Actions secret from stdin (avoids shell history exposure)
gh secret set GEMINI_API_KEY < /path/to/keyfile

# Set non-secret Actions config variables
gh variable set PYTHON_VERSION --body "3.11"
```
