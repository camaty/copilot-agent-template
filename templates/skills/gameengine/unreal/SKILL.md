---
name: gameengine-unreal
description: "Unreal Engine development: C++/Blueprints, Niagara, Lumen/Nanite, and asset pipeline. Triggers: unreal, ue4, ue5, blueprint, uasset, niagara, lumen, nanite."
domain: gameengine
subdomain: unreal
facets:
  # - lang:cpp
  # - lang:blueprint
  # - pipeline:lumen
  # - pipeline:nanite
  # - target:pc
  # - target:console
applies_when:
  any_of:
    - "task targets Unreal Engine 4.27 or Unreal Engine 5.x"
    - "task involves UCLASS / USTRUCT / UFUNCTION authoring"
    - "task involves Blueprints, Niagara, Lumen, Nanite, or World Partition"
version: 0.1.0
---
# Game Engine / Unreal

## When to use

The task modifies an Unreal project — C++ classes, Blueprints, materials, levels, plugins, or build configuration. For pure DCC content authored in Maya/Blender for Unreal import, see `3dcg`.

## Canon

- **Reflection system** — `UCLASS`, `USTRUCT`, `UPROPERTY`, `UFUNCTION` macros expose C++ to Blueprints, serialization, GC, and the editor.
- **Garbage collection** — `UObject`-derived classes are GC-managed; raw pointers to `UObject` outside of `UPROPERTY` are unsafe.
- **Actor / Component / Subsystem** — composition primitives. Subsystems replace global singletons.
- **Blueprint** — visual scripting; great for designer-tunable behavior, poor for tight loops.
- **Build configurations** — `Debug`, `Development`, `Test`, `Shipping`. Logging and assertions strip in `Shipping`.
- **Modules and `.Build.cs`** — engine units of compilation; dependency declarations live in C# build files.

## Recommended patterns

1. **C++ for systems and performance-critical code; Blueprints for content and designer-facing logic.** Keep the interface between them small and stable.
2. **Always wrap `UObject` references in `UPROPERTY()`** to participate in GC and serialization.
3. **Use `TObjectPtr<T>` (UE5) or `TWeakObjectPtr<T>`** as appropriate over raw pointers.
4. **Subsystems (`UGameInstanceSubsystem`, `UWorldSubsystem`)** instead of `Get*Singleton()` patterns.
5. **Data-driven design via `UDataAsset` and `UDataTable`**; commit them as text-friendly source where possible.
6. **Source control with One File Per Actor (UE5)** or partitioned levels to avoid map-merge conflicts.
7. **Automation tests** via the Unreal Automation framework; gauntlet tests for end-to-end.

## Pitfalls

- ❌ **Raw pointer to a `UObject` member without `UPROPERTY`.** Eligible for GC; dangling reference.
- ❌ **Tick-based logic that should be event-driven.** Every actor ticking 60 Hz adds up fast.
- ❌ **Heavy logic in Blueprint Tick.** Move to C++ or to event-driven Blueprints.
- ❌ **Editor-only code outside `WITH_EDITOR` guards.** Breaks Shipping builds.
- ❌ **Hard references in Blueprints to large content** — pulls assets into memory transitively.
- ❌ **Modifying engine source without tracking the patch.** Upgrades become impossible.
- ❌ **Submitting `.uasset` merge resolutions without verifying in-editor** — silent corruption.

## Procedure

1. Confirm engine version (UE major.minor) and source vs binary build; pin in tooling.
2. Decide C++ vs Blueprint per system based on perf and authoring audience.
3. Add new C++ classes via the editor wizard (gets module integration right) or by hand with a matching `.Build.cs` update.
4. Author data assets for tunables; reference via `TSoftObjectPtr` to avoid early loads.
5. Run automation tests in Editor and a cooked Development build; smoke-test a packaged Shipping build before release.

## Validation

```sh
{{LINT_COMMAND}}     # e.g. clang-format / project linter
{{BUILD_COMMAND}}    # UnrealBuildTool: <UE>/Engine/Build/BatchFiles/RunUAT.sh BuildCookRun ...
{{TEST_COMMAND}}     # UE Automation: -ExecCmds="Automation RunTests <Filter>; Quit"
```

## See also

- [`../_shared/canon.md`](../_shared/canon.md)
- Unreal documentation: Programming with C++, Blueprints, Niagara, Lumen, World Partition
