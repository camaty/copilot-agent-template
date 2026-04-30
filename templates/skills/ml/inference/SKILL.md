---
name: ml-inference
description: "Serving, batch inference, quantization, and deployment of trained models. Triggers: inference, serving, deploy, quantize, ONNX, TensorRT, latency, throughput."
domain: ml
subdomain: inference
facets:
  # - framework:pytorch
  # - framework:onnx
  # - target:gpu
  # - target:cpu
  # - target:edge
  # - precision:int8
applies_when:
  any_of:
    - "task takes an existing trained model and runs predictions in production"
    - "task involves quantization, distillation, or graph optimization for deployment"
    - "task involves serving a model behind an API or batch pipeline"
    - "task is latency- or throughput-bound"
version: 0.1.0
---
# Machine Learning / Inference

## When to use

Open this skill when the input is a trained checkpoint and the goal is to serve, optimize, or batch-process predictions. For producing the checkpoint, see [`../training/SKILL.md`](../training/SKILL.md).

## Canon

- **Serving topology** — single-replica, replicated, sharded, or model-parallel. Choose by latency / memory / throughput targets.
- **p50 / p95 / p99 latency** — characterize the full distribution; means hide tail behavior.
- **Quantization** — reducing weight/activation precision (fp16, bf16, int8, int4) for memory and speed at a calibrated quality cost.
- **Calibration set** — a small representative dataset used to choose quantization scales.
- **Warmup** — first few requests are slow due to JIT/CUDA caches; exclude from latency measurement.
- **Batching** — static, dynamic, or continuous (LLM-specific). Larger batches trade latency for throughput.

## Recommended patterns

1. **Freeze the model graph** before deployment (TorchScript, ONNX, TensorRT, OpenVINO) for predictable performance.
2. **Quantize with calibration**, then re-evaluate on the validation set; reject if quality drops beyond a documented threshold.
3. **Measure with realistic workloads.** Synthetic uniform inputs hide cache and branch-prediction behavior.
4. **Pin and pre-load** the model on process start; never lazy-load on the request path.
5. **Pre-allocate buffers** when possible; allocation in the hot path adds GC / fragmentation cost.
6. **Bound concurrency per replica** to a value derived from a load test, not by guessing.
7. **Health and readiness probes that exercise an actual inference**, not just process liveness.

## Pitfalls

- ❌ **Reporting latency without warmup.** First few hundred ms include JIT/CUDA setup.
- ❌ **Quantizing without re-evaluating quality.** Silent regression in production.
- ❌ **Different preprocessing in training and serving.** Subtle skew destroys metrics.
- ❌ **Logging full inputs/outputs.** Often PII; almost always too expensive.
- ❌ **CPU-thread contention with the framework's intra-op pool** when running many replicas per host.
- ❌ **Assuming GPU memory is reclaimed between requests.** Caching allocators retain it.
- ❌ **Treating an LLM's tokenizer as language-agnostic.** Same string → different token counts across languages.

## Procedure

1. Define SLOs: target p95 latency, throughput, error rate, and quality (offline metric tied to training eval).
2. Pick the serving runtime (Triton, vLLM, TGI, BentoML, custom) based on model and target hardware.
3. Export and freeze the graph; verify outputs match the training framework within tolerance.
4. Apply quantization or distillation; re-run the eval harness and document quality delta.
5. Load test against realistic inputs; record p50/p95/p99, throughput, and resource usage.
6. Add observability: per-stage latency, queue depth, error class, output sanity checks.

## Validation

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
# Inference-specific:
# - Parity test: served output ≈ training-framework output within tolerance.
# - Load test (e.g. `vegeta`, `locust`, `oha`) reaches SLO at target concurrency.
```

## See also

- [`../training/SKILL.md`](../training/SKILL.md) — produces the checkpoints this skill consumes
- ONNX Runtime, TensorRT, vLLM, Triton Inference Server documentation
