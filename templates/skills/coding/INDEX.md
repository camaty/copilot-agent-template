---
domain: coding
version: 0.1.0
---
# Coding — Domain Index

> Generic software-engineering skills. Use this domain when the task is primarily about writing or modifying source code in any language.

## What this domain covers

Source code authorship, refactoring, debugging, API design, performance tuning, and tooling. Language-specific knowledge is expressed via `facets:` (`lang:python`, `lang:rust`, …) rather than as separate folders.

## Subdomain decision tree

Pick the first matching row.

| If the task involves… | Open this subdomain |
|---|---|
| Sockets, HTTP/gRPC servers, protocol design, latency or throughput SLOs | [`network/SKILL.md`](./network/SKILL.md) |
| Microcontrollers, RTOS, bare-metal, memory-constrained targets, hardware peripherals | [`embedded/SKILL.md`](./embedded/SKILL.md) |
| WebGPU compute/render pipelines, TSL or WGSL shader authoring, high-performance GPU compute in a browser | [`webgpu/SKILL.md`](./webgpu/SKILL.md) |
| Physically based volumetric simulations (blast waves, fluids, smoke) encoded in GLSL/WGSL shaders | [`shader-sim/SKILL.md`](./shader-sim/SKILL.md) |
| Distributes codegen across a planner model and multiple local executor models (Map-Reduce, multi-agent) | [`mapreduce-codegen/SKILL.md`](./mapreduce-codegen/SKILL.md) |
| Moving multi-GB 3D binary assets (splats, point clouds, datasets) over UDP-based protocols (Aspera/QUIC/UDT) | [`spatial-transfer/SKILL.md`](./spatial-transfer/SKILL.md) |
| Static security analysis (CodeQL, secret scanning, dependency review) over agent- or LLM-generated code | [`agent-sca/SKILL.md`](./agent-sca/SKILL.md) |
| Designing public/internal HTTP/REST/gRPC APIs, OpenAPI/Protobuf schemas, versioning, pagination, idempotency | [`api-design/SKILL.md`](./api-design/SKILL.md) |
| Logs, metrics, traces, OpenTelemetry, SLI/SLO/error budgets, dashboards as code | [`observability/SKILL.md`](./observability/SKILL.md) |
| Schema design, migrations, indexes, transactions, query plans across SQL / document / vector stores | [`databases/SKILL.md`](./databases/SKILL.md) |
| WebXR / OpenXR sessions, reference spaces, controller / hand input, anchors, hit testing, frame-pacing budgets | [`xr/SKILL.md`](./xr/SKILL.md) |
| HRTF / binaural rendering, ambisonics (FOA / HOA), Web Audio graphs, AudioWorklet DSP, room reverb | [`spatial-audio/SKILL.md`](./spatial-audio/SKILL.md) |
| ROS 2 nodes, DDS QoS, tf2 / URDF, Nav2 / MoveIt 2 / ros2_control, Gazebo or Isaac Sim integration | [`robotics/SKILL.md`](./robotics/SKILL.md) |
| _none of the above_ | apply [`_shared/`](./_shared/) only and proceed with general practice |

Add a new subdomain only when its canon and pitfall set diverge meaningfully from the above. See [`../EXTENDING.md`](../EXTENDING.md).

## Facet vocabulary

| Axis | Allowed values |
|---|---|
| `lang:`    | `python`, `typescript`, `javascript`, `rust`, `go`, `c`, `cpp`, `java`, `kotlin`, `swift`, `ruby`, `csharp`, `shell`, `glsl`, `wgsl` |
| `target:`  | `linux`, `macos`, `windows`, `wasm`, `mcu`, `rtos`, `browser`, `mobile`, `gpu`, `network`, `embedded`, `headset` |
| `style:`   | `oop`, `functional`, `data-oriented`, `actor`, `event-driven` |
| `vendor:`  | `openai`, `qwen`, `anthropic`, `mistral`, `github-advanced-security`, `aspera`, `opentelemetry`, `prometheus`, `grafana`, `postgres`, `khronos`, `webaudio`, `ros2`, `nvidia` |

## Shared resources

- [`_shared/canon.md`](./_shared/canon.md)
- [`_shared/pitfalls.md`](./_shared/pitfalls.md)

## Related domains

- `ml` — when the code is primarily a model training / inference pipeline
- `gameengine` — when targeting Unity or Unreal scripting layers
