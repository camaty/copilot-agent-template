---
domain: coding
version: 0.1.0
---
# Coding — Domain Index

> Generic software-engineering skills. Use this domain when the task is primarily about writing or modifying source code in any language.

## What this domain covers

Source code authorship, refactoring, debugging, API design, performance tuning, and tooling. Language-specific knowledge is expressed via `facets:` (`lang:python`, `lang:rust`, …) rather than as separate folders.

## Subdomain decision tree

Pick the first matching row.

| If the task involves… | Open this subdomain |
|---|---|
| Sockets, HTTP/gRPC servers, protocol design, latency or throughput SLOs | [`network/SKILL.md`](./network/SKILL.md) |
| Microcontrollers, RTOS, bare-metal, memory-constrained targets, hardware peripherals | [`embedded/SKILL.md`](./embedded/SKILL.md) |
| Distributes codegen across a planner model and multiple local executor models (Map-Reduce, multi-agent) | [`mapreduce-codegen/SKILL.md`](./mapreduce-codegen/SKILL.md) |
| _none of the above_ | apply [`_shared/`](./_shared/) only and proceed with general practice |

Add a new subdomain only when its canon and pitfall set diverge meaningfully from the above. See [`../EXTENDING.md`](../EXTENDING.md).

## Facet vocabulary

| Axis | Allowed values |
|---|---|
| `lang:`    | `python`, `typescript`, `javascript`, `rust`, `go`, `c`, `cpp`, `java`, `kotlin`, `swift`, `ruby`, `csharp`, `shell` |
| `target:`  | `linux`, `macos`, `windows`, `wasm`, `mcu`, `rtos`, `browser`, `mobile` |
| `style:`   | `oop`, `functional`, `data-oriented`, `actor`, `event-driven` |
| `vendor:`  | `openai`, `qwen`, `anthropic`, `mistral`, `github-advanced-security` |

## Shared resources

- [`_shared/canon.md`](./_shared/canon.md)
- [`_shared/pitfalls.md`](./_shared/pitfalls.md)

## Related domains

- `ml` — when the code is primarily a model training / inference pipeline
- `gameengine` — when targeting Unity or Unreal scripting layers
