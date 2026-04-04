---
applyTo: "**"
---
# {{PROJECT_NAME}} — Project Instructions

{{PROJECT_DESCRIPTION}}. See [`AGENTS.md`](../AGENTS.md) for full context.

## Non-negotiable constraints
{{KEY_CONSTRAINTS}}

## Source layout (`{{SOURCE_DIR}}`)
{{KEY_MODULES}}

## Verification commands
```sh
{{LINT_COMMAND}}    # Must pass before any commit
{{BUILD_COMMAND}}   # Build output
{{TEST_COMMAND}}    # All tests
```

## Agents available
Use `@Plan` to decompose tasks before writing code, `@Implementer` to execute an approved plan, `@Reviewer` to audit completed changes, `@Explore` to research the codebase read-only, and `@Verification` to run tests.
