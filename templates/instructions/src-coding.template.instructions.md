---
description: "Use when writing or editing source files in {{SOURCE_DIR}}. Covers linting rules, formatting, naming conventions, import ordering, and {{PROJECT_NAME}}-specific code patterns."
applyTo: "{{SOURCE_GLOB}}"
---
# Source Code Conventions (`{{SOURCE_GLOB}}`)

## Naming
{{NAMING_CONVENTIONS}}

## Import Ordering
{{IMPORT_ORDER}}

## Formatting
{{CODE_STYLE_RULES}}
Formatter: **{{FORMATTER}}**

## Architecture Patterns

### Never edit `{{OUTPUT_DIR}}` directly
All changes must go in `{{SOURCE_DIR}}` or permitted directories. `{{OUTPUT_DIR}}` is generated output.

{{ARCHITECTURE_OVERVIEW}}

## Verification
After changes:
```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_UNIT_COMMAND}}
```
