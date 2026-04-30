---
name: 3dcg-garment-sim
description: "Convert 2D garment designs into avatar-ready 3D meshes and apply physics-based cloth simulation. Triggers: garment, cloth, drape, sewing pattern, 2D-to-3D, PBD, FEM, avatar clothing, SMPL, VRM clothing."
domain: 3dcg
subdomain: garment-sim
facets:
  - lang:python
  - target:avatar
  - format:obj
  - format:gltf
applies_when:
  any_of:
    - "task generates 3D garment geometry from a flat design, sewing pattern, or single image"
    - "task simulates cloth drape on a parametric body (SMPL, SMPL-X, VRM) with physics"
    - "task fits clothing meshes to multiple body shapes or animated poses"
    - "task needs collision-stable cloth on top of avatar animation"
version: 0.1.0
---
# 3D CG / Garment Simulation

## When to use

Open this skill when the goal is to turn a 2D garment description (sewing
pattern, flat sketch, photograph, or designer reference) into a 3D mesh
that drapes correctly on a parametric avatar — and to keep that drape
stable while the avatar is animated. For pure offline rendering of a
pre-simulated cloth cache, the parent canon and renderer-specific
subdomains (`blender/`, `houdini/`) are usually enough.

If the task does not match the activation hints, return to [`../INDEX.md`](../INDEX.md)
and pick another subdomain.

## Canon (must-know terms and invariants)

- **Sewing pattern** — the set of 2D panels (with seam allowances) that,
  once stitched, form a 3D garment. Each panel is a polygon; seams are
  paired edges that must be welded with matching vertex counts.
- **Drape pose / A-pose** — the canonical body pose used when first
  positioning panels around the avatar. Always drape from a pose with
  arms slightly away from the torso to avoid penetration at the
  armpits.
- **SMPL / SMPL-X** — parametric human body models (10 / 16 shape
  parameters, plus pose and expression). The avatar's vertex order is
  fixed; this is what enables generalisation across body shapes.
- **PBD (Position-Based Dynamics)** — fast, unconditionally stable
  cloth integrator used by most real-time and DCC engines (Marvelous
  Designer, CLO 3D, Unity Cloth). Constraints (distance, bending,
  collision) are projected directly on positions each substep.
- **FEM cloth** — finite-element cloth (St-Venant Kirchhoff or Baraff–
  Witkin); higher fidelity, anisotropic warp/weft response, but
  needs implicit integration to stay stable at large time steps.
- **Collision proxy** — a low-poly capsule/SDF approximation of the
  avatar used during simulation. Cloth never collides against the full
  rigged mesh — it collides against the proxy plus a small offset
  (typically 1–3 mm).
- **Skinning weight transfer** — once a garment is draped, the cloth
  vertices receive the avatar's nearest-bone skinning weights so the
  garment animates with the rig (cheap LODs, cinematics, real-time).
- **Two-sided material** — cloth interiors must render; one-sided
  materials produce missing geometry on inside-out folds.

For terminology shared across the whole `3dcg` domain, see
[`../_shared/canon.md`](../_shared/canon.md) (when present) or
[`../../coding/_shared/canon.md`](../../coding/_shared/canon.md) for
generic engineering canon.

## Recommended patterns

1. **Start from a sewing pattern, not a free-form mesh.** Even when the
   input is an image, recover panels (via photogrammetry or a pattern
   estimator like Sewformer / NeuralTailor) before simulating. Patterns
   give clean topology, predictable seams, and reusable assets across
   body shapes.
2. **Use a collision proxy with margin, not the full body mesh.**
   Replace the rigged avatar with a capsule chain or SDF + a 1–3 mm
   offset. Solver stability triples and self-intersection at the neck,
   armpits, and crotch drops to near zero.
3. **Drape in two phases — gravity then animation.** First simulate the
   garment to rest on a static A-pose for ~3 seconds of sim time, then
   bake the rest pose, then run animation. Skipping phase one produces
   visible "snap-in" artefacts on the first animated frame.
4. **Transfer skin weights from the avatar after drape.** Use nearest-
   bone or heat-diffusion weight transfer so the garment can play back
   without resimulating. Cache simulation only for hero shots.
5. **Parametrise material by GSM and stiffness, not raw spring
   constants.** Authoring in fabric-real units (g/m², bending stiffness
   in mN·m) keeps assets portable across DCC tools (Marvelous, Houdini
   Vellum, CLO, Blender Cloth).
6. **Validate against multiple shape parameters.** A garment that drapes
   on the mean body must also drape on ±2σ shape vectors; sweep at
   least 5 shape samples in CI before shipping a garment asset.

## Pitfalls (subdomain-specific)

- ❌ **Simulating against the full rigged mesh.** Tiny self-intersections
  at limb joints make the cloth solver explode. Always use a proxy.
- ❌ **Mismatched seam vertex counts.** A 32-vertex panel edge sewn to a
  31-vertex partner causes a "zip-up" failure that silently leaves a
  gap or a singular triangle. Resample both edges to the same length.
- ❌ **Draping from T-pose.** Arms straight out create armpit
  penetration that a proxy alone cannot fix. Always start from A-pose
  (~30° shoulder abduction).
- ❌ **One-sided materials on cloth.** Wind, hem flips, and inside-out
  folds expose the back face. Author every garment material as
  two-sided with optional thickness offset.
- ❌ **Substep too large for the bending stiffness.** PBD goes unstable
  when `dt × √(k_bend)` exceeds ~0.6. Halve substeps before stiffening
  fabric.
- ❌ **Ignoring frame-rate when caching.** Sim caches at 30 fps replayed
  at 60 fps interpolate linearly through collision constraints, causing
  visible pop-through. Either resimulate or cache at the playback rate.
- ❌ **Skin-weight transfer through the cloth.** Using the cloth's own
  vertices as weight donors causes layering artefacts (sleeves
  deforming with the chest). Always source weights from the body.

## Procedure

1. **Acquire / recover the sewing pattern.**
   - If patterns are provided (DXF-AAMA, .pat), import directly.
   - If only an image or a 3D mesh exists, run a pattern recovery model
     (e.g. NeuralTailor, Sewformer) to extract 2D panels and seam
     correspondence. Manually verify seam topology.
2. **Prepare the avatar.**
   - Pose the SMPL/SMPL-X (or VRM) avatar to A-pose with shape
     parameters frozen.
   - Generate a collision proxy: capsule chain along the skeleton, or
     a smoothed SDF at the body surface, plus a configurable offset
     (default 2 mm).
3. **Position panels around the avatar.**
   - Rotate and translate each 2D panel to its anatomical location
     (front-torso panel in front of chest, sleeve panels around upper
     arms, etc.). Use bone-relative anchors for repeatability.
   - Stitch seam pairs: weld matching edges, ensure consistent winding,
     resample to equal vertex counts.
4. **Run gravity drape.**
   - Material: assign GSM (e.g. 180 g/m² cotton, 80 g/m² silk),
     bending stiffness, friction (cloth↔body ≈ 0.4).
   - Solver: PBD with 8–16 substeps at 120 Hz, or implicit FEM at 60 Hz.
   - Simulate ~3 s of sim time, monitor max-stretch and penetration
     metrics; abort and resubstep if either exceeds threshold.
5. **Bake the rest pose.**
   - Snapshot vertex positions; this becomes the new garment rest
     state. Save as `<garment>.rest.obj` or USD prim with attribute
     `pref` (rest reference) for downstream tools.
6. **Transfer skinning weights.**
   - For each garment vertex, find the nearest body vertex (within a
     radius cap; use closest-point-on-surface, not nearest-vertex, to
     avoid tunnelling weights to the wrong limb).
   - Copy bone weights; renormalise; clamp to ≤ 4 influences for engine
     compatibility.
7. **Animate & optionally re-simulate.**
   - For background characters: rely on skinning + a single
     post-processing smooth pass.
   - For hero shots: run a short FEM/PBD simulation per shot using the
     skinned positions as soft constraints (collision + drape only).
8. **Export.**
   - For real-time / VRM: skinned glTF with weights, no cache.
   - For offline: Alembic or USD point caches alongside the rest mesh.
9. **Validate** (see below) and commit the garment asset with material
   metadata (GSM, friction, bending) embedded in the file.

## Validation

After completing the procedure, run:

```sh
# Static checks on the pipeline scripts
ruff check pipelines/garment/
mypy pipelines/garment/ --ignore-missing-imports

# Unit + integration tests
pytest tests/garment_sim/ -v

# Garment-specific quality gates:
# - Penetration: mean cloth↔body distance during animation > 0.5 mm.
# - Self-intersection count per frame < 5 triangles.
# - Stretch ratio: 0.85 ≤ |edge|/|edge_rest| ≤ 1.15 on 99 % of edges.
# - Shape sweep: drape stable on body shape betas in {-2, -1, 0, +1, +2}σ.
# - Seam continuity: no open seams (boundary-edge count == hem edges).
```

For visual review, render a turn-table on the mean body shape and on
±2σ shapes; diff against a baseline image with a 2 % tolerance.

## See also

- [`../3dgs/SKILL.md`](../3dgs/SKILL.md) — for capturing real garments as
  3D Gaussian Splats before pattern recovery.
- [`../../ml/motion-fm/SKILL.md`](../../ml/motion-fm/SKILL.md) — supplies
  the avatar animation that the garment then drapes over.
- [`../blender/SKILL.md`](../blender/SKILL.md) — Blender's Cloth modifier
  for in-DCC iteration.
- [`../houdini/SKILL.md`](../houdini/SKILL.md) — Houdini Vellum for
  high-fidelity production cloth.
- SMPL / SMPL-X — <https://smpl.is.tue.mpg.de/>
- VRM 1.0 specification — <https://vrm.dev/>
- Sewformer (sewing-pattern recovery from images) — <https://maria-korosteleva.github.io/SewFormer/>
- Marvelous Designer / CLO 3D — industry-standard pattern-based cloth.
