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
│   └── embedded/SKILL.md
├── 3dcg/                           # 3D CG / DCC tools
│   ├── INDEX.md
│   ├── blender/SKILL.md
│   └── houdini/SKILL.md
├── cad/                            # parametric / mechanical CAD
│   ├── INDEX.md
│   └── parametric/SKILL.md
├── ml/                             # machine learning
│   ├── INDEX.md
│   ├── training/SKILL.md
│   └── inference/SKILL.md
└── gameengine/                     # real-time CG / game engines
    ├── INDEX.md
    ├── unity/SKILL.md
    └── unreal/SKILL.md
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

## Extending

See [`EXTENDING.md`](./EXTENDING.md).
