---
name: containers-docker-and-packaging
description: >-
  Author clean, minimal, secure, reproducible Dockerfiles (including PyTorch/CUDA,
  RDKit, and TeX Live research containers), `.dockerignore`, `docker-compose.yml`,
  devcontainers, and modern `pyproject.toml` + `uv` Python packages. Use this skill
  whenever containerizing ML/software projects, shrinking slow Docker builds,
  hardening containers, or packaging Python libraries.
---

# Containers, Docker & Reproducible Packaging

## 1. Reproducible & Secure `Dockerfile` Rules

1. **Pin Exact Base Image Tags**: Never use `FROM python:latest` or `FROM nvidia/cuda:latest`—pin explicit versions (e.g., `python:3.11.10-slim`, `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime`).
2. **Optimize Layer Caching**: Copy only lockfiles (`pyproject.toml`, `uv.lock`, `requirements.txt`, `package-lock.json`) and install dependencies *before* `COPY . .` so source edits reuse cached dependency layers!
3. **Keep Images Lean**:
   - Use multi-stage builds (`FROM ... AS builder` -> copy wheel/venv/binary into `slim` runtime image).
   - Pair `apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*` in a single `RUN` layer, and pass `--no-cache-dir` to `pip` (or `--mount=type=cache`).
   - Always ship a `.dockerignore` excluding `.git`, `.env`, `*.pt`, `*.ckpt`, `datasets/`, `__pycache__/`, and `node_modules/`.
4. **Hardening & Secrets**:
   - Create and switch to a **non-root `USER`** before `ENTRYPOINT`/`CMD`.
   - Never bake API keys into `ENV` or `ARG` (they persist permanently in `docker history`!)—inject secrets at runtime via `--env-file` or BuildKit `--mount=type=secret`.
   - Use JSON exec form (`CMD ["python", "-m", "app"]`) rather than shell form so `SIGTERM` reaches PID 1 cleanly.

## 2. Modern Python Packaging (`pyproject.toml` + `uv`)

- Use PEP 621 `pyproject.toml` (`[project]`, `[project.optional-dependencies]`, `[project.scripts]`) with `src/` layout so tests always import the installed package rather than accidental CWD shadowing.
- Lock exact transitive dependencies (`uv lock` -> `uv sync --frozen`) for reproducible research artifacts and CI builds.

## 3. Automated Dockerfile Linter

Always audit `Dockerfile`s before building or committing with [lint_dockerfile.py](./scripts/lint_dockerfile.py):

```bash
python3 skills/containers-docker-and-packaging/scripts/lint_dockerfile.py --file Dockerfile
```
