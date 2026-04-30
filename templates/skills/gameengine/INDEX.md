---
domain: gameengine
version: 0.1.0
---
# Game Engine — Domain Index

> Real-time CG and gameplay development on commercial game engines. For offline rendering and DCC content creation, see [`3dcg`](../3dcg/INDEX.md).

## What this domain covers

Engine-specific scripting, rendering features, asset pipelines, gameplay frameworks, and platform/build configuration. Knowledge that depends on a specific engine lives in subdomains; cross-engine concepts (frame budget, draw calls, GC pressure, asset interchange) live in `_shared/`.

## Subdomain decision tree

| If the task involves… | Open this subdomain |
|---|---|
| Unity (C#, MonoBehaviour, ScriptableObject, URP/HDRP, Addressables) | [`unity/SKILL.md`](./unity/SKILL.md) |
| Unreal Engine (C++/Blueprints, UE5, Niagara, Lumen, Nanite) | [`unreal/SKILL.md`](./unreal/SKILL.md) |
| Godot, Bevy, custom engine | _add a new subdomain — see [`../EXTENDING.md`](../EXTENDING.md)_ |

## Facet vocabulary

| Axis | Allowed values |
|---|---|
| `lang:`     | `csharp`, `cpp`, `blueprint`, `gdscript`, `rust` |
| `target:`   | `pc`, `console`, `mobile`, `vr`, `xr`, `web` |
| `pipeline:` | `urp`, `hdrp`, `builtin`, `lumen`, `nanite` |
| `genre:`    | `fps`, `rpg`, `puzzle`, `simulation`, `multiplayer` |

## Shared resources

The `_shared/` folder is **not yet created** for this domain — add it when a third subdomain is introduced or when canon starts duplicating across `unity/` and `unreal/`:

- `_shared/canon.md` — frame budget, GC, draw calls, LOD, asset import, profiler basics
- `_shared/pitfalls.md`

See [`../coding/_shared/`](../coding/_shared/) for a reference layout.

## Related domains

- `3dcg` — upstream content; assets travel via FBX, glTF, USD
- `coding` — for backend services, matchmaking, telemetry
- `ml` — for in-engine ML inference (animation, behavior, upscaling)
