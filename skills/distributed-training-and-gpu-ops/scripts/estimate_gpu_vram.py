#!/usr/bin/env python3
"""Estimate per-GPU VRAM requirements for Transformer training (DDP / ZeRO / FSDP / LoRA)."""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate per-GPU VRAM for Transformer training.")
    parser.add_argument("--params-b", type=float, required=True, help="Total model parameters in billions (e.g. 7 for 7B).")
    parser.add_argument("--trainable-frac", type=float, default=1.0, help="Fraction of trainable params (1.0=full FT, ~0.01=LoRA).")
    parser.add_argument("--precision-bytes", type=float, default=2.0, help="Weight bytes per param (2.0=bf16/fp16, 0.5=4bit QLoRA, 4.0=fp32).")
    parser.add_argument("--optimizer", choices=["adamw", "adamw8bit", "sgd"], default="adamw")
    parser.add_argument("--batch-size", type=int, default=1, help="Micro-batch size per GPU.")
    parser.add_argument("--seq-len", type=int, default=2048, help="Sequence length.")
    parser.add_argument("--hidden-size", type=int, default=4096, help="Model hidden dimension d_model.")
    parser.add_argument("--num-layers", type=int, default=32, help="Number of transformer layers.")
    parser.add_argument("--num-gpus", type=int, default=1, help="Number of GPUs in data/FSDP shard group.")
    parser.add_argument("--zero-stage", type=int, choices=[0, 1, 2, 3], default=0, help="0=DDP, 1=ZeRO-1, 2=ZeRO-2, 3=FSDP/ZeRO-3.")
    parser.add_argument("--grad-checkpointing", action="store_true", help="Enable activation checkpointing.")
    args = parser.parse_args()

    total_params = args.params_b * 1e9
    trainable_params = total_params * max(0.0, min(1.0, args.trainable_frac))
    gpus = max(1, args.num_gpus)
    gib = 1024 ** 3

    # Weights
    weight_bytes = total_params * args.precision_bytes
    if args.zero_stage == 3:
        weight_bytes /= gpus

    # Gradients (bf16/fp32 -> 2 bytes typical in mixed precision or 4 bytes in fp32)
    grad_bytes = trainable_params * (4.0 if args.precision_bytes >= 4.0 else 2.0)
    if args.zero_stage >= 2:
        grad_bytes /= gpus

    # Optimizer states (AdamW mixed precision: fp32 master copy 4B + m 4B + v 4B = 12B/trainable param)
    if args.optimizer == "adamw":
        opt_bytes_per_param = 12.0 if args.precision_bytes < 4.0 else 8.0
    elif args.optimizer == "adamw8bit":
        opt_bytes_per_param = 6.0 if args.precision_bytes < 4.0 else 2.0
    else:
        opt_bytes_per_param = 4.0

    opt_bytes = trainable_params * opt_bytes_per_param
    if args.zero_stage >= 1:
        opt_bytes /= gpus

    # Approximate Transformer activation memory (FlashAttention-enabled: ~10*B*S*H*L bytes without ckpt, ~2*B*S*H*L with ckpt)
    act_factor = 2.0 if args.grad_checkpointing else 10.0
    act_bytes = act_factor * args.batch_size * args.seq_len * args.hidden_size * args.num_layers * 2.0

    # CUDA context + fragmentation headroom (~1.5 GiB + 10% buffer)
    subtotal_gib = (weight_bytes + grad_bytes + opt_bytes + act_bytes) / gib
    total_gib = subtotal_gib * 1.10 + 1.5

    print("=== Per-GPU VRAM Estimate ===")
    print(f"Config          : {args.params_b:g}B params (trainable={args.trainable_frac*100:.1f}%), {args.num_gpus} GPU(s), ZeRO/FSDP Stage {args.zero_stage}, grad_ckpt={args.grad_checkpointing}")
    print(f"Weights         : {weight_bytes / gib:6.2f} GiB")
    print(f"Gradients       : {grad_bytes / gib:6.2f} GiB")
    print(f"Optimizer ({args.optimizer:<8}): {opt_bytes / gib:6.2f} GiB")
    print(f"Activations     : {act_bytes / gib:6.2f} GiB (micro-batch={args.batch_size}, seq={args.seq_len})")
    print(f"Est. Total Peak : {total_gib:6.2f} GiB (includes ~10% allocator fragmentation + CUDA context)")

    tiers = [(24, "RTX 4090 / A10G / L4"), (40, "A100-40GB"), (48, "L40S / A6000"), (80, "A100/H100-80GB"), (141, "H200-141GB")]
    fit = next((name for cap, name in tiers if total_gib <= cap * 0.95), "Requires multi-node FSDP/TP or lower micro-batch")
    print(f"Minimum GPU Fit : {fit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
