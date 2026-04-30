---
name: cad-topology-assembly
description: "Topology-constrained programmatic assembly of CAD parts using point-to-point mates, axis alignment, and snap rules. Triggers: assembly, topology, mates, constraints, gearbox, furniture, IKEA, snap, connectivity, STEP, B-rep."
domain: cad
subdomain: topology-assembly
facets:
  - lang:python
  - format:step
  - format:brep
applies_when:
  any_of:
    - "task defines point-to-point or axis-aligned mates between CAD parts"
    - "task programmatically assembles gears, furniture, or modular components"
    - "task encodes IKEA-style topology rules for part connectivity"
version: 0.1.0
---
# CAD / Topology-Constrained Assembly

## When to use

The task programmatically positions and constrains two or more CAD parts relative to each other — aligning axes, mating faces, or snapping connectors according to explicit topology rules. Typical cases: generating a gearbox from a library of teeth profiles, assembling flat-pack furniture from a catalogue, or defining connectivity graphs for modular architectural components.

If the task is only about modeling individual solid bodies with no inter-part constraints, use [`parametric/SKILL.md`](../parametric/SKILL.md) instead.

## Canon (must-know terms and invariants)

- **Topology constraint** — a declarative rule that removes one or more degrees of freedom between two parts (e.g. "face A of Part 1 is coplanar with face B of Part 2").
- **Mate / joint** — the assembly-level entity encoding a topology constraint; one mate = one rule; stacking mates removes DoF incrementally.
- **DoF (degrees of freedom)** — a rigid body in 3-D space has 6 DoF; a fully assembled part must have 0 DoF remaining after all mates are applied.
- **Connector** — a named attachment point (origin + normal + optional axis) declared on a part; programmatic assembly matches connectors by name or role rather than raw face IDs.
- **Snap rule** — a higher-level topology rule (e.g. peg-in-hole, dovetail slot) that resolves to one or more mates when instantiated.
- **Assembly graph** — a directed graph where nodes are part instances and edges are mates; cycles indicate over-constraint.
- **B-rep** — Boundary Representation; the underlying solid model format (OpenCASCADE / Parasolid / ACIS); all mate computations operate on B-rep topology.

For CAD-wide terminology see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Declare connectors on parts at design time** — embed named attachment points (origin, normal, axis) as metadata rather than computing them from raw face IDs at assembly time; this decouples topology rules from geometry changes.
2. **Build an assembly graph before writing geometry** — model the part-instance graph, validate it for cycles and under-constraint, then resolve connectors and apply transforms in topological order.
3. **Encode snap rules as constraint templates** — parameterise each connection type (peg-in-hole, face-mate, slot-key) as a reusable function that takes two connector objects and emits a transform; keep geometry out of the rule logic.
4. **Verify DoF count after each mate** — after applying every constraint, assert `remaining_dof == 0`; surface errors early rather than letting downstream STEP export silently carry floating sub-assemblies.
5. **Export position data alongside STEP** — write a sidecar JSON (or YAML) containing the resolved transforms; this allows downstream tools to verify assembly state without parsing B-rep topology.
6. **Use OpenCASCADE (pythonocc-core) for kernel-level work** — it exposes `BRep_Builder`, `TopoDS_Compound`, and `BRepAlgoAPI` natively from Python; prefer it over subprocess-based automation of commercial tools when cross-platform portability matters.

## Pitfalls (subdomain-specific)

- ❌ **Referencing raw face IDs instead of connectors** — face indices change on any model edit; always use named or role-tagged attachment points.
- ❌ **Applying mates without DoF tracking** — over-constrained assemblies still export to STEP but fail in downstream FEA/motion solvers; count DoF incrementally.
- ❌ **Assuming face normals are outward-pointing** — OpenCASCADE face orientation depends on construction order; always query `BRepAdaptor_Surface` or check `IsReversed()` before using normals for alignment.
- ❌ **Mixing coordinate systems silently** — parts authored in different units or with non-identity placement transforms will assemble incorrectly; normalise all parts to a common origin and unit before building the assembly graph.
- ❌ **Exporting the assembly without shape healing** — small gaps and edge tolerances from B-rep booleans accumulate; run `ShapeFix_Shape` before STEP export to avoid import failures in downstream tools.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Define connectors on each part** — for every attachment point, store `{name, origin: (x,y,z), normal: (nx,ny,nz), axis: (ax,ay,az)}` as part metadata (JSON sidecar or embedded property).
2. **Declare snap rules** — write a constraint template for each connection type used in the assembly (e.g. `face_mate`, `axis_align`, `peg_in_hole`, `slot_key`).
3. **Build the assembly graph** — create part instances and edges representing mates; validate the graph (no cycles, no floating sub-assemblies, DoF = 0 when all rules applied).
4. **Resolve transforms** — traverse the graph in topological order; for each mate edge, compute the rigid transform that satisfies the snap rule and accumulate it on the child instance.
5. **Construct the B-rep compound** — use `BRep_Builder` (pythonocc) or equivalent to create a `TopoDS_Compound`; place each part shape at its resolved transform using `BRepBuilderAPI_Transform`.
6. **Heal the shape** — run `ShapeFix_Shape` to close gaps and normalise tolerances.
7. **Export to STEP** — use `STEPControl_Writer` with `AP214` or `AP242` schema; write the sidecar JSON of resolved transforms alongside the STEP file.
8. **Validate** — re-import the STEP file in a second tool (or pythonocc `STEPControl_Reader`), check part count and mass properties against expected values.

If this skill includes bundled scripts or starter files (siblings of this `SKILL.md`), prefer those local assets over inline commands.

## Validation

After completing the procedure, run:

```sh
# Static analysis
python -m py_compile your_assembly_script.py
ruff check .

# Unit tests (mock connector resolution, DoF counting)
pytest tests/test_topology_assembly.py -v

# Integration: generate a known assembly and verify STEP round-trip
python scripts/verify_assembly_roundtrip.py --expected fixtures/expected_gearbox.json
```

## See also

- [`parametric/SKILL.md`](../parametric/SKILL.md) — individual part modeling before assembly
- [`api-harness/SKILL.md`](../api-harness/SKILL.md) — wrapping CAD operations behind an LLM-safe schema
- [pythonocc-core documentation](https://github.com/tpaviot/pythonocc-core) — Python bindings for OpenCASCADE
- ISO 10303-214 / 10303-242 (STEP AP214 / AP242) — assembly structure and PMI
