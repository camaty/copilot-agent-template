---
name: coding-spatial-audio
description: "Spatial audio engineering: HRTF binaural rendering, ambisonics (1st–7th order), Web Audio API, real-time DSP, room acoustics. Triggers: spatial audio, 3D audio, binaural, HRTF, ambisonics, Ambix, FOA, HOA, Web Audio, PannerNode, Resonance Audio, Steam Audio, AudioWorklet."
domain: coding
subdomain: spatial-audio
facets:
  - lang:typescript
  - lang:javascript
  - lang:cpp
  - lang:rust
  - target:browser
  - target:headset
  - target:mobile
  - vendor:webaudio
applies_when:
  any_of:
    - "task spatialises sources with HRTF / binaural rendering for headphones"
    - "task encodes, rotates, or decodes ambisonic (FOA / HOA) audio"
    - "task implements Web Audio graphs (PannerNode, ConvolverNode, AudioWorklet)"
    - "task ports Steam Audio / Resonance Audio / Oculus Audio SDK pipelines"
    - "task tunes real-time DSP latency, occlusion, reverb, or reflections"
version: 0.1.0
---
# Coding / Spatial Audio

## When to use

Open this skill when the deliverable produces, processes, or
spatialises audio in a 3D scene — XR sessions, games, virtual
production, or accessibility audio. For generic browser GPU work,
use [`../webgpu/SKILL.md`](../webgpu/SKILL.md). For voice-driven
ML pipelines (TTS / ASR), prefer [`../../ml/inference/SKILL.md`](../../ml/inference/SKILL.md)
and treat the spatialiser as a downstream stage.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **HRTF (Head-Related Transfer Function)** — per-ear FIR filters
  that approximate the diffraction of sound around the listener's
  head and pinnae. Convolved per ear, per source, *every block*.
- **ITD / ILD** — Interaural Time Difference and Interaural Level
  Difference; the two primary cues HRTFs encode (≤ ~700 µs ITD,
  up to ~20 dB ILD).
- **Ambisonics** — full-sphere periphonic format. *Order N* uses
  `(N + 1)²` channels (1st-order = 4, 3rd-order = 16,
  7th-order = 64). Encode: directional → channels; rotate: head
  pose → matrix multiply on channels; decode: channels → speakers
  or virtual binaural HRTF.
- **Channel ordering & normalisation** — **Ambix** (ACN ordering,
  SN3D normalisation) is the de-facto standard for files and
  streams. **FuMa** is legacy; convert at ingest.
- **B-format / A-format** — A-format = raw mic capsules;
  B-format = decoded WXYZ (1st-order). Always work in B-format /
  Ambix downstream.
- **Distance attenuation** — inverse, inverse-square, or linear
  (Web Audio `PannerNode.distanceModel`); pair with a soft
  `refDistance` and `maxDistance` clip to avoid divide-by-zero.
- **Doppler** — sample-rate-correct Doppler must resample, not
  retune, the source. Most engines disable it by default.
- **Occlusion / obstruction / exclusion** — occlusion = both
  direct and reverb attenuated; obstruction = direct only;
  exclusion = reverb only. Drive from raycasts, not just
  distance.
- **Early reflections + late reverb** — first 80 ms encodes
  spatial cues (room size, source direction); after that the
  reverberation tail is largely diffuse. Hybrid engines simulate
  early reflections geometrically and switch to a feedback delay
  network (FDN) or convolution for the tail.
- **Convolution reverb** — IR length × sample rate × source count
  is your CPU bill. Use partitioned convolution (FFT block size
  ≥ buffer) for IRs > 1 s.
- **AudioWorklet** — runs in the audio thread at ~3 ms quanta
  (128 samples @ 44.1 kHz). Anything more than vector math and
  ring buffers belongs in the main thread or a `Worker`.
- **Buffer-size / latency budget** — XR comfort: ≤ 20 ms
  end-to-end. Web Audio default quantum is 128 samples; native
  engines typically run 64–256 samples. Lower buffers raise CPU
  and dropout risk.
- **Sample-rate hygiene** — Web Audio resamples to the device
  rate (typically 48 kHz). Author IRs, HRTFs, and ambisonic
  assets at the same rate to avoid hidden lowpass.

## Recommended patterns

1. **Use ambisonics as the bus, HRTF as the sink.** Encode all
   sources into a single Nth-order ambisonic bus, rotate by head
   pose, then decode once via a virtual-loudspeaker HRTF. Cost
   scales with *bus order*, not source count.
2. **Pin head rotation to the audio block.** Read pose at the
   start of each render quantum; interpolate linearly across
   samples to avoid zipper noise during fast head motion.
3. **Pre-load and cache HRTF / IR sets.** Decoding a SOFA file or
   IR WAV inside the audio thread will glitch; do it on the main
   thread and pass `AudioBuffer` / `Float32Array` references.
4. **Partitioned convolution for long IRs.** ≥ 1 s reverbs need
   non-uniform partitioned (Gardner) FFT convolution to stay
   under budget at 128-sample quanta.
5. **Group sources by region and acoustic.** One ConvolverNode
   per *space* (room, outside, tunnel), not per source. Sources
   send to the matching reverb bus.
6. **Soft-clip at the master, never at sources.** A single output
   limiter prevents clipping under crowd scenes; per-source
   clamps lose loudness perception.
7. **Smooth all parameter changes.** Ramp gain, position, and
   filter frequency over ≥ 5 ms (`linearRampToValueAtTime`); set
   `automationRate: 'k-rate'` only for non-audible params.
8. **Decouple gameplay tick from audio tick.** Push events to a
   lock-free SPSC queue; the audio thread polls per quantum and
   never blocks.
9. **Mirror your XR coordinate system.** Web Audio is right-
   handed Y-up; OpenXR is right-handed Y-up; Unreal is left-
   handed Z-up. Pick the listener frame and convert at the
   boundary, not in the audio thread.
10. **Render an ambisonic bed for music and ambience.** Decoded
    once per frame and head-rotated; drastically cheaper than
    one HRTF per stem.

## Pitfalls (subdomain-specific)

- ❌ **Allocating in the audio callback / AudioWorklet `process`.**
  Any GC pause = audible click. Use ring buffers and pre-sized
  typed arrays.
- ❌ **Using `AudioListener.setPosition()` (deprecated).** Use
  the `positionX/Y/Z` AudioParams with ramps.
- ❌ **Mixing FuMa and Ambix without conversion.** WX/Y/Z order
  and SN3D vs maxN scaling cause silent left/right swaps.
- ❌ **Per-source HRTF convolution in a 100-source scene.**
  CPU explodes; bus through ambisonics or virtualise.
- ❌ **Updating `PannerNode` parameters from `setTimeout`.**
  Jitter audible as panning chatter; use `setValueAtTime`
  scheduled to `audioContext.currentTime`.
- ❌ **Ignoring sample-rate mismatch.** A 44.1 kHz HRTF on a
  48 kHz context is not catastrophic, but a 22 kHz IR is — high
  frequencies vanish.
- ❌ **Designing HRTFs from a single subject.** One HRTF set
  fits poorly for ~30 % of listeners. Provide selection or use
  a generic plus front-back reversal cue (head-tracking).
- ❌ **Running occlusion raycasts every audio block.** Throttle
  to gameplay tick and interpolate gain in the audio thread.
- ❌ **Boosting bass to "feel 3D".** Low frequencies (< 500 Hz)
  carry weak directional cues; spatial localisation is in
  ~1–6 kHz. EQ won't fix a missing HRTF.
- ❌ **Forgetting `AudioContext.resume()` after a user gesture.**
  Browsers suspend the context until the first interaction;
  silent failure on autoplay otherwise.
- ❌ **Rotating ambisonics with naïve Euler matrices.** Use
  proper SH (Wigner-D / shelf-filter) rotations; Euler causes
  gimbal artefacts at the poles.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Decide the listener model.** Headphones (binaural / HRTF)
   vs loudspeakers (VBAP / ambisonic decode) vs both. The bus
   topology follows.
2. **Pick the spatial bus.** First-order ambisonics for mobile/
   web; 3rd-order for VR comfort; 7th-order for high-end VFX.
3. **Choose / load HRTF and IR assets** (SOFA for HRTF, WAV for
   IRs). Resample to the device rate at load time.
4. **Build the graph.** Sources → distance + occlusion gain →
   ambisonic encoder → (rotation by head pose) → reverb sends
   → virtual binaural decoder → master limiter → destination.
5. **Wire head pose.** From XR session per frame; interpolate
   in the audio thread.
6. **Add reverb zones.** One IR / FDN per acoustic region;
   crossfade on transitions.
7. **Smoke-test on real headphones and in-headset.** PC speakers
   mask many problems.
8. **Profile on the audio thread.** Render-time budget per
   quantum, dropout count, glitch rate. Web Audio:
   `AudioContext.baseLatency` and the Performance Inspector.
9. **A/B against a flat stereo mix** to verify the spatialiser
   adds, not subtracts, intelligibility.
10. **Document the listener axis convention** in code comments
    and the asset manifest.

## Validation

After completing the procedure, run:

```sh
# Web Audio
npm run lint -- src/audio
npx web-test-runner audio/**/*.test.ts        # AudioWorklet tested via OfflineAudioContext
npx playwright test audio/                    # cross-browser smoke

# Native (Steam Audio / Resonance / Oculus Audio)
ctest --label-regex audio                     # gtest with golden buffers
sox golden.wav under_test.wav -n stat 2>&1 \
    | grep "RMS amplitude"                    # bit-exact / RMS diff
ffmpeg -i out.wav -af "loudnorm=print_format=json" -f null - \
    2>&1 | grep integrated_loudness           # LUFS sanity
```

## See also

- [`../xr/SKILL.md`](../xr/SKILL.md) — for the head-pose source
  feeding the listener.
- [`../../ml/inference/SKILL.md`](../../ml/inference/SKILL.md) —
  for TTS / ASR producing or consuming audio streams.
- Web Audio API — <https://webaudio.github.io/web-audio-api/>
- AES SOFA (HRTF) format — <https://www.sofaconventions.org/>
- Ambix specification — <https://www.ambisonic.info/ambisonics.html>
- Steam Audio docs — <https://valvesoftware.github.io/steam-audio/>
- Google Resonance Audio — <https://resonance-audio.github.io/resonance-audio/>
