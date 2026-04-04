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

## How To Verify Changes

- `{{PACKAGE_MANAGER}} install` installs dependencies.
- `{{BUILD_COMMAND}}` builds the project.
- `{{LINT_COMMAND}}` runs linting.
- `{{TEST_COMMAND}}` runs all tests.

## Read These When Relevant

- `README.md` — public API and usage
- Any `docs/` entries for subsystem deep-dives

## Repo-Specific Constraints

{{KEY_CONSTRAINTS}}
