---
name: interactive-ml-demos-and-apps
description: >-
  Build fast, responsive interactive ML/AI research demos, model playgrounds, and
  data dashboards using Streamlit, Gradio, or FastAPI + clean HTML/JS. Covers model
  resource caching, streaming LLM tokens, non-blocking background jobs, scientific
  chart/molecule UI integration, Chrome DevTools inspection, and deployment to
  HuggingFace Spaces or Cloud Run. Use this skill when creating interactive demos
  for models, finance backtests, chemistry tools, or PaperOrchestra pipelines.
---

# Interactive ML Demos & Research Apps

Use this skill to turn research models, financial backtesters, molecule explorers, or multi-agent pipelines into crisp, reliable demos that reviewers and collaborators can actually run without crashing.

## 1. Framework Selection

- **Gradio**: Fastest choice for single-model I/O playgrounds (text/image/audio/SMILES in -> prediction/visualization out) and zero-friction **HuggingFace Spaces** hosting.
- **Streamlit**: Best for multi-panel analytical dashboards (financial equity/drawdown curves, ablation filters, experiment log explorers, PaperOrchestra run monitors).
- **FastAPI + Static HTML/JS (SSE Streaming)**: Best when you need custom interactive UX, WebSockets/SSE token streaming, strict API schemas, or production multi-user concurrency.

## 2. Mandatory Performance & UX Invariants

1. **Never Reload Models on Every Rerun**:
   - In Streamlit, wrap heavyweight checkpoints, tokenizers, or DB pools in `@st.cache_resource` and pure data transforms in `@st.cache_data(ttl=...)`.
   - In FastAPI, load models once inside the `lifespan` async context manager—never inside route handlers or at module import time.
2. **Never Block the UI Event Loop**:
   - Stream LLM generations incrementally (`st.write_stream`, Gradio generator `yield`, or FastAPI `StreamingResponse` SSE).
   - Offload multi-minute pipelines (like `paper_writing_cli.py`, docking, or backtests) to background subprocesses/workers with live progress polling and clean cancel/cleanup hooks.
3. **Ship 3 Curated One-Click Examples**:
   - Reviewers and demo visitors rarely invent complex inputs from scratch—pre-populate 3 representative example payloads (e.g., canonical SMILES, sample ticker/date range, or `cvpr_example.json`) so the app delivers an immediate "aha" moment on click #1.
4. **Input Validation & Cost Guardrails**:
   - Cap input lengths, max upload sizes, and max tokens/iterations on public demos; read API keys strictly from server environment variables (or optional masked password inputs never logged to disk).
5. **Visual & Performance Verification**:
   - Pair with Antigravity's `browser` subagent and the **Chrome DevTools** plugin (`chrome-devtools`, `a11y-debugging`, `debug-optimize-lcp`) to verify zero console errors, responsive layout, and clean interactive flows before sharing!
