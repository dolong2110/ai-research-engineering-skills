---
name: python-ml-engineering
description: >-
  Write clean, reproducible, high-performance Python and ML/AI research code
  (PyTorch, JAX, NumPy, LLM pipelines). Enforces type annotations, typed configs,
  explicit tensor shape contracts, deterministic seeding, data-leakage prevention,
  and numerical stability. Use this skill when implementing, refactoring, or
  optimizing Python or machine learning code.
---

# Python & ML Research Engineering

Use this skill when writing or refactoring Python modules, model architectures, data pipelines, or multi-agent LLM back-ends so research prototypes remain clean, reproducible, and bug-free.

## 1. Code Structure & Configuration Discipline

1. **Typed Configs Over Flag Sprawl**: Group hyperparameters, paths, and model names in `pydantic.BaseModel` or `@dataclass(frozen=True)` schemas rather than passing 15 loose positional arguments across functions.
2. **Type Hints & Docstrings on Boundaries**: Annotate public function signatures (`def forward(...) -> Tensor:`) and return schemas. Keep modules cohesive and single-purpose.
3. **Explicit Tensor Shape Contracts**: Annotate non-trivial tensor transformations inline with symbolic shapes:
   ```python
   # video_feats: [B, T, N_patches, D] -> pooled: [B, T, D]
   pooled = video_feats.mean(dim=2)
   ```
4. **No Hardcoded Machine Paths or Secrets**: Resolve paths via `pathlib.Path` relative to config/repo roots; read credentials strictly via environment variables.

## 2. ML Correctness & Reproducibility Guardrails

- **Deterministic Seeding**: Seed `random`, `numpy.random`, and framework RNGs (`torch.manual_seed`, `torch.cuda.manual_seed_all`, dataloader `worker_init_fn` + `torch.Generator`) from an explicit `seed: int` recorded in run metadata.
- **Train / Eval Mode Hygiene**: Always pair `model.eval()` with `with torch.inference_mode():` (or `torch.no_grad()`), and restore `model.train()` immediately after validation loops.
- **Zero Split Leakage**: Fit normalizers, tokenizers, vocabulary statistics, and threshold selectors **exclusively on the training split**—never on combined `train + val + test` data.
- **Numerical Stability**: Prefer log-space ops (`F.cross_entropy` on raw logits, `torch.logsumexp`) over manual `torch.log(torch.softmax(x) + 1e-8)`. Guard divisions with explicit `eps`.
- **LLM / API Wrapper Resilience**: Use bounded retries with exponential backoff + jitter on transient 429/5xx errors, fail fast on 400/auth/context-length errors, and validate structured outputs with Pydantic schemas.

## 3. Static ML & Python Code Audit

Run [ml_code_check.py](./scripts/ml_code_check.py) on modified Python files or directories to catch silent ML/Python footguns (mutable default args, bare `except:`, `.eval()` without `no_grad`/`inference_mode`, hardcoded `/Users/` paths, and leftover debug prints/breakpoints):

```bash
python3 skills/python-ml-engineering/scripts/ml_code_check.py --path methods utils
```
