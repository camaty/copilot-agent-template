---
description: "Implement a scoped change in {{PROJECT_NAME}} using the generated agent workflow"
name: "Implement Change"
argument-hint: "Feature, bugfix, or refactor request"
agent: "{{AUTONOMOUS_AGENT_NAME}}"
---
Implement the requested change in {{PROJECT_NAME}}.

Requirements:
- Read [AGENTS.md](../../AGENTS.md) and respect project constraints
- Keep changes tightly scoped to the user request
- **Point-to-Point edits only** — never rewrite entire files; use Search/Replace blocks per file
- Run `{{LINT_COMMAND}}`, `{{BUILD_COMMAND}}`, and `{{SAST_COMMAND}}` (if configured) before finishing
- Run the narrowest relevant tests before reporting complete
- If the task is ambiguous or risky, stop and ask a clarifying question before editing
- Report any verification that could not be run (e.g., SAST tool not installed)
- On repeated failures, emit a circuit-breaker event and escalate rather than guessing
