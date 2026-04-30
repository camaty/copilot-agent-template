---
name: gameengine-unity
description: "Unity engine development: C# scripting, MonoBehaviour, ScriptableObject, URP/HDRP, DOTS/ECS, Addressables, asset pipeline. Triggers: unity, monobehaviour, prefab, urp, hdrp, addressables, scriptableobject, dots, ecs, burst, jobs, il2cpp."
domain: gameengine
subdomain: unity
facets:
  - lang:csharp
  - pipeline:urp
  - pipeline:hdrp
  - target:pc
  - target:mobile
  - target:vr
  - vendor:unity
applies_when:
  any_of:
    - "task targets Unity 2021 LTS or newer (preferred 2022 LTS / 6 LTS)"
    - "task involves MonoBehaviour, ScriptableObject, prefabs, scenes, or Addressables"
    - "task involves URP, HDRP, Shader Graph, or VFX Graph"
    - "task involves DOTS / Entities / Burst / Jobs"
    - "task ships an Editor extension or build pipeline tooling"
version: 0.1.0
---
# Game Engine / Unity

## When to use

Open this skill when the task modifies a Unity project — scripts,
scenes, prefabs, render pipeline assets, build settings, or editor
tooling. For purely backend services consumed by Unity, prefer
`coding`. For synthetic-data generation with the Perception package,
see [`../synthetic-data/SKILL.md`](../synthetic-data/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **MonoBehaviour lifecycle** — `Awake` → `OnEnable` → `Start` →
  `Update` → `LateUpdate` → `OnDisable` → `OnDestroy`. Order across
  objects within a phase is unspecified; declare explicit dependencies.
- **ScriptableObject** — asset-backed data container; preferred for
  shared config and data-driven design. Survives play-mode resets.
- **Prefab variant** — inheritance for prefabs; overrides cascade
  from base. Nested prefabs are the modern composition primitive.
- **Addressables** — modern asset addressing/loading with content
  catalog and remote bundles. Replaces `Resources/` and direct
  `AssetBundles`.
- **Render pipelines** — Built-in (legacy), URP (broad target,
  mobile/VR/PC), HDRP (high-end PC/console). Mutually incompatible
  at the shader level; pick one per project.
- **Domain reload** — Editor reloads the C# domain on script change;
  static state resets unless `[InitializeOnEnterPlayMode]` /
  `[RuntimeInitializeOnLoadMethod]` configured.
- **Assembly Definition (asmdef)** — module boundary; controls
  references, platforms, and editor-only code. Speeds up iteration.
- **DOTS / Entities / Burst / Jobs** — data-oriented stack for
  CPU-heavy gameplay; ECS world, struct components, Burst-
  compiled jobs that bypass GC.
- **IL2CPP** — AOT compilation for iOS/console/WebGL builds.
  Reflection paths must survive code stripping (`link.xml`).
- **Profiler markers** — `using (new ProfilerMarker("Foo").Auto())
  { … }` — instrument hot paths so the Profiler shows your code.
- **Job system + Burst** — multithreaded math without GC; struct
  jobs scheduled across worker threads; Burst HPC# subset is
  vectorised.

## Recommended patterns

1. **Composition over inheritance.** Prefer many small
   `MonoBehaviour`s and `ScriptableObject` data assets over deep
   class hierarchies.
2. **Data-driven design via `ScriptableObject`** for tunables;
   designers edit assets, not code; assets diff cleanly.
3. **Use Addressables from day one.** `Resources/` and direct
   `AssetBundle` paths are dead ends.
4. **Pool frequently-spawned objects** (bullets, VFX);
   `Instantiate`/`Destroy` allocate and trigger GC.
5. **Cache component lookups.** `GetComponent` in `Update` is a
   recurring perf bug; cache in `Awake`.
6. **Edit-Mode + Play-Mode tests** via Unity Test Framework; keep
   editor logic out of runtime assemblies.
7. **Assembly Definition files** to enforce layering and shrink
   iteration time. Editor-only code in editor-only asmdefs.
8. **Use Profiler markers + Deep Profile sparingly**; profile on
   target device, not in the Editor.
9. **Lock the render pipeline early.** Switching URP↔HDRP late is
   weeks of shader work.
10. **Burst-compile hot math**; mark methods with `[BurstCompile]`
    and structs with `[BurstCompile(CompileSynchronously=true)]`
    in tests so failures surface immediately.
11. **Use `new InputSystem`** (Input System package), not legacy
    `Input.GetKey`; survives multi-platform input variation.
12. **Author shaders in Shader Graph** for portability across URP
    and HDRP targets; hand-written HLSL for last-mile perf only.

## Pitfalls (subdomain-specific)

- ❌ **Allocating in `Update`.** `new`, LINQ, `string` concatenation
  — all GC pressure per frame. Use `StringBuilder`, pooled lists,
  `for` over `foreach` on `List<T>`.
- ❌ **Synchronous scene loads on the main thread.** Use
  `LoadSceneAsync`; show a progress UI.
- ❌ **Mixing render pipelines.** A URP shader renders pink under
  HDRP and vice versa.
- ❌ **Saving editor-only state in serialised fields without
  `#if UNITY_EDITOR`** — ships in builds, bloats memory.
- ❌ **Large prefabs as a single asset** — merge conflicts become
  unrecoverable. Split via nested prefabs or prefab variants.
- ❌ **`FindObjectOfType` on the hot path.** O(n) over the scene;
  cache references at startup.
- ❌ **Reflection-heavy serialisation** without `link.xml` — IL2CPP
  strips types, runtime crashes on console/mobile.
- ❌ **Coroutines holding scene references across scene loads.**
  Stop them in `OnDisable`/`OnDestroy`.
- ❌ **Static state surviving play mode** when domain reload is
  disabled — old values bleed into new runs. Reset explicitly.
- ❌ **Deep Inspector overrides on prefab instances** — each scene-
  level override increases save churn and diff noise.
- ❌ **Direct `Camera.main` access per frame** — performs a tag
  search; cache once.
- ❌ **`async void` in Unity callbacks.** Exceptions vanish; use
  `UniTask` or wrap in a coroutine.

Domain-wide pitfalls (when present) live in `../_shared/pitfalls.md`.

## Procedure

1. **Confirm Unity version** (LTS preferred) and active render
   pipeline. Pin in `ProjectSettings` and CI image.
2. **Identify whether the change is runtime, editor, or build-
   pipeline**; place code in the matching assembly (asmdef).
3. **Author data via ScriptableObjects** and reference them through
   Addressables or serialized fields.
4. **Write Edit-Mode tests for pure logic; Play-Mode tests for
   MonoBehaviour interactions.**
5. **Profile with the Unity Profiler** before optimising; verify GC
   alloc per frame is zero on hot paths; capture on target device.
6. **For DOTS work**, isolate Burst-compiled jobs in their own
   asmdef + tests; assert determinism per seed.
7. **Build for the target platform in CI** to catch IL2CPP /
   stripping issues early; smoke-test the resulting build.
8. **Localise asset moves** with `*.meta` file discipline; never
   rename outside the Editor (breaks GUIDs).

## Validation

After completing the procedure, run:

```sh
# Lint / format
dotnet format Unity.sln --verify-no-changes
# Unity static analysis (Project Auditor) is optional but
# recommended on hot-path assemblies.

# Unity batch build (Linux/macOS path; adjust for Windows)
unity-editor -batchmode -nographics -quit \
    -projectPath . \
    -buildTarget StandaloneLinux64 \
    -executeMethod BuildPipeline.Run \
    -logFile -

# Edit Mode + Play Mode tests via Unity Test Framework
unity-editor -batchmode -nographics -projectPath . \
    -runTests -testPlatform editmode -testResults editmode.xml -logFile -
unity-editor -batchmode -nographics -projectPath . \
    -runTests -testPlatform playmode -testResults playmode.xml -logFile -

# IL2CPP smoke build (catches stripping / reflection issues)
unity-editor -batchmode -nographics -quit \
    -projectPath . -buildTarget Android \
    -executeMethod BuildPipeline.RunIL2CPP -logFile -

# Profiler regression: open .data file in CI and assert frame budget
python tools/profile_check.py captures/latest.data --max-ms 16.6
```

## See also

- [`../unreal/SKILL.md`](../unreal/SKILL.md) — when a project shares
  pipelines across Unity and Unreal.
- [`../synthetic-data/SKILL.md`](../synthetic-data/SKILL.md) — Unity
  Perception for ML data generation.
- [`../godot/SKILL.md`](../godot/SKILL.md) — open-source alternative.
- Unity Manual: Scripting, Render Pipelines, Addressables, Profiler.
- Unity DOTS / Entities documentation.
