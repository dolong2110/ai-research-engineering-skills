---
name: systematic-debugging
description: >-
  Diagnose and resolve software bugs, multi-threaded/multiprocess hangs, LLM JSON/LaTeX
  parsing failures, and ML training pathologies (NaNs, loss spikes, zero metric lift)
  using a disciplined Reproduce -> Isolate -> Hypothesize -> Verify workflow. Use this
  skill whenever encountering errors, unexpected outputs, flaky behavior, or degraded
  model performance.
---

# Systematic Root-Cause Debugging

**Iron Law:** Never stack speculative patches on top of unverified guesses. Find the root cause before changing production logic; if a hypothesis fails, revert the probe cleanly before testing the next one.

## 1. The 4-Step Debugging Loop

1. **Reproduce Minimally & Deterministically**:
   - Capture the exact command, stack trace, input file, random seed, and environment (`which python`, package versions).
   - Shrink the failing case: if Stage 4 of a 30-minute pipeline fails, isolate Stage 4 on saved intermediate files rather than rerunning Stages 1–3 (`paper-orchestra-run/references/pipeline_artifacts.md`).
2. **Trace Data Across Module Boundaries**:
   - Inspect actual inputs and outputs at the boundary right before the failure (types, shapes, keys, raw LLM string before regex/JSON parsing, subprocess `returncode` + `stderr`).
3. **Form One Falsifiable Hypothesis at a Time**:
   - State: *"I hypothesize X fails because Y; logging Z will show W."* Verify before editing logic.
4. **Fix at the Source & Add a Guardrail**:
   - Fix the root producer of bad state rather than masking `None`/`KeyError` downstream with silent `try/except: pass`. Add an assertion or regression test (`testing-and-verification`).

## 2. Domain-Specific Triage Playbooks

### A. Multi-Agent / LLM Pipeline Failures
- **Malformed JSON / LaTeX extraction**: Log the raw model response length and finish reason (`MAX_TOKENS` truncation often drops closing ```` ``` ```` fences!). Prefer schema-constrained generation (`response_schema` / `response_mime_type="application/json"`) or `json_repair` fallback.
- **ThreadPool / ProcessPool hangs or rate limits**: Lower `max_workers` to `1` temporarily to surface swallowed exceptions, deadlocks, or 429 bursts clearly.

### B. ML Training & Evaluation Pathologies
- **`NaN` / `Inf` Loss**: Enable anomaly detection (`torch.autograd.detect_anomaly(True)`) for 1 batch; check division by zero in IoU/cosine losses when masks are empty (e.g., Null-subset empty ground-truth masks!), `fp16` overflow (prefer `bf16`), or excessive learning rate.
- **Model Stuck at Chance / Zero Gain Over Baseline**:
  1. Verify labels and predictions use the same index/coordinate convention (`[x, y]` vs `[row, col]`, `0..1` vs `0..255`).
  2. Check `optimizer.param_groups` actually contains the new module's parameters!
  3. Run the 2-sample Single-Batch Overfit check (`testing-and-verification`).
