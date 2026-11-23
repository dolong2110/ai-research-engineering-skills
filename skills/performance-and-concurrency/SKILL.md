---
name: performance-and-concurrency
description: >-
  Profile CPU/memory hotspots, eliminate I/O and lock-contention bottlenecks, and
  write safe concurrent/parallel code (`asyncio`, `ThreadPoolExecutor`,
  `ProcessPoolExecutor`, vectorization, batching, and backpressure). Use this skill
  when speeding up slow scripts or services, debugging high latency or OOMs, or
  designing thread/process-safe pipelines.
---

# Performance Optimization & Safe Concurrency

## 1. Measure First (Amdahl's Law)

Never guess where time or memory goes. Before refactoring for speed, run [profile_hotspot.py](./scripts/profile_hotspot.py) on a representative workload to pinpoint the top cumulative and self-time functions plus peak heap allocations:

```bash
python3 skills/performance-and-concurrency/scripts/profile_hotspot.py \
  --script paper_writing_cli.py -- --help
```

## 2. Choosing the Right Execution Model in Python

| Bottleneck Type | Symptoms | Right Tool | Wrong Tool |
| :--- | :--- | :--- | :--- |
| **Network / Disk / LLM API I/O** | High wall-clock time, low CPU (<10%), threads waiting on sockets | `asyncio` + `Semaphore(N)` or `ThreadPoolExecutor(max_workers=N)` | `ProcessPoolExecutor` (unnecessary IPC/pickle overhead) |
| **Pure-Python CPU Loops** | 1 core pinned at 100%, GIL contention across threads | Vectorize in **NumPy / PyTorch / Cython** first; else `ProcessPoolExecutor` on coarse chunks | `ThreadPoolExecutor` (serialized by GIL in standard CPython) |
| **Subprocess Fan-Out (`pdflatex`, `ffmpeg`)** | Spawning external OS binaries | `ThreadPoolExecutor` / `asyncio.create_subprocess_exec` capped to CPU core count | Unbounded parallel `Popen` (OOMs host!) |
| **Memory Bandwidth / GC Churn** | Multi-GB RSS spikes, high `gc` pause time | Streaming generators (`yield`), chunked I/O, `mmap`, pre-allocated typed buffers | Materializing `[load(x) for x in million_items]` in RAM |

## 3. Concurrency Safety Checklist

1. **Shared State Synchronization**: Protect every shared mutable dict/list/counter accessed across threads with a `threading.Lock` (keep critical sections tiny—never perform network or file I/O inside the lock!).
2. **Atomic File Writes**: When workers write checkpoint JSONs (`paper_writing_log.json`, `outline.json`), write to `<path>.tmp.<pid>` and `os.replace()` atomically so crashes or readers never see half-written files.
3. **Bounded Concurrency & Backpressure**: Always bound in-flight tasks (`asyncio.Semaphore(k)` or bounded `Queue(maxsize=k)`) rather than submitting 100,000 coroutines/futures at once.
4. **Clean Cancellation & Timeouts**: Propagate timeouts to child tasks/subprocesses and clean up temp files/child PIDs in `try ... finally` blocks.
