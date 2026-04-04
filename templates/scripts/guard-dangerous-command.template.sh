#!/usr/bin/env sh
set -eu

# Hook helper: ask for confirmation before obviously destructive commands.
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

case "$tool_name" in
  run_in_terminal|terminal|shell|bash|"")
    ;;
  *)
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
    exit 0
    ;;
esac

if ! printf '%s' "$normalized" | grep -Eq 'git push|git commit|git reset --hard|rm -rf |docker system prune|terraform apply|kubectl delete '; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Potentially destructive command detected. Confirm before continuing."}}'
