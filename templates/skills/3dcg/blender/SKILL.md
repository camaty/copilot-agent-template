---
name: 3dcg-blender
description: "Blender modeling, geometry nodes, Python add-ons, and Cycles/EEVEE rendering. Triggers: blender, bpy, geometry nodes, cycles, eevee, .blend."
domain: 3dcg
subdomain: blender
facets:
  # - lang:python
  # - renderer:cycles
  # - renderer:eevee
  # - format:usd
applies_when:
  any_of:
    - "task targets Blender 3.x or 4.x"
    - "task involves `bpy`, geometry nodes, or Blender add-on packaging"
    - "task involves Cycles or EEVEE materials and rendering"
version: 0.1.0
---
# 3D CG / Blender

## When to use

The task runs inside Blender, automates Blender via `bpy`, or ships a Blender add-on. For asset interchange (USD/FBX/glTF) only, the parent canon may be sufficient.

## Canon

- **Operator vs function** — `bpy.ops.*` requires a valid context; prefer low-level `bpy.data.*` mutations from scripts.
- **Depsgraph** — Blender's dependency graph; evaluated objects live in `depsgraph.objects`, not `bpy.data.objects`.
- **Linear vs sRGB** — Blender works in linear; image textures are color-managed on import.
- **Geometry Nodes domains** — `POINT`, `EDGE`, `FACE`, `CORNER`, `CURVE`, `INSTANCE`. Attribute transfers must respect the source domain.

## Recommended patterns

1. **Drive automation through `bpy.data` and direct property assignment**, not `bpy.ops`, when running headless.
2. **Run headless with `blender -b -P script.py`** for reproducible builds. Add `--factory-startup` to ignore user prefs.
3. **Use Geometry Nodes for procedural assets** before reaching for Python-driven mesh editing.
4. **Pin the Blender version** in CI (`blender --version` check) — APIs change between minor releases.
5. **Package add-ons as a folder + `__init__.py`** with `bl_info`; ship a zip in releases.

## Pitfalls

- ❌ **`bpy.ops.*` from the command line** without an active context — silently fails or crashes.
- ❌ **Editing meshes while in Edit Mode from Python** — must toggle to Object Mode for `mesh.update()`.
- ❌ **Forgetting `--factory-startup`** in CI — user preferences leak in.
- ❌ **Saving over the source `.blend`** during automation. Always write to a separate output path.
- ❌ **Color space confusion on textures** — non-color data (normal, roughness) must be marked `Non-Color`.

## Procedure

1. Confirm Blender major.minor version targeted; pin in tooling.
2. Prefer `bpy.data` reads/writes; use `bpy.ops` only when no equivalent low-level API exists.
3. For add-ons, scaffold with `bl_info`, register/unregister hooks, and a `tests/` folder run via `blender -b -P`.
4. For renders, set the renderer, samples, color management, and output format explicitly — never rely on user defaults.
5. Validate in CI by rendering a single low-res frame and diffing pixels against a baseline.

## Validation

```sh
{{LINT_COMMAND}}      # e.g. ruff for the add-on Python sources
{{BUILD_COMMAND}}     # e.g. zip -r addon.zip <addon>/
{{TEST_COMMAND}}      # blender -b --factory-startup -P tests/run.py
```

## See also

- [`../_shared/canon.md`](../_shared/canon.md)
- Blender Python API reference (versioned)
