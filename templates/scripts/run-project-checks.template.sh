#!/usr/bin/env sh
set -eu

printf '%s\n' "Running project verification..."

# Remove unavailable commands or replace them with ':' when materializing this template.
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
