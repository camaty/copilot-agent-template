---
domain: 3dcg
version: 0.1.0
---
# 3D CG — Domain Index

> Offline 3D computer graphics: modeling, sculpting, look-development, simulation, rendering, and DCC tool automation. For real-time engines (Unity, Unreal), use the [`gameengine`](../gameengine/INDEX.md) domain instead.

## What this domain covers

Asset creation pipelines, scene assembly, materials/shaders for offline rendering, simulations (FX, fluids, cloth), rendering settings, and DCC tool scripting. Knowledge that depends on a specific DCC vendor lives in subdomains; cross-DCC concepts live in `_shared/`.

## Subdomain decision tree

| If the task involves… | Open this subdomain |
|---|---|
| Blender (modeling, geometry nodes, Python add-ons, EEVEE / Cycles) | [`blender/SKILL.md`](./blender/SKILL.md) |
| Houdini (procedural, VEX, HDAs, Solaris/USD, Karma, simulations) | [`houdini/SKILL.md`](./houdini/SKILL.md) |
| 3D Gaussian Splatting viewer, FSR super-resolution, splat streaming or compositing | [`3dgs/SKILL.md`](./3dgs/SKILL.md) |
| 2D-to-3D garment generation and physics-based cloth on parametric avatars (SMPL/VRM) | [`garment-sim/SKILL.md`](./garment-sim/SKILL.md) |
| Authoring or composing OpenUSD scenes (layers, references, payloads, variants, kinds, asset resolvers) | [`usd-pipeline/SKILL.md`](./usd-pipeline/SKILL.md) |
| Maya, 3ds Max, Cinema 4D, Modo, ZBrush, Substance | _add a new subdomain — see [`../EXTENDING.md`](../EXTENDING.md)_ |

## Facet vocabulary

| Axis | Allowed values |
|---|---|
| `lang:`     | `python`, `vex`, `mel`, `osl`, `hlsl`, `glsl`, `ts`, `wgsl` |
| `renderer:` | `cycles`, `eevee`, `karma`, `arnold`, `redshift`, `vray`, `renderman` |
| `format:`   | `usd`, `alembic`, `fbx`, `gltf`, `obj`, `splat`, `pcd` |
| `pipeline:` | `solo`, `studio`, `vfx`, `archviz`, `product`, `avatar` |
| `target:`   | `browser`, `avatar` |

## Shared resources

The `_shared/` folder is **not yet created** for this domain — add it when a third subdomain is introduced or when canon starts duplicating across siblings:

- `_shared/canon.md` — coordinate systems, units, color management, USD basics
- `_shared/pitfalls.md` — interchange and DCC-portability anti-patterns

See [`../coding/_shared/`](../coding/_shared/) for a reference layout.

## Related domains

- `gameengine` — real-time/runtime CG; shares assets via USD/glTF/FBX
- `cad` — when assets originate from mechanical CAD and need tessellation
- `ml` — for ML-driven workflows (denoising, super-resolution, generative)
