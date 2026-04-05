# copilot-agent-template

A generalized VS Code GitHub Copilot agent customization kit. Given any project repository, the `@Setup` agent reads the codebase and generates a tailored customization package for that project: root `AGENTS.md`, workspace `.github/` files, and `.vscode/settings.json`.

## What it generates

```
<your-project>/
├── AGENTS.md                        # Project constraints + file map
├── CLAUDE.md                        # Claude Code guidance (generated when .claude.json or CLAUDE.md detected)
├── .claude.json                     # Claude Code permission settings (generated when Claude Code patterns detected)
├── .vscode/
│   └── settings.json                # Agent handoff + skill location settings
└── .github/
  ├── copilot-instructions.md      # Always-on workspace instructions
  ├── agents/
  │   ├── <project>.agent.md       # Autonomous "do everything" agent
  │   ├── explore.agent.md         # Read-only exploration
  │   ├── plan.agent.md            # Task planning, outputs plan for approval
  │   ├── implementer.agent.md     # Executes an approved plan via handoff
  │   ├── reviewer.agent.md        # Security + quality auditor
  │   └── verification.agent.md    # Runs lint / build / tests
  ├── instructions/
  │   ├── src-coding.instructions.md
  │   └── testing.instructions.md
  ├── prompts/
  │   ├── plan-change.prompt.md
  │   ├── implement-change.prompt.md
  │   └── verify-workspace.prompt.md
  ├── hooks/
  │   └── pre-tool-use.json        # Optional advisory confirmation hook example
  ├── scripts/
  │   ├── guard-dangerous-command.sh
  │   └── run-project-checks.sh    # Optional POSIX helpers when sh is available
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

In your project:

```
@<ShortAgentName> # full autonomous agent, for example @APP
@Plan             # design an implementation plan
@Reviewer         # audit code changes
@Verification     # run tests + lint
@Explore          # read-only codebase exploration
```

`Implementer` is primarily intended as a handoff target from `@Plan` rather than the main entry point for users.

## Re-running setup

If the project structure changes significantly, re-run `@Setup` to refresh the customization files. The agent will detect existing customization files and summarize which files should be created or updated.

## Template reference

See [`templates/`](./templates/) for the raw templates with `{{PLACEHOLDER}}` markers. The setup agent fills these in automatically from project analysis.

Key templates:
- `templates/AGENTS.template.md` — project constraints and file map (always generated)
- `templates/CLAUDE.template.md` — Claude Code guidance (generated when Claude Code patterns detected)
- `templates/claude.template.json` — Claude Code permission settings (generated when Claude Code patterns detected)
- `templates/copilot-instructions.template.md` — always-on Copilot instructions

## Schema reference

See [`schema/project-profile.md`](./schema/project-profile.md) for the full list of extraction targets. You can edit the generated `AGENTS.md` to tune what the agents know.
