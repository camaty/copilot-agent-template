---
description: "Use when writing or editing test files. Covers {{PROJECT_NAME}} test pyramid structure, coverage targets, {{TEST_FRAMEWORK}} syntax, helpers, and test runner details."
applyTo: "{{TEST_DIR}}/**"
---
# Testing Conventions (`{{TEST_DIR}}/**`)

## Test Pyramid

{{TEST_STRUCTURE}}

## Commands

```sh
{{TEST_COMMAND}}              # All tests
{{TEST_UNIT_COMMAND}}         # Unit only (fast, no build required)
{{TEST_INTEGRATION_COMMAND}}  # Integration (run after {{BUILD_COMMAND}})
```

## Coverage Targets
{{COVERAGE_TARGETS}}

## Test Framework: `{{TEST_FRAMEWORK}}`

## File / Test Structure

- Test files: match the source file name + `.test.<ext>` (e.g., `MyModule.test.js` for `{{SOURCE_DIR}}MyModule.js`)
- `describe` block: class or module name
- `it` / `test` block: plain-English description of behavior

## Helpers
- `{{TEST_DIR}}/helpers/` — shared utilities for all test tiers
- Import from helpers rather than duplicating setup code

## Anti-Patterns
- Do not write tests that depend on specific timing values
- Do not assert exact floating-point equality for computed values; use epsilon tolerances
- Do not import from `{{OUTPUT_DIR}}` in tests — import from `{{SOURCE_DIR}}` directly
- Do not skip flaky tests silently — fix or document them
