---
name: cad-freecad-scripting
description: "Open-source FreeCAD automation: PartDesign, Sketcher, Assembly, expressions, FEM, and headless `freecadcmd`. Triggers: FreeCAD, freecadcmd, PartDesign, Sketcher, Spreadsheet, Assembly4, FEM, App.ActiveDocument, OCCT, OpenCascade."
domain: cad
subdomain: freecad-scripting
facets:
  - lang:python
  - vendor:freecad
  - format:step
  - format:brep
applies_when:
  any_of:
    - "task automates FreeCAD via Python (`App`, `Part`, `PartDesign`, `Sketcher`)"
    - "task runs FreeCAD headlessly via `freecadcmd` for batch generation"
    - "task ships a FreeCAD workbench, macro, or CI-generated CAD asset"
    - "task wraps OCCT (OpenCascade) operations through FreeCAD bindings"
version: 0.1.0
---
# CAD / FreeCAD Scripting

## When to use

Open this skill when the task automates FreeCAD via Python — batch
parametric generation, custom workbenches, or open-source CI-driven
CAD pipelines. For commercial CAD (Fusion, SolidWorks, Onshape),
prefer [`../parametric/SKILL.md`](../parametric/SKILL.md). For LLM-
constrained CAD APIs, see [`../api-harness/SKILL.md`](../api-harness/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Document model** — `App.ActiveDocument` (or `App.newDocument()`)
  contains *objects* with names and labels; objects expose typed
  properties read/written via `obj.PropertyName`.
- **Workbenches** — PartDesign (modern, feature-history), Part
  (CSG-style, no history), Sketcher, Draft, Arch, FEM, Assembly4
  (community), TechDraw (drawings).
- **Sketcher** — 2D constraint solver. Constraints have indices;
  modifications by index break on edits — refer by name when
  possible.
- **PartDesign body** — container that holds an ordered feature
  history. The "Tip" is the visible result.
- **OCCT (OpenCascade)** — the underlying B-rep kernel. FreeCAD's
  `Part.TopoShape` wraps OCCT shapes; many operations call into
  OCCT directly.
- **Topology naming problem** — FreeCAD's classic weakness. After
  edits, face/edge identifiers may drift; *Toponaming* (RealThunder
  / 1.x branch) mitigates. Always name reference geometry rather
  than indexing topology.
- **Spreadsheet** — `Spreadsheet::Sheet` object holding aliases that
  drive parameters via expressions (`<<Spreadsheet>>.length`).
- **Expressions** — `=Sketch.Constraints.length * 2`; bind
  parameters across objects without Python.
- **`freecadcmd`** — headless console binary for CI. No UI; many
  GUI-only commands unavailable. Use the Python API directly.
- **`recompute()`** — recomputation is not automatic in scripts;
  call `doc.recompute()` after writes.
- **STEP / IGES / BREP / OBJ / glTF** — supported interchange.
  STEP AP203/AP214 are well supported; AP242 is partial.

## Recommended patterns

1. **Headless via `freecadcmd`** for any CI-generated asset; pin
   FreeCAD version in the runner image.
2. **Drive parameters from a Spreadsheet.** Aliases in a sheet are
   the public knobs; Python sets them, expressions cascade.
3. **Refer to geometry by named property**, never by index.
   `body.Origin.OriginFeatures` is stable; `face.Index = 7` is
   not.
4. **Use PartDesign for parts with history**, Part workbench only
   for one-off CSG.
5. **`doc.recompute()` after every batch of writes.** Without it,
   downstream features see stale geometry.
6. **Save as native `.FCStd` plus STEP** for diff and longevity;
   add OBJ/glTF if the asset feeds visualisation.
7. **Sketch fully constrained** — green sketch in the GUI maps to
   `Sketch.FullyConstrained = True` in script.
8. **Wrap reusable parametric models as macros** (`.FCMacro` in
   the macro path) or as a custom workbench under
   `Mod/MyWorkbench/`.
9. **Toponaming-aware authoring** — keep a stable feature tree,
   avoid mid-history rewrites. Use the LinkStage 3 branch when
   topology stability matters and license permits.
10. **Headless rendering / preview** via `Mesh` export + an
    external renderer; FreeCAD's preview is GUI-only.
11. **Test parameter sweeps** as a PDG-style fan-out: a Python
    driver iterates parameter sets, recomputes, exports STEP per
    variant, compares mass-properties.

## Pitfalls (subdomain-specific)

- ❌ **Skipping `doc.recompute()`** — downstream operations consume
  the previous shape; nothing visibly fails until export looks
  wrong.
- ❌ **Indexing topology** (`face[7]`, `edge[3]`) — toponaming
  drift breaks scripts on edit. Use named planes / datum geometry.
- ❌ **`freecadcmd` invoking GUI commands.** `Gui.runCommand` is
  not available; many `FreeCADGui.*` calls crash.
- ❌ **Importing STEP and editing the body** — imported bodies
  are non-parametric `Part::Feature`; can't be edited via
  PartDesign. Convert via `Part to PartDesign body` first.
- ❌ **Sketch under-constrained but "passes"** — solver picks an
  arbitrary configuration; subsequent edits flip orientation.
- ❌ **Running Python with the system FreeCAD vs the AppImage.**
  Different OCCT versions; STEP round-trips differ. Pin one.
- ❌ **Saving spreadsheet-driven parts without recompute** — the
  saved file shows the new value but holds stale geometry.
- ❌ **Writing to `obj.Shape` directly** — that property is
  computed; assign via the upstream feature.
- ❌ **Macros depending on selection** in CI — there is no GUI
  selection. Drive everything explicitly.
- ❌ **Mixing units silently.** FreeCAD's internal unit is mm;
  imports may carry m. Always inspect and normalise.
- ❌ **Assembly2/A2plus vs Assembly4** — different paradigms.
  Pick one per project; don't mix.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md)
or domain-shared canon as it appears.

## Procedure

1. **Pin the FreeCAD version** (AppImage URL / Docker image) in
   the repo and CI.
2. **Author a Spreadsheet** for the parameter set; name aliases
   meaningfully.
3. **Build the model in PartDesign** with a fully constrained
   sketch and feature-named references; bind dimensions to the
   spreadsheet via expressions.
4. **Wrap automation as a Python script** that opens the doc,
   sets spreadsheet values, calls `recompute`, exports STEP,
   exits cleanly.
5. **Run via `freecadcmd`** in CI; capture stderr; assert exit
   code 0.
6. **Validate exports** — open STEP in a second tool (OCCT
   `STEPControl_Reader` or commercial CAD) and compare mass
   properties.
7. **Generate drawings via TechDraw** for any visible asset; emit
   PDF.
8. **Bundle as a workbench / macro** for end-user reuse if the
   tool is reusable.

## Validation

After completing the procedure, run:

```sh
# Static checks
ruff check freecad_pipeline/
mypy --ignore-missing-imports freecad_pipeline/

# Headless smoke: build & export a parametric variant
freecadcmd freecad_pipeline/build.py -- --variant default --out out/

# Variant sweep
python freecad_pipeline/sweep.py configs/variants.yaml

# Geometry validation: STEP re-import + mass props equality
python freecad_pipeline/validate_step.py out/*.step --tol 1e-6

# OCCT-level checks (via pythonocc or FreeCAD)
freecadcmd -c "
import sys
sys.path.insert(0, 'freecad_pipeline')
from validate_topology import check
sys.exit(0 if check('out/asset.FCStd') else 1)"
```

## See also

- [`../parametric/SKILL.md`](../parametric/SKILL.md) — same
  pipeline shape on commercial vendors.
- [`../api-harness/SKILL.md`](../api-harness/SKILL.md) — when an
  LLM drives FreeCAD via a constrained schema.
- [`../topology-assembly/SKILL.md`](../topology-assembly/SKILL.md)
  — programmatic constraint-driven assembly atop FreeCAD.
- FreeCAD docs — <https://wiki.freecad.org/>
- FreeCAD Python API reference — <https://wiki.freecad.org/Python_scripting_tutorial>
- OpenCascade documentation — <https://dev.opencascade.org/doc/refman/html/>
