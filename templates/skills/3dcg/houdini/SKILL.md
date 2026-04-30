---
name: 3dcg-houdini
description: "SideFX Houdini procedural workflows, VEX, HDAs, Solaris/USD, and Karma rendering. Triggers: houdini, hip, hda, vex, solaris, karma, sops, lops."
domain: 3dcg
subdomain: houdini
facets:
  # - lang:vex
  # - lang:python
  # - renderer:karma
  # - format:usd
applies_when:
  any_of:
    - "task uses SideFX Houdini (any modern major version)"
    - "task involves SOPs, LOPs (Solaris/USD), DOPs (simulations), or Karma rendering"
    - "task ships a Houdini Digital Asset (HDA)"
version: 0.1.0
---
# 3D CG / Houdini

## When to use

The task runs in Houdini, builds an HDA, or automates Houdini via `hou` / `hython`. For pure USD authoring without Houdini-specific nodes, prefer cross-DCC USD references in `_shared/canon.md`.

## Canon

- **Network contexts** — SOPs (geometry), DOPs (simulation), LOPs (Solaris/USD), CHOPs (channels), COPs (compositing). Patterns differ per context.
- **Attribute classes** — `point`, `vertex`, `prim`, `detail`. Promotion direction matters (gather vs scatter).
- **HDA** — Houdini Digital Asset; encapsulated, versioned subnetwork with a typed parameter interface.
- **Solaris / LOPs** — Houdini's USD-native context; never edit USD via Python in LOPs, use nodes.
- **`hython`** — headless Houdini Python interpreter for batch and CI.

## Recommended patterns

1. **Procedural by default.** Avoid baked geometry; expose parameters on HDAs.
2. **Wrap reusable graphs as HDAs** with semantic version bumps. Lock the definition before publishing.
3. **Use `hython` for CI**: cook a HIP, write an output, compare against a baseline.
4. **Solaris over Mantra/Karma direct** for any modern pipeline that touches USD downstream.
5. **Author attributes at the lowest necessary class** (point > prim > detail) to avoid unnecessary promotion.

## Pitfalls

- ❌ **Editing geometry in `Python SOP` when a `Wrangle` (VEX) suffices** — VEX is parallel and orders of magnitude faster.
- ❌ **Storing absolute paths in HIPs.** Use `$HIP`, `$JOB`, or HDA-relative paths.
- ❌ **Unbounded simulation substeps** — DOP networks can hang CI silently. Set hard caps.
- ❌ **Forgetting to lock HDAs before publishing** — downstream users overwrite the definition by accident.
- ❌ **Mixing Mantra and Karma render settings on the same camera** — color management diverges.

## Procedure

1. Identify the network context (SOP / LOP / DOP / …) and stay within it unless promotion is necessary.
2. For new procedural tools, prototype as a subnet, then promote to an HDA with a parameter interface.
3. Use VEX wrangles for per-element math; reserve Python for orchestration and tool UI.
4. For pipeline integration, write a `hython` driver that opens the HIP, sets parameters, cooks, exports.
5. Validate by rendering or exporting a deterministic frame and diffing against a checked-in baseline.

## Validation

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}     # hython tests/cook_baseline.py
```

## See also

- [`../_shared/canon.md`](../_shared/canon.md)
- SideFX docs: VEX language reference, Solaris/LOPs guide.
