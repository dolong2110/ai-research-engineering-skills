# LLM Post-Training, RAG & NLP Evaluation Reference

## 1. Subfield Metrics & Baselines Matrix

| NLP / LLM Task | Required Metrics | Essential Baselines |
| :--- | :--- | :--- |
| **Code / Math / Verifiable Reasoning** | Unbiased `pass@1`, `pass@k`, `Maj@k` vs. total inference tokens | Single-pass CoT, Self-Consistency (`Maj@k`) at matched token budget |
| **Retrieval-Augmented Generation (RAG)** | Retrieval `Recall@k`, `nDCG@k` + Generation Exact Match / F1 + **Citation Precision & Faithfulness (NLI)** | Dense retriever (BGE/E5) + Hybrid BM25+RRF + Reranker + Long-context no-RAG baseline |
| **Preference Alignment / Open-Ended Chat** | Position-swapped Win Rate, **Length-Controlled Win Rate**, safety/refusal false-positive rate | SFT-only, standard DPO, Best-of-$N$ at matched KL / compute |
| **Information Extraction / Sequence Labeling** | Entity-level strict span Precision, Recall, **Micro & Macro F1** | Fine-tuned DeBERTa-v3 / ModernBERT (encoder baselines often beat 100× larger LLMs at 1% latency!) |
| **Compression / KV-Cache / Speculative Decoding** | Perplexity, LongBench / Needle-in-a-Haystack accuracy, **Tokens/sec**, TTFT (ms), Peak VRAM (GB) | FP16/BF16 dense baseline, standard INT4/AWQ or H2O/StreamingLLM |

## 2. ARR / ACL / EMNLP Specific Publication Requirements

- **Mandatory `Limitations` Section**: Placed right after Conclusion (does not count toward the 8-page main limit in ARR, **but missing it causes desk rejection!**).
- **Language Specificity (Bender Rule)**: Explicitly name the language(s) studied (e.g., *"We evaluate on English financial filings..."*) rather than assuming English = language-universal.
- **Artifact & Annotator Reporting**: Document dataset licenses, PII scrubbing, prompt templates used for synthetic data or judging (in Appendix), and human annotator instructions + hourly compensation when collecting human labels.
