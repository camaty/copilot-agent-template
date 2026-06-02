---
name: 3dcg-blender
description: "Blender modeling, geometry nodes, Python add-ons, and Cycles/EEVEE rendering. Triggers: blender, bpy, geometry nodes, cycles, eevee, .blend, blender add-on, blender headless, asset browser."
domain: 3dcg
subdomain: blender
facets:
  - lang:python
  - renderer:cycles
  - renderer:eevee
  - format:usd
  - format:gltf
  - format:fbx
applies_when:
  any_of:
    - "task targets Blender 3.x or 4.x"
    - "task involves `bpy`, geometry nodes, or Blender add-on packaging"
    - "task involves Cycles or EEVEE materials and rendering"
    - "task automates Blender headlessly via `blender -b -P`"
    - "task ships content via the Blender Asset Browser"
version: 0.1.0
---
# 3D CG / Blender

## When to use

Open this skill when the task runs inside Blender, automates Blender via
`bpy`/`hython`, ships a Blender add-on, or renders frames via Cycles or
EEVEE. For asset interchange (USD/FBX/glTF) only, the parent canon may
be sufficient.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Operator vs function** — `bpy.ops.*` requires a valid context
  (active scene, selection, mode). Prefer low-level `bpy.data.*`
  mutations from headless scripts.
- **Depsgraph** — Blender's dependency graph; *evaluated* objects
  live in `depsgraph.objects`, not `bpy.data.objects`. Reading
  modifier results requires the evaluated copy.
- **Linear vs sRGB** — Blender works in linear scene-referred light;
  image textures are color-managed on import (sRGB by default,
  Non-Color for normal/roughness).
- **Geometry Nodes domains** — `POINT`, `EDGE`, `FACE`, `CORNER`,
  `CURVE`, `INSTANCE`. Attribute transfers must respect the source
  domain or values silently corrupt.
- **Collections vs scenes** — collections group objects within a
  scene; scenes are independent timelines and render settings.
  Linked overrides are the modern pipeline primitive.
- **Library override** — modern asset reuse mechanism (Blender 3.x+)
  replacing legacy proxy. Edits cascade safely across files.
- **Cycles vs EEVEE** — Cycles is path-traced, physically based, slow
  but accurate. EEVEE is rasterised, fast, approximate; PBR shaders
  largely portable but light/shadow behavior differs.
- **bl_info** — Add-on metadata block at the top of `__init__.py`;
  required for installation and version pinning.
- **Headless invocation** — `blender -b file.blend -P script.py
  --factory-startup` for reproducible CI; user prefs do not leak.

## Recommended patterns

1. **Drive automation through `bpy.data` and direct property
   assignment**, not `bpy.ops`, when running headless. `bpy.ops`
   silently no-ops on missing context.
2. **Run headless with `blender -b -P script.py --factory-startup`**
   for reproducible builds. Add `--python-exit-code 1` so script
   errors fail the CI run.
3. **Use Geometry Nodes for procedural assets** before reaching for
   Python-driven mesh editing — better perf, depsgraph-aware,
   editable by artists.
4. **Pin the Blender version** in CI and add-on `bl_info`. APIs change
   between minor releases; `bpy.app.version` checks belong at module
   import time.
5. **Package add-ons as a folder + `__init__.py`** with `bl_info`,
   `register()`, and `unregister()`. Ship a zip in releases.
6. **Author materials as Principled BSDF** for portability across
   Cycles, EEVEE, glTF, USD. Custom node groups break round-trip.
7. **Use library overrides for asset linking** — collection-level
   linking with overrides survives source edits cleanly.
8. **Bundle resources via the Asset Browser** with proper catalog
   metadata; consumers drag-and-drop without path surgery.
9. **Color-manage explicitly** — declare view transform (Filmic,
   AgX in 4.0+) and color space per texture; never rely on default.
10. **Render with explicit settings, not user defaults** — sample
    counts, color management, output format, file paths all set in
    code or scene template.

## Pitfalls (subdomain-specific)

- ❌ **`bpy.ops.*` from the command line** without an active context
  — silently fails or crashes the kernel. Switch to `bpy.data` API.
- ❌ **Editing meshes while in Edit Mode from Python** — must toggle
  to Object Mode for `mesh.update()`, or use BMesh API correctly
  (`bm.from_edit_mesh` then `bm.to_mesh`).
- ❌ **Forgetting `--factory-startup`** in CI — user preferences,
  startup file, and addon state leak in non-deterministically.
- ❌ **Saving over the source `.blend`** during automation. Always
  write to a separate output path; use `bpy.ops.wm.save_as_mainfile`
  with `copy=True` if the source must be preserved.
- ❌ **Color-space confusion on textures** — non-color data (normal,
  roughness, displacement) must be marked `Non-Color`; otherwise
  the sRGB curve corrupts values.
- ❌ **Reading `bpy.data.objects[x].matrix_world`** when modifiers
  changed it — read from `depsgraph.id_eval_get(obj)` instead.
- ❌ **Hard-coding Python paths in add-ons.** Use `__file__` +
  `os.path.dirname` or `bpy.utils.user_resource()`.
- ❌ **Mixing EEVEE-only nodes (e.g. SSR controls) into materials
  shipped to Cycles users.** Wrap in `if context.scene.render.engine`.
- ❌ **Running Cycles renders without `bpy.context.scene.render
  .threads = N`** in CI — defaults to all cores, starves the runner.
- ❌ **Shipping `.blend` files from a different major version**
  without re-saving — backwards compat is best-effort, not
  guaranteed.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md)
and (when present) [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Confirm Blender major.minor version targeted** and pin in
   `bl_info` and CI. `bpy.app.version` guard at import time.
2. **Plan headless vs interactive** — headless implies `bpy.data`
   API and `--factory-startup`; interactive can use operators.
3. **Prefer `bpy.data` reads/writes**; reach for `bpy.ops` only when
   no equivalent low-level API exists (some modifiers, baking).
4. **For add-ons:** scaffold with `bl_info`, `register/unregister`
   hooks, and a `tests/` folder runnable via
   `blender -b --factory-startup -P tests/run.py`.
5. **For renders:** set the renderer, samples, denoiser, color
   management view transform, and output format explicitly. Use
   the compositor for color grades to keep raw data linear.
6. **For procedural assets:** prefer Geometry Nodes; expose
   parameters on the modifier; provide an Asset Browser entry.
7. **For interchange:** export glTF for real-time, USD for
   pipelines, FBX only when the consumer requires it. Always re-
   import the export and diff bbox + vertex counts in CI.
8. **Validate** by rendering a single low-res frame and diffing
   pixels (PSNR > 40 dB) against a checked-in baseline.

## Validation

After completing the procedure, run:

```sh
# Lint / format add-on Python
ruff check addon/
black --check addon/

# Static type check (best-effort; bpy stubs are partial)
mypy --ignore-missing-imports addon/

# Package the add-on
( cd addon && zip -r ../my_addon.zip . -x '*__pycache__*' )

# Headless smoke test in the pinned Blender version
blender -b --factory-startup --python-exit-code 1 \
        -P tests/smoke.py
blender -b --factory-startup --python-exit-code 1 \
        tests/fixtures/scene.blend -P tests/render_baseline.py
python tests/diff_render.py output.png tests/golden/baseline.png

# Geometry interchange round-trip (glTF / USD)
blender -b --factory-startup -P tests/export_roundtrip.py
```

## See also

- [`../houdini/SKILL.md`](../houdini/SKILL.md) — high-end procedural
  authoring and FX simulations.
- [`../usd-pipeline/SKILL.md`](../usd-pipeline/SKILL.md) — when
  Blender is one stage in a larger USD pipeline.
  modifier for in-DCC iteration.
- Blender Python API reference (versioned) — <https://docs.blender.org/api/>
- Blender Asset Browser docs — <https://docs.blender.org/manual/en/latest/files/asset_libraries/index.html>
