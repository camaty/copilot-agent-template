---
name: gameengine-synthetic-data
description: "Generate physically accurate synthetic training datasets in Unity (Perception) and Unreal (Simulation for Synthetic Data). Triggers: synthetic data, domain randomization, Unity Perception, UE Synthetic Data, sensor sim, ground truth, autonomous, sim-to-real."
domain: gameengine
subdomain: synthetic-data
facets:
  - vendor:unity
  - vendor:unreal
  - lang:python
  - lang:csharp
  - lang:cpp
  - target:gpu
applies_when:
  any_of:
    - "task generates synthetic training data from a Unity or Unreal Engine simulation"
    - "task trains autonomous-vehicle, robotics, or inertial-navigation models on engine-generated data"
    - "task configures domain randomisation, lighting variation, or scenario sweeps in a game engine"
    - "task needs ground-truth labels (depth, segmentation, bounding boxes, pose) at scale"
version: 0.1.0
---
# Game Engine / Synthetic Data Generation

## When to use

Open this skill when ML training requires labelled data at a scale or
quality that real-world capture cannot meet — autonomous driving with
rare-event coverage, indoor robotics, drone navigation, factory
inspection — and the engine team can run headless render farms.

If the task is to consume an *existing* synthetic dataset for training,
prefer [`../../ml/training/SKILL.md`](../../ml/training/SKILL.md). For
runtime ML inside a shipped game (animation, upscaling), this skill
does not apply.

If the activation hints don't match, return to [`../INDEX.md`](../INDEX.md)
and pick another subdomain.

## Canon (must-know terms and invariants)

- **Domain randomisation (DR)** — deliberately varying lighting,
  textures, geometry, and camera intrinsics across samples so that a
  network trained on synthetic data generalises to the real domain.
  Without DR, models overfit to the simulator's biases.
- **Sim-to-real gap** — the residual distribution mismatch between
  simulator output and real sensors. Reduced by DR (texture/lighting),
  high-fidelity sensor models (lens, motion blur, rolling shutter,
  noise), and material PBR accuracy.
- **Ground truth (GT) channel** — a render output beyond RGB: depth,
  surface normals, semantic segmentation, instance segmentation, 2D/3D
  bounding boxes, optical flow, 6-DOF pose, materials. Each must be
  rendered deterministically in the same frame as RGB.
- **Unity Perception** — Unity's official synthetic-data package
  (`com.unity.perception`); provides labelers, randomisers, and the
  Solo dataset format.
- **Unreal SmartSuite / Synthetic Data tools** — Unreal Engine's
  EasySynth, Substrate, Movie Render Queue with custom passes, and
  NVIDIA Omniverse Replicator (when used with UE). Replicator is also
  available on USD-native pipelines.
- **Solo dataset format** — Unity Perception's per-frame JSON +
  binary output; `SOLOEndpoint` and `SOLOReader` in Python parse it.
- **Replicator API** — Omniverse's randomisation graph; samples
  parameters and triggers writers per-frame.
- **Headless mode** — running the engine without a display
  (`-batchmode -nographics` for Unity, `-RenderOffScreen` for Unreal).
  Required for cluster/cloud render farms.
- **Sensor model** — software approximation of a real camera/lidar:
  intrinsics (focal, principal point, distortion), extrinsics, noise,
  exposure, motion blur, rolling shutter, lens flare.
- **Frame determinism** — given a fixed seed, the same scenario
  produces byte-identical RGB and GT. Required for dataset
  reproducibility and bug triage.

## Recommended patterns

1. **Treat the dataset like code.** Version the scenario definition,
   randomiser parameters, and engine version together; tag dataset
   builds with the commit hash + engine version + seed range.
2. **Render GT in the same frame as RGB.** Two-pass approaches (render
   RGB, then re-render GT) drift due to non-determinism in physics or
   skinned animation. Use Unity Perception's labelers or UE's custom
   passes that share the frame.
3. **Randomise structure, not just textures.** Object counts, layouts,
   occlusion patterns, distractor placement matter more than texture
   colour jitter for generalisation.
4. **Author one camera, then sweep extrinsics.** A single calibrated
   sensor model with extrinsic sweeps gives reproducible coverage;
   ad-hoc per-shot cameras break label correspondence.
5. **Render at 2× target resolution and downsample.** Engine MSAA and
   mip-mapping artefacts disappear after a downsample, and the
   resulting dataset matches sensor MTF more accurately.
6. **Cap samples per scene; rebuild scenes often.** A million frames
   from one scene is high correlation; aim for ≤ 10k frames per
   procedurally generated scene, then regenerate the scene.
7. **Run on a render farm, not a workstation.** Use containers
   (NVIDIA Omniverse OVX, Unity Cloud Build, custom Kubernetes with
   Vulkan/headless GPU) and a job queue (Argo, Nomad, Slurm).
8. **Validate with a real-data probe.** Hold out a small real
   evaluation set; if synthetic-trained accuracy on it does not
   improve when synthetic data scales 10×, randomisation is wrong.

## Pitfalls (subdomain-specific)

- ❌ **Default Unity / Unreal post-processing on.** Bloom, vignette,
  tonemap-AGX bake into RGB but not into GT, breaking depth/seg
  alignment. Disable or render two passes deterministically.
- ❌ **Letting the asset library leak.** A model trained on the same
  500 free-marketplace cars overfits brutally. Track asset-id
  histograms and require N ≥ 50 unique assets per class.
- ❌ **Wall-clock-seeded randomisation.** Re-runs produce different
  data; bug repro becomes impossible. Always seed deterministically
  per frame index.
- ❌ **Skipping motion blur / rolling shutter.** Networks trained on
  globally exposed synthetic frames fail on mobile and automotive
  cameras. Model rolling shutter as a per-row time offset.
- ❌ **Rendering only daytime.** Most failure cases are dusk, glare,
  rain, fog. Schedule explicit weather/time-of-day sweeps.
- ❌ **Mixing engines without a unified label schema.** Switching
  Unity ↔ Unreal mid-project requires renormalising semantic-class
  IDs and intrinsics; choose one schema upfront (e.g. COCO, Kitti,
  nuScenes-compatible).
- ❌ **Forgetting GPU determinism flags.** Unreal's TAA and Unity's
  HDRP DLSS are temporal; freezing them or using deterministic AA
  (FXAA, SMAA) is required for reproducibility.
- ❌ **Ignoring licence terms on marketplace assets.** Many assets
  forbid synthetic-data redistribution. Audit assets before release.

## Procedure

1. **Choose engine & toolchain.**
   - Unity: install the *Perception* package; pick HDRP for max
     fidelity, URP for throughput.
   - Unreal: install *Movie Render Queue* + *EasySynth* or NVIDIA
     Omniverse *Replicator* (for USD scenes).

2. **Define the scenario.**
   - List entities (vehicles, pedestrians, props), their spatial
     bounds, count distributions, and label IDs.
   - Define the camera/lidar sensor: intrinsics, extrinsics, noise
     model, exposure curve.
   - Author as a YAML/JSON config under version control.

3. **Configure randomisers (DR).**
   - Unity Perception: implement `Randomizer` subclasses for
     lighting (directional sun angle), HDRI sky, camera FOV jitter,
     object placement, material variation.
   - Unreal/Replicator: build a randomisation graph that samples
     spawn poses, materials, and lights per frame.
   - Ensure each randomiser receives a deterministic per-frame seed
     derived from `(scenario_id, frame_id)`.

4. **Configure ground-truth labelers.**
   - Bounding-box 2D/3D, semantic segmentation, depth (camera-space
     metric, not normalised), surface normals, optical flow, 6-DOF
     instance pose, occlusion %.
   - Verify GT and RGB share the same camera matrix and frame index.

5. **Run a pilot at 100 frames.**
   - Confirm: file naming follows `seed_xxxx/frame_yyyyy.{rgb,depth,seg}`;
     metadata JSON parses; labels visualise correctly with `solo` /
     `replicator-omniverse` viewers.
   - Inspect a random sample manually for label drift.

6. **Scale to the render farm.**
   - Containerise the engine (Unity Linux headless image, Unreal
     headless container with Vulkan).
   - Job queue: shard `(scenario_id × seed_range)` into tasks; emit
     one tarball per task to object storage.
   - Throttle GPU concurrency; engines OOM under heavy parallel
     scenes.

7. **Aggregate & index.**
   - Combine task outputs into a single dataset directory; build a
     manifest (Parquet) listing every frame with its scenario,
     seed, sensor pose, and label hashes.
   - Hand off via the spatial-transfer skill (large binaries,
     UDP-based transport).

8. **Validate on a real probe set.**
   - Train a small baseline on N synthetic frames; evaluate on the
     real probe; confirm metric improves as N grows. If it
     plateaus, return to step 3 and broaden randomisation.

## Validation

After completing the procedure, run:

```sh
# Lint / static checks for engine-side scripts
dotnet format --verify-no-changes      # Unity C#
clang-format --dry-run --Werror **/*.cpp # Unreal C++

# Validate the dataset structure
python -m perception.solo_validator dataset/    # Unity Perception SOLO
python -m replicator.validate dataset/          # Omniverse Replicator

# Statistical checks (synthetic dataset hygiene)
# - Unique-asset count per class >= 50
# - Class balance: max-min ratio <= 4x
# - Lighting / time-of-day distribution covers >= 4 quartiles
# - GT alignment: random IoU(rgb_seg_overlay, depth_overlay) >= 0.99
python -m datasets.stats dataset/ --report stats.json

# Determinism check
python -m datasets.diff_seeds dataset/ --seed 42 --rerun /tmp/dataset_rerun
diff -r dataset/seed_42 /tmp/dataset_rerun/seed_42  # must be empty
```

## See also

- [`../unity/SKILL.md`](../unity/SKILL.md) — Unity-specific scripting
  context for Perception package authoring.
- [`../unreal/SKILL.md`](../unreal/SKILL.md) — Unreal-specific scripting
  for Movie Render Queue and Replicator.
- [`../../ml/training/SKILL.md`](../../ml/training/SKILL.md) — consuming
  the generated dataset.
- [`../../ml/vlm-spatial/SKILL.md`](../../ml/vlm-spatial/SKILL.md) —
  feeding 3D scenes to VLMs for label augmentation.
- [`../../coding/spatial-transfer/SKILL.md`](../../coding/spatial-transfer/SKILL.md)
  — moving multi-TB datasets off the render farm.
- Unity Perception — <https://github.com/Unity-Technologies/com.unity.perception>
- NVIDIA Omniverse Replicator — <https://developer.nvidia.com/omniverse/replicator>
- Unreal EasySynth — <https://github.com/ydrive/EasySynth>
