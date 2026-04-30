---
name: gameengine-unity
description: "Unity engine development: C# scripting, MonoBehaviour, ScriptableObject, URP/HDRP, and asset pipeline. Triggers: unity, monobehaviour, prefab, urp, hdrp, addressables."
domain: gameengine
subdomain: unity
facets:
  # - lang:csharp
  # - pipeline:urp
  # - pipeline:hdrp
  # - target:pc
  # - target:mobile
applies_when:
  any_of:
    - "task targets Unity 2021 LTS or newer"
    - "task involves MonoBehaviour, ScriptableObject, prefabs, scenes, or Addressables"
    - "task involves URP, HDRP, Shader Graph, or VFX Graph"
version: 0.1.0
---
# Game Engine / Unity

## When to use

The task modifies a Unity project — scripts, scenes, prefabs, render pipeline assets, build settings, or editor tooling. For purely backend services consumed by Unity, prefer `coding`.

## Canon

- **MonoBehaviour lifecycle** — `Awake` → `OnEnable` → `Start` → `Update` → `LateUpdate` → `OnDisable` → `OnDestroy`. Order across objects is unspecified within a phase.
- **ScriptableObject** — asset-backed data container; preferred for shared config and data-driven design.
- **Prefab variant** — inheritance for prefabs; overrides cascade.
- **Addressables** — modern asset addressing/loading; replaces Resources and direct AssetBundles.
- **Render pipelines** — Built-in (legacy), URP (broad target), HDRP (high-end). They are mutually incompatible at the shader level.
- **Domain reload** — Editor reloads the C# domain on script change; static state resets unless flagged.

## Recommended patterns

1. **Composition over inheritance.** Prefer many small `MonoBehaviour`s and `ScriptableObject` data assets over deep class hierarchies.
2. **Data-driven design via `ScriptableObject`** for tunables; designers edit assets, not code.
3. **Use Addressables from day one.** `Resources/` and direct `AssetBundle` paths are dead ends.
4. **Pool frequently-spawned objects** (bullets, VFX); `Instantiate`/`Destroy` allocate and trigger GC.
5. **Cache component lookups.** `GetComponent` in `Update` is a recurring perf bug.
6. **Edit Mode + Play Mode tests** via Unity Test Framework; keep editor logic out of runtime assemblies.
7. **Assembly Definition files** to enforce layering and shrink iteration time.

## Pitfalls

- ❌ **Allocating in `Update`.** `new`, LINQ, `string` concatenation — all GC pressure per frame.
- ❌ **Synchronous scene loads on the main thread.** Use `LoadSceneAsync`.
- ❌ **Mixing render pipelines.** A URP shader will render pink under HDRP and vice versa.
- ❌ **Saving editor-only state in serialized fields without `#if UNITY_EDITOR`** — ships in builds.
- ❌ **Large prefabs as a single asset** — merge conflicts become unrecoverable. Split via nested prefabs.
- ❌ **`FindObjectOfType` on the hot path.** O(n) over the scene.
- ❌ **Reflection-heavy serialization** without considering IL2CPP stripping on console/mobile builds.

## Procedure

1. Confirm Unity version (LTS preferred) and active render pipeline.
2. Identify whether the change is runtime, editor, or build-pipeline; place code in the matching assembly.
3. Author data via ScriptableObjects and reference them through Addressables or serialized fields.
4. Write Edit Mode tests for pure logic; Play Mode tests for MonoBehaviour interactions.
5. Profile with the Unity Profiler before optimizing; verify GC alloc per frame is zero on hot paths.
6. Build for the target platform in CI to catch IL2CPP / stripping issues early.

## Validation

```sh
{{LINT_COMMAND}}      # e.g. dotnet format on the project's .csproj
{{BUILD_COMMAND}}     # Unity batch build: -batchmode -nographics -quit -executeMethod ...
{{TEST_COMMAND}}      # Unity Test Framework: -runTests -testPlatform editmode|playmode
```

## See also

- [`../_shared/canon.md`](../_shared/canon.md)
- Unity Manual: Scripting, Render Pipelines, Addressables, Profiler
