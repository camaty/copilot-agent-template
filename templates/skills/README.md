# Skills Templates

This directory contains the reusable scaffold for **domain skills** — knowledge packs that the `@Setup` agent (and downstream Copilot agents) consult when working in a particular technical domain.

## Layering model

The skill layout follows a **logical 4-layer / physical 3-layer + facet** model. See [`../../doc/ARCHITECTURE.md`](../../doc/ARCHITECTURE.md) for full background.

| Logical layer | Where it lives | Purpose |
|---|---|---|
| **L0 Constitution** | `AGENTS.md`, `policy.md` (project root) | Inviolable rules |
| **L1 Domain skill** | `<project>/.github/skills/<domain>/<subdomain>/SKILL.md` | Domain-specific canon, patterns, pitfalls |
| **L2 Task playbook** | `<project>/.github/prompts/*.prompt.md` | Procedure that composes multiple skills |
| **L3 Operator harness** | `<project>/.github/agents/*.agent.md`, workflows | Execution rails |

Physical folder depth is capped at **3 levels** under `skills/` (`<domain>/<subdomain>/<artifact>`). Anything finer (language, runtime, style) is expressed via **facets** in the SKILL.md front-matter, never as deeper folders.

## Directory layout

```
templates/skills/
├── README.md                       # this file
├── EXTENDING.md                    # how to add a new domain / subdomain
├── _layout/                        # reusable skeletons (do not copy as-is)
│   ├── DOMAIN_INDEX.template.md
│   └── SUBDOMAIN_SKILL.template.md
├── core-domain/                    # legacy generic skill (kept for back-compat)
│   ├── SKILL.template.md
│   └── command-wrapper.template.sh
├── coding/                         # general software engineering
│   ├── INDEX.md
│   ├── _shared/
│   │   ├── canon.md
│   │   └── pitfalls.md
│   ├── network/SKILL.md
│   ├── embedded/SKILL.md
│   ├── webgpu/SKILL.md
│   ├── shader-sim/SKILL.md
│   ├── mapreduce-codegen/SKILL.md
│   ├── spatial-transfer/SKILL.md
│   ├── agent-sca/SKILL.md
│   ├── api-design/SKILL.md
│   ├── observability/SKILL.md
│   ├── databases/SKILL.md
│   ├── xr/SKILL.md
│   ├── spatial-audio/SKILL.md
│   └── robotics/SKILL.md
├── 3dcg/                           # 3D CG / DCC tools
│   ├── INDEX.md
│   ├── blender/SKILL.md
│   ├── houdini/SKILL.md
│   ├── 3dgs/SKILL.md
│   ├── garment-sim/SKILL.md
│   └── usd-pipeline/SKILL.md
├── cad/                            # parametric / mechanical CAD
│   ├── INDEX.md
│   ├── parametric/SKILL.md
│   ├── api-harness/SKILL.md
│   ├── topology-assembly/SKILL.md
│   └── freecad-scripting/SKILL.md
├── ml/                             # machine learning
│   ├── INDEX.md
│   ├── training/SKILL.md
│   ├── inference/SKILL.md
│   ├── motion-fm/SKILL.md
│   ├── vlm-spatial/SKILL.md
│   ├── llm-finetuning/SKILL.md
│   ├── diffusion/SKILL.md
│   └── edge-inference/SKILL.md
└── gameengine/                     # real-time CG / game engines
    ├── INDEX.md
    ├── unity/SKILL.md
    ├── unreal/SKILL.md
    ├── synthetic-data/SKILL.md
    └── godot/SKILL.md
```

## Selection flow (what an agent reads, in order)

1. The agent identifies the active **domain** from task context.
2. It opens `<domain>/INDEX.md` — a 1-page decision tree mapping task signals to a subdomain.
3. It opens the chosen `<domain>/<subdomain>/SKILL.md` and follows the procedure.
4. If facets in the SKILL front-matter match the task (e.g. `lang:rust`, `target:rtos`), the agent applies the listed addenda.
5. `<domain>/_shared/` is consulted for canon and pitfalls common to the whole domain.

This keeps the read-path **2–3 hops deep** regardless of how many subdomains exist.

## Front-matter contract

Every `SKILL.md` starts with YAML front-matter:

```yaml
---
name: <stable-id>          # e.g. coding-network
description: "<one line>"   # used by Copilot skill matcher
domain: <domain>            # mirrors folder
subdomain: <subdomain>      # mirrors folder
facets:                     # orthogonal tags, NOT folder levels
  - lang:python
  - lang:c
  - target:linux
applies_when:               # plain-language activation hints
  any_of:
    - "task involves <X>"
version: 0.1.0
---
```

Keep a single SKILL.md ≤ 2,000 tokens. Move depth into siblings (`canon.md`, `patterns.md`, `pitfalls.md`, `checklist.md`, `examples/`).

## Runtime skill creation (meta-tools)

Skills can also be created **at runtime** by an agent as it learns new techniques — no human scaffolding required. Two scripts in `../../templates/scripts/` support this:

- **`create_skill.py`** — called by the agent after successfully solving a novel task. Writes a `SKILL.md` stub (with the winning code embedded) into `<skills_dir>/<domain>/<subdomain>/`.
- **`refactor_skills.py`** — run nightly (cron or GitHub Actions schedule). Scans all accumulated `SKILL.md` files, detects overlapping skills by token similarity, and optionally writes consolidated draft files for review.

See the [Agent meta-tools section of the root README](../../README.md#agent-meta-tools-autonomous-skill-creation-and-nightly-refactoring) for full usage examples and the four-phase OJT loop they support.

## Extending

See [`EXTENDING.md`](./EXTENDING.md).

## Skill catalog (Generative Spatial Computing)

[`SKILL_CATALOG.md`](./SKILL_CATALOG.md) lists 24 catalogued skills across eleven clusters — the original five priority clusters (web graphics, AI/CAD, digital humans, secure infra, embodied AI) plus six follow-on clusters covering cross-cutting service foundations (API design, observability, databases), pipeline & open-source CAD/CG (OpenUSD, FreeCAD), generative-model specialisations (LLM fine-tuning, diffusion), an open-source game engine (Godot), immersive XR & spatial interaction (WebXR/OpenXR, spatial audio), and robotics & on-device AI (ROS 2, edge inference). Each entry has a numeric ID; pass any subset to `@Setup generate-skills` to scaffold them in parallel:

```
@Setup generate-skills 1 2 3          # generate skills #1, #2, and #3
@Setup generate-skills cluster:1      # generate all skills in cluster 1
@Setup generate-skills all            # generate all 24 skills
```
