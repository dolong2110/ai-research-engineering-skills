---
name: prompt-and-agent-eval-engineering
description: >-
  Build systematic evaluation harnesses, golden datasets, tool-call trajectory
  graders, failure-mode taxonomies, and automated quality/cost/latency regression
  gates for prompts, RAG pipelines, and multi-agent LLM systems. Use this skill
  before and after changing prompts, models, retrieval parameters, or agent tools.
---

# Prompt & Agent Eval Engineering

Never iterate on prompts, retrievers, or multi-agent graphs by "vibe checking" 3 examples. One prompt edit frequently fixes 2 edge cases while silently breaking 5 others.

## 1. Build a 3-Layer Evaluation Harness

1. **Deterministic Code Graders (Fastest, Free, Run First)**:
   - Schema validity (JSON/Pydantic parse), required fields, citation key existence, unit tests on generated code, tool-call argument types, latency/token budget ceilings.
2. **Trajectory & Grounding Assertions (For Agents & RAG)**:
   - Verify **tool-call precision/order** (did the agent verify citations before claiming them? did it respect read-only bounds?), **retrieval recall** (was the gold chunk retrieved in top-$k$?), and **faithfulness** (no unsupported claims outside context).
3. **Calibrated LLM-as-a-Judge (Only Where Code Can't Grade)**:
   - Use binary pass/fail rubrics per failure mode (much higher inter-rater agreement than vague 1–10 scales!), swap `(A, B)` positions for pairwise checks (`llm-and-nlp-research`), and calibrate against human labels.

## 2. Error Analysis & Failure Taxonomy Loop

1. Collect 50–100 realistic representative + adversarial cases into a versioned `evals/golden.jsonl` (tagged by `category`, e.g., `retrieval_miss`, `tool_error`, `json_format`, `edge_case`).
2. Inspect every failure and assign a mutually exclusive **root-cause tag** before editing prompts—fix the highest-frequency failure cluster first!
3. Run paired baseline vs. candidate evaluation on the exact same golden IDs and gate merges on **net pass rate + zero critical slice regressions + cost/latency bounds**.

## 3. Paired Eval Regression & McNemar Significance CLI

Run [compare_eval_runs.py](./scripts/compare_eval_runs.py) to diff `baseline.jsonl` vs. `candidate.jsonl` (`{"id": "...", "category": "...", "passed": true, "latency_ms": 820, "cost_usd": 0.002}`), flagging exact regressed IDs, slice deltas, cost/latency shifts, and McNemar's paired test:

```bash
python3 skills/prompt-and-agent-eval-engineering/scripts/compare_eval_runs.py \
  --baseline evals/run_v1.jsonl \
  --candidate evals/run_v2.jsonl
```
