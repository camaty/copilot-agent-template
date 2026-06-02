---
name: gameengine-unreal
description: "Unreal Engine development: C++/Blueprints, UCLASS/USTRUCT reflection, Niagara, Lumen/Nanite, World Partition, Gameplay Ability System. Triggers: unreal, ue4, ue5, blueprint, uasset, niagara, lumen, nanite, world-partition, gas, replication, ubt."
domain: gameengine
subdomain: unreal
facets:
  - lang:cpp
  - lang:blueprint
  - pipeline:lumen
  - pipeline:nanite
  - target:pc
  - target:console
  - target:mobile
  - vendor:unreal
applies_when:
  any_of:
    - "task targets Unreal Engine 4.27 or Unreal Engine 5.x"
    - "task involves UCLASS / USTRUCT / UFUNCTION authoring"
    - "task involves Blueprints, Niagara, Lumen, Nanite, or World Partition"
    - "task involves Gameplay Ability System, replication, or dedicated servers"
    - "task ships a UE plugin, source-built engine, or BuildCookRun pipeline"
version: 0.1.0
---
# Game Engine / Unreal

## When to use

Open this skill when the task modifies an Unreal project — C++
classes, Blueprints, materials, levels, plugins, build configuration,
or replicated/multiplayer systems. For pure DCC content authored in
Maya / Blender for Unreal import, see `3dcg`. For synthetic-data
pipelines using Movie Render Queue + Replicator, see
[`../synthetic-data/SKILL.md`](../synthetic-data/SKILL.md).

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Reflection system** — `UCLASS`, `USTRUCT`, `UPROPERTY`,
  `UFUNCTION` macros expose C++ to Blueprints, serialisation, GC,
  the editor, and replication. `UHT` (Unreal Header Tool)
  generates the bridge code at build time.
- **Garbage collection** — `UObject`-derived classes are GC-managed;
  raw pointers to `UObject` outside of `UPROPERTY` are unsafe and
  silently dangle.
- **Actor / Component / Subsystem** — composition primitives.
  Subsystems (`UGameInstanceSubsystem`, `UWorldSubsystem`) replace
  ad-hoc global singletons.
- **Blueprint** — visual scripting; great for designer-tunable
  behaviour, poor for tight loops. The C++/BP boundary is a perf
  cliff if crossed thousands of times per frame.
- **Build configurations** — `Debug`, `DebugGame`, `Development`,
  `Test`, `Shipping`. Logging and `check()` strip in `Shipping`;
  `ensure()` survives but reports once.
- **Modules + `.Build.cs`** — engine units of compilation;
  dependency declarations live in C# build files.
- **World Partition (UE5)** — streamed, grid-partitioned levels;
  `One File Per Actor` (OFPA) keeps source-control manageable.
- **Lumen** — real-time global illumination; **Nanite** — virtual
  geometry for billions-of-triangle assets. Both UE5; both have
  platform-specific gotchas.
- **Niagara** — modern VFX system; replaces Cascade in UE5.
- **Gameplay Ability System (GAS)** — opinionated framework for
  abilities, attributes, and effects in multiplayer games.
- **Replication** — networked state sync; `UPROPERTY(Replicated)`
  + `GetLifetimeReplicatedProps`. Authority is server-side; clients
  are predictive.
- **Soft references** — `TSoftObjectPtr<T>`, `FSoftClassPath`; do
  not pull the asset into memory until explicitly loaded.

## Recommended patterns

1. **C++ for systems and performance-critical code; Blueprints for
   content and designer-facing logic.** Keep the C++/BP interface
   small, stable, and documented.
2. **Always wrap `UObject` references in `UPROPERTY()`** to
   participate in GC and serialisation. No exceptions.
3. **Use `TObjectPtr<T>` (UE5) or `TWeakObjectPtr<T>`** as
   appropriate over raw pointers.
4. **Subsystems instead of `Get*Singleton()` patterns.** Lifetime
   is engine-managed and BP-accessible.
5. **Data-driven design via `UDataAsset` and `UDataTable`** — commit
   them as text-friendly source where possible (CSV-import for
   data tables; UAsset only when binary is required).
6. **Source control with One File Per Actor (UE5)** or partitioned
   levels to avoid map-merge conflicts.
7. **Automation tests** via the Unreal Automation framework;
   gauntlet tests for end-to-end; replication-aware tests for
   networked systems.
8. **Soft references for large content.** `TSoftObjectPtr` plus
   `FStreamableManager::RequestAsyncLoad` keeps menus snappy.
9. **Replication: server-authoritative with client prediction.**
   Use `OnRep_*` for cosmetic updates; reconcile in `Tick`.
10. **Use `UE_LOG` with categories**, not `printf`. Categories
    can be filtered per build, per device, per shipping config.
11. **Profile with Unreal Insights** (frame trace) and `stat unit`/
    `stat scenerendering`; never optimise without a capture.
12. **Plugin architecture** for cross-project features so engine
    upgrades don't drag the feature with them.

## Pitfalls (subdomain-specific)

- ❌ **Raw pointer to a `UObject` member without `UPROPERTY`.**
  Eligible for GC; dangling reference. The crash is non-
  deterministic.
- ❌ **Tick-based logic that should be event-driven.** Every actor
  ticking 60 Hz adds up fast; disable Tick by default
  (`PrimaryActorTick.bCanEverTick = false`).
- ❌ **Heavy logic in Blueprint Tick.** Move to C++ or to event-
  driven Blueprints.
- ❌ **Editor-only code outside `WITH_EDITOR` guards.** Breaks
  Shipping builds at link time.
- ❌ **Hard references in Blueprints to large content.** Pulls
  assets into memory transitively; menus take seconds to open.
- ❌ **Modifying engine source without tracking the patch.**
  Upgrades become impossible. Use plugins or `FCoreDelegates`.
- ❌ **Submitting `.uasset` merge resolutions without verifying
  in-editor.** Silent corruption, lost work.
- ❌ **`UFUNCTION(BlueprintCallable)` on hot-path methods.** The
  reflection bridge is not free.
- ❌ **Replicating large arrays naively.** Use `FastArraySerializer`
  or chunked replication; otherwise bandwidth saturates.
- ❌ **Treating `Cast<T>(actor)` as free.** It walks the class
  hierarchy; cache or refactor when in a hot loop.
- ❌ **Ignoring `bAlwaysRelevant` on networked actors.** Players
  far from an actor still pay the replication cost.
- ❌ **Spawning Niagara systems per-shot without pooling.** Use
  Niagara System Pool for projectiles / impacts.

Domain-wide pitfalls (when present) live in `../_shared/pitfalls.md`.

## Procedure

1. **Confirm engine version** (UE major.minor) and source vs binary
   build; pin in tooling and CI image.
2. **Decide C++ vs Blueprint per system** based on perf and
   authoring audience. Document the boundary.
3. **Add new C++ classes via the editor wizard** (gets module
   integration right) or by hand with a matching `.Build.cs`
   update.
4. **Author data assets for tunables**; reference via
   `TSoftObjectPtr` to avoid early loads.
5. **For multiplayer**, design the authority model first
   (server-authoritative + client prediction is the default);
   write replication tests before behaviour tests.
6. **Run automation tests in Editor and a cooked Development
   build**; smoke-test a packaged Shipping build before release.
7. **Profile on the target hardware**, not in PIE; use Unreal
   Insights traces.
8. **Plugin-ise** systems likely to outlive the project.

## Validation

After completing the procedure, run:

```sh
# Static checks
clang-format --dry-run --Werror Source/**/*.cpp Source/**/*.h

# Build
"$UE_ROOT/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun \
    -project="$(pwd)/MyGame.uproject" \
    -platform=Linux -clientconfig=Development -build -cook -stage \
    -archivedirectory=Build

# Automation tests (Editor)
"$UE_ROOT/Engine/Binaries/Linux/UnrealEditor" \
    "$(pwd)/MyGame.uproject" \
    -ExecCmds="Automation RunTests Project; Quit" -ReportOutputPath=AutomationReports \
    -unattended -nopause -nullrhi

# Shipping build smoke
"$UE_ROOT/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun \
    -project="$(pwd)/MyGame.uproject" \
    -platform=Linux -clientconfig=Shipping -build -cook -stage -archive

# Replication tests for networked systems
"$UE_ROOT/Engine/Binaries/Linux/UnrealEditor" "$(pwd)/MyGame.uproject" \
    -ExecCmds="Automation RunTests Networking; Quit" -nullrhi -unattended
```

## See also

- [`../unity/SKILL.md`](../unity/SKILL.md) — when a project shares
  pipelines across Unity and Unreal.
- [`../synthetic-data/SKILL.md`](../synthetic-data/SKILL.md) — UE
  Movie Render Queue + Replicator for ML data generation.
- Unreal documentation: Programming with C++, Blueprints, Niagara,
  Lumen, World Partition, Gameplay Ability System.
- Unreal Insights — <https://docs.unrealengine.com/5.0/en-US/unreal-insights-in-unreal-engine/>
