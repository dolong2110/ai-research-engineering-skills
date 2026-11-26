---
name: systems-cpp-rust-triton-kernels
description: >-
  Engineer high-performance, low-latency C++20/Rust systems (cache-friendly data
  structures, SIMD, lock-free queues, PyBind11/PyO3 bindings, sanitizers) and
  custom GPU kernels in Triton/CUDA (roofline arithmetic intensity, coalesced
  memory loads, shared-memory tiling, warp efficiency). Use this skill when
  optimizing critical hot loops beyond Python, building LOB/matching engines,
  or authoring custom ML GPU kernels.
---

# High-Performance C++, Rust & Triton/CUDA GPU Kernels

Move hot loops out of Python only **after** profiling confirms Python/framework overhead (`performance-and-concurrency`). When crossing into C++, Rust, or custom GPU kernels, optimize for the **memory hierarchy first**—DRAM/HBM bandwidth dominates modern compute!

## 1. Roofline Analysis First (Before Writing Any Kernel)

Compute your kernel's **Arithmetic Intensity** $I = \text{FLOPs} / \text{Bytes Moved}$ and compare against the hardware **Ridge Point** $R = \text{Peak TFLOP/s} / \text{Memory TB/s}$ using [roofline_analyzer.py](./scripts/roofline_analyzer.py):

```bash
python3 skills/systems-cpp-rust-triton-kernels/scripts/roofline_analyzer.py \
  --hardware H100-SXM --flops 1e12 --bytes 2e9 --measured-ms 0.85
```

- **$I < R$ (Memory-Bandwidth Bound — LayerNorm, Softmax, RoPE, Decode Attention, Vector Ops)**:
  - **Fuse** consecutive elementwise + reduction passes into a single SRAM/register kernel (cutting HBM round-trips from 4× to 1× gives a direct 3×–4× speedup!).
- **$I \ge R$ (Compute Bound — Large GEMM, Prefill Attention)**:
  - Maximize Tensor Core occupancy via power-of-2 block tiles (`BLOCK_M, BLOCK_N, BLOCK_K`), pipelined async copies (`num_stages`), and autotuning `num_warps`.

## 2. Low-Latency C++20 / Rust Engineering Checklist

- **Data-Oriented Memory Layout**: Prefer **Structure of Arrays (SoA)** and contiguous flat vectors (`std::vector` / `Vec`) over pointer-chasing linked lists or `std::map` on hot paths; pad contended atomics to 64-byte cache lines (`alignas(64)`) to eliminate false sharing.
- **Zero-Allocation Hot Paths**: Pre-allocate arena/slab pools and SPSC lock-free ring buffers at startup—never call `malloc`/`new` inside per-tick LOB or matching loops!
- **Mandatory Safety & Verification**: Always compile & run C++ tests under `-fsanitize=address,undefined` (`ASan` + `UBSan`) and `-fsanitize=thread` (`TSan`), and verify zero regressions with `algorithms-and-data-structures/scripts/benchmark_and_complexity.py` against a clean Python reference oracle!
- **Python Bridges**: Expose vectorized bulk batch APIs via **nanobind / PyBind11** (C++) or **PyO3 + maturin** (Rust), releasing the GIL (`py::gil_scoped_release` / `py.allow_threads`) around heavy compute.

## 3. Triton / CUDA Kernel Verification Protocol

1. Test numerical correctness against a `float64` PyTorch eager reference across **non-power-of-2 shapes** (e.g., `N=13, 127, 1025` to catch masking/boundary bugs!).
2. Benchmark with CUDA events (`triton.testing.do_bench`) after warmup—never time asynchronous GPU kernels with `time.perf_counter()` without `torch.cuda.synchronize()`!
