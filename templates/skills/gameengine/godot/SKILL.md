---
name: gameengine-godot
description: "Godot Engine 4.x development: GDScript and C# scripting, scene/node tree, signals, autoload, multiplayer, GDExtension. Triggers: godot, gdscript, gdextension, scene, node, signal, autoload, godot 4, multiplayer api, mono, c-sharp godot."
domain: gameengine
subdomain: godot
facets:
  - lang:gdscript
  - lang:csharp
  - lang:cpp
  - target:pc
  - target:mobile
  - target:web
  - vendor:godot
applies_when:
  any_of:
    - "task targets Godot 4.x"
    - "task involves GDScript, C# (Mono), or GDExtension (C++) scripting"
    - "task involves scenes, nodes, signals, groups, or autoloads"
    - "task uses Godot's high-level multiplayer API"
    - "task ships an editor plugin or custom resource"
version: 0.1.0
---
# Game Engine / Godot

## When to use

Open this skill when the task targets Godot 4.x — scripts, scenes,
shaders, GDExtension plugins, exports, or editor tooling. For Unity
and Unreal, see the sibling skills. For pure backend services, use
`coding`.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Scene tree** — every running game has a single tree of `Node`s;
  scenes (`.tscn` / `.scn`) are reusable subtrees. The `SceneTree`
  singleton drives the loop.
- **Node lifecycle** — `_ready` (after children), `_process` (per
  frame), `_physics_process` (fixed delta), `_input` /
  `_unhandled_input` (events), `_exit_tree`. Order across siblings
  is tree-order.
- **Signals** — typed publish/subscribe primitives between nodes;
  preferred over polling. `signal foo(arg: int)`; emit with
  `foo.emit(42)`; connect via `node.foo.connect(callable)`.
- **Autoload (singleton)** — a script/scene that exists at the root
  for the whole run; declared in Project Settings → Autoload.
- **Resource** — data asset (`.tres` / `.res`); shared by reference
  unless duplicated. Custom resources via `class_name MyData
  extends Resource` are the data-driven primitive.
- **Composition (nodes)** vs inheritance (scripts) — Godot favours
  small nodes composed in scenes over deep class hierarchies.
- **GDScript** — Python-like, statically typed (with hints), JIT-
  free; primary scripting language. C# (Mono) and GDExtension
  (C++/Rust via godot-cpp / gdext) for perf.
- **Servers** — low-level layer (`RenderingServer`, `PhysicsServer`,
  `AudioServer`); used to bypass scene tree for thousands of
  entities.
- **High-level multiplayer** — `MultiplayerAPI`, RPCs via
  `@rpc(...)`, `MultiplayerSpawner`/`Synchronizer` nodes.
- **Project resources path** — `res://` (read-only at runtime,
  packed into `.pck`); `user://` (writable user data).
- **Export presets** — per-platform builds (Linux, Windows, macOS,
  Android, iOS, Web). Templates downloaded per Godot version.
- **GDExtension** — language binding ABI (replaces GDNative).
  Compile against the target Godot version's headers.

## Recommended patterns

1. **Composition over inheritance.** Many small nodes in a scene
   beat a deep class chain; reuse via scene instancing.
2. **Communicate via signals**, not by walking the tree to call
   methods. Signals localise change.
3. **Type your GDScript.** `var hp: int = 100`, `func foo(a: int)
   -> void`. Static types catch errors at parse time and double
   throughput.
4. **Custom Resources for data**, not constants in scripts.
   Designers edit `.tres` in the inspector; they diff cleanly.
5. **Autoloads sparingly** — global state is debt. Use them for
   true singletons (event bus, save manager); not as a substitute
   for proper data flow.
6. **Use groups for cross-scene queries.** `add_to_group("enemies")`
   then `get_tree().get_nodes_in_group("enemies")`. Cheaper than
   `find_node`.
7. **Pool spawning** for projectiles, VFX, and damage numbers;
   `instance` is not free, especially on mobile/web exports.
8. **For thousands of entities, drop to servers.** Skip the scene
   tree; use `RenderingServer.canvas_item_*` and `PhysicsServer`
   directly.
9. **Multiplayer: server-authoritative.** Validate on the host;
   never trust a client RPC argument without a check.
10. **C# vs GDScript** — pick one for application code; don't
    cross the boundary on hot paths. C# is faster for arithmetic,
    GDScript faster to iterate.
11. **GDExtension (C++/Rust)** for hot loops only; profile first.
    The plugin must be rebuilt per Godot patch version.
12. **Editor plugins** isolated in `addons/` with a clear
    `plugin.cfg`; never modify project settings without UI for
    teammates.
13. **Reproducible exports** in CI via `godot --headless --export-
    release` with the appropriate preset.

## Pitfalls (subdomain-specific)

- ❌ **`get_node("Path/To/Node")` everywhere.** Brittle on rename;
  use `@onready var foo: Node = $Path/To/Node` or scene-local
  unique names (`%Foo`).
- ❌ **`_process` running when paused unintentionally.** Set
  `process_mode = Node.PROCESS_MODE_PAUSABLE` (default), check
  `get_tree().paused`.
- ❌ **Untyped GDScript on hot paths.** 2–4× slower than typed.
- ❌ **Signal connections without `CONNECT_ONE_SHOT` on
  one-time events** — leaks if the emitter outlives the
  receiver.
- ❌ **Heavy work in `_process` instead of timers / async.**
  Frames drop; mobile/web buckle.
- ❌ **Storing references to freed nodes.** `is_instance_valid()`
  before use; or use `WeakRef`.
- ❌ **Mixing `Node2D` and `Control` parents incorrectly.** Mouse
  filtering and z-ordering rules differ; UI siblings drift.
- ❌ **`load()` on the main thread for large resources.** Use
  `ResourceLoader.load_threaded_request`.
- ❌ **Autoload that mutates scene tree on `_ready`.** Order of
  autoload execution matters; defer with `call_deferred`.
- ❌ **Trusting client RPC arguments** in multiplayer. Always
  validate on the authority.
- ❌ **C# project not regenerated** after adding files via the
  editor; the `.csproj` lists files, run `dotnet build` after
  edits.
- ❌ **GDExtension built against a different Godot version.**
  Crashes loading the library; rebuild on every minor bump.
- ❌ **`@export` of a typed array without specifying inner type
  (`Array[Foo]`).** Inspector shows generic Variant array; data
  loads incorrectly.

Domain-wide pitfalls live in `../_shared/pitfalls.md` (when present).

## Procedure

1. **Pin Godot major.minor** in CI image and the repo (`.tool-
   versions` or similar). Pin export templates to the same
   version.
2. **Plan scenes around composition** — reusable subtrees, each
   with a single responsibility; instance them where needed.
3. **Define signals + custom Resources** as the data-flow
   contract before writing logic.
4. **Type GDScript everywhere**; for C#, enable nullable
   reference types and warnings-as-errors.
5. **Author multiplayer with explicit authority** — server-
   authoritative model, RPC validation, deterministic step on
   physics if rollback is needed.
6. **Test logic via GUT (GDScript)** or .NET test runner (C#);
   editor-mode integration tests via headless run with a small
   test scene.
7. **Profile** on target devices (especially mobile/web) with the
   built-in profiler and `--print-fps`.
8. **Export deterministically** in CI with `godot --headless
   --export-release "<preset>" out/game.exe`.
9. **Bundle assets** in `.pck` for shipping; user-writable data in
   `user://`.

## Validation

After completing the procedure, run:

```sh
# Static analysis
godot --headless --check-only --quit                # parses every script
gdformat --check **/*.gd                            # GDScript formatter
dotnet format --verify-no-changes                   # C# components

# Project import & headless smoke
godot --headless --import --quit
godot --headless --quit-after 60 --main-scene res://tests/smoke.tscn

# Tests
# - GUT (GDScript) tests
godot --headless --script addons/gut/gut_cmdln.gd \
      -gdir=res://tests/unit -gexit
# - C# tests
dotnet test

# Export per preset
godot --headless --export-release "Linux/X11" out/game.x86_64
godot --headless --export-release "Web"        out/web/index.html

# Run packaged build smoke
out/game.x86_64 --headless --quit-after 60 --main-scene res://tests/smoke.tscn
```

## See also

- [`../unity/SKILL.md`](../unity/SKILL.md), [`../unreal/SKILL.md`](../unreal/SKILL.md)
  — when a project shares pipelines across engines.
- [`../synthetic-data/SKILL.md`](../synthetic-data/SKILL.md) —
  Godot is also serviceable for low-cost synthetic-data scenes.
- Godot Docs — <https://docs.godotengine.org/en/stable/>
- GDExtension docs — <https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/>
- GUT (Godot Unit Test) — <https://github.com/bitwes/Gut>
