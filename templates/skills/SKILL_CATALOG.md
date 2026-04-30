# Skill Catalog — Generative Spatial Computing

> **How to use this catalog**
>
> Each entry has a short numeric ID. To generate one or more skills in parallel, pass their IDs to the `@Setup` agent or a dedicated generation prompt:
>
> ```
> @Setup generate-skills 1 3 7          # generate skills #1, #3, and #7
> @Setup generate-skills 1-5            # generate skills #1 through #5
> @Setup generate-skills cluster:2      # generate all skills in cluster 2
> @Setup generate-skills all            # generate all 20 skills
> ```
>
> The agent reads this catalog, resolves each ID to its `target_path`, `domain`, `subdomain`, and `facets`, then scaffolds the files using `_layout/SUBDOMAIN_SKILL.template.md` (for subdomains) or `_layout/DOMAIN_INDEX.template.md` (for new domain index files).

---

## Cluster 1 — Next-gen Web Graphics & Spatial Rendering

Skills covering WebGPU compute, 3DGS streaming, FSR, and shader-resident physics.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 01 | WebGPU rendering & TSL/WGSL | `coding/webgpu/SKILL.md` | `coding` | `webgpu` | `lang:wgsl`, `lang:ts`, `target:browser` |
| 02 | 3DGS viewer & FSR super-resolution | `3dcg/3dgs/SKILL.md` | `3dcg` | `3dgs` | `lang:ts`, `lang:wgsl`, `format:splat`, `target:browser` |
| 03 | Shader-resident volumetric simulation | `coding/shader-sim/SKILL.md` | `coding` | `shader-sim` | `lang:glsl`, `lang:wgsl`, `target:browser` |

### ID 01 — WebGPU rendering & TSL/WGSL

```yaml
id: 01
target_path: coding/webgpu/SKILL.md
domain: coding
subdomain: webgpu
facets:
  - lang:wgsl
  - lang:ts
  - target:browser
applies_when:
  any_of:
    - "task involves WebGPU compute pipelines or render pipelines"
    - "task uses GPUDevice, GPUCommandEncoder, or GPUBuffer directly"
    - "task writes TSL (Three Shading Language) or WGSL shaders"
    - "task targets high-performance GPU compute in a browser"
description: >
  Patterns and pitfalls for writing multi-pass render pipelines and compute
  kernels against the WebGPU API, including TSL/WGSL shader authoring,
  buffer management, and feature-detection for fallback paths.
new_files:
  - coding/webgpu/SKILL.md
update_files:
  - coding/INDEX.md        # add row for webgpu subdomain
```

### ID 02 — 3DGS viewer & FSR super-resolution

```yaml
id: 02
target_path: 3dcg/3dgs/SKILL.md
domain: 3dcg
subdomain: 3dgs
facets:
  - lang:ts
  - lang:wgsl
  - format:splat
  - target:browser
applies_when:
  any_of:
    - "task streams or renders 3D Gaussian Splatting scenes"
    - "task applies AMD FSR or similar upscaling to a 3DGS viewport"
    - "task composites splat data with rasterised geometry"
    - "task edits or filters Gaussian splat data at runtime"
description: >
  Pipeline for streaming large .splat/.ply datasets to a browser viewer,
  applying FSR-based super-resolution, and compositing splats with standard
  mesh geometry. Covers tile-based loading, sort passes, and splat editing.
new_files:
  - 3dcg/3dgs/SKILL.md
update_files:
  - 3dcg/INDEX.md          # add row for 3dgs subdomain
```

### ID 03 — Shader-resident volumetric simulation

```yaml
id: 03
target_path: coding/shader-sim/SKILL.md
domain: coding
subdomain: shader-sim
facets:
  - lang:glsl
  - lang:wgsl
  - target:browser
  - target:gpu
applies_when:
  any_of:
    - "task simulates Taylor–Sedov blast wave, fluid, or smoke inside a shader"
    - "task encodes a physical simulation entirely in GLSL or WGSL"
    - "task needs real-time volumetric effects without CPU physics"
description: >
  Techniques for encoding physically based volumetric simulations (blast
  waves, fluids, smoke) directly in GLSL/WGSL fragment or compute shaders,
  including time-step parameterisation, boundary conditions, and perf budgets.
new_files:
  - coding/shader-sim/SKILL.md
update_files:
  - coding/INDEX.md        # add row for shader-sim subdomain
```

---

## Cluster 2 — Deterministic AI Control & Procedural CAD

Skills covering LLM-safe CAD APIs, topology-constrained assembly, and multi-agent codegen.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 04 | Smart-CG API harness | `cad/api-harness/SKILL.md` | `cad` | `api-harness` | `lang:python`, `lang:ts`, `vendor:llm` |
| 05 | Topology-constrained assembly | `cad/topology-assembly/SKILL.md` | `cad` | `topology-assembly` | `lang:python`, `format:step`, `format:brep` |
| 06 | Map-Reduce multi-agent codegen | `coding/mapreduce-codegen/SKILL.md` | `coding` | `mapreduce-codegen` | `lang:python`, `vendor:openai`, `vendor:qwen` |

### ID 04 — Smart-CG API harness

```yaml
id: 04
target_path: cad/api-harness/SKILL.md
domain: cad
subdomain: api-harness
facets:
  - lang:python
  - lang:ts
  - vendor:llm
applies_when:
  any_of:
    - "task constrains an LLM to a strict OpenAPI specification or JSON Schema for 3D scene operations"
    - "task adds a deterministic checker or validator layer between an LLM and a CAD/CG API"
    - "task prevents hallucinated geometry by validating LLM output before execution"
description: >
  Architecture patterns for wrapping CAD or CG APIs in a harness that gives an
  LLM a strict, schema-validated action space, then applies a deterministic
  geometry checker before any writes, eliminating hallucinated meshes or
  invalid assembly operations.
new_files:
  - cad/api-harness/SKILL.md
update_files:
  - cad/INDEX.md           # add row for api-harness subdomain
```

### ID 05 — Topology-constrained assembly

```yaml
id: 05
target_path: cad/topology-assembly/SKILL.md
domain: cad
subdomain: topology-assembly
facets:
  - lang:python
  - format:step
  - format:brep
applies_when:
  any_of:
    - "task defines point-to-point or axis-aligned mates between CAD parts"
    - "task programmatically assembles gears, furniture, or modular components"
    - "task encodes IKEA-style topology rules for part connectivity"
description: >
  Methods for defining topology constraints (point-to-point mates, axis
  alignment, IKEA-style snap rules) that drive fully automated, programmatic
  assembly of functional CAD models such as gearboxes or flat-pack furniture.
new_files:
  - cad/topology-assembly/SKILL.md
update_files:
  - cad/INDEX.md           # add row for topology-assembly subdomain
```

### ID 06 — Map-Reduce multi-agent codegen

```yaml
id: 06
target_path: coding/mapreduce-codegen/SKILL.md
domain: coding
subdomain: mapreduce-codegen
facets:
  - lang:python
  - vendor:openai
  - vendor:qwen
applies_when:
  any_of:
    - "task distributes code generation across a planner model and multiple executor models"
    - "task uses a Map-Reduce pattern where a high-level model fans out subtasks to local models"
    - "task coordinates Qwen or similar local LLMs as executor agents"
description: >
  Orchestration pattern in which a high-level planner model decomposes a large
  coding task, fans it out to multiple local executor models (e.g. Qwen) that
  write and verify code against layered references, then a reducer merges and
  validates the results.
new_files:
  - coding/mapreduce-codegen/SKILL.md
update_files:
  - coding/INDEX.md        # add row for mapreduce-codegen subdomain
```

---

## Cluster 3 — Digital Humans & Motion Foundation Models

Skills covering BVH extraction, motion generation, and 3D garment simulation.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 07 | Motion foundation model & BVH extraction | `ml/motion-fm/SKILL.md` | `ml` | `motion-fm` | `lang:python`, `format:bvh`, `format:vrm` |
| 08 | 2D-to-3D garment fitting | `3dcg/garment-sim/SKILL.md` | `3dcg` | `garment-sim` | `lang:python`, `target:avatar` |

### ID 07 — Motion foundation model & BVH extraction

```yaml
id: 07
target_path: ml/motion-fm/SKILL.md
domain: ml
subdomain: motion-fm
facets:
  - lang:python
  - format:bvh
  - format:vrm
applies_when:
  any_of:
    - "task extracts skeletal kinematics from a monocular RGB video"
    - "task generates or retargets BVH animation data"
    - "task applies motion data to VRM or similar avatar formats"
    - "task trains or fine-tunes an autoregressive motion generation model"
description: >
  Workflow for training or applying autoregressive motion foundation models
  that extract per-frame skeletal kinematics from a single RGB video, output
  high-fidelity BVH animation clips, and retarget them to VRM or other
  standard avatar rigs.
new_files:
  - ml/motion-fm/SKILL.md
update_files:
  - ml/INDEX.md            # add row for motion-fm subdomain
```

### ID 08 — 2D-to-3D garment fitting

```yaml
id: 08
target_path: 3dcg/garment-sim/SKILL.md
domain: 3dcg
subdomain: garment-sim
facets:
  - lang:python
  - target:avatar
applies_when:
  any_of:
    - "task generates 3D garment geometry from a flat design or image"
    - "task simulates cloth drape on an avatar with physics"
    - "task fits clothing to a parametric body model"
description: >
  Pipeline to convert 2D garment designs or photographs into avatar-ready 3D
  clothing meshes, then apply physics-based cloth simulation (FEM or position-
  based dynamics) to produce natural drape and collision responses.
new_files:
  - 3dcg/garment-sim/SKILL.md
update_files:
  - 3dcg/INDEX.md          # add row for garment-sim subdomain
```

---

## Cluster 4 — Secure Dev & Transport Infrastructure for Spatial Assets

Skills covering high-throughput 3D file transfer and SCA over agent-generated code.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 09 | High-throughput spatial-asset transfer | `coding/spatial-transfer/SKILL.md` | `coding` | `spatial-transfer` | `lang:python`, `target:network`, `vendor:aspera` |
| 10 | Agent-code static security analysis | `coding/agent-sca/SKILL.md` | `coding` | `agent-sca` | `lang:python`, `lang:ts`, `vendor:github-advanced-security` |

### ID 09 — High-throughput spatial-asset transfer

```yaml
id: 09
target_path: coding/spatial-transfer/SKILL.md
domain: coding
subdomain: spatial-transfer
facets:
  - lang:python
  - target:network
  - vendor:aspera
applies_when:
  any_of:
    - "task transfers large 3DGS scenes, point clouds, or training datasets between hosts"
    - "task uses UDP-based high-bandwidth transfer (Aspera FASP, UDT, QUIC, or similar)"
    - "task builds a sync pipeline for multi-GB 3D binary assets"
description: >
  Patterns for reliably moving large 3D binary assets (3DGS .splat files,
  point clouds, ML training sets) between team members or cloud storage using
  UDP-based high-bandwidth protocols (Aspera FASP or equivalents), including
  checksum verification and resume support.
new_files:
  - coding/spatial-transfer/SKILL.md
update_files:
  - coding/INDEX.md        # add row for spatial-transfer subdomain
```

### ID 10 — Agent-code static security analysis (SCA)

```yaml
id: 10
target_path: coding/agent-sca/SKILL.md
domain: coding
subdomain: agent-sca
facets:
  - lang:python
  - lang:ts
  - vendor:github-advanced-security
applies_when:
  any_of:
    - "task audits agent-generated scripts or pipelines for security vulnerabilities"
    - "task configures CodeQL or secret scanning over auto-generated code"
    - "task checks for injection, async race conditions, or insecure deserialization in AI output"
description: >
  Workflow for integrating GitHub Advanced Security (CodeQL, secret scanning,
  dependency review) into pipelines that accept auto-generated code from
  Copilot agents, ensuring injections, async race conditions, and hardcoded
  secrets are caught before merge.
new_files:
  - coding/agent-sca/SKILL.md
update_files:
  - coding/INDEX.md        # add row for agent-sca subdomain
```

---

## Cluster 5 — Embodied AI & Synthetic Data Generation

Skills covering Unity/UE simulation environments and VLM-driven spatial understanding.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 11 | Unity/UE synthetic data environments | `gameengine/synthetic-data/SKILL.md` | `gameengine` | `synthetic-data` | `vendor:unity`, `vendor:unreal`, `lang:python`, `lang:csharp` |
| 12 | VLM spatial understanding | `ml/vlm-spatial/SKILL.md` | `ml` | `vlm-spatial` | `lang:python`, `format:splat`, `format:pcd` |

### ID 11 — Unity/UE synthetic data environments

```yaml
id: 11
target_path: gameengine/synthetic-data/SKILL.md
domain: gameengine
subdomain: synthetic-data
facets:
  - vendor:unity
  - vendor:unreal
  - lang:python
  - lang:csharp
applies_when:
  any_of:
    - "task generates synthetic training data from a Unity or Unreal Engine simulation"
    - "task trains inertial navigation or autonomous mobility models on engine-generated data"
    - "task configures domain randomisation or scenario variation in a game engine simulation"
description: >
  Infrastructure for generating physically accurate synthetic datasets inside
  Unity (Perception package) or Unreal Engine (Simulation for Synthetic Data)
  at scale, including domain randomisation, sensor model configuration, and
  export pipelines for robot and autonomous vehicle ML training.
new_files:
  - gameengine/synthetic-data/SKILL.md
update_files:
  - gameengine/INDEX.md    # add row for synthetic-data subdomain
```

### ID 12 — VLM spatial understanding

```yaml
id: 12
target_path: ml/vlm-spatial/SKILL.md
domain: ml
subdomain: vlm-spatial
facets:
  - lang:python
  - format:splat
  - format:pcd
applies_when:
  any_of:
    - "task uses a vision-language model to interpret a 3D scene (point cloud or 3DGS)"
    - "task autonomously edits or re-arranges objects in a real scanned space"
    - "task queries semantic layout of a 3D environment using natural language"
description: >
  Integration patterns for feeding 3D scan data (point clouds, 3DGS captures)
  to VLMs (GPT-4o vision, LLaVA, etc.), extracting semantic object layout, and
  driving autonomous re-arrangement or annotation of real-world scanned spaces.
new_files:
  - ml/vlm-spatial/SKILL.md
update_files:
  - ml/INDEX.md            # add row for vlm-spatial subdomain
```

---

## Cluster 6 — Cross-cutting Service Foundations

Skills covering the building blocks every networked service eventually needs: API contracts, observability signals, and data stores.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 13 | API design (REST / gRPC / OpenAPI / Protobuf) | `coding/api-design/SKILL.md` | `coding` | `api-design` | `lang:python`, `lang:typescript`, `lang:go`, `target:network` |
| 14 | Observability (logs / metrics / traces / OTel / SLOs) | `coding/observability/SKILL.md` | `coding` | `observability` | `lang:python`, `lang:typescript`, `lang:go`, `target:network` |
| 15 | Databases (relational / document / vector, schema, migrations) | `coding/databases/SKILL.md` | `coding` | `databases` | `lang:python`, `lang:typescript`, `lang:go`, `target:linux` |

### ID 13 — API design

```yaml
id: 13
target_path: coding/api-design/SKILL.md
domain: coding
subdomain: api-design
facets:
  - lang:python
  - lang:typescript
  - lang:go
  - target:network
applies_when:
  any_of:
    - "task designs a new HTTP, REST, or gRPC API surface"
    - "task introduces or evolves an OpenAPI / Protobuf schema"
    - "task adds versioning, pagination, idempotency, or error semantics to an existing API"
description: >
  Patterns for spec-first API design (OpenAPI 3.1, Protobuf): resource modelling,
  cursor pagination, idempotency keys, error envelopes, backwards compatibility,
  and contract testing.
new_files:
  - coding/api-design/SKILL.md
update_files:
  - coding/INDEX.md
```

### ID 14 — Observability

```yaml
id: 14
target_path: coding/observability/SKILL.md
domain: coding
subdomain: observability
facets:
  - lang:python
  - lang:typescript
  - lang:go
  - lang:rust
  - target:network
applies_when:
  any_of:
    - "task adds or improves logs, metrics, traces, or profiling for a service"
    - "task instruments code with OpenTelemetry / Prometheus / OpenMetrics"
    - "task defines SLIs / SLOs / error budgets"
description: >
  Instrumentation patterns: OpenTelemetry SDKs, structured logs, RED/USE
  methodology, low-cardinality metrics + high-cardinality traces, multi-window
  multi-burn-rate SLO alerts, dashboards-as-code.
new_files:
  - coding/observability/SKILL.md
update_files:
  - coding/INDEX.md
```

### ID 15 — Databases

```yaml
id: 15
target_path: coding/databases/SKILL.md
domain: coding
subdomain: databases
facets:
  - lang:python
  - lang:typescript
  - lang:go
  - target:linux
applies_when:
  any_of:
    - "task designs or migrates a database schema (relational, document, or vector)"
    - "task tunes a slow query, an index, or a transaction"
    - "task adds caching, replication, or sharding to a data tier"
    - "task integrates a vector store for retrieval"
description: >
  Schema design, online migrations, indexing strategies, isolation/MVCC,
  N+1 avoidance, connection pooling, replication, and pgvector-style vector
  retrieval; query-plan-driven optimisation discipline.
new_files:
  - coding/databases/SKILL.md
update_files:
  - coding/INDEX.md
```

---

## Cluster 7 — Pipeline Authoring & Open-Source CAD/CG

Skills covering OpenUSD authoring across DCC tools and FreeCAD-based open-source CAD automation.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 16 | OpenUSD pipeline (layers, references, payloads, variants) | `3dcg/usd-pipeline/SKILL.md` | `3dcg` | `usd-pipeline` | `lang:python`, `format:usd`, `pipeline:vfx` |
| 19 | FreeCAD scripting (headless `freecadcmd`, OCCT, workbenches) | `cad/freecad-scripting/SKILL.md` | `cad` | `freecad-scripting` | `lang:python`, `vendor:freecad`, `format:step` |

### ID 16 — OpenUSD pipeline

```yaml
id: 16
target_path: 3dcg/usd-pipeline/SKILL.md
domain: 3dcg
subdomain: usd-pipeline
facets:
  - lang:python
  - lang:cpp
  - format:usd
  - pipeline:vfx
  - pipeline:archviz
applies_when:
  any_of:
    - "task authors or composes USD scenes (`.usda`, `.usdc`, `.usdz`)"
    - "task uses references, payloads, variants, sublayers, or specialises"
    - "task ships an asset resolver, USD plugin, or USD-driven pipeline stage"
description: >
  Cross-DCC OpenUSD authoring: composition arcs (LIVRPS), kinds, schemas,
  asset resolvers (Ar 2.0), variants, and `usdz` packaging — including
  `usdchecker` and CI round-trip patterns.
new_files:
  - 3dcg/usd-pipeline/SKILL.md
update_files:
  - 3dcg/INDEX.md
```

### ID 19 — FreeCAD scripting

```yaml
id: 19
target_path: cad/freecad-scripting/SKILL.md
domain: cad
subdomain: freecad-scripting
facets:
  - lang:python
  - vendor:freecad
  - format:step
  - format:brep
applies_when:
  any_of:
    - "task automates FreeCAD via Python (`App`, `Part`, `PartDesign`, `Sketcher`)"
    - "task runs FreeCAD headlessly via `freecadcmd` for batch generation"
    - "task ships a FreeCAD workbench, macro, or CI-generated CAD asset"
description: >
  Open-source parametric CAD automation: spreadsheet-driven parameters,
  PartDesign feature trees, headless `freecadcmd` in CI, toponaming-aware
  authoring, and STEP round-trip validation.
new_files:
  - cad/freecad-scripting/SKILL.md
update_files:
  - cad/INDEX.md
```

---

## Cluster 8 — Generative-Model Specialisations

Skills covering LLM fine-tuning (PEFT + alignment) and diffusion model training/inference.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 17 | LLM fine-tuning (LoRA / QLoRA / DPO / ORPO) | `ml/llm-finetuning/SKILL.md` | `ml` | `llm-finetuning` | `lang:python`, `framework:huggingface`, `precision:int4` |
| 18 | Diffusion models (training, schedulers, ControlNet, distillation) | `ml/diffusion/SKILL.md` | `ml` | `diffusion` | `lang:python`, `framework:huggingface`, `precision:bf16` |

### ID 17 — LLM fine-tuning

```yaml
id: 17
target_path: ml/llm-finetuning/SKILL.md
domain: ml
subdomain: llm-finetuning
facets:
  - lang:python
  - framework:pytorch
  - framework:huggingface
  - target:gpu
  - precision:bf16
  - precision:int4
applies_when:
  any_of:
    - "task fine-tunes a pretrained LLM (full or PEFT)"
    - "task uses LoRA, QLoRA, or other parameter-efficient adapters"
    - "task aligns a model with DPO, ORPO, KTO, or RLHF"
    - "task curates an SFT or preference dataset for instruction tuning"
description: >
  PEFT (LoRA, QLoRA), instruction tuning, and preference optimisation
  (DPO/ORPO) for LLMs: chat-template discipline, loss masking, sequence
  packing, evaluation against task-specific + general benchmarks, adapter
  merging, and quantised serving.
new_files:
  - ml/llm-finetuning/SKILL.md
update_files:
  - ml/INDEX.md
```

### ID 18 — Diffusion models

```yaml
id: 18
target_path: ml/diffusion/SKILL.md
domain: ml
subdomain: diffusion
facets:
  - lang:python
  - framework:pytorch
  - framework:huggingface
  - target:gpu
  - precision:fp16
  - precision:bf16
applies_when:
  any_of:
    - "task trains, fine-tunes, or distils a diffusion model"
    - "task implements or tunes a sampler (DDIM, DPM-Solver, LCM, Turbo)"
    - "task adds ControlNet, IP-Adapter, T2I-Adapter, or LoRA to a diffusion pipeline"
    - "task optimises diffusion inference latency"
description: >
  Diffusion / flow-matching for image, video, and audio: schedulers,
  classifier-free guidance, ControlNet / IP-Adapter / LoRA, EMA, Min-SNR
  weighting, step distillation (LCM, Turbo, Hyper-SD), and inference perf.
new_files:
  - ml/diffusion/SKILL.md
update_files:
  - ml/INDEX.md
```

---

## Cluster 9 — Open-Source Game Engine

Skills covering Godot 4.x, the leading open-source competitor to Unity / Unreal.

| ID | Name | Target path | Domain | Subdomain | Key facets |
|----|------|-------------|--------|-----------|------------|
| 20 | Godot 4.x (GDScript / C# / GDExtension, scenes, multiplayer) | `gameengine/godot/SKILL.md` | `gameengine` | `godot` | `lang:gdscript`, `lang:csharp`, `vendor:godot` |

### ID 20 — Godot

```yaml
id: 20
target_path: gameengine/godot/SKILL.md
domain: gameengine
subdomain: godot
facets:
  - lang:gdscript
  - lang:csharp
  - lang:cpp
  - target:pc
  - target:mobile
  - target:web
  - vendor:godot
applies_when:
  any_of:
    - "task targets Godot 4.x"
    - "task involves GDScript, C# (Mono), or GDExtension scripting"
    - "task involves scenes, nodes, signals, groups, or autoloads"
    - "task uses Godot's high-level multiplayer API"
description: >
  Open-source real-time engine workflows on Godot 4.x: scene-tree composition,
  signal-driven architecture, custom resources, autoloads, server-authoritative
  multiplayer via the high-level API, GDExtension bindings, and headless CI
  exports.
new_files:
  - gameengine/godot/SKILL.md
update_files:
  - gameengine/INDEX.md
```

---

## Quick-reference table

| ID | Cluster | Subdomain | Target path |
|----|---------|-----------|-------------|
| 01 | 1 — Web Graphics | webgpu | `coding/webgpu/SKILL.md` |
| 02 | 1 — Web Graphics | 3dgs | `3dcg/3dgs/SKILL.md` |
| 03 | 1 — Web Graphics | shader-sim | `coding/shader-sim/SKILL.md` |
| 04 | 2 — AI/CAD | api-harness | `cad/api-harness/SKILL.md` |
| 05 | 2 — AI/CAD | topology-assembly | `cad/topology-assembly/SKILL.md` |
| 06 | 2 — AI/CAD | mapreduce-codegen | `coding/mapreduce-codegen/SKILL.md` |
| 07 | 3 — Digital Humans | motion-fm | `ml/motion-fm/SKILL.md` |
| 08 | 3 — Digital Humans | garment-sim | `3dcg/garment-sim/SKILL.md` |
| 09 | 4 — Secure Infra | spatial-transfer | `coding/spatial-transfer/SKILL.md` |
| 10 | 4 — Secure Infra | agent-sca | `coding/agent-sca/SKILL.md` |
| 11 | 5 — Embodied AI | synthetic-data | `gameengine/synthetic-data/SKILL.md` |
| 12 | 5 — Embodied AI | vlm-spatial | `ml/vlm-spatial/SKILL.md` |
| 13 | 6 — Service Foundations | api-design | `coding/api-design/SKILL.md` |
| 14 | 6 — Service Foundations | observability | `coding/observability/SKILL.md` |
| 15 | 6 — Service Foundations | databases | `coding/databases/SKILL.md` |
| 16 | 7 — Pipeline & OSS CAD/CG | usd-pipeline | `3dcg/usd-pipeline/SKILL.md` |
| 17 | 8 — Generative Models | llm-finetuning | `ml/llm-finetuning/SKILL.md` |
| 18 | 8 — Generative Models | diffusion | `ml/diffusion/SKILL.md` |
| 19 | 7 — Pipeline & OSS CAD/CG | freecad-scripting | `cad/freecad-scripting/SKILL.md` |
| 20 | 9 — OSS Game Engine | godot | `gameengine/godot/SKILL.md` |

## Scaffold commands (agent reference)

When the agent processes a `generate-skills` request it should, for each ID:

1. Read the entry block above to obtain `target_path`, `domain`, `subdomain`, `facets`, `applies_when`, `description`, `new_files`, and `update_files`.
2. For each path listed in `new_files`:
   - Create parent directories as needed.
   - Copy `_layout/SUBDOMAIN_SKILL.template.md` → target path.
   - Fill all `{{PLACEHOLDER}}` values from the catalog entry's fields.
3. For each path listed in `update_files`:
   - Append a new row to the subdomain decision table in the relevant `INDEX.md`.
4. If the `domain` folder does not yet have an `INDEX.md`, also copy `_layout/DOMAIN_INDEX.template.md` → `<domain>/INDEX.md` and fill its placeholders.
5. Verify: `facets` values must exist in the parent domain's facet vocabulary table; if missing, add them there first.
6. Emit a `[SKILL:generated]` lane event for each file created.
