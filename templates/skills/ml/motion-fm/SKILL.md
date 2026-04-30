---
name: ml-motion-fm
description: "Training and applying motion foundation models for BVH extraction and VRM avatar retargeting. Triggers: motion, BVH, VRM, skeleton, kinematics, motion generation, retarget, monocular video, autoregressive motion."
domain: ml
subdomain: motion-fm
facets:
  - lang:python
  - format:bvh
  - format:vrm
applies_when:
  any_of:
    - "task extracts skeletal kinematics from a monocular RGB video"
    - "task generates or retargets BVH animation data"
    - "task applies motion data to VRM or similar avatar formats"
    - "task trains or fine-tunes an autoregressive motion generation model"
version: 0.1.0
---
# Machine Learning / Motion Foundation Model

## When to use

Open this skill when the goal is to extract per-frame skeletal kinematics from a
single RGB video, generate BVH animation clips with an autoregressive model, or
retarget those clips to a VRM or other standard avatar rig. For generic model
training that is not motion-specific, see [`../training/SKILL.md`](../training/SKILL.md).
For serving a trained motion model behind an API, see
[`../inference/SKILL.md`](../inference/SKILL.md).

If the task does not match the activation hints, return to [`../INDEX.md`](../INDEX.md) and pick another subdomain.

## Canon (must-know terms and invariants)

- **BVH (Biovision Hierarchy)** — text-based skeletal animation format: a
  hierarchy section defines joint names and offsets; a motion section records
  per-frame channel values (rotation + optional translation). The root joint
  carries global position; all other joints carry local rotations only.
- **VRM** — glTF 2.0 extension for humanoid avatars; defines a normalised
  humanoid bone map (HumanBodyBones) that every compliant rig must satisfy.
  Retargeting maps source skeleton joint names → VRM bone IDs.
- **Monocular pose estimation** — recovering 3-D joint positions from a single
  camera without depth sensors. Outputs are noisy; smooth with a Kalman filter
  or learned temporal model before writing BVH.
- **Motion foundation model (MFM)** — an autoregressive (transformer or
  Mamba-based) model pre-trained on large motion-capture corpora that can
  generate, interpolate, or complete BVH clips conditioned on text, audio,
  or seed frames.
- **Retargeting** — mapping skeletal animation from a source rig (any joint
  count / proportions) to a target rig (VRM humanoid map). Must preserve
  contact constraints (feet on ground, hands on surface).
- **Global trajectory vs. local pose** — always separate root translation from
  joint rotations during training; mixing them degrades both tasks.

For general ML terminology, see [`../training/SKILL.md`](../training/SKILL.md).

## Recommended patterns

1. **Decouple pose lifting from motion modelling** — run a dedicated 2-D/3-D
   pose estimator (MediaPipe, ViTPose, 4D-Humans) to produce per-frame joint
   coordinates, then feed the resulting sequence to the motion foundation model
   as a conditioning signal rather than raw video.
2. **Separate root trajectory from local rotations** — encode root XZ
   translation and heading as a separate stream; keep local joint rotations in
   a rotation-6D or quaternion representation to avoid gimbal lock.
3. **Smooth before writing BVH** — apply an exponential moving average or
   one-euro filter per channel after pose lifting; jerky raw estimates break
   physics-based cloth and IK.
4. **Use a canonical T-pose as the retargeting reference** — normalise source
   and target rigs to T-pose before computing the mapping matrix; avoids
   rest-pose offsets corrupting the retargeted clip.
5. **Validate contact constraints after retargeting** — foot-skating is the
   most visible artefact; run a foot-contact detector and apply a simple IK
   correction pass if skating exceeds 1 cm/frame.
6. **Pin the motion-capture corpus version** — large public datasets (AMASS,
   HumanAct12, BABEL) have versioned splits; record the exact split and any
   filtering applied alongside every checkpoint.

## Pitfalls (subdomain-specific)

- ❌ **Training on raw BVH without normalising rest pose** — different MoCap
  suits produce different T-poses; blend shapes and animations will be
  incorrect after retargeting if rest poses differ.
- ❌ **Euler angles in training data** — gimbal lock at extreme joint angles
  corrupts gradients; convert to rotation-6D or quaternions before any model
  sees the data.
- ❌ **Ignoring frame rate mismatch** — BVH and VRM animations each have an
  explicit frame rate; resampling without anti-aliasing introduces jitter.
- ❌ **Assuming joint count parity between source and target** — the VRM
  humanoid map has 54 defined bones; a MoCap skeleton may have hundreds;
  always use the name→bone-ID mapping, never positional index.
- ❌ **Dropping global translation during retargeting** — VRM avatars need
  absolute root position for ground-plane alignment; discarding it produces
  avatars that float or sink.

Domain-wide pitfalls live in [`../training/SKILL.md`](../training/SKILL.md).

## Procedure

1. **Prepare the motion corpus.** Download and unpack AMASS (or your
   proprietary MoCap data). Convert all clips to a canonical representation:
   rotation-6D local joints + separate root trajectory. Split train/val/test
   deterministically; record splits and data hashes.
2. **Run 2-D/3-D pose lifting on input video.** Feed source RGB video through a
   pretrained pose estimator (e.g. `mmpose`, `4D-Humans`). Apply a temporal
   smoothing filter per joint channel. Output: `T × J × 3` joint positions in
   camera space.
3. **Convert to BVH.** Use a rig definition (joint names, parent chain, rest
   offsets) to produce a valid BVH file. Validate channel counts and frame
   count match the BVH header.
4. **Train or fine-tune the MFM.** Load a pre-trained checkpoint (e.g.
   MotionGPT, MDM, FLAME). Fine-tune on your corpus with the frozen or
   partially frozen backbone; track validation loss and FID per epoch.
5. **Generate or retarget the BVH clip.** Either synthesise a clip from a text
   or seed-frame prompt, or pass the lifted BVH through the model for
   completion/style transfer.
6. **Retarget to VRM.** Map source joint names to VRM `HumanBodyBones`. Apply
   rest-pose correction. Run foot-contact detection; apply IK correction if
   skating > threshold. Export as `.vrm` + embedded animation or as a separate
   `.bvh` / glTF animation track.
7. **Validate.** Run the validation suite below; review rendered animation in a
   VRM viewer (three-vrm, UniVRM) for visual artefacts.

## Validation

```sh
# Lint / static checks
ruff check .
mypy src/ --ignore-missing-imports

# Unit + integration tests
pytest tests/ -v

# Motion-specific checks:
# - BVH parser round-trip: write then re-read; joint positions must match within 1e-4.
# - Retargeting smoke test: load retargeted VRM in three-vrm and assert no NaN transforms.
# - FID (Fréchet Inception Distance) on held-out motion clips must not regress > 5 % vs. baseline.
# - Foot-skating metric: mean foot velocity during contact frames < 1 cm/frame.
```

## See also

- [`../training/SKILL.md`](../training/SKILL.md) — generic training discipline and experiment tracking
- [`../inference/SKILL.md`](../inference/SKILL.md) — serving a trained motion model behind an API
- [`../../3dcg/garment-sim/SKILL.md`](../../3dcg/garment-sim/SKILL.md) — cloth simulation on the resulting animated avatar
- AMASS dataset — <https://amass.is.tue.mpg.de/>
- VRM specification — <https://vrm.dev/en/univrm/humanoid/humanoid_target/>
- MotionGPT — <https://motion-gpt.github.io/>
