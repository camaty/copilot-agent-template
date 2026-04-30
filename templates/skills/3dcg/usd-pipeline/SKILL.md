---
name: 3dcg-usd-pipeline
description: "Pixar USD authoring across DCC tools: layers, references, payloads, variants, kinds, and asset resolvers. Triggers: USD, OpenUSD, usda, usdc, usdz, layers, references, payloads, variants, sublayer, asset resolver, omniverse."
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
    - "task integrates Omniverse, Houdini Solaris, Maya USD, or Blender USD"
version: 0.1.0
---
# 3D CG / OpenUSD Pipeline

## When to use

Open this skill when the task authors USD directly, designs a USD-
based asset pipeline, or integrates DCC tools through USD layers.
For DCC-internal authoring without USD interchange, use
[`../blender/SKILL.md`](../blender/SKILL.md) or
[`../houdini/SKILL.md`](../houdini/SKILL.md). For runtime rendering
of USD via WebGPU, see [`../../coding/webgpu/SKILL.md`](../../coding/webgpu/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Stage** — composed view of one or more layers; what renderers
  and DCCs read.
- **Layer** — a single `.usda`/`.usdc` file; immutable to consumers,
  edited at authoring time.
- **Composition arcs** — sublayer, reference, payload, variant set,
  inherit, specialise. Each combines layers differently and follows
  *LIVRPS* strength order (Local, Inherits, Variants, References,
  Payloads, Specialises).
- **Reference** — embeds another layer's prims at a path; default
  prim is used if no path supplied.
- **Payload** — a deferred reference; lets DCCs unload heavy assets
  (geometry caches, sims). Use for anything > a few MB.
- **Variant set** — named choice between alternative opinions
  (`shadingVariant=Wood`, `geoVariant=LowRes`).
- **Kinds** — `assembly`, `group`, `component`, `subcomponent`.
  Tools navigate at the `component` level by convention.
- **Schema** — typed prim definitions (Xform, Mesh, Camera,
  UsdGeomScope, custom via `usdGenSchema`).
- **Asset resolver** — plug-in that maps asset paths
  (`@/asset/sphere.usd@`) to physical files; default is path-based,
  but Ar 2.0 supports versioned and async resolvers.
- **Strength ordering (LIVRPS)** — the recipe for "who wins" when
  multiple opinions touch the same property.
- **Time samples** — animation per attribute as `(time → value)`
  pairs; `timeCodesPerSecond` is per-stage metadata.
- **Material binding** — `material:binding` rel; bound in scope or
  per-instance.
- **`usdz`** — zero-compression zip of a USD asset for AR /
  Omniverse delivery.

## Recommended patterns

1. **One asset per file, one purpose per layer.** Geometry,
   materials, animation, and shot edits each in their own layer
   stacked via sublayers.
2. **Use references for asset reuse** within a single sequence;
   payloads for heavy caches; sublayers for shot-level edits.
3. **Pin asset versions** in references with explicit asset paths
   (`@./assets/chair_v003.usd@`); resolve via the asset resolver,
   not the OS.
4. **Define a `defaultPrim`** in every authored asset; otherwise
   downstream references must guess.
5. **Author kinds correctly** — `component` for the visible asset
   root, `assembly` only when grouping components. DCC navigation
   relies on this.
6. **Variants for art-direction switches**, not for runtime
   behaviour. Don't smuggle gameplay state into variants.
7. **Materials in their own layer** with `UsdPreviewSurface` plus
   render-specific (Karma, MaterialX, Arnold) shaders alongside;
   binding lives where assets compose.
8. **Stage-level metadata** (`upAxis`, `metersPerUnit`,
   `timeCodesPerSecond`) authored in a single root layer; never
   override per-shot.
9. **Use `usdchecker --strict`** in CI on every authored asset.
10. **Diff by composing** — `usddiff` composes both stages; a raw
    text diff misses LIVRPS effects.
11. **Asset resolver discipline** — choose Ar 2.0 + a versioning
    resolver early; retrofitting is painful.

## Pitfalls (subdomain-specific)

- ❌ **Reusing a prim path across components without `defaultPrim`.**
  References resolve to the wrong root.
- ❌ **Writing animation directly into the asset layer.** Mix-ins
  go in a shot/animation layer; never in the asset.
- ❌ **Strong opinion at the wrong level.** A property edited in
  the asset layer can't be overridden weakly downstream; use
  variants or shot edits.
- ❌ **Using payloads everywhere.** They lazy-load — if you always
  need them, references are simpler and cheaper.
- ❌ **Mismatched units.** Authoring in cm while a downstream
  expects metres yields scene 100× too small.
- ❌ **Forgetting `metersPerUnit`/`upAxis`.** USD doesn't pick
  defaults the way artists expect.
- ❌ **Custom schemas without `usdGenSchema`.** Hand-written
  schemas drift; round-trip with the codegen tool.
- ❌ **Editing `.usdc` (binary) by hand.** Use Python or a USD-
  aware DCC; `.usdc` is not a text format.
- ❌ **Variant sets containing references with conflicting opinions
  unaware of LIVRPS.** Result depends on arc order; document the
  intended winner.
- ❌ **Material bindings on a `Mesh` prim that lives inside a
  reference whose root is overridden.** The override clobbers
  the binding silently.
- ❌ **`usdz` with non-relative asset paths.** They break on every
  consumer; package-relative only.
- ❌ **One huge layer per shot.** Diff/merge is painful; split by
  department.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Decide the layer topology** — asset, look, shot, sequence.
   Document layer ownership per department.
2. **Set stage metadata** in a single root layer (`upAxis`,
   `metersPerUnit`, `timeCodesPerSecond`).
3. **Author assets** with `defaultPrim`, kind=component, and a
   stable internal hierarchy (`/Root/Geom`, `/Root/Materials`).
4. **Author materials** in a `look` layer; bind from the asset
   layer.
5. **Compose shots** by sublayering asset references plus a shot
   edit layer; use payloads for sim caches.
6. **Variants** for switchable looks (`UsdVariantSets.SetSelection`)
   selected by the consuming DCC or pipeline tool.
7. **Configure the asset resolver** (Ar 2.0 plugin) so paths like
   `@<asset>/<name>@<version>@` resolve deterministically.
8. **Validate** with `usdchecker --strict`; render a frame with
   Karma/Storm; diff against golden.
9. **Pack `usdz`** for delivery to AR / Omniverse runtimes.

## Validation

After completing the procedure, run:

```sh
# Lint authored USD
usdchecker --strict shot.usda
usdchecker --strict assets/**/*.usd*

# Composition diff against the previous version
usddiff prev/shot.usda shot.usda

# Round-trip via Houdini/Maya/Blender exporters in CI
hython tests/usd_roundtrip.py    # Solaris export → re-import → assert equality
blender -b --factory-startup -P tests/usd_blender_roundtrip.py

# Render smoke (storm or karma)
usdview --norender shot.usda      # opens cleanly
husk --renderer Karma --frame 1001 --output out.exr shot.usda

# Static checks for python tooling
ruff check pipeline/usd
mypy --ignore-missing-imports pipeline/usd
```

## See also

- [`../houdini/SKILL.md`](../houdini/SKILL.md) — Solaris/LOPs is
  the most common authoring environment.
- [`../blender/SKILL.md`](../blender/SKILL.md) — Blender USD I/O.
- [`../3dgs/SKILL.md`](../3dgs/SKILL.md) — splat assets in USD
  scenes (custom schema or pointInstancer).
- [`../garment-sim/SKILL.md`](../garment-sim/SKILL.md) — garment
  caches as USD geometry caches via payload.
- Pixar USD documentation — <https://openusd.org/release/>
- USD glossary & composition arcs — <https://openusd.org/release/glossary.html>
- NVIDIA Omniverse USD authoring guide.
