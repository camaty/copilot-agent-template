---
name: coding-webgpu
description: "Multi-pass WebGPU render/compute pipeline authoring in TSL/WGSL. Triggers: WebGPU, GPUDevice, GPUCommandEncoder, GPUBuffer, TSL, WGSL, shader, compute pipeline, render pipeline, browser GPU."
domain: coding
subdomain: webgpu
facets:
  - lang:wgsl
  - lang:typescript
  - target:browser
applies_when:
  any_of:
    - "task involves WebGPU compute pipelines or render pipelines"
    - "task uses GPUDevice, GPUCommandEncoder, or GPUBuffer directly"
    - "task writes TSL (Three Shading Language) or WGSL shaders"
    - "task targets high-performance GPU compute in a browser"
version: 0.1.0
---
# Coding / WebGPU

## When to use

Use this skill when the task requires authoring or debugging WebGPU pipelines in the browser — including multi-pass render pipelines, compute dispatches, TSL/WGSL shader code, GPU buffer management, or feature-detection for fallback paths. If the task is purely about CPU-side TypeScript logic or a non-GPU rendering API, return to [`../INDEX.md`](../INDEX.md) and pick another subdomain.

## Canon (must-know terms and invariants)

- **GPUDevice** — The root GPU context obtained via `adapter.requestDevice()`; all GPU resources are created from it and become invalid if the device is lost. Always register a `device.lost` handler.
- **GPUCommandEncoder** — Records GPU commands (render passes, compute passes, copies) into a `GPUCommandBuffer`. It is single-use: call `.finish()` exactly once, then submit. Never hold an encoder across async boundaries.
- **GPUBindGroup / GPUBindGroupLayout** — A bind group bundles resources (buffers, textures, samplers) that a shader accesses together. Layouts must match the pipeline's `GPUPipelineLayout`; mismatches cause silent draw-call drops on some drivers.
- **WGSL** — WebGPU Shading Language; the only first-class shader language in the WebGPU spec. Compiled from strings at pipeline-creation time; errors surface as `GPUCompilationInfo` messages.
- **TSL** — Three.js Shading Language; a TypeScript DSL that compiles to WGSL (or GLSL for WebGL fallback). Prefer TSL when the project already uses Three.js r167+.
- **Pipeline layout** — An explicit `GPUPipelineLayout` derived from `GPUBindGroupLayout` descriptors. Prefer explicit layouts over `'auto'`; `'auto'` creates a per-pipeline-unique layout that blocks bind-group reuse across pipelines.

For terminology shared across the whole `coding` domain, see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Feature-detect before entering the WebGPU path** — Check `navigator.gpu` at startup; if absent or `requestAdapter()` returns `null`, fall back to WebGL or inform the user. Gate all WebGPU imports behind this check to avoid bundle bloat on unsupported browsers.
2. **Hoist pipeline and shader creation to init** — `device.createShaderModule()` and `device.createRenderPipeline()` / `device.createComputePipeline()` are expensive. Call them once at startup; in the render loop only record commands and submit.
3. **Use explicit pipeline layouts when sharing bind groups** — Declare `GPUBindGroupLayout` objects once, derive a shared `GPUPipelineLayout` from them, and reuse the same bind groups across multiple pipelines. This eliminates redundant resource rebinding and enables the driver to cache pipeline state.
4. **Align and pad uniform structs to 16-byte boundaries** — Every struct member in a WGSL uniform must be aligned to its element size, and the struct itself must be padded to a multiple of 16 bytes. Use `@align` attributes explicitly; rely on `offsetof`-style calculations in TypeScript to verify layout before uploading data.
5. **Pool and reuse GPU buffers; avoid `mapAsync` in the hot path** — `mapAsync` stalls the GPU timeline. Use staging (upload/readback) buffers that are mapped once and kept alive, or double-buffer to pipeline CPU writes with GPU reads.

## Pitfalls (subdomain-specific)

- ❌ **Using `'auto'` pipeline layout when sharing resources between pipelines** — `'auto'` generates a fresh, non-interoperable layout per pipeline; bind groups from one pipeline cannot be passed to another. Always use explicit layouts for any shared resource.
- ❌ **Calling `device.createShaderModule()` or `createRenderPipeline()` inside the render loop** — Shader compilation triggers GPU-driver JIT; doing it per-frame causes severe frame drops. Hoist to init and cache the result.
- ❌ **Failing to handle `device.lost`** — The GPU context can be lost (driver crash, tab backgrounding on mobile, power state change). Without a `device.lost.then(recover)` handler the app silently stops rendering.
- ❌ **Submitting a mapped buffer as a binding** — A `GPUBuffer` cannot be simultaneously mapped (CPU-accessible) and used as a shader binding. Always call `.unmap()` before recording commands that read the buffer.
- ❌ **Ignoring WGSL compilation errors** — `createShaderModule()` does not throw; check `module.getCompilationInfo()` (async) and surface any errors before creating pipelines that depend on the module.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Detect support** — `if (!navigator.gpu) throw new Error('WebGPU not supported');`
2. **Acquire adapter and device**:
   ```ts
   const adapter = await navigator.gpu.requestAdapter({ powerPreference: 'high-performance' });
   if (!adapter) throw new Error('No GPU adapter found');
   const device = await adapter.requestDevice();
   device.lost.then(info => console.error('GPU device lost:', info.message));
   ```
3. **Configure the canvas context**:
   ```ts
   const ctx = canvas.getContext('webgpu') as GPUCanvasContext;
   ctx.configure({ device, format: navigator.gpu.getPreferredCanvasFormat(), alphaMode: 'premultiplied' });
   ```
4. **Author shaders** — write WGSL source or use TSL node graph. For raw WGSL:
   ```ts
   const module = device.createShaderModule({ code: wgslSource });
   const info = await module.getCompilationInfo();
   if (info.messages.some(m => m.type === 'error')) throw new Error('Shader compile error');
   ```
5. **Create bind group layouts, pipeline layout, and pipeline** (once, at init):
   ```ts
   const bgl = device.createBindGroupLayout({ entries: [...] });
   const layout = device.createPipelineLayout({ bindGroupLayouts: [bgl] });
   const pipeline = device.createRenderPipeline({ layout, vertex: { module, entryPoint: 'vs' }, fragment: { module, entryPoint: 'fs', targets: [{ format }] }, primitive: { topology: 'triangle-list' } });
   ```
6. **Create bind groups** (once per resource set):
   ```ts
   const bindGroup = device.createBindGroup({ layout: bgl, entries: [{ binding: 0, resource: { buffer: uniformBuffer } }] });
   ```
7. **Per-frame render loop**:
   ```ts
   const encoder = device.createCommandEncoder();
   const pass = encoder.beginRenderPass({ colorAttachments: [{ view: ctx.getCurrentTexture().createView(), loadOp: 'clear', storeOp: 'store', clearValue: [0, 0, 0, 1] }] });
   pass.setPipeline(pipeline);
   pass.setBindGroup(0, bindGroup);
   pass.draw(vertexCount);
   pass.end();
   device.queue.submit([encoder.finish()]);
   ```
8. **For compute passes**, replace `beginRenderPass` with `beginComputePass`, set the compute pipeline, call `pass.dispatchWorkgroups(x, y, z)`, then `pass.end()`.

## Validation

After completing the procedure, run:

```sh
npx tsc --noEmit
npx eslint src --ext .ts
npx vitest run
```

If the project uses a custom build tool, substitute the equivalent lint, type-check, and test commands.

## See also

- [`../shader-sim/SKILL.md`](../shader-sim/SKILL.md) — shader-resident volumetric simulation that builds on WebGPU compute pipelines
- [WebGPU Explainer (W3C)](https://gpuweb.github.io/gpuweb/explainer/)
- [WGSL Specification](https://www.w3.org/TR/WGSL/)
- [Three.js TSL documentation](https://threejs.org/docs/#api/en/renderers/common/nodes/NodeMaterial)
