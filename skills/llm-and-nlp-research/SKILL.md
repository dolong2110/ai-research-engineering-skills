---
name: llm-and-nlp-research
description: >-
  Design, train, align, and evaluate Large Language Models (LLMs), Retrieval-Augmented
  Generation (RAG), agentic pipelines, and NLP systems. Covers pretraining/SFT/DPO/GRPO,
  PEFT (LoRA/QLoRA), KV-cache & quantization efficiency, contamination checks,
  multi-prompt variance, position-debiased LLM-as-a-Judge evaluation, and unbiased
  pass@k metrics. Use this skill whenever working on LLM, RAG, reasoning, alignment,
  or NLP research.
---

# LLM & NLP Research Methodology

Use this skill to enforce modern ACL / EMNLP / NAACL / ICLR / NeurIPS rigor across LLM adaptation, prompting/RAG/agent architectures, and contamination-resistant evaluation.

## 1. Training, Alignment & Efficiency Ablations

Read [llm_eval_and_posttraining.md](./references/llm_eval_and_posttraining.md) when designing post-training, RAG, or inference experiments:

- **Fair Data & Token Accounting**: Report exact training tokens, effective batch size, sequence packing, chat template format, and whether synthetic teacher distillation comes from a stronger proprietary model.
- **Post-Training Controls**:
  - When proposing a preference/RL objective (DPO, SimPO, GRPO / RLVR), compare against **SFT on preferred completions** and **Best-of-$N$ rejection sampling** under matched generation compute!
  - For **PEFT (LoRA / DoRA / QLoRA)**, report trainable parameter %, rank $r$, $\alpha$, target modules (`q_proj..down_proj`), peak training VRAM, and full-finetuning gap.
- **Test-Time Compute & Agentic Parity**:
  - Never compare a 10-call multi-agent / self-consistency / tree-search pipeline against a single greedy `temperature=0` baseline! Always include **pass@$k$ / Majority@$k$ (Self-Consistency)** at **matched total generated tokens or API cost**.

## 2. Rigorous NLP & LLM Evaluation Protocol

1. **Prompt Variance Reporting**: Evaluate across **$\ge 3$ semantically equivalent prompt templates** (or few-shot orderings) and report `mean ± std`—single-prompt deltas of `<1.5%` are frequently prompt noise.
2. **Benchmark Contamination Audit**: Check n-gram overlap against pretraining/SFT mixtures, include a post-cutoff dynamic benchmark (e.g., LiveCodeBench / fresh arXiv / fresh filings), or evaluate counterfactual perturbations where memorized shortcuts fail.
3. **LLM-as-a-Judge Bias Mitigation**:
   - Always evaluate **both `(Response A, Response B)` and `(Response B, Response A)`**! Count a win only when consistent across both orderings (or average swapped probabilities), and report **response length (token count)** alongside win rates to rule out verbosity bias.
   - Calibrate automated judges against a 50–100 item human-annotated subset using Cohen's $\kappa$.

## 3. Unbiased `pass@k`, Position-Debiased Judge & Cohen's $\kappa$ CLI

Run [nlp_llm_eval_metrics.py](./scripts/nlp_llm_eval_metrics.py) to compute Chen et al. unbiased `pass@k` from multi-sample evaluations or audit swapped pairwise LLM-judge logs for position & verbosity bias:

```bash
# Compute unbiased pass@1, pass@5, pass@10 from JSONL {"id": ..., "n": 16, "c": 5}
python3 skills/llm-and-nlp-research/scripts/nlp_llm_eval_metrics.py pass-at-k \
  --input runs/codegen_samples.jsonl --ks 1,5,10

# Audit swapped pairwise LLM-judge results & Cohen's kappa
python3 skills/llm-and-nlp-research/scripts/nlp_llm_eval_metrics.py pairwise-judge \
  --input runs/judge_swapped.jsonl
```
