---
name: coding-xr
description: "Immersive XR runtime work on WebXR and OpenXR: session lifecycle, reference spaces, input sources, layers, anchors, hit testing, and performance budgets. Triggers: WebXR, OpenXR, VR, AR, MR, headset, controller, hand tracking, anchors, hit test, immersive-vr, immersive-ar."
domain: coding
subdomain: xr
facets:
  - lang:typescript
  - lang:javascript
  - lang:cpp
  - lang:csharp
  - target:browser
  - target:headset
  - target:mobile
  - vendor:khronos
applies_when:
  any_of:
    - "task targets a WebXR `immersive-vr` or `immersive-ar` session"
    - "task uses the OpenXR loader, layers, or runtime extensions (Meta, Pico, Vision Pro, SteamVR)"
    - "task wires controller / hand-tracking input, reference spaces, or world anchors"
    - "task implements hit testing, plane detection, depth, or passthrough composition"
    - "task profiles or budgets frame time, reprojection, or motion-to-photon latency"
version: 0.1.0
---
# Coding / Immersive XR (WebXR & OpenXR)

## When to use

Open this skill when the deliverable runs *inside* a head-mounted or
handheld XR session and is bound by the strict frame-pacing rules of
WebXR or OpenXR. For browser GPU work that is *not* in an XR session,
use [`../webgpu/SKILL.md`](../webgpu/SKILL.md). For 3D Gaussian
Splatting payloads streamed into an XR viewer, compose this skill
with [`../../3dcg/3dgs/SKILL.md`](../../3dcg/3dgs/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Session vs context** — a `XRSession` (WebXR) / `XrSession`
  (OpenXR) is the *only* place head-pose-correct rendering may
  happen. Outside the session you have no head pose and must not
  block its frame loop.
- **Reference spaces** — `local`, `local-floor`, `bounded-floor`,
  `unbounded` (WebXR); `LOCAL`, `STAGE`, `VIEW`, `UNBOUNDED`
  (OpenXR). Pick the *weakest* space that meets the UX; stronger
  spaces (`bounded-floor`) may be unavailable on some runtimes and
  must have a graceful fallback.
- **`xrFrame` / `xrWaitFrame` / `xrBeginFrame` / `xrEndFrame`** —
  the runtime, not your engine, owns the frame clock. Read pose
  *inside* the frame callback only; never cache it across frames.
- **Views and viewports** — multiview rendering exposes 2 (stereo)
  or more views per frame, each with its own projection and
  viewport. Use `multiview` / `OVR_multiview2` / OpenXR multiview
  layer to render both eyes in one draw stream.
- **Input sources** — WebXR `XRInputSource` (gamepad-like + grip
  + targetRay spaces); OpenXR action sets bound to interaction
  profiles (`/interaction_profiles/khr/simple_controller`,
  `/oculus/touch_controller`, `/htc/vive_controller`, …). Never
  hard-code per-vendor button indices; always go through the
  profile / action.
- **Hand tracking** — WebXR `XRHand` (25 joints, palm → tip);
  OpenXR `XR_EXT_hand_tracking` (26 joints incl. palm). Both
  expose pose *and* radius per joint, but availability and update
  rate are runtime-dependent.
- **Anchors and persistence** — `XRAnchor` (WebXR) /
  `XR_FB_spatial_entity` / `XR_MSFT_spatial_anchor` (OpenXR) pin
  content to the real world. Persistence (saving an anchor across
  sessions) is a separate, runtime-specific extension.
- **Hit testing & planes** — `XRHitTestSource` /
  `XR_MSFT_scene_understanding` / `XR_FB_scene` expose real-world
  geometry. Treat results as *suggestions*; topology can change
  every frame.
- **Layers** — WebXR `XRCompositionLayer` (quad, cylinder,
  equirect, projection) / OpenXR composition layers render at the
  runtime's native resolution and refresh, *bypassing* your
  swapchain. Use them for HUD, video, and text — they look sharp
  and avoid reprojection blur.
- **Foveated rendering** — fixed (`XR_FB_foveation`,
  `XR_FB_foveation_configuration`) or eye-tracked
  (`XR_FB_eye_tracking_social`, `XR_FB_foveation_vulkan`). Saves
  GPU time at the cost of peripheral detail.
- **Reprojection / asynchronous timewarp** — the runtime
  re-projects your last submitted frame to the head pose at
  display time. Drop a frame and you'll judder; submit at the
  wrong pose and you'll get warp artefacts.
- **Motion-to-photon budget** — keep ≤ 11 ms (90 Hz) or ≤ 8.3 ms
  (120 Hz) end-to-end. Anything slower triggers reprojection and,
  past two frames, sim-sickness.
- **Passthrough / AR composition** — `XR_FB_passthrough`,
  `XR_HTC_passthrough`, WebXR `immersive-ar` blend mode
  (`opaque`, `additive`, `alpha-blend`). Premultiplied alpha is
  the contract on most runtimes.

## Recommended patterns

1. **Feature-detect, then fall back.** Probe
   `navigator.xr.isSessionSupported('immersive-ar')` and
   `XR_KHR_*` extensions before requesting features. Ship a
   non-XR mode for unsupported devices.
2. **Request only the features you use.** WebXR
   `requiredFeatures` aborts the session if missing;
   `optionalFeatures` degrades gracefully. Mirror this in
   OpenXR by enabling extensions conditionally.
3. **Drive the loop from the runtime's frame callback**
   (`session.requestAnimationFrame` / `xrWaitFrame`). Your engine
   tick must be a *callee*, not a caller, of this loop.
4. **Bind input through actions, not raw buttons.** WebXR: use
   `XRInputSource.gamepad` mappings tied to profiles. OpenXR:
   action sets + suggested bindings per interaction profile.
5. **Pick the weakest reference space that works.** Prefer
   `local-floor` over `bounded-floor`; only request `unbounded`
   for world-scale AR.
6. **Use composition layers for UI.** Quad layers for menus,
   cylinder for curved HUDs, equirect for skyboxes; all render at
   native res and skip reprojection blur.
7. **Single-pass stereo by default** (`OVR_multiview2`,
   OpenXR multiview). Halves CPU draw cost; mind shader uniform
   indexing differences.
8. **Budget per frame, not per scene.** Target ≤ 8 ms GPU and
   ≤ 4 ms CPU at 90 Hz; reserve the rest for compositor + warp.
9. **Throttle anchors and hit tests.** Recreate hit-test sources
   on user intent (e.g. trigger pull), not every frame.
10. **Handle session lifecycle explicitly.** Listen for
    `end`, `visibilitychange`, `inputsourceschange`,
    `selectstart` / `selectend`; release GPU resources on
    `end`.
11. **Test on real hardware early.** Emulators (WebXR API
    Emulator, OpenXR runtime simulators) miss reprojection,
    foveation, and tracking-loss behaviour.

## Pitfalls (subdomain-specific)

- ❌ **Caching `XRPose` across frames.** It is only valid for the
  current `XRFrame`; reading it later returns stale data.
- ❌ **Calling `requestAnimationFrame` on `window` inside an XR
  session.** That's the 2D loop and will tear; always use
  `session.requestAnimationFrame`.
- ❌ **Hard-coding controller button indices.** Indices vary
  per vendor and per WebXR profile; route through
  `gamepad.mapping === 'xr-standard'` or OpenXR actions.
- ❌ **Mixing world-locked and head-locked content in one
  draw.** Head-locked UI in the projection layer judders during
  reprojection; put it on a quad layer instead.
- ❌ **Ignoring `visibilitychange`.** When the user removes the
  headset or the system menu opens, your loop keeps running and
  burning battery; pause it.
- ❌ **Submitting frames at the wrong pose.** You must render
  with the pose returned by *this* frame's callback, not the
  previous one.
- ❌ **Requesting `bounded-floor` without a fallback.** Many
  runtimes (mobile AR) don't expose it; the session creation
  fails outright.
- ❌ **Using non-premultiplied alpha in AR composition.** Most
  runtimes assume premultiplied; you'll see bright fringes.
- ❌ **High-frequency haptics in tight loops.** WebXR
  `gamepad.hapticActuators[].pulse()` is rate-limited; queue or
  debounce.
- ❌ **Allocating in the frame callback.** GC pauses kill VR
  comfort; pre-allocate matrices, vectors, and pose buffers.
- ❌ **Assuming hand and controller are mutually exclusive.**
  On Quest the user can switch mid-session; handle both
  `inputSource.hand` *and* `inputSource.gamepad` per frame.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Pick the runtime.** WebXR (browser, no install) vs OpenXR
   (native engine, broadest hardware). Hybrid: WebXR + OpenXR
   layer via WebView is possible but rare.
2. **Enumerate required features.** Reference spaces, input
   profiles, hand tracking, anchors, hit testing, passthrough.
   Mark each `required` or `optional`.
3. **Bootstrap the session.** WebXR
   `navigator.xr.requestSession('immersive-vr', { … })`; OpenXR
   `xrCreateInstance` → `xrCreateSession` with the matching
   graphics binding (D3D/Vulkan/OpenGL/Metal).
4. **Set up the swapchain(s).** One projection layer + zero or
   more composition layers. Use multiview where supported.
5. **Wire the frame loop.** Acquire pose → cull → render views →
   submit. Profile every step; never skip `xrEndFrame` /
   `XRSession`'s frame submission.
6. **Bind input.** Build action sets / map `XRInputSource`s; emit
   high-level events (`select`, `squeeze`, `pinch`).
7. **Add world understanding** as needed: hit-test, anchors,
   planes, mesh, depth, passthrough.
8. **Profile on device.** GPU time per view, CPU per loop,
   reprojection ratio, dropped frames. Use Meta OVR Metrics
   Tool, RenderDoc, or the WebXR Performance API.
9. **Validate on at least two runtimes** (e.g. Quest + PCVR or
   Quest + Vision Pro) — interaction profiles diverge.
10. **Lock down a comfort pass.** Fixed-foveation level, IPD
    handling, smooth vs snap turning, vignette on translation.

## Validation

After completing the procedure, run:

```sh
# WebXR (browser)
npx playwright test xr/                     # session lifecycle smoke
npm run lint -- src/xr                      # eslint + tsc
npx web-test-runner xr/**/*.test.ts         # unit tests with WebXR mock

# OpenXR (native)
xrgears                                     # Khronos sample sanity run
xrtools validate-layer ./build/MyLayer.so   # layer manifest check
ctest --label-regex xr                      # gtest harness with mock runtime
ovrgpuprofiler --capture frame --count 240  # frame-time + reprojection
```

## See also

- [`../webgpu/SKILL.md`](../webgpu/SKILL.md) — for the GPU
  pipeline running inside `XRWebGLLayer` / native swapchains.
- [`../../3dcg/3dgs/SKILL.md`](../../3dcg/3dgs/SKILL.md) — for
  splat datasets composited into an XR session.
- [`../spatial-audio/SKILL.md`](../spatial-audio/SKILL.md) — for
  HRTF / ambisonic audio aligned to the head pose.
- WebXR Device API — <https://www.w3.org/TR/webxr/>
- OpenXR specification — <https://registry.khronos.org/OpenXR/>
- WebXR samples — <https://immersive-web.github.io/webxr-samples/>
- Khronos OpenXR SDK — <https://github.com/KhronosGroup/OpenXR-SDK>
