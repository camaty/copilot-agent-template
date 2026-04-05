# AGENTS.md

## Overview

- **{{PROJECT_NAME}}** is {{PROJECT_DESCRIPTION}}.
- Tech stack: {{TECH_STACK}}.
- The main deliverables are in `{{OUTPUT_DIR}}`.

## Why This Repo Is Structured This Way

{{ARCHITECTURE_OVERVIEW}}

## File Structure

```text
{{PROJECT_NAME}}/
{{FILE_TREE}}
```

## Working Model

- Most feature work flows through `{{KEY_ENTRY_POINTS}}`.
- Changes to core logic may affect multiple subsystems — read the relevant source files before planning.
- `src/` and `tests/` (or equivalent) must be updated together when behavior changes.

## Clawable Workflow

All Copilot agent work flows through five lanes in order. Every agent emits a structured lane event before and after each phase:

| Lane | Agent | Emits |
|------|-------|-------|
| explore | `@Explore` | `▶/✓ [LANE:explore]` |
| plan | `@Plan` | `▶/✓ [LANE:plan]` |
| implement | `@Implementer` | `▶/✓ [LANE:implement:step:{N}]` |
| verify | `@Verification` | `▶/✓ [LANE:verify:{command}]` |
| review | `@Reviewer` | `▶/✓ [LANE:review]` |

Use `@{{AUTONOMOUS_AGENT_NAME}}` to run the full pipeline autonomously. Use individual agents for targeted work.

When working from a GitHub Issue, paste the issue body or URL to `@{{AUTONOMOUS_AGENT_NAME}}` (VS Code) or use the **Issue From GitHub** prompt shortcut.

## How To Verify Changes

- `{{PACKAGE_MANAGER}} install` installs dependencies.
- `{{LINT_COMMAND}}` runs linting.
- `{{BUILD_COMMAND}}` builds the project.
- `{{TEST_COMMAND}}` runs all tests.
- `{{E2E_GATE_COMMAND}}` runs the end-to-end regression gate (required before merge).

## Read These When Relevant

- `README.md` — public API and usage
- `{{DOCS_DIR}}/ARCHITECTURE.md` — full component map and data flows
- Any `docs/` entries for subsystem deep-dives

## Repo-Specific Constraints

{{KEY_CONSTRAINTS}}
