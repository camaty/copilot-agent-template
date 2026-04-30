---
name: 3dcg-3dgs
description: "3D Gaussian Splatting browser viewer, FSR super-resolution, and splat-mesh compositing. Triggers: 3dgs, gaussian splatting, splat, .splat, .ply, FSR, super-resolution, tile streaming."
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
version: 0.1.0
---
# 3D CG / 3DGS

## When to use

The task streams or renders a 3D Gaussian Splatting scene in a browser, applies FSR-based super-resolution to a 3DGS viewport, composites splat data with rasterised mesh geometry, or edits/filters Gaussian attributes (position, opacity, SH coefficients) at runtime.

If the task does not match the activation hints, return to [`../INDEX.md`](../INDEX.md) and pick another subdomain.

## Canon (must-know terms and invariants)

- **3DGS (3D Gaussian Splatting)** — Represents a scene as a set of anisotropic 3D Gaussians, each with position, covariance, opacity, and spherical-harmonic colour coefficients. Rendered by projecting Gaussians onto the 2D image plane and alpha-compositing them back-to-front.
- **Splat sort** — Gaussians must be depth-sorted (back-to-front) every frame for correct alpha compositing. GPU radix sort is the standard approach; CPU sort is only viable for small scenes.
- **`.splat` format** — Packed binary stream of 32 bytes per Gaussian (position `f32×3`, scale `f32×3`, colour `u8×4`, rotation quaternion `u8×4`). The lossless equivalent is `.ply` with named per-element properties.
- **FSR (AMD FidelityFX Super Resolution)** — Spatial upscaler that reconstructs a high-resolution frame from a lower-resolution render; applied as a post-process compute pass after the splat composite, before display.
- **Tile-based streaming** — Large scenes are partitioned into spatial tiles; tiles are fetched on demand as the camera moves, allowing progressive rendering without an upfront full-file download.

For terminology shared across the whole `3dcg` domain, see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **GPU radix sort each frame** — Run a WebGPU compute pass that depth-sorts splat indices before the render pass. Never sort on the CPU for scenes with more than ~50k Gaussians.
2. **Tile-based incremental streaming** — Partition the `.splat` file into spatial tiles; maintain a camera-distance priority queue and issue `fetch()` requests sorted by proximity. Decode tile headers to locate byte ranges.
3. **Shared depth buffer for compositing** — Render the splat scene to an off-screen texture; composite over rasterised geometry using the same depth buffer so splats occlude correctly behind meshes.
4. **FSR post-process at 0.67× internal resolution** — Render splats at a reduced resolution, then dispatch a WGSL FSR 2 compute pass to upsample to display resolution. Always feed linear (non-sRGB) input to FSR.
5. **Per-Gaussian compute editing** — Filter or transform Gaussian attributes (position, opacity, SH bands) inside a compute shader before the sort pass, avoiding round-trips to the CPU.

## Pitfalls (subdomain-specific)

- ❌ **Skipping the depth-sort pass** — Gaussians rendered without back-to-front order produce severe transparency artefacts that worsen with camera movement.
- ❌ **Loading the entire `.splat` file before rendering** — Blocks the main thread and delays time-to-first-pixel; always stream progressively and begin rendering as tiles arrive.
- ❌ **Assuming a fixed coordinate system** — `.splat` files use right-handed Y-up or Z-up convention depending on the exporter. Normalise axes on load, not at render time.
- ❌ **Passing an sRGB framebuffer to FSR** — FSR requires a linear input; apply gamma correction or an sRGB→linear conversion only after the FSR pass.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. Parse the `.splat` or `.ply` header to determine per-Gaussian attribute layout (byte offsets, types) and total Gaussian count.
2. Upload the Gaussian attribute buffer to a `GPUBuffer` (`STORAGE | COPY_DST`); allocate a parallel index buffer for the sort pass.
3. Each frame, run the GPU radix sort compute pipeline to produce a depth-sorted index buffer based on the current view projection.
4. Execute the splat render pipeline: project each Gaussian to a screen-space 2D ellipse, write colour + alpha to an off-screen render target using additive or alpha-over blending.
5. Composite the splat texture over the rasterised scene, using the shared depth buffer to handle occlusion by opaque meshes.
6. If FSR is enabled, dispatch the FSR compute pass on the low-resolution splat output before presentation to the swap chain.
7. For tile streaming, maintain a sorted fetch queue; on each tile arrival, append Gaussian data to the GPU buffer and re-run the sort pass for the expanded dataset.

If this skill includes bundled scripts or starter files (siblings of this `SKILL.md`), prefer those local assets over inline commands.

## Validation

After completing the procedure, run:

```sh
npx tsc --noEmit          # type-check TypeScript sources
npx eslint src/           # lint
npx vitest run            # unit tests for splat parser and sort utilities
```

## See also

- [`blender/SKILL.md`](../blender/SKILL.md) — exporting scenes as `.ply` from Blender for use as splat source data
- Kerbl et al. (2023): "3D Gaussian Splatting for Real-Time Radiance Field Rendering" — original paper
- AMD FidelityFX Super Resolution 2 — <https://gpuopen.com/fidelityfx-superresolution-2/>
- WebGPU spec — <https://www.w3.org/TR/webgpu/>
