---
name: security-and-production-ops
description: >-
  Audit code for security vulnerabilities (command/SQL injection, unsafe
  deserialization, SSRF, path traversal, TLS/crypto flaws, secret exposure) and
  enforce production engineering readiness (structured logging, health probes,
  graceful shutdown, timeouts, and reproducible CI/container builds). Use this skill
  when auditing security, hardening external inputs, or preparing services/tools for
  production deployment.
---

# Security Hardening & Production Operations

## 1. Secure-by-Default Coding Rules

1. **Zero Shell-Interpolated Commands**:
   - Always pass argument lists (`subprocess.run(["pdflatex", tex_name], shell=False, timeout=30)`)—never `shell=True` or `os.system(f"...")` on user-, file-, or LLM-derived strings!
2. **Safe Serialization Only**:
   - Never call `pickle.loads`, `torch.load(..., weights_only=False)`, `eval()`, `exec()`, or `yaml.load()` (without `SafeLoader`) on untrusted artifacts. When executing LLM-generated plotting code (like `execute_plot_code_worker`), isolate subprocess execution with strict timeouts and stripped environment variables.
3. **Parameterized Queries & Path Containment**:
   - Bind all SQL values via placeholders (`cursor.execute("SELECT ... WHERE id = %s", (uid,))`).
   - Resolve user-supplied file paths via `cand = (base_dir / rel).resolve()` and assert `cand.is_relative_to(base_dir.resolve())` to block `../../` path traversal and zip-slip attacks.
4. **Outbound Network & TLS Hygiene**:
   - Never disable certificate verification (`verify=False`). Enforce explicit `timeout=(connect_sec, read_sec)` on every `requests` / `httpx` call (an omitted timeout in `requests.get(...)` can hang forever!).
   - Block SSRF to link-local/metadata IPs (`169.254.169.254`, `127.0.0.0/8`, `10.0.0.0/8`) when fetching user-supplied URLs.

## 2. Production Readiness & Observability Checklist

- **Structured Context Logging**: Log structured key-value/JSON events (`request_id`, `paper_id`, `stage`, `duration_ms`, `model`, `attempt`) instead of bare `print()` strings in services; never log API keys, bearer tokens, or raw PII.
- **Graceful Shutdown**: Handle `SIGTERM`/`SIGINT` cleanly so background workers flush state and child processes terminate without orphan leaks.
- **Pinned Reproducible Builds**: Pin direct and transitive dependencies (`requirements.lock` / `uv.lock`), run containers as non-root users, and verify `/healthz` checks real readiness.

## 3. Automated Static Security Scan

Run [security_static_scan.py](./scripts/security_static_scan.py) across Python files before deploying or open-sourcing code:

```bash
python3 skills/security-and-production-ops/scripts/security_static_scan.py --path .
```
