---
name: testing-and-verification
description: >-
  Design and run fast, deterministic unit tests, LLM/API mock tests, ML model
  sanity checks (single-batch overfit, gradient flow, tensor shape & equivariance
  invariants), and regression tests. Use this skill whenever adding features,
  modifying pipelines, fixing bugs, or verifying ML training code before launching
  expensive runs.
---

# Testing & Verification (Software, Agents & ML)

Never declare code "done" or launch multi-hour GPU / API jobs without fast, deterministic verification.

## 1. Three-Tier Verification Strategy

### Tier 1: Pure Logic & Parser Unit Tests (<2 seconds, Offline)
- Test JSON/LaTeX/BibTeX parsers, data transforms, metric calculators, and prompt builders with edge-case fixtures (malformed JSON fences, trailing commas, Unicode/LaTeX escapes, empty lists, NaNs).
- **Never hit live paid LLM or external HTTP APIs in unit tests**: inject mock responses via `unittest.mock.patch` or dependency injection so tests run deterministically inside offline sandboxes.

### Tier 2: Pre-Flight ML Sanity Suite (<30 seconds, Before Any Full Run)
Before launching a full training or evaluation job, verify four invariants on synthetic tiny tensors (`B=2, T=4, H=16, W=16`):
1. **Shape & Dtype Check**: Forward pass produces expected output shapes without silent broadcasting (`[B, 1]` + `[B]` -> `[B, B]` bug!).
2. **Non-Zero Gradient Flow**: Run `loss.backward()` once and assert `p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum() > 0` for every trainable parameter (`p.requires_grad`), while frozen backbone parameters have `p.grad is None`.
3. **Batch Independence Check**: Zero out input index `0` vs. modify input index `1` (with BatchNorm in eval or LayerNorm) and verify sample `0`'s logits do not change—catches accidental cross-batch mixing (`view` vs `transpose` bug)!
4. **Single-Batch Overfit Test**: Train for 30–50 steps on 2 fixed examples with augmentation off; loss must approach `0` (proves loss sign, optimizer wiring, and label alignment are valid).

### Tier 3: End-to-End Dry-Run / 1-Step Integration Test
- Run the full CLI entrypoint for `max_steps=1` / `n_samples=2` writing into a `tempfile.TemporaryDirectory()`, verifying checkpoint save/load, metric serialization, and cleanup.

## 2. Running Tests Cleanly

```bash
# Run pytest quietly with short tracebacks and fail-fast
python3 -m pytest -q --tb=short -x

# Syntax-check all modified Python files when pytest is not configured
python3 -m compileall -q methods utils autoraters
```

## 3. Bug-Fix Rule

Whenever fixing a bug, **write a failing reproduction test first** (or alongside the fix) that fails without the patch and passes with it.
