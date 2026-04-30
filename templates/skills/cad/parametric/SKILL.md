---
name: cad-parametric
description: "Feature-based parametric CAD modeling, assemblies, and drawings across major vendor tools. Triggers: CAD, parametric, sketch, feature, assembly, mate, STEP, drawing."
domain: cad
subdomain: parametric
facets:
  # - vendor:autodesk
  # - vendor:dassault
  # - vendor:onshape
  # - vendor:freecad
  # - lang:python
  # - lang:featurescript
  # - format:step
applies_when:
  any_of:
    - "task creates or edits parametric solid models with a feature history"
    - "task involves assemblies, mates/joints, or drawings"
    - "task targets Fusion 360, SolidWorks, Onshape, FreeCAD, NX, or Creo"
version: 0.1.0
---
# CAD / Parametric

## When to use

The task creates, edits, or automates parametric feature-based CAD. For pure tessellated / mesh work (3D printing post-export, visualization), prefer `3dcg` after the export step.

## Canon

- **Sketch → Feature → Body → Component → Assembly** — the canonical model hierarchy.
- **Fully constrained sketch** — every DoF removed. Under-constrained sketches break on edit.
- **Feature history (timeline)** — ordered list of operations; reorder is rarely safe.
- **Reference geometry** — datums, planes, axes used by features. Externally-referenced geometry creates parent/child fragility.
- **Mate / joint** — assembly constraints between components.
- **GD&T / MBD** — Geometric Dimensioning & Tolerancing; Model-Based Definition (annotations on the 3D model rather than a 2D drawing).

## Recommended patterns

1. **Fully constrain every sketch** before promoting to a feature.
2. **Drive parameters from a single source** (parameter table, configuration, or external file) instead of hard-coding dimensions.
3. **Author master sketches/skeletons** for top-down assembly design; downstream parts reference the skeleton, not each other.
4. **Use STEP AP242** for long-term archival and cross-vendor exchange; native formats for active editing.
5. **Version control models as native + STEP** — STEP is diff-friendlier (still poor, but better) and survives kernel changes.
6. **Automate via the vendor's official API** (Fusion API, SolidWorks API, Onshape FeatureScript / REST). Avoid screen scraping.

## Pitfalls

- ❌ **External references across files** without a skeleton — moving a part breaks dozens of downstream features.
- ❌ **Editing a feature mid-history without checking children** — silently invalidates downstream features.
- ❌ **Round-tripping through STL** for editable geometry — loses parametric data and exact surfaces.
- ❌ **Mixing units within an assembly** (mm vs in) — vendor handling varies; prefer a single unit system.
- ❌ **Storing tolerances only in the drawing** — MBD-aware downstream tools won't see them.
- ❌ **Committing binary CAD files without LFS** — repo size explodes; diffs are useless.

## Procedure

1. Confirm vendor + version; native files often break across major versions.
2. For new parts, plan the sketch hierarchy and parameter source before drawing.
3. For automation, prefer the official scripting API; commit scripts alongside models.
4. On export, always emit STEP (and the native format) with a documented unit and tolerance.
5. Verify imports in a second tool when interchange matters — kernels disagree at edge cases.

## Validation

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
# CAD-specific manual checks:
# - Re-open the file in target version; confirm zero rebuild errors
# - Round-trip STEP → import → compare mass properties within tolerance
```

## See also

- ISO 10303-242 (STEP AP242) for archival/exchange
- Vendor API references (Fusion 360, SolidWorks, Onshape FeatureScript, FreeCAD Python)
