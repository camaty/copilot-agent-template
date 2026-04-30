---
name: ml-inference
description: "Serving, batch inference, quantization, and deployment of trained models with latency/throughput SLOs. Triggers: inference, serving, deploy, quantize, ONNX, TensorRT, vLLM, Triton, latency, throughput, batching, KV cache, distillation."
domain: ml
subdomain: inference
facets:
  - lang:python
  - framework:pytorch
  - framework:onnx
  - target:gpu
  - target:cpu
  - target:edge
  - precision:int8
  - precision:fp16
applies_when:
  any_of:
    - "task takes an existing trained model and runs predictions in production"
    - "task involves quantization, distillation, or graph optimization for deployment"
    - "task involves serving a model behind an API or batch pipeline"
    - "task is latency- or throughput-bound"
    - "task involves continuous batching, KV cache, or speculative decoding"
version: 0.1.0
---
# Machine Learning / Inference

## When to use

Open this skill when the input is a trained checkpoint and the goal is
to serve, optimise, or batch-process predictions. For producing the
checkpoint, see [training](../training/SKILL.md). For LLM-specific
serving (KV cache, paged attention, speculative decoding), this skill
applies — vLLM/TGI/Triton patterns are covered here.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Serving topology** — single-replica, replicated (data-parallel),
  sharded (tensor-parallel), or model-parallel (pipeline-parallel).
  Choose by latency / memory / throughput targets and HBM size.
- **p50 / p95 / p99 latency** — characterise the full distribution;
  means hide tail behaviour. p99 is what users actually feel.
- **Quantization** — reducing weight/activation precision (`fp16`,
  `bf16`, `int8`, `int4`, `fp8`) for memory and speed at a calibrated
  quality cost. Weight-only vs full quantisation differ in quality.
- **Calibration set** — a small representative dataset used to choose
  quantization scales / clipping thresholds. Drawn from production-
  like inputs, never from training data alone.
- **Warmup** — first few requests are slow due to JIT, CUDA caches,
  and CUDA graphs being captured. Exclude from latency measurement.
- **Batching** — static (fixed batch), dynamic (assemble from queue
  with timeout), continuous / iteration-level (LLM-specific). Larger
  batches trade latency for throughput.
- **KV cache** — decoder-LLM cache of attention key/value tensors per
  token. Memory-dominant resource; PagedAttention (vLLM) is the
  modern allocator pattern.
- **Speculative decoding** — small draft model proposes tokens, big
  model verifies in one pass. 2–3× speedup on long generations.
- **Continuous batching** — schedule requests at the iteration level,
  not the request level. Standard in vLLM/TGI; doubles throughput
  at the cost of more complex schedulers.
- **Tail amplification** — slow shards dominate sharded inference;
  always provision identical hardware and pin processes to NUMA.
- **Graph capture** — TorchScript / `torch.compile` / TensorRT /
  ONNX Runtime; freezes the dispatch path for predictable
  performance.

## Recommended patterns

1. **Freeze the model graph** before deployment (`torch.compile`,
   TorchScript, ONNX, TensorRT, OpenVINO) for predictable latency.
2. **Quantise with calibration**, then re-evaluate on the validation
   set; reject if quality drops beyond a documented threshold (e.g.
   ≤ 1 % on the gold metric).
3. **Measure with realistic workloads.** Synthetic uniform inputs
   hide cache and branch-prediction behaviour; replay production
   traces.
4. **Pin and pre-load** the model on process start; never lazy-load
   on the request path.
5. **Pre-allocate buffers** when possible; allocation in the hot path
   adds GC / fragmentation cost.
6. **Bound concurrency per replica** to a value derived from a load
   test, not by guessing.
7. **Health and readiness probes that exercise an actual inference**,
   not just process liveness — reuse a fixed canary input.
8. **For LLMs, use a runtime with continuous batching + paged KV
   cache** (vLLM, TGI, TensorRT-LLM). Hand-rolled loops leave 2–4×
   throughput on the table.
9. **Speculative decoding** for long generations when the draft
   model is materially smaller than the target.
10. **Token-budget your endpoints.** Reject requests at the gate
    when projected output × queue exceeds budget; better than OOM.
11. **Observability is part of the artifact** — per-stage latency,
    queue depth, KV-cache utilisation, error class, output sanity
    checks emitted by default.

## Pitfalls (subdomain-specific)

- ❌ **Reporting latency without warmup.** First few hundred ms
  include JIT/CUDA setup; not what users see in steady state.
- ❌ **Quantising without re-evaluating quality.** Silent regression
  in production. Always run the eval harness post-quant.
- ❌ **Different preprocessing in training and serving.** Subtle
  skew destroys metrics; reuse the exact transforms / tokeniser.
- ❌ **Logging full inputs/outputs** at INFO. Often PII; almost
  always too expensive at scale; use sampled DEBUG for diagnostics.
- ❌ **CPU-thread contention with the framework's intra-op pool**
  when running many replicas per host. Set `OMP_NUM_THREADS` and
  pin replicas to non-overlapping cores.
- ❌ **Assuming GPU memory is reclaimed between requests.** Caching
  allocators retain memory; OOM later under spiky load.
- ❌ **Treating an LLM tokeniser as language-agnostic.** Same string
  → different token counts across languages; budget per-language.
- ❌ **Single-replica deploy without rolling.** Cold restarts spike
  service errors to 100 %; deploy with N ≥ 2 + drain policy.
- ❌ **Static batching for variable-length LLM workloads.** Pads
  short requests, wastes 50 %+ of FLOPs.
- ❌ **Running quantised int8 weights at fp32 activations on
  GPUs that don't fuse the dequant** — slower than fp16; profile
  the fused kernel exists.
- ❌ **Reading Python objects (lists, dicts) inside the inference
  hot loop.** Pre-tensorise everything; the GIL bites under load.
- ❌ **Serving without graceful shutdown.** Replica restarts drop
  in-flight requests; honour SIGTERM with a drain timeout.

Domain-wide pitfalls (when present) live in `../_shared/pitfalls.md`.

## Procedure

1. **Define SLOs**: target p95 latency, throughput (requests/s and
   tokens/s for LLMs), error rate, and quality (offline metric tied
   to the training eval).
2. **Pick the serving runtime** (Triton, vLLM, TGI, TensorRT-LLM,
   ONNX Runtime, BentoML, custom) based on model and target
   hardware.
3. **Export and freeze the graph**; verify outputs match the training
   framework within tolerance (`max_abs_diff < 1e-3` for fp32,
   `< 5e-3` for fp16).
4. **Apply quantisation or distillation**; re-run the eval harness
   and document quality delta. Block release if delta exceeds
   budget.
5. **Load test** against realistic inputs; record p50/p95/p99,
   throughput, and resource utilisation. Tools: `oha`, `vegeta`,
   `locust`, `ghz` (gRPC), `genai-perf` (LLM).
6. **Add observability**: per-stage latency, queue depth, GPU util,
   KV-cache util (LLM), error class, output sanity checks.
7. **Capacity plan** — replicas per region; headroom ≥ 30 % above
   p95 expected load; autoscale with cool-down to avoid thrash.
8. **Roll out** with staged traffic (canary → 10 % → 100 %) and
   automated rollback on error-rate / latency regressions.
9. **Burn-in** the new replica with the canary set before promoting.

## Validation

After completing the procedure, run:

```sh
# Static checks
ruff check serving/
mypy --strict serving/

# Build & unit tests
pytest tests/serving/ -v

# Parity test: served output vs training-framework output
python -m tests.parity --tol 1e-3

# Quality test (post-quantisation): eval on val set
python -m eval.run --runtime trt-llm --max-quality-delta 0.01

# Load test under realistic mix
oha -z 60s -c 64 https://svc.local/v1/predict
genai-perf --service-kind openai --endpoint-type chat \
    --random-seed 42 --request-rate 50 --num-prompts 1000

# Soak test (catches memory leaks, KV-cache fragmentation)
locust -f tests/loadtest.py --headless -u 200 -r 10 -t 30m

# Failure-mode tests
toxiproxy-cli toxic add upstream -t latency -a latency=2000
# Send the serving process SIGTERM and assert in-flight
# requests drain within drain_timeout (use the runtime's
# graceful-shutdown helper rather than ad-hoc signal calls).
python -m tests.shutdown --pidfile /run/serving.pid --drain 30
```

## Validation gates (PR-ready criteria)

- Parity: `max_abs_diff` ≤ tolerance vs training framework.
- Quality: Δ on gold metric ≤ documented budget.
- Load: p95 latency ≤ SLO at target concurrency; error rate ≤ SLO.
- Soak: 30-min steady run, no memory growth past baseline.

## See also

- [`../training/SKILL.md`](../training/SKILL.md) — produces the
  checkpoints this skill consumes.
- [`../llm-finetuning/SKILL.md`](../llm-finetuning/SKILL.md) — when
  serving a fine-tuned LLM (LoRA merging, adapter hot-swap).
- [`../vlm-spatial/SKILL.md`](../vlm-spatial/SKILL.md) — VLM serving
  with multi-view 3D context.
- ONNX Runtime — <https://onnxruntime.ai/>
- TensorRT-LLM — <https://github.com/NVIDIA/TensorRT-LLM>
- vLLM (PagedAttention) — <https://vllm.ai/>
- Triton Inference Server — <https://github.com/triton-inference-server>
