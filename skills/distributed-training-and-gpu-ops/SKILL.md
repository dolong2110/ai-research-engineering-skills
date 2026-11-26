---
name: distributed-training-and-gpu-ops
description: >-
  Configure, profile, and troubleshoot GPU and multi-GPU ML/LLM training workloads
  (PyTorch DDP, FSDP, DeepSpeed ZeRO, mixed precision bf16/fp8, torch.compile,
  gradient checkpointing, DataLoader throughput, Slurm preemption checkpointing,
  and VRAM budgeting). Use this skill when sizing GPU memory, fixing CUDA OOMs,
  accelerating slow training loops, or launching distributed cluster jobs.
---

# Distributed Training & GPU Operations

Use this skill whenever sizing GPU memory, debugging CUDA OOMs, accelerating PyTorch/JAX training throughput, or configuring multi-GPU / Slurm cluster runs.

## 1. Budget GPU VRAM Before Launching Expensive Runs

Run [estimate_gpu_vram.py](./scripts/estimate_gpu_vram.py) before allocating nodes to avoid trial-and-error OOM crashes across full fine-tuning, LoRA, DDP, and FSDP/ZeRO:

```bash
python3 skills/distributed-training-and-gpu-ops/scripts/estimate_gpu_vram.py \
  --params-b 7 \
  --batch-size 4 \
  --seq-len 4096 \
  --hidden-size 4096 \
  --num-layers 32 \
  --num-gpus 4 \
  --zero-stage 3 \
  --grad-checkpointing
```

## 2. High-Throughput Single- & Multi-GPU Training Checklist

1. **Precision First**:
   - Prefer `bfloat16` (`torch.amp.autocast("cuda", dtype=torch.bfloat16)`) over `float16` on Ampere/Hopper/Blackwell GPUs—same dynamic range as `fp32`, no `GradScaler` overflow tuning required.
   - Enable TF32 for matmul/cuDNN (`torch.set_float32_matmul_precision("high")`).
2. **Eliminate DataLoader Starvation**:
   - Profile GPU utilization (`nvidia-smi dmon -s u`); if GPU util oscillates `0% <-> 100%`, the input pipeline is bottlenecked.
   - Set `pin_memory=True`, `persistent_workers=True`, `prefetch_factor=2..4`, and tune `num_workers` (typically `2..4` per GPU). Pre-shard datasets into sequential binary/Parquet/WebDataset shards instead of opening millions of tiny files!
3. **Choosing Parallelism Strategy**:
   - **Fits on 1 GPU**: Standard **DDP** (`torchrun --nproc_per_node=N`) with `DistributedSampler(shuffle=True)` and `sampler.set_epoch(epoch)` every epoch!
   - **Optimizer states / weights exceed 1 GPU**: **FSDP2 / ZeRO-2** (shards optimizer + grads) or **FSDP Full Shard / ZeRO-3** (shards weights too) + **Activation Checkpointing** (`checkpoint_wrapper`) before reaching for Tensor Parallelism (which demands high-bandwidth NVLink).
4. **Correct Gradient Accumulation & Loss Scaling**:
   - Divide loss by `grad_accum_steps`, wrap intermediate micro-steps in `model.no_sync()` under DDP/FSDP to skip redundant `all_reduce` traffic, and clip gradients (`clip_grad_norm_`) **after** accumulation and **before** `optimizer.step()`.
5. **Preemption-Safe Cluster Checkpointing (Slurm / Spot VMs)**:
   - Save checkpoints atomically (write to `ckpt.tmp` -> `os.replace`) including model, optimizer, scheduler, RNG states, global step, and dataloader offset; log only from `rank == 0`; guard `dist.barrier()` calls with explicit NCCL timeouts (`TORCH_NCCL_ASYNC_ERROR_HANDLING=1`).

## 3. Fast OOM Triage Order

When hitting `CUDA out of memory`, apply levers in order of lowest quality/speed penalty:
1. Enable **activation/gradient checkpointing** (cuts activation memory ~60–80% for ~20–30% extra compute).
2. Switch to **FlashAttention / SDPA** (`F.scaled_dot_product_attention`) to turn $O(L^2)$ attention matrices into $O(L)$.
3. Reduce micro-batch size + increase `grad_accum_steps` to preserve effective global batch size.
4. Use **8-bit / paged AdamW** or **FSDP / ZeRO-3** sharding, or switch from full fine-tuning to **LoRA / QLoRA**.
