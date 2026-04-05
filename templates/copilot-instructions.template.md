---
applyTo: "**"
---
# {{PROJECT_NAME}} — Project Instructions

{{PROJECT_DESCRIPTION}}. See [`AGENTS.md`](../AGENTS.md) and [`{{DOCS_DIR}}/ARCHITECTURE.md`](../{{DOCS_DIR}}/ARCHITECTURE.md) for full context.

## Non-negotiable constraints
{{KEY_CONSTRAINTS}}

## Source layout (`{{SOURCE_DIR}}`)
{{KEY_MODULES}}

## Verification commands
```sh
{{LINT_COMMAND}}    # Must pass before any commit
{{BUILD_COMMAND}}   # Build output
{{TEST_COMMAND}}    # All tests
{{E2E_GATE_COMMAND}}  # End-to-end regression gate
```

## Autonomous pipeline

All agent work flows through five lanes in order. Every agent emits a structured lane event before and after each phase so state is machine-readable:

```
▶ [LANE:explore]   → ✓ [LANE:explore:complete]
▶ [LANE:plan]      → ✓ [LANE:plan:complete]
▶ [LANE:implement] → ✓ [LANE:implement:complete]
▶ [LANE:verify]    → ✓ [LANE:verify:complete]
▶ [LANE:review]    → ✓ [LANE:review:complete]
```

A `✗ [LANE:{name}:blocked]` event means the lane failed and needs attention before the pipeline can proceed.

## Agents available

| Agent | Purpose | Invoke |
|-------|---------|--------|
| `@{{AUTONOMOUS_AGENT_NAME}}` | Full autonomous pipeline (explore→plan→implement→verify→review) | High-level tasks |
| `@Plan` | Design a plan, wait for approval, handoff to Implementer | Complex features |
| `@Explore` | Read-only codebase research and Q&A | Questions |
| `@Implementer` | Execute an approved plan (handoff only) | Via Plan |
| `@Reviewer` | Security + quality audit | After implementation |
| `@Verification` | Run lint / build / tests | Spot checks |

Prompt shortcuts in `.github/prompts/`:
- **Plan Change** — design a plan for a requested change
- **Implement Change** — run the full pipeline for a specific request
- **Verify Workspace** — run the narrowest relevant verification
- **Issue From GitHub** — start a coding task from a GitHub issue

## Environment awareness

Copilot can be triggered from multiple environments. Behave accordingly:

| Environment | Handoff buttons | Terminal | How to start |
|-------------|-----------------|----------|--------------|
| VS Code agent chat | ✓ available | ✓ full | `@{{AUTONOMOUS_AGENT_NAME}} <task>` or use a prompt shortcut |
| GitHub.com browser agent | ✗ none | ✗ none | `@copilot <task>` in a repository |
| GitHub Issue (assigned) | ✗ none | ✗ sandboxed | Assign the issue to Copilot on github.com |
| GitHub Copilot Workspace | context-dependent | ✗ sandboxed | Open issue → "Open in Workspace" |

When running in a browser or issue context **without handoff buttons**: output the next agent's full prompt inline so the user can paste it or continue in the same session.

## Starting from a GitHub Issue

When a task comes from a GitHub Issue (assigned or pasted):
1. Extract the **task title** from the issue heading
2. Extract **acceptance criteria** from `- [ ]` checkboxes or numbered requirements
3. Extract **relevant files** from code references in the body
4. Run the full autonomous pipeline treating acceptance criteria as the definition of done
5. Do not comment on or close the issue directly — report results in chat or in a PR description
