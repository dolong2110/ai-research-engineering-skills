#!/usr/bin/env python3
"""Roofline arithmetic intensity, memory-vs-compute bottleneck diagnosis, and utilization calculator."""

import argparse
import sys

HARDWARE_PRESETS = {
    # (peak_bf16_tflops, mem_bandwidth_tb_s)
    "H100-SXM": (989.0, 3.35),
    "H200-SXM": (989.0, 4.80),
    "A100-80GB": (312.0, 2.04),
    "L40S": (362.0, 0.864),
    "RTX-4090": (330.0, 1.008),
    "M3-Max": (28.0, 0.400),
}


def analyze(hw_name: str, peak_tflops: float, bw_tbs: float, flops: float, total_bytes: float, measured_ms: float | None) -> int:
    ai = flops / max(1.0, total_bytes)
    ridge = peak_tflops / bw_tbs  # FLOPs / Byte
    bottleneck = "MEMORY-BANDWIDTH BOUND (fuse ops / cut HBM trips)" if ai < ridge else "COMPUTE BOUND (maximize Tensor Core tiling)"

    # Theoretical minimum time (seconds)
    t_mem_s = total_bytes / (bw_tbs * 1e12)
    t_comp_s = flops / (peak_tflops * 1e12)
    t_ideal_ms = max(t_mem_s, t_comp_s) * 1000.0
    achievable_tflops = min(peak_tflops, ai * bw_tbs)

    print(f"=== Roofline Kernel Analysis ({hw_name}) ===")
    print(f"  Hardware Specs       : Peak={peak_tflops:.1f} TFLOP/s, HBM/RAM BW={bw_tbs:.3f} TB/s, Ridge Point={ridge:.1f} FLOPs/Byte")
    print(f"  Kernel Workload      : {flops:.3e} FLOPs, {total_bytes / 1e6:.2f} MB moved -> AI = {ai:.2f} FLOPs/Byte")
    print(f"  Regime Diagnosis     : {bottleneck}")
    print(f"  Roofline Ceiling     : {achievable_tflops:.2f} TFLOP/s | Ideal Min Time = {t_ideal_ms:.4f} ms")
    if measured_ms is not None and measured_ms > 0:
        achieved_tflops = (flops / (measured_ms / 1000.0)) / 1e12
        achieved_bw = (total_bytes / (measured_ms / 1000.0)) / 1e12
        util = min(100.0, (t_ideal_ms / measured_ms) * 100.0)
        print(f"  Measured Performance : {measured_ms:.4f} ms ({achieved_tflops:.2f} TFLOP/s, {achieved_bw:.3f} TB/s) -> {util:.1f}% of Roofline ceiling")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Roofline arithmetic intensity & GPU kernel efficiency analyzer.")
    parser.add_argument("--hardware", choices=sorted(HARDWARE_PRESETS.keys()), default="H100-SXM")
    parser.add_argument("--peak-tflops", type=float, default=None, help="Override peak TFLOP/s.")
    parser.add_argument("--bw-tbs", type=float, default=None, help="Override memory bandwidth in TB/s.")
    parser.add_argument("--flops", type=float, help="Total FLOPs executed by kernel.")
    parser.add_argument("--bytes", type=float, help="Total global memory bytes read + written.")
    parser.add_argument("--measured-ms", type=float, default=None, help="Optional measured kernel runtime in ms.")
    parser.add_argument("--self-test", action="store_true", help="Run GEMM vs. Softmax roofline demo on H100.")
    args = parser.parse_args()

    if args.self_test:
        # 1. BF16 Matmul 4096x4096x4096: 2*N^3 FLOPs, 3*N^2*2 bytes
        n = 4096
        analyze("H100-SXM (GEMM 4096^3)", *HARDWARE_PRESETS["H100-SXM"], 2.0 * n ** 3, 3.0 * n * n * 2.0, 0.20)
        # 2. BF16 Softmax 4096x4096: ~5*N^2 FLOPs, 2*N^2*2 bytes
        analyze("H100-SXM (Softmax 4096^2)", *HARDWARE_PRESETS["H100-SXM"], 5.0 * n * n, 2.0 * n * n * 2.0, 0.035)
        return 0

    if args.flops is None or args.bytes is None:
        parser.error("Provide --flops and --bytes (or run --self-test).")

    preset_tf, preset_bw = HARDWARE_PRESETS[args.hardware]
    return analyze(
        args.hardware,
        args.peak_tflops or preset_tf,
        args.bw_tbs or preset_bw,
        args.flops,
        args.bytes,
        args.measured_ms,
    )


if __name__ == "__main__":
    sys.exit(main())
