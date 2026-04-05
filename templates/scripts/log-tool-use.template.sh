#!/usr/bin/env sh
# PostToolUse audit-log hook.
# Appends a one-line entry to .github/tool-use.log so every tool call is
# traceable. Useful for debugging blocked pipeline lanes and auditing agent actions.
set -eu

payload="$(cat)"
normalized="$(printf '%s' "$payload" | tr '\n' ' ')"

extract_json_string() {
  key="$1"
  printf '%s' "$normalized" | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

tool_name="$(extract_json_string toolName)"
if [ -z "$tool_name" ]; then
  tool_name="$(extract_json_string tool_name)"
fi
if [ -z "$tool_name" ]; then
  tool_name="unknown"
fi

log_dir="$(dirname "$0")/../"
log_file="${log_dir}tool-use.log"
mkdir -p "$(dirname "$log_file")"

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || printf 'unknown-time')"
printf '%s tool=%s\n' "$timestamp" "$tool_name" >> "$log_file"

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","permissionDecision":"allow"}}'
