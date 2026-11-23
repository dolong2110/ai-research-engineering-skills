---
name: git-and-code-review
description: >-
  Maintain clean Git history, run pre-commit secret/binary/syntax checks, structure
  atomic Conventional Commits, and perform thorough correctness and security code
  reviews. Use this skill before committing, opening pull requests, reviewing diffs,
  or preparing research code for public open-source release.
---

# Git Hygiene & Rigorous Code Review

## 1. Pre-Commit Safety Gate

Always run [pre_commit_hygiene.py](./scripts/pre_commit_hygiene.py) before creating commits or sharing a branch—especially in research repositories where `.env` API keys, large `.pdf`/`.ckpt`/`.pt` artifacts, or merge markers are easy to stage by mistake:

```bash
python3 skills/git-and-code-review/scripts/pre_commit_hygiene.py
```

## 2. Atomic Commits & Conventional Messages

- Keep each commit focused on **one logical change** (separate refactoring from bug fixes, and separate code changes from generated outputs).
- Format commit messages clearly:
  ```text
  <type>(<scope>): <imperative summary under 72 chars>

  - Why this change was needed (root cause or motivation)
  - Key technical design choice and how it was verified
  ```
  Common `<type>` values: `feat`, `fix`, `refactor`, `test`, `docs`, `perf`, `chore`.

## 3. High-Signal Code Review Checklist

When asked to review local changes (`git diff`) or a pull request, prioritize **real bugs and risks** over style nitpicks:

1. **Correctness & Edge Cases**: Empty inputs, off-by-one indexing, silent exception swallowing, race conditions on shared state/files across threads (`Lock` coverage).
2. **Research / ML Integrity**: Any subtle train-test leakage, silent metric filtering, mismatched baseline preprocessing, or broken reproducibility?
3. **Security & Secrets**: Hardcoded tokens, unsafe shell interpolation (`shell=True` with untrusted strings), path traversal, or unstripped author metadata.
4. **Resource & Cost Safety**: Unbounded retry loops, missing HTTP/subprocess timeouts, loading multi-GB files repeatedly inside tight loops.

Report findings ordered by severity (`[CRITICAL]`, `[HIGH]`, `[MEDIUM]`, `[LOW]`) with clickable `file://` line links and a concrete fix snippet.
