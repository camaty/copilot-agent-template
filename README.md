# copilot-agent-template

> 🌐 [日本語](./README.ja.md)

A generalized VS Code GitHub Copilot agent customization kit. Given any project repository, the `@Setup` agent reads the codebase and generates a tailored customization package for that project: root `AGENTS.md`, workspace `.github/` files, `.vscode/settings.json`, and an optional GitHub Actions event trigger so that labeling a GitHub issue is enough to start a fully autonomous coding run.

## Autonomous coding loop

This template replicates the three-layer autonomous pattern used by [claw-code](https://github.com/ultraworkers/claw-code):

| Layer | claw-code | Copilot equivalent |
|---|---|---|
| **Execution loop** | OmX / oh-my-codex | `<project>.agent.md` — explore → plan → implement → verify (retry ×3) → review → report |
| **Event trigger** | clawhip | `copilot-autoassign.yml` — label issue → GitHub Actions assigns to Copilot → agent opens PR |
| **Multi-agent coordination** | OmO / oh-my-openagent | Agent handoffs: Plan → Implementer → Reviewer → Verification, with disagreement recovery |

**Human interface**: file a GitHub issue and add the `copilot` label — from a browser, phone, or CLI. The agents handle the rest.

## What it generates

```
<your-project>/
├── AGENTS.md                          # Project constraints + file map
├── CLAUDE.md                          # Claude Code guidance (when .claude.json or .claude/ detected)
├── .claude.json                       # Claude Code permission settings (when Claude Code patterns detected)
├── .vscode/
│   └── settings.json                  # Agent handoff + skill location settings
└── .github/
  ├── copilot-instructions.md        # Always-on workspace instructions + env awareness
  ├── workflows/
  │   └── copilot-autoassign.yml     # Event trigger: label issue → Copilot opens PR
  ├── agents/
  │   ├── <project>.agent.md         # Autonomous pipeline agent
  │   ├── explore.agent.md           # Read-only exploration
  │   ├── plan.agent.md              # Task planning, outputs plan for approval
  │   ├── implementer.agent.md       # Executes an approved plan (lane events per step)
  │   ├── reviewer.agent.md          # Security + quality auditor
  │   └── verification.agent.md      # Runs lint / build / tests / E2E gate
  ├── instructions/
  │   ├── src-coding.instructions.md
  │   └── testing.instructions.md
  ├── prompts/
  │   ├── plan-change.prompt.md
  │   ├── implement-change.prompt.md
  │   └── verify-workspace.prompt.md
  ├── hooks/
  │   ├── pre-tool-use.json          # Advisory confirmation before destructive commands
  │   └── post-tool-use.json         # Optional audit log after tool calls
  ├── scripts/
  │   ├── guard-dangerous-command.sh
  │   └── run-project-checks.sh      # Optional POSIX helpers when sh is available
  └── skills/
    └── <domain>/
      ├── SKILL.md
      └── [optional bundled assets]
```

## Workflow

### 1. Clone this repo alongside your project

```sh
# In a parent directory that contains your project:
git clone https://github.com/your-org/copilot-agent-template
```

Or as a submodule:

```sh
cd your-project
git submodule add https://github.com/your-org/copilot-agent-template .agent-setup
```

### 2. Open VS Code with both folders as a multi-root workspace

```jsonc
// .code-workspace
{
  "folders": [
    { "path": "/path/to/your-project" },
    { "path": "/path/to/copilot-agent-template" }
  ]
}
```

Or just open both folders: **File → Add Folder to Workspace**.

### 3. Run the `@Setup` agent

In VS Code Copilot Chat, type:

```
@Setup /path/to/your-project
```

The agent will:
1. Read your project's `README.md`, package manager manifest, architecture docs, and representative source and test files
2. Identify your tech stack, conventions, build and test commands, runtime settings, and domain constraints
3. Generate root `AGENTS.md`, `.github/`, `.vscode/settings.json`, prompts, and any hooks, helper scripts, or skill assets that fit the project's actual runtime conventions
4. If the project uses Claude Code (detected via `.claude.json`, `CLAUDE.md`, or a `.claude/` directory), also generate `CLAUDE.md` and `.claude.json`
5. Show which files will be created or updated, then ask for confirmation before writing

The included PreToolUse hook is a convenience example, not a hard security boundary. If you need stronger protection, point the hook at a user-managed script outside the repository or protect the helper script with OS-level permissions.

Shell-based helpers assume a POSIX `sh` runtime. Setup should only generate them when the target project already relies on `sh`; otherwise it should skip them and leave a platform-specific follow-up to the user.

### 4. Close the template from the workspace (optional)

Once setup is done, you can remove this repo from the workspace. The generated customization files live in `AGENTS.md`, `.github/`, and `.vscode/settings.json` inside your project.

### 5. Use the generated agents

**From VS Code Copilot Chat:**

```
@<ShortAgentName> implement X    # full autonomous run (explore → plan → implement → verify → review)
@Plan             design an implementation plan
@Reviewer         audit code changes
@Verification     run tests + lint
@Explore          read-only codebase exploration
```

Use prompt shortcuts from `.github/prompts/` (VS Code only):
- **Plan Change** — structured plan for a feature or bugfix
- **Implement Change** — run the full pipeline for a specific request
- **Verify Workspace** — targeted lint/build/test run

**From any device (GitHub issue → autonomous PR):**

1. File or pick a GitHub issue describing the task
2. Add the label `copilot` (or the label configured during setup)
3. The `copilot-autoassign.yml` workflow assigns it to the Copilot Coding Agent
4. The agent runs the full pipeline and opens a PR — no local environment needed

To create the label if it doesn't already exist: **Issues → Labels → New label** → name it `copilot`.

**From GitHub.com (browser agent session):**
```
@copilot implement <task description>
@copilot plan <feature request>
```
Handoff buttons are not available in the browser; agents will output the next step's prompt inline for continuation.

`Implementer` is primarily intended as a handoff target from `@Plan` rather than the main entry point for users.

## Autonomous pipeline

All agents emit structured lane events before and after each pipeline phase, making every state machine-readable:

```
▶ [LANE:explore]   → ✓ [LANE:explore:complete]
▶ [LANE:plan]      → ✓ [LANE:plan:complete]
▶ [LANE:implement] → ✓ [LANE:implement:complete]
▶ [LANE:verify]    → ✓ [LANE:verify:complete]
▶ [LANE:review]    → ✓ [LANE:review:complete]
```

A `✗ [LANE:{name}:blocked]` event means the lane failed and the pipeline is paused. The blocked agent reports the reason and, where possible, delegates back to the previous agent for self-correction.

For large tasks that span multiple sessions, the autonomous agent emits a `SESSION CHECKPOINT` block at end-of-context so work can resume in a new session without re-running completed lanes.

## Re-running setup

If the project structure changes significantly, re-run `@Setup` to refresh the customization files. The agent will detect existing customization files and summarize which files should be created or updated.

## Template reference

See [`templates/`](./templates/) for the raw templates with `{{PLACEHOLDER}}` markers. The setup agent fills these in automatically from project analysis.

Key templates:
- `templates/agents/autonomous.template.agent.md` — full autonomous pipeline with retry loop (always generated)
- `templates/workflows/copilot-autoassign.template.yml` — event trigger: label issue → Copilot opens PR (generated when GitHub Actions detected)
- `templates/AGENTS.template.md` — project constraints and file map (always generated)
- `templates/CLAUDE.template.md` — Claude Code guidance (generated when Claude Code patterns detected)
- `templates/claude.template.json` — Claude Code permission settings (generated when Claude Code patterns detected)
- `templates/copilot-instructions.template.md` — always-on Copilot instructions

## Schema reference

See [`schema/project-profile.md`](./schema/project-profile.md) for the full list of extraction targets. You can edit the generated `AGENTS.md` to tune what the agents know.
