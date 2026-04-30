---
name: 3dcg-houdini
description: "SideFX Houdini procedural workflows, VEX, HDAs, Solaris/USD, Karma rendering, Vellum, FLIP, Pyro. Triggers: houdini, hip, hda, vex, solaris, lops, sops, dops, karma, vellum, flip, pyro, hython."
domain: 3dcg
subdomain: houdini
facets:
  - lang:vex
  - lang:python
  - renderer:karma
  - format:usd
  - format:alembic
  - pipeline:vfx
applies_when:
  any_of:
    - "task uses SideFX Houdini (any modern major version, 19.5+)"
    - "task involves SOPs, LOPs (Solaris/USD), DOPs (simulations), or Karma rendering"
    - "task ships a Houdini Digital Asset (HDA)"
    - "task automates Houdini headlessly via `hython`"
    - "task targets Vellum, FLIP, Pyro, or Bullet simulations"
version: 0.1.0
---
# 3D CG / Houdini

## When to use

Open this skill when the task runs in Houdini, builds an HDA, automates
Houdini via `hou`/`hython`, or authors USD via Solaris. For pure USD
authoring without Houdini-specific nodes, prefer cross-DCC USD
references in `_shared/canon.md` or the dedicated USD skill.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Network contexts** — SOPs (geometry), DOPs (simulation), LOPs
  (Solaris/USD), CHOPs (channels/animation), COPs (compositing),
  TOPs (task graph for distributed work). Patterns differ per
  context; rules don't transfer 1:1.
- **Attribute classes** — `point`, `vertex`, `prim`, `detail`.
  Promotion direction matters (gather vs scatter); always
  authoritatively author at the lowest sufficient class.
- **HDA (Houdini Digital Asset)** — encapsulated, versioned subnetwork
  with a typed parameter interface. The unit of reuse and
  collaboration in Houdini.
- **Solaris / LOPs** — Houdini's USD-native context. Edit USD via
  nodes, not Python; node operations produce diffable USD layers.
- **`hython`** — Houdini's Python interpreter, with `hou` module;
  used for batch cooking, CI, and pipeline scripting.
- **VEX** — Houdini's vector-expression language; SIMD, parallel
  per-element, orders of magnitude faster than equivalent Python.
- **PDG/TOPs** — task graph for fan-out work (renders, sims,
  exports) with caching and dependency tracking.
- **Vellum / FLIP / Pyro / Bullet** — DOP solvers for cloth/wires,
  liquids, smoke/fire, rigid bodies. Each has distinct substep,
  collision, and caching idioms.
- **Karma vs Mantra** — Karma is the modern USD-native renderer
  (XPU CPU+GPU); Mantra is legacy. Modern pipelines use Karma.
- **`$HIP`, `$JOB`, `$HFS`** — Houdini path variables. `$HIP` is the
  HIP file's directory; `$JOB` the project root. Always parameterise
  with these instead of absolute paths.

For terminology shared across the whole `3dcg` domain, see
[`../_shared/canon.md`](../_shared/canon.md) (when present).

## Recommended patterns

1. **Procedural by default.** Avoid baked geometry; expose every
   meaningful knob as an HDA parameter. The point of Houdini is
   re-cookability.
2. **Wrap reusable graphs as HDAs** with semantic version bumps. Lock
   the definition before publishing; downstream files reference by
   namespace + version.
3. **Use `hython` for CI** — open a HIP, set parameters, cook a ROP,
   write outputs, compare against a baseline. Catch regressions
   before artists do.
4. **Solaris over Mantra/Karma direct** for any modern pipeline that
   touches USD downstream; layer per shot, sequence, and global.
5. **Author attributes at the lowest necessary class** (point > prim
   > detail) to avoid unnecessary promotion and broken VEX.
6. **VEX for per-element math; Python for orchestration.** A VEX
   wrangle that processes 1M points is ~1000× faster than the
   equivalent Python SOP.
7. **PDG/TOPs for fan-out** — render farms, sim sweeps, asset
   conversion. Cache per node; reruns only redo dirty branches.
8. **Materialize sims to disk** with explicit cache nodes (Geometry
   ROP, USD Render ROP) before downstream consumers; never re-sim
   on demand.
9. **Parameter expressions over hard-coded values.** `ch("../knob")`,
   `chs()`, channel references survive HDA refactors.
10. **Solaris layer hygiene** — one shot/asset/lighting layer per
    purpose; never compose all edits into a single sublayer.

## Pitfalls (subdomain-specific)

- ❌ **Editing geometry in `Python SOP` when a `Wrangle` (VEX)
  suffices.** VEX is parallel and orders of magnitude faster.
- ❌ **Storing absolute paths in HIPs.** Use `$HIP`, `$JOB`, or
  HDA-relative paths. Hard-coded paths break on any other
  workstation.
- ❌ **Unbounded simulation substeps.** DOP networks can hang CI
  silently. Set hard caps and a wall-clock timeout in the ROP.
- ❌ **Forgetting to lock HDAs before publishing** — downstream
  users overwrite the definition by accident.
- ❌ **Mixing Mantra and Karma render settings on the same camera**
  — colour management, lens, and AOV semantics diverge.
- ❌ **Authoring Solaris geometry via Python `Sop Modify` outside
  LOPs.** Round-trip loses USD layer semantics; use the Edit node.
- ❌ **Caching to `$HIP/cache` and committing it.** Caches belong in
  external storage, indexed by content hash; commit only the HIP
  and the recipe.
- ❌ **Reading evaluated geometry from `node.geometry()` mid-cook.**
  Cook order is not user-controllable; chain via `Object Merge` or
  read in a child node.
- ❌ **Promoting attributes without considering interpolation.**
  `point→vertex` averages; `point→prim` picks first; surprising
  defaults corrupt UVs and normals.
- ❌ **Treating `For Each Loop` as cheap.** Block-style loops
  serialise; for parallel work use `Compile Block` or `Detail
  Wrangle` over points.

## Procedure

1. **Identify the network context** (SOP / LOP / DOP / TOP / …) and
   stay within it unless promotion is necessary.
2. **For new procedural tools**, prototype as a subnet, then promote
   to an HDA with a parameter interface. Lock & version before
   committing.
3. **Use VEX wrangles for per-element math**; reserve Python for
   orchestration, tool UI, and pipeline glue.
4. **For pipeline integration**, write a `hython` driver that opens
   the HIP, sets parameters, cooks a ROP, and exits with a non-zero
   code on failure.
5. **For sims**, define explicit substep counts, collision
   tolerances, and cache paths; render from cache, never live.
6. **For Solaris**, author every change as a sublayer; never inline
   into the main stage; reference assets by USD asset path.
7. **For renders**, use Karma + Husk for batch on the farm; verify
   per-AOV outputs against a checked-in golden image.
8. **Validate** by rendering a deterministic frame and diffing
   against a baseline.

## Validation

After completing the procedure, run:

```sh
# Lint scripts (tooling Python, not VEX)
ruff check pipeline/ tools/
black --check pipeline/ tools/

# Cook & render baseline frame
hython tests/cook_baseline.py
hython tests/render_baseline.py
python tests/diff_render.py output.exr tests/golden/baseline.exr

# HDA contract tests
hython tests/hda_contract.py    # verify parameter names, defaults, types

# USD round-trip (Solaris)
husk --renderer Karma --frame 1001 --output out.exr stage.usd
usdchecker --strict shot.usd        # USD validation
```

## See also

- [`../blender/SKILL.md`](../blender/SKILL.md) — for upstream/
  downstream interop with Blender content.
- [`../3dgs/SKILL.md`](../3dgs/SKILL.md) — splat consumption.
- [`../garment-sim/SKILL.md`](../garment-sim/SKILL.md) — Vellum
  cloth for production-grade garment work.
- [`../usd-pipeline/SKILL.md`](../usd-pipeline/SKILL.md) — broader
  USD authoring patterns.
- SideFX docs: VEX language reference, Solaris/LOPs guide, PDG/TOPs.
- Pixar USD documentation — composition arcs, layers, references.
