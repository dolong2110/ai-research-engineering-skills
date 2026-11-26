---
name: model-serving-and-inference-optimization
description: >-
  Optimize and benchmark ML/DL/LLM inference serving (vLLM, SGLang, TensorRT,
  ONNX Runtime), KV-cache memory sizing, quantization (FP8, AWQ, GPTQ, INT4),
  speculative decoding, continuous batching, and latency/throughput SLA testing
  (TTFT, TPOT, p50/p95/p99, tokens/sec). Use this skill when speeding up model
  inference, cutting serving cost, or load-testing model endpoints.
---

# Model Serving & Inference Optimization

Use this skill when deploying ML/LLM models for low-latency or high-throughput serving, sizing KV-cache capacity, benchmarking quantization trade-offs, or debugging tail-latency spikes.

## 1. Measure the Right Serving Metrics (Not Averages!)

Always measure under realistic concurrency (`C = 1, 4, 16, 64`), reporting **tail latencies** and **throughput** together:
- **LLMs (Streaming)**:
  - **TTFT** (*Time To First Token*, prefill bound) — `p50`, `p95`, `p99`
  - **TPOT / ITL** (*Time Per Output Token / Inter-Token Latency*, memory-bandwidth bound) — `p50`, `p95`, `p99`
  - **End-to-End Latency** & **System Output Throughput** (`output tokens / sec` across concurrent requests)
- **Non-LLM ML (Vision / GNN / Quant Models)**: `p50` / `p95` / `p99` latency (`ms`), QPS at SLA, batch size, and peak GPU/CPU memory.

Run [benchmark_inference_latency.py](./scripts/benchmark_inference_latency.py) on recorded JSONL request logs (or its built-in self-test) to compute exact `TTFT`, `TPOT`, `p50/p95/p99`, throughput, and SLA pass/fail:

```bash
python3 skills/model-serving-and-inference-optimization/scripts/benchmark_inference_latency.py \
  --input runs/serving_traces.jsonl \
  --sla-ttft-p99-ms 500 \
  --sla-tpot-p99-ms 50
```

## 2. Inference Acceleration Levers (Highest ROI First)

1. **Engine & Batching**: Use **vLLM / SGLang** (PagedAttention + continuous batching + prefix/radix caching for shared system prompts!) instead of naive HuggingFace `model.generate()` loops. For vision/tabular/GNNs, use `torch.inference_mode()` + `torch.compile(mode="reduce-overhead")` or **ONNX Runtime / TensorRT**.
2. **Quantization with Accuracy Verification**:
   - Start with **FP8** (Hopper/Blackwell) or **W4A16 (AWQ / GPTQ)**—reduces memory-bandwidth bottleneck ~2×–3.5× during decode!
   - Always verify task quality on a golden eval slice (`prompt-and-agent-eval-engineering`)—quantization often preserves perplexity while silently breaking structured JSON formatting or math/code accuracy!
3. **KV-Cache Sizing**:
   - Per-token KV cache bytes = $2 \times L \times n_{\text{kv\_heads}} \times d_{\text{head}} \times \text{bytes}$ (GQA shrinks this dramatically; FP8 KV-cache doubles concurrent context capacity).
4. **Prefix Caching & Speculative Decoding**:
   - Keep stable instructions/few-shot examples at the **exact prefix** of every prompt so RadixAttention / automatic prefix caching hits >90% and cuts TTFT dramatically.
   - Use speculative decoding (draft model or Eagle/Medusa) when batch sizes are low (`C <= 8`) and latency matters most.
