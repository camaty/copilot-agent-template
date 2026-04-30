---
name: ml-vlm-spatial
description: "Use vision-language models to interpret 3D scenes (point clouds, 3DGS) and drive autonomous re-arrangement, query, or annotation. Triggers: VLM, GPT-4o vision, LLaVA, point cloud understanding, 3DGS query, spatial reasoning, scene re-arrangement, embodied AI."
domain: ml
subdomain: vlm-spatial
facets:
  - lang:python
  - format:splat
  - format:pcd
  - target:gpu
applies_when:
  any_of:
    - "task uses a vision-language model to interpret a 3D scene (point cloud or 3DGS)"
    - "task autonomously edits, re-arranges, or annotates objects in a real scanned space"
    - "task answers natural-language queries about the semantic layout of a 3D environment"
    - "task grounds an LLM action plan in a captured 3D scene"
version: 0.1.0
---
# Machine Learning / VLM Spatial Understanding

## When to use

Open this skill when the task pairs a 3D scene representation (a point
cloud, a 3DGS capture, an RGBD scan, or a USD scene) with a vision-
language model that must reason about objects and layout in natural
language — answer queries, plan re-arrangement, propose edits, or
annotate. Typical clients: home-robot scene understanding, AR
content authoring, smart-home spatial assistants, real-estate scene QA.

For pure 2D image VQA, prefer the parent
[`../inference/SKILL.md`](../inference/SKILL.md). For training a
VLM from scratch, see [`../training/SKILL.md`](../training/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **VLM (Vision-Language Model)** — a multimodal model that accepts
  images (and increasingly video) plus text and emits text. Examples:
  GPT-4o, Claude 3.5 with vision, Gemini 1.5/2, LLaVA, Qwen-VL, CogVLM.
- **3D scene representation** — point cloud (`.pcd`, `.ply`, `.las`),
  3D Gaussian Splat (`.splat`), mesh (`.obj`, `.glb`, `.usd`), or
  RGBD video. Each requires a different "rendering for the VLM"
  strategy.
- **Multi-view rendering** — VLMs do not consume 3D natively; the
  pipeline renders the scene from N viewpoints (4–24 typical) and
  feeds the views as images. View choice dramatically affects answer
  quality.
- **Open-vocabulary 3D segmentation** — assigning each point/splat a
  semantic label drawn from an open vocabulary (any free-text
  description), not a fixed class set. Implemented via 2D models
  (CLIP, SAM, Grounding-DINO) lifted to 3D by back-projection.
- **Grounded answer** — an answer accompanied by a reference to a
  specific 3D region (a bounding box, a point set, a splat selection)
  so the user can verify or act on it.
- **Scene graph** — a structured representation of the scene as
  objects with attributes and relations (`chair on rug`,
  `lamp behind sofa`). Often emitted by the VLM and refined by a
  geometric checker.
- **Coordinate convention** — Z-up vs Y-up vs camera-up varies per
  capture tool. Always convert to a single canonical frame
  (typically right-handed, Z-up, metres) before VLM-side reasoning.
- **Action grounding** — translating a VLM-emitted instruction
  ("move the chair next to the window") into 3D transforms with
  collision and physics constraints.

## Recommended patterns

1. **Decouple capture, lifting, and reasoning.** Capture pipeline →
   open-vocabulary 3D segmentation → scene graph → VLM reasoning.
   Each stage cached and individually testable.
2. **Render multiple views per query.** A single canonical view loses
   half the scene. Render 4 orthographic views (top, front, two
   sides) for layout, plus 4 free-orbit perspective views for
   detail. Stitch into a single contact sheet for the VLM.
3. **Always emit grounded references.** The VLM should output JSON
   like `{"answer": "...", "referent": {"type": "object", "id": 42}}`
   so downstream code can act on the answer. Free-text answers are
   not actionable.
4. **Prefer 2D-lifted segmentation over 3D-only.** Open-vocabulary 3D
   models are still weak; lift CLIP/SAM/Grounding-DINO masks from
   multi-view 2D to 3D via back-projection or splat-attention.
5. **Constrain edits with a geometry checker.** Anything the VLM
   proposes ("place the lamp 30 cm left of the sofa") must pass
   collision + reachability checks before being applied. Treat the
   VLM as a planner, not an executor.
6. **Cache embeddings, not raw images.** Per-object CLIP embeddings
   stored alongside the scene graph let later queries skip
   re-rendering. Image caches dominate cost otherwise.
7. **Use a small local VLM for inner loops.** GPT-4o-class models for
   final answers; Qwen-VL or LLaVA-Next for hot-loop
   "is-this-region-relevant" filtering. Cuts cost 50–100×.
8. **Pin the VLM version in the registry entry.** Behavioural drift
   between minor releases (e.g. GPT-4o-2024-08 → 2024-11) silently
   changes scene-graph schemas; record the model id beside every
   cached output.

## Pitfalls (subdomain-specific)

- ❌ **Sending the raw splat or point cloud to the VLM.** Today's
  VLMs cannot ingest 3D directly; they hallucinate confidently.
  Always render to images.
- ❌ **One canonical view only.** A "front" view of a 3DGS room
  occludes 60 % of the scene. Always render multiple views.
- ❌ **Inconsistent coordinate frames.** A capture in Y-up + a
  scene-graph in Z-up gives the VLM swapped axes; "above" and
  "behind" become wrong. Normalise on ingest.
- ❌ **Free-text-only output.** Without grounded referents, the
  downstream actuator cannot move anything; build JSON schemas with
  required `referent` fields.
- ❌ **Trusting VLM distance estimates.** "About 50 cm away" is
  unreliable; metric distance must come from the 3D geometry, not
  the VLM's text.
- ❌ **Ignoring lighting drift between views.** Auto-exposure differs
  per render; the VLM may interpret it as different scene state.
  Lock exposure across the contact sheet.
- ❌ **Re-rendering on every query.** A high-res 3DGS render at 8
  views costs > 1 s of GPU; batch and cache by `(scene_hash,
  viewpoint)`.
- ❌ **Letting the VLM choose object IDs.** IDs must be assigned by
  the segmentation pipeline; the VLM only references them.

## Procedure

1. **Ingest & normalise the capture.**
   - Convert to a canonical frame (right-handed, Z-up, metres).
   - Estimate floor plane (RANSAC on lowest points or splats);
     align scene so floor = z = 0.
   - Tag the scene with `scene_id`, capture device, timestamp, and
     a content hash.

2. **Open-vocabulary 3D segmentation.**
   - Render 24–48 RGB views (low-res, ~512²) covering the upper
     hemisphere.
   - Run SAM + CLIP (or Grounding-DINO + SAM) on each view to get
     2D masks with embeddings.
   - Lift masks to 3D: for each splat/point, accumulate the most
     consistent 2D label from views where it projects in-mask.
   - Cluster connected components per label → object instances with
     stable integer IDs.

3. **Build the scene graph.**
   ```json
   {
     "scene_id": "...",
     "frame": "Z-up,m",
     "objects": [
       {"id": 1, "label": "sofa", "bbox_3d": [...], "centroid": [...]},
       {"id": 2, "label": "lamp", "bbox_3d": [...], "centroid": [...]}
     ],
     "relations": [
       {"src": 2, "rel": "above_floor", "value": 0.81},
       {"src": 2, "rel": "near", "tgt": 1, "distance_m": 0.42}
     ]
   }
   ```
   Relations are computed geometrically (AABB overlap, distance,
   support, occlusion) — not by the VLM.

4. **Render the VLM context pack.**
   - For each query, render: 4 orthographic + 4 perspective views
     with object IDs overlaid as small numbered markers.
   - Stitch into a single contact-sheet image; embed the scene
     graph JSON in the prompt.

5. **Query the VLM.**
   - System prompt: define the JSON schema, include unit
     conventions, demand grounded `referent` fields, forbid
     numeric distance guesses.
   - User prompt: the natural-language query plus the contact-
     sheet image plus the scene graph.
   - Parse the VLM JSON; reject and retry on schema violation.

6. **Validate & ground the answer.**
   - For each `referent`, look up object IDs in the scene graph;
     fail closed if any ID is unknown.
   - For action plans, run a collision + reachability check
     against the 3D geometry before applying.

7. **Apply or surface the result.**
   - Surface: highlight referenced objects in the viewer (e.g.
     three-vrm splat viewer with object selection).
   - Apply: emit a transform list to the executor (game engine,
     robot planner) with explicit world-frame coordinates.

8. **Cache & log.**
   - Store `(scene_hash, query, vlm_model_id) → answer` for
     deterministic re-runs.
   - Emit a `[SKILL:vlm-spatial][answer scene=… model=… grounded=N]`
     event for traceability.

## Validation

After completing the procedure, run:

```sh
# Lint / static checks
ruff check .
mypy --strict src/

# Unit + integration tests
pytest tests/vlm_spatial/ -v

# Schema regression: every VLM output must validate against
# scene_answer.schema.json
python -m vlm_spatial.validate_schemas tests/golden/*.json

# Spatial-grounding gate (held-out probe set):
# - Object reference accuracy >= 0.85 on the 100-query probe
# - Distance MAE <= 5 cm on relations the system claims
# - Scene-graph build is deterministic (re-run hash equality)
python -m vlm_spatial.eval --probe tests/probes/probe_v3.json
```

## See also

- [`../motion-fm/SKILL.md`](../motion-fm/SKILL.md) — pairing scene
  understanding with avatar motion planning.
- [`../inference/SKILL.md`](../inference/SKILL.md) — serving the VLM
  behind a low-latency API.
- [`../../3dcg/3dgs/SKILL.md`](../../3dcg/3dgs/SKILL.md) — primary
  capture format consumed here.
- [`../../gameengine/synthetic-data/SKILL.md`](../../gameengine/synthetic-data/SKILL.md)
  — synthetic 3D scenes for VLM benchmarking.
- LLaVA-Next — <https://llava-vl.github.io/>
- SAM (Segment Anything) — <https://segment-anything.com/>
- Grounding-DINO — <https://github.com/IDEA-Research/GroundingDINO>
- OpenScene / LangSplat — open-vocab 3D segmentation references.
