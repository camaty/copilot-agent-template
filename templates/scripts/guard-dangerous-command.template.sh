#!/usr/bin/env sh
set -eu

# PreToolUse hook helper: request confirmation before obviously destructive or
# irreversible commands. This is an advisory guard — it asks before acting, not
# a hard security boundary. For stronger protection, move this script outside
# the repository and protect it with OS-level permissions.
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

# Patterns that require confirmation before proceeding:
#   git destructive ops, force-push, hard reset
#   filesystem wipe, recursive delete
#   cloud/infra apply and destroy
#   credential exposure (echo $KEY, cat .env, printenv)
#   gh CLI ops that mutate remote state (issue close, pr merge, release create)
#   eval of dynamic content
if ! printf '%s' "$normalized" | grep -Eq \
  'git push|git commit|git reset --hard|git rebase -i|git clean -f|git stash drop|\
rm -rf |find .* -delete|chmod -R 777|\
docker system prune|docker rm |docker rmi |\
terraform apply|terraform destroy|kubectl delete|kubectl apply|\
gh issue (close|delete|edit)|gh pr (merge|close)|gh release create|\
aws .* delete|gcloud .* delete|az .* delete|\
printenv .*KEY|printenv .*SECRET|printenv .*TOKEN|\
cat \.env|echo \$[A-Z_]*KEY|echo \$[A-Z_]*SECRET|echo \$[A-Z_]*TOKEN|\
eval '; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
  exit 0
fi

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Potentially destructive or irreversible command detected. Confirm before continuing."}}'
