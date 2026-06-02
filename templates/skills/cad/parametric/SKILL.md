---
name: cad-parametric
description: "Feature-based parametric CAD modeling, assemblies, drawings, and CAM-adjacent automation across major vendors. Triggers: CAD, parametric, sketch, feature, assembly, mate, joint, STEP, IGES, drawing, FeatureScript, iLogic, Fusion API, SolidWorks API, Onshape."
domain: cad
subdomain: parametric
facets:
  - vendor:autodesk
  - vendor:dassault
  - vendor:onshape
  - vendor:freecad
  - lang:python
  - lang:featurescript
  - format:step
  - format:iges
  - format:brep
applies_when:
  any_of:
    - "task creates or edits parametric solid models with a feature history"
    - "task involves assemblies, mates/joints, or drawings"
    - "task targets Fusion 360, SolidWorks, Onshape, FreeCAD, NX, or Creo"
    - "task automates CAD via a vendor scripting API (FeatureScript, iLogic, VBA, Python)"
    - "task interchanges CAD via STEP / IGES / Parasolid / JT"
version: 0.1.0
---
# CAD / Parametric

## When to use

Open this skill when the task creates, edits, or automates parametric
feature-based CAD. Typical scenarios: scripting Fusion / SolidWorks /
Onshape, hand-authoring FeatureScript, generating drawings, or
exchanging via STEP. For tessellated / mesh work (3D printing post-
export, visualisation), prefer `3dcg` after the export step.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Sketch → Feature → Body → Component → Assembly** — the canonical
  modelling hierarchy. Each level has its own constraint vocabulary.
- **Fully constrained sketch** — every degree of freedom (DoF)
  removed. Under-constrained sketches break unpredictably on edit.
- **Feature history (timeline / tree)** — ordered list of operations.
  Reorder is rarely safe; insertion at the end is.
- **Reference geometry** — datums, planes, axes, points used by
  features. Externally-referenced geometry creates parent/child
  fragility (a.k.a. "topology naming" problems).
- **Topology naming** — vendor-specific identifier scheme for B-rep
  faces/edges so features survive history edits. FreeCAD's classic
  weakness; SolidWorks/Onshape/Fusion handle it differently.
- **Mate / joint** — assembly constraints between components
  (concentric, planar, distance, angle, gear). Joints are the modern
  replacement for legacy mate stacks.
- **GD&T / MBD** — Geometric Dimensioning & Tolerancing; Model-Based
  Definition (annotations on the 3D model rather than a 2D drawing).
  AP242 carries MBD semantically; STL/OBJ do not.
- **B-rep (Boundary Representation)** — exact geometry as faces /
  edges / vertices. Distinct from mesh; what STEP / Parasolid /
  ACIS / OpenCascade store.
- **Kernel** — the modelling kernel (Parasolid, ACIS, Granite,
  OpenCascade). STEP transfer between different kernels can have
  edge-case discrepancies in tolerances and trimming.
- **Configuration / variant** — a single file representing multiple
  size/material variations via parameter sets.
- **Drawing view** — projection of the 3D model with dimensions and
  GD&T. Should be auto-generated, not hand-redrawn.

## Recommended patterns

1. **Fully constrain every sketch** before promoting to a feature.
   Under-constrained sketches are bugs.
2. **Drive parameters from a single source** — a parameter table,
   configuration, or external file. Hard-coded dimensions are anti-
   patterns.
3. **Author master sketches / skeletons** for top-down assembly
   design. Downstream parts reference the skeleton, not each other.
4. **Use STEP AP242** for long-term archival and cross-vendor
   exchange (carries MBD); native formats for active editing only.
5. **Version-control models as native + STEP.** STEP is text-ish
   (still poor for diff, but better) and survives kernel changes.
6. **Automate via the vendor's official API** — FeatureScript
   (Onshape), Fusion API (Python/JS), SolidWorks API (VBA/.NET),
   iLogic (Inventor), FreeCAD Python. Avoid screen-scraping.
7. **Prefer joints over legacy mates** in modern Fusion/Inventor;
   joints carry motion semantics for downstream simulation.
8. **Generate drawings from templates** with auto-populated title
   blocks; check drawings into source control as native + PDF.
9. **Tag features with a stable name / id** so scripts can edit by
   reference, not by index. Index-based edits break on insertions.
10. **Run kernel-vs-kernel STEP round-trip** in CI when interchange
    matters; mass / volume / centroid must match within tolerance.

## Pitfalls (subdomain-specific)

- ❌ **External references across files** without a skeleton —
  moving a part breaks dozens of downstream features.
- ❌ **Editing a feature mid-history without checking children** —
  silently invalidates downstream features.
- ❌ **Round-tripping through STL** for editable geometry — loses
  parametric data, exact surfaces, and tolerances.
- ❌ **Mixing units within an assembly** (mm vs in) — vendor handling
  varies; prefer a single unit system documented in repo settings.
- ❌ **Storing tolerances only in the drawing** — MBD-aware
  downstream tools won't see them; carry GD&T on the 3D model.
- ❌ **Committing binary CAD files without LFS** — repo size
  explodes; diffs are useless. Prefer Onshape (server-side history)
  or Git-LFS + a paired STEP for diff context.
- ❌ **Index-based feature edits in scripts.** Inserting any feature
  earlier renumbers; reference features by name or persistent id.
- ❌ **Trusting STEP "minor mismatches" silently.** A 0.001 mm gap
  becomes a 0.001 mm leak in CFD; verify mass props after import.
- ❌ **Scripted operations without a parametric expression for
  rebuild.** Hard-coded geometry survives once and breaks on edit.
- ❌ **Using sketch fillets where feature fillets would survive
  better.** Feature fillets are robust to upstream sketch edits;
  sketch fillets disappear on dimension change.
- ❌ **Using `Move/Copy Body` without a feature handle.** Subsequent
  edits cannot find the body.

## Procedure

1. **Confirm vendor + version** — native files often break across
   major versions. Pin in repo metadata (`.tooling-versions`).
2. **For new parts**, plan the sketch hierarchy and parameter source
   before drawing. Decide configurations vs derived parts.
3. **Build sketches fully constrained** with named dimensions tied
   to parameters; fillet/chamfer as features, not in sketches.
4. **For assemblies**, author a skeleton, link components to it,
   and use joints (not legacy mates) for motion.
5. **For automation**, prefer the official scripting API. Commit
   scripts alongside models in the repo.
6. **On export**, always emit STEP (AP242 if MBD-relevant) plus
   the native format with documented unit and tolerance.
7. **For drawings**, generate from templates; auto-populate title
   block; commit native + PDF.
8. **Verify imports in a second tool** when interchange matters —
   kernels disagree at edge cases (tangent edges, sliver faces).

## Validation

After completing the procedure, run:

```sh
# Static checks for automation scripts
ruff check automation/             # FreeCAD / Fusion Python
dotnet format --verify-no-changes  # SolidWorks .NET / iLogic
# FeatureScript: lint via Onshape's built-in checker before merge.

# Tests (where the API supports headless)
pytest tests/cad/ -v               # FreeCAD-based CI
fusion --headless --run-script tests/run_fusion_tests.py

# CAD-specific manual checks (must be scripted in CI):
# - Re-open the file in target version; assert zero rebuild errors
# - Round-trip STEP → import → mass-props equality within 1e-6
# - Drawing regeneration: compare PDF page count + title block fields
# - Configuration sweep: each variant rebuilds without error
python tools/cad_smoke.py --file shaft.step --tolerance 1e-6
```

## See also

- [`../api-harness/SKILL.md`](../api-harness/SKILL.md) — when an LLM
  drives the parametric API and needs schema validation.
- [`../topology-assembly/SKILL.md`](../topology-assembly/SKILL.md) —
  programmatic constraint-driven assembly.
- [`../freecad-scripting/SKILL.md`](../freecad-scripting/SKILL.md) —
  open-source automation when no commercial seat is available.
- ISO 10303-242 (STEP AP242) — archival/exchange with MBD.
- Vendor API references: Fusion 360, SolidWorks, Onshape FeatureScript,
  Inventor iLogic, FreeCAD Python.
