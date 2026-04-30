---
name: coding-shader-sim
description: "Shader-resident volumetric simulation (blast waves, fluids, smoke) in GLSL/WGSL. Triggers: shader simulation, volumetric, blast wave, fluid shader, smoke shader, Taylor-Sedov, GLSL physics, WGSL compute, GPU simulation."
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
version: 0.1.0
---
# Coding / Shader-Sim

## When to use

Open this skill when the physical simulation itself runs entirely on the GPU — encoded in GLSL fragment/compute shaders or WGSL compute shaders — with no CPU-side physics loop. Common cases: real-time blast waves (Taylor–Sedov), smoke advection, Navier–Stokes fluid, or reaction-diffusion effects.

If the simulation is computed on the CPU and only *rendered* by a shader, prefer the parent domain canon and skip this skill. If the task also writes a WebGPU render pipeline to display the simulation, pair this skill with [`../webgpu/SKILL.md`](../webgpu/SKILL.md).

If the task does not match the activation hints above, return to [`../INDEX.md`](../INDEX.md) and pick another subdomain.

## Canon (must-know terms and invariants)

- **Ping-pong (double-buffering)** — using two textures or storage buffers alternately as read-source and write-target across simulation steps; mandatory because GPUs forbid reading and writing the same resource in one pass.
- **Time-step (Δt) parameterisation** — the simulation's physical time advance per frame; must be kept ≤ the CFL stability limit (Δt ≤ Δx / c_max) to avoid numerical blow-up.
- **CFL condition** — Courant–Friedrichs–Lewy stability criterion; the wave or advection signal must not travel more than one grid cell per time-step.
- **Boundary conditions** — rules applied at the grid edge: Dirichlet (fixed value), Neumann (zero gradient / reflective), or absorbing (sponge layer).
- **Splat / kernel** — a weight function (Gaussian, cubic spline) used when scattering or gathering particle contributions onto a grid.
- **Volumetric ray-march** — per-pixel integration of a 3-D scalar field (density, temperature) along a view ray to produce a 2-D image.

For terminology shared across the whole `coding` domain, see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Ping-pong texture pairs** — allocate two same-format textures (or storage buffers) at simulation startup; each step reads from buffer A and writes to buffer B, then swap. Never read and write the same binding in one dispatch.
2. **Fixed Δt with sub-stepping** — choose Δt to satisfy the CFL condition at maximum expected velocity; if the frame time is larger than Δt, run multiple sub-steps per frame rather than increasing Δt.
3. **Sponge / absorbing boundary layers** — surround the domain with a zone where fields are damped toward ambient values each step; prevents wave reflections from the grid edge without complex absorbing-boundary PML math.
4. **Float16 storage for density/temperature fields** — halves bandwidth vs float32 and is sufficient for visual fidelity; reserve float32 for pressure and velocity where precision matters.
5. **Separate advection and pressure-projection passes** — split Navier–Stokes into (a) semi-Lagrangian advection pass, (b) divergence computation, (c) iterative Jacobi/red-black pressure solve, (d) velocity correction. Each pass maps cleanly to one compute dispatch or fragment draw.
6. **Mip-mapped density lookup for ray-marching** — build a mip chain of the 3-D density texture; skip empty macro-cells early in the ray-march using lower mip levels (empty-space skipping).

## Pitfalls (subdomain-specific)

- ❌ **Reading and writing the same texture in one pass.** Always use a second ping-pong buffer; undefined behaviour otherwise.
- ❌ **Δt too large for grid resolution.** Violating the CFL condition causes exponential amplitude blow-up within a few frames.
- ❌ **Forgetting to reset boundary texels every step.** Boundary values accumulate error if not re-enforced each pass.
- ❌ **Using `gl_FragCoord.xy` as integer grid indices without `floor()`.** Sub-pixel offsets cause one-texel shifts in the stencil neighbourhood.
- ❌ **Unbounded Jacobi iterations.** Cap at 20–40 iterations per frame; the pressure solve converges visually long before mathematical convergence.
- ❌ **Storing velocity in RGB8 or unorm formats.** Velocity is signed and exceeds [0,1]; use `RG16F` / `RGBA16F` or `R32F` storage textures.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Define the grid.** Choose a 2-D or 3-D resolution (e.g. 256×256×128) and create two sets of storage textures (ping / pong) for each physical field: velocity, density, temperature, pressure.
2. **Implement the advection pass.** Write a compute shader that reads velocity at each cell, traces a backward semi-Lagrangian path (position − Δt·v), and samples the previous density/temperature field bilinearly at that position.
3. **Implement the divergence and pressure-projection passes.** Compute divergence of the advected velocity field, then run 20–40 Jacobi iterations to solve the Poisson pressure equation, then subtract the pressure gradient from velocity to enforce incompressibility (or the appropriate compressibility model for blast waves).
4. **Enforce boundary conditions.** After each pass, clamp or set field values at grid edges according to the chosen boundary type (reflective, sponge, or open).
5. **Swap ping-pong buffers.** After all passes complete, swap the read/write texture pair for the next frame.
6. **Implement the visualisation pass.** Ray-march the density/temperature field (fragment shader or separate compute pass), apply transfer-function colour mapping (e.g. hot emission, scattering), and write to the output render target.
7. **Tune Δt and sub-step count.** Start with Δt = 0.016 s / max-expected-speed, then increase sub-steps if the simulation is visually unstable.

If this skill includes bundled scripts or starter files (siblings of this `SKILL.md`), prefer those local assets over inline commands.

## Validation

After completing the procedure, run:

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
# Verify no NaN/Inf in simulation output: inspect the density texture with a GPU debugger (RenderDoc, Xcode GPU Frame Capture) after 100 steps.
# Confirm ping-pong swap: pause at frame 2 and check that read/write bindings are inverted vs frame 1.
```

## See also

- [`../webgpu/SKILL.md`](../webgpu/SKILL.md) — WebGPU compute pipelines and WGSL authoring patterns; pair with this skill when deploying to the browser via the WebGPU API.
- [The Book of Shaders](https://thebookofshaders.com/) — foundational GLSL patterns.
- Stam, J. (1999). *Stable Fluids.* SIGGRAPH — canonical reference for semi-Lagrangian advection and pressure projection.
- [WebGPU spec §Compute pipelines](https://www.w3.org/TR/webgpu/#compute-pipelines) — storage texture binding rules relevant to ping-pong.
