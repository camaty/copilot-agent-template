---
name: ml-edge-inference
description: "On-device / edge inference: ONNX Runtime, TensorFlow Lite, Core ML, ExecuTorch, NPU/DSP delegates, quantisation (int8/int4), graph optimisation, mobile and embedded deployment. Triggers: edge inference, on-device, mobile ML, ONNX Runtime, TFLite, Core ML, ExecuTorch, NNAPI, NPU, Hexagon DSP, ANE, quantization, edge AI."
domain: ml
subdomain: edge-inference
facets:
  - lang:python
  - lang:cpp
  - lang:swift
  - lang:kotlin
  - framework:pytorch
  - framework:tensorflow
  - framework:onnx
  - target:mobile
  - target:edge
  - target:cpu
  - target:gpu
  - precision:int8
  - precision:int4
  - precision:fp16
applies_when:
  any_of:
    - "task ships an ML model to a phone, browser, microcontroller, or embedded SoC"
    - "task converts a PyTorch / TF / JAX model to ONNX, TFLite, Core ML, or ExecuTorch"
    - "task quantises (int8, int4) or compiles a model for an NPU / DSP / GPU delegate"
    - "task tunes inference latency, memory, or thermal envelope on-device"
    - "task wires platform delegates: NNAPI, Core ML, Hexagon DSP, GPU, XNNPACK"
version: 0.1.0
---
# Machine Learning / Edge Inference

## When to use

Open this skill when the deliverable is a model that runs on
the *user's* hardware — a phone, headset, browser, microcontroller,
or single-board computer — under tight latency, memory, and power
budgets. For server-side inference (large GPU, dynamic batching,
autoscaling), use [`../inference/SKILL.md`](../inference/SKILL.md)
instead. For training and quantisation-aware fine-tuning that
*precedes* edge deployment, see
[`../training/SKILL.md`](../training/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Runtimes** — choose the one that fits your platform set:
  *ONNX Runtime* (cross-platform, broad delegate matrix),
  *TensorFlow Lite / LiteRT* (Android-first, NNAPI/Core ML),
  *Core ML* (Apple-only, ANE), *ExecuTorch* (PyTorch-native edge),
  *MediaPipe / LiteRT for Web*, *TVM / IREE* (compile-then-run).
- **Delegates / Execution Providers** — runtime adapters that
  hand subgraphs to hardware: TFLite delegates (NNAPI, GPU,
  Core ML, Hexagon, XNNPACK); ORT EPs (CoreML, NNAPI, QNN,
  CUDA, DirectML, WebGPU, WebNN). Unsupported ops fall back
  to CPU — *measure*, don't assume.
- **Quantisation** — *PTQ* (post-training, fast, accuracy hit
  varies) vs *QAT* (quant-aware training, best accuracy, more
  effort). Schemes: per-tensor / per-channel; symmetric /
  asymmetric; int8 weights+activations; int4 weight-only
  (LLMs); fp16 / bf16 activations.
- **Operator coverage** — every runtime/delegate has a *supported
  op list*. Anything outside it forces fallbacks or model
  rewrites. Check before you train.
- **Graph optimisation** — constant folding, op fusion (e.g.
  Conv-BN-ReLU), layout transform (NHWC ↔ NCHW), dead-code
  elimination. Done at conversion time; verify with the
  runtime's profiler.
- **Memory planning** — arena allocators reuse buffers across
  ops. Peak memory ≠ sum of tensors; query the runtime's
  arena size after planning.
- **Cold start vs steady state** — model load + arena alloc +
  first-inference compile (delegate-specific) can dwarf the
  per-frame cost. Pre-warm with a dummy input on a background
  thread.
- **Thermal throttling** — sustained NPU / GPU at peak clock
  for ~30 s on a phone trips the SoC's thermal governor;
  steady-state perf is 30–60 % of burst.
- **Battery** — energy ≈ ops × per-op-energy; lower-precision
  delegates (NPU > GPU > CPU) typically win even at equal
  latency.
- **Weight format** — TFLite `.tflite` (FlatBuffer), ONNX
  `.onnx` (Protobuf), Core ML `.mlpackage` (bundle),
  ExecuTorch `.pte`. *Never* ship un-quantised checkpoints
  to mobile.
- **Versioning** — opset (ONNX), schema version (TFLite),
  spec version (Core ML). Pin the converter version; a newer
  opset can break older runtimes.

## Recommended patterns

1. **Pick the runtime per platform set, not per project.**
   Apple-exclusive: Core ML. Android-first: TFLite + NNAPI /
   GPU delegate. Cross-platform incl. Windows/Linux: ONNX
   Runtime. PyTorch-only and willing to live on the leading
   edge: ExecuTorch.
2. **Author the model with edge ops in mind.** Avoid dynamic
   shapes, control flow, and exotic ops; replace with static
   alternatives during training, not after conversion.
3. **Quantise post-training first; reach for QAT only on a
   measured accuracy regression.** Per-channel symmetric int8
   for CNNs, weight-only int4 (GPTQ / AWQ) for LLMs.
4. **Validate numerically at the conversion boundary.** Run
   the original and converted models on a held-out set; assert
   max abs / cosine / top-k agreement.
5. **Pre-warm on a background thread.** Load the model, run a
   dummy inference at app start; cache the prepared arena.
6. **Pin tensor layouts.** NHWC for TFLite/Core ML/most NPUs;
   NCHW for ONNX Runtime defaults; explicit transposes are
   cheaper than implicit fallbacks.
7. **Bench under thermal soak.** Run a 60 s loop, log p50/p95
   per-second; report sustained perf, not peak.
8. **Ship one model per platform tier.** A single `.onnx` for
   all Android phones is fine for CPU; for NPU you'll often
   need vendor-specific compilation (QNN, OpenVINO).
9. **Profile the delegate fallback boundary.** ORT's
   `enable_profiling`; TFLite Benchmark Tool's per-op
   breakdown; XCode Instruments for Core ML.
10. **Encrypt or obfuscate sensitive weights** if IP-protected.
    Mobile binaries are easy to extract; consider on-device
    decryption or split-execution.
11. **Plan model updates out-of-band** of the app store. Sign
    and version the model file; treat it like a config blob
    fetched at start-up.

## Pitfalls (subdomain-specific)

- ❌ **Optimising on a desktop simulator only.** The Android
  emulator's NNAPI delegate is *not* representative; thermal
  and DSP behaviour are absent. Always bench on real
  hardware.
- ❌ **Quantising without a calibration set that matches
  production distribution.** Big accuracy regression hidden
  on the validation set surfaces in the wild.
- ❌ **Assuming the GPU delegate is always faster.** On modern
  iPhones the ANE often beats GPU; on low-end Android, CPU +
  XNNPACK can beat a misconfigured GPU delegate.
- ❌ **Dynamic shapes / control flow.** TFLite and Core ML
  silently fall back to CPU or fail to convert; design with
  static shapes (or pad + mask).
- ❌ **Mixing op precisions ad hoc.** Per-op fp32/int8 mixes
  insert dequant/quant on every boundary; cluster precisions
  by subgraph.
- ❌ **Skipping the post-conversion numeric check.** A silent
  layout transpose error can produce visually-plausible-but-
  wrong outputs.
- ❌ **Over-quantising classification heads.** Final softmax /
  logits often need fp16/fp32 to preserve top-k ordering.
- ❌ **Reloading the model every inference.** Cold-start cost
  dominates; cache the interpreter / session.
- ❌ **Running large models in the UI thread.** Even 10 ms
  models cause jank; offload to a background dispatcher.
- ❌ **Ignoring opset / runtime version skew.** Models built
  with ONNX opset 19 fail on older mobile ORT bundles; pin
  the converter and the runtime in CI.
- ❌ **Shipping one giant model when distillation gives ≥ 2× at
  ≤ 1 % accuracy loss.** Distil first, then quantise.

Domain-wide pitfalls live in [`../inference/SKILL.md`](../inference/SKILL.md).

## Procedure

1. **Specify the device matrix and SLA.** Target SoCs, OS
   versions, latency, memory, power, accuracy floor. This
   selects the runtime.
2. **Train with edge in mind.** Static shapes, supported ops,
   QAT if PTQ won't meet the accuracy floor.
3. **Convert.** PyTorch → ONNX (`torch.onnx.export` /
   `torch.export` + `executorch`); ONNX → TFLite via
   `onnx2tf`; PyTorch → Core ML via `coremltools`.
4. **Quantise** with a representative calibration set
   (≥ 200 samples covering distribution edges). Inspect
   per-layer scales; clip outliers manually if needed.
5. **Optimise the graph.** Run the runtime's optimiser
   (`onnxruntime.tools.optimizer_for_mobile`,
   `tflite_convert --optimizations`).
6. **Numeric validation.** Compare against fp32 baseline on
   a held-out set; gate the build on top-1 / top-5 / mAP.
7. **Pick the delegate(s) per device tier**, document the
   selection logic, and ship a CPU fallback path for every
   tier.
8. **Bench on hardware.** Cold + warm + soak; record
   p50/p95/p99 latency and energy if available.
9. **Wire the app integration.** Background load, async
   inference, queue back-pressure, UI thread isolation.
10. **Set up regression CI.** Re-run conversion + numeric +
    on-device bench on every model change.

## Validation

After completing the procedure, run:

```sh
# Conversion + numeric parity
python -m onnxruntime.tools.check_onnx_model_mobile_usability model.onnx
python tools/numeric_parity.py --fp32 ref.onnx --quant model.int8.onnx \
    --calib data/calib --tol 1e-2

# On-device benchmarks
adb shell /data/local/tmp/benchmark_model \
    --graph=/data/local/tmp/model.tflite --num_runs=200 \
    --use_gpu=true --profiling_output_csv_file=/sdcard/prof.csv
xcrun coremlc compile model.mlpackage build/ \
    && xcrun simctl spawn booted ./bench --model build/model.mlmodelc

# ONNX Runtime mobile
onnxruntime_perf_test -e coreml -r 200 -m times -I model.ort

# Regression
pytest tests/edge --benchmark-only --benchmark-autosave
```

## See also

- [`../inference/SKILL.md`](../inference/SKILL.md) — for the
  server-side inference path; many patterns (dynamic batching,
  KV-cache) do *not* apply at the edge.
- [`../training/SKILL.md`](../training/SKILL.md) — for QAT and
  distillation that precede edge conversion.
- [`../../coding/robotics/SKILL.md`](../../coding/robotics/SKILL.md)
  — when the edge target is an on-board robot accelerator.
- [`../../coding/embedded/SKILL.md`](../../coding/embedded/SKILL.md)
  — for MCU-class deployments (TFLite Micro, microTVM).
- ONNX Runtime — <https://onnxruntime.ai/docs/>
- TensorFlow Lite / LiteRT — <https://ai.google.dev/edge/litert>
- Core ML Tools — <https://apple.github.io/coremltools/>
- ExecuTorch — <https://pytorch.org/executorch/stable/>
- MLPerf Mobile / Tiny — <https://mlcommons.org/benchmarks/>
