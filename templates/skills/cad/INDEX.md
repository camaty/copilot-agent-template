---
domain: cad
version: 0.1.0
---
# CAD — Domain Index

> Mechanical / parametric computer-aided design: solid modeling, assemblies, drawings, and CAM-adjacent workflows. For tessellated/visual CG, see [`3dcg`](../3dcg/INDEX.md).

## What this domain covers

B-rep / NURBS solid modeling, parametric history, assemblies and constraints, drawing generation, and CAD-to-downstream interchange (STEP, IGES, Parasolid, JT). Vendor-specific automation lives in subdomains.

## Subdomain decision tree

| If the task involves… | Open this subdomain |
|---|---|
| Feature-based parametric modeling (Fusion 360, SolidWorks, Onshape, FreeCAD, NX) | [`parametric/SKILL.md`](./parametric/SKILL.md) |
| LLM-driven CAD/CG API calls that need a schema-validated action space and geometry checker | [`api-harness/SKILL.md`](./api-harness/SKILL.md) |
| Programmatic multi-part assembly with topology constraints, snap rules, or connector-based mates | [`topology-assembly/SKILL.md`](./topology-assembly/SKILL.md) |
| Direct/explicit modeling (SpaceClaim, Creo Direct), MBD, GD&T-heavy | _add a new subdomain — see [`../EXTENDING.md`](../EXTENDING.md)_ |
| Mesh or generative-design output | _add a new subdomain or use [`3dcg`](../3dcg/INDEX.md) for downstream rendering_ |

## Facet vocabulary

| Axis | Allowed values |
|---|---|
| `lang:`     | `python`, `ts`, `csharp`, `cpp`, `featurescript`, `ilogic` |
| `vendor:`   | `autodesk`, `dassault`, `ptc`, `siemens`, `onshape`, `freecad`, `llm` |
| `format:`   | `step`, `iges`, `parasolid`, `jt`, `stl`, `3mf`, `brep` |
| `kernel:`   | `parasolid`, `acis`, `opencascade` |

## Shared resources

The `_shared/` folder is **not yet created** for this domain — add it when a second subdomain is introduced:

- `_shared/canon.md` — units, tolerances, B-rep terminology, file format trade-offs
- `_shared/pitfalls.md` — interchange and history-stability anti-patterns

See [`../coding/_shared/`](../coding/_shared/) for a reference layout.

## Related domains

- `3dcg` — for visualization or marketing renders of CAD models
- `coding` — when building standalone CAD-adjacent tooling (e.g. STEP parsers)
