# Workflow: New Project Setup

End-to-end guide for using `copilot-agent-template` to add Copilot agent customization to a new project.

---

## Prerequisites

- VS Code with GitHub Copilot Chat installed
- The target project already has a `README.md` and at least some source files

---

## Step 1 — Clone this repo

```sh
# Option A: standalone clone next to your project
cd ~/projects
git clone https://github.com/your-org/copilot-agent-template

# Option B: as a submodule inside your project (temporary)
cd your-project
git submodule add https://github.com/your-org/copilot-agent-template .agent-setup
```

---

## Step 2 — Open a multi-root workspace

Add both folders to VS Code:

```jsonc
// my-project.code-workspace
{
  "folders": [
    { "name": "my-project", "path": "/path/to/my-project" },
    { "name": "agent-template", "path": "/path/to/copilot-agent-template" }
  ]
}
```

Or via the menu: **File → Add Folder to Workspace**, then add `copilot-agent-template`.

---

## Step 3 — Run @Setup

In GitHub Copilot Chat, switch to the `@Setup` agent and provide your project path:

```
@Setup /path/to/my-project
```

The agent will go through 6 numbered phases:

| Phase | What happens |
|-------|-------------|
| **0 — Inspect** | Lists existing `AGENTS.md`, `.github/`, and `.vscode/settings.json`; starts read-only analysis |
| **1 — Analyze** | Reads README, package.json/pyproject.toml, source + test files, and any existing customization files |
| **2 — Plan writes** | Summarizes which files will be created, updated, or left unchanged and asks for confirmation |
| **3 — Generate** | Writes root `AGENTS.md`, `.github/`, `.vscode/settings.json`, prompts, hooks, and helper scripts |
| **4 — Validate** | Checks YAML syntax, JSON syntax, line count, and placeholder fill |
| **5 — Next steps** | Tells you what to do next |

Expected duration: 3-10 minutes depending on project size.

---

## Step 4 — Review generated files

Open each generated file and spot-check:

- `AGENTS.md` — does the file tree look right? Are the constraints accurate?
- `CLAUDE.md` — (if generated) do the verification commands use fully qualified paths from repo root? Is the repo shape accurate?
- `.claude.json` — (if generated) is the `defaultMode` setting appropriate for your workflow?
- `.github/copilot-instructions.md` — is the project summary accurate? Under 200 lines?
- `.github/agents/*.agent.md` — do the `description` fields have meaningful trigger phrases?
- `.github/instructions/*.instructions.md` — are `applyTo` globs correct for your codebase?
- `.github/prompts/*.prompt.md` — do the prompt bodies route to the right agent with the right scope?
- `.github/hooks/*.json` — if generated, do the hook commands point to existing scripts, and is the helper path appropriate for the level of protection you want?
- `.github/scripts/*.sh` — if generated, do the wrappers use commands that actually exist in the project and match the project's runtime conventions?
- `.github/skills/*/SKILL.md` — is the domain procedure correct, and do any bundled assets make sense?
- `.vscode/settings.json` — are the recommended agent and skill settings appropriate for your workspace?

Edit any file that needs tuning.

---

## Step 5 — Commit

```sh
cd your-project
# Base files (always generated)
git add AGENTS.md .github/ .vscode/settings.json
# Claude Code files (only when generated; silently skipped if absent)
git add CLAUDE.md .claude.json 2>/dev/null || :
git commit -m "chore: add Copilot agent customization"
```

---

## Step 6 — Remove template from workspace

If you used the standalone clone, close it from VS Code:
**File → Remove Folder from Workspace**, select `agent-template`.

If you used a submodule and don't want to keep it:
```sh
git submodule deinit .agent-setup
git rm .agent-setup
git commit -m "chore: remove temporary agent-setup submodule"
```

---

## Step 7 — Start using agents

### From VS Code Copilot Chat

```
@<ShortAgentName>  Implement <feature>   # full autonomous run
@Plan              Add support for <feature>
@Explore           How does <subsystem> work?
@Verification      Run all tests
```

### From any device — event-driven autonomous run

If the trigger workflow was generated (requires GitHub Actions on the project):

1. File a GitHub issue describing the task in plain language
2. Add the label `copilot` (or the label you chose during setup)
3. The workflow assigns the issue to the Copilot Coding Agent automatically
4. The agent runs: explore → plan → implement → verify (with up to 3 self-correction retries) → review → open PR
5. Review the PR — no local environment needed

To create the label if it doesn't already exist: **Issues → Labels → New label** → name it `copilot`.

---

## Updating customization later

If the project structure changes significantly, re-run `@Setup` to refresh:

```
@Setup /path/to/my-project
```

The agent will inspect existing customization files, preserve matching patterns where useful, and summarize what it plans to create or update before writing.

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `@Setup` agent not visible | Ensure `copilot-agent-template` is in the VS Code workspace |
| Generated files look wrong | Run `@Setup` again with more context: *"The main language is Python, build tool is Make"* |
| `description` causes YAML error | Wrap the value in double quotes; escape inner `"` with `\"` |
| `applyTo` glob not matching | Test the glob in the VS Code file search to verify it matches |
| Agent not being discovered | Check that `description` contains the same keywords you type in chat |
| Build commands use wrong directory | If your build root is a subdirectory (e.g. `rust/`), hint Setup: *"The Rust workspace is in rust/"* |
| `CLAUDE.md` not generated | Setup generates it when `.claude.json`, `CLAUDE.md`, or `.claude/` is detected; add one of those to trigger generation, or add a `.claude.json` with `{"permissions":{"defaultMode":"default"}}` |
| `copilot-autoassign.yml` not generated | Setup only generates it when GitHub Actions workflows already exist in `.github/workflows/`; create an empty workflow file to trigger detection, or add `--with-actions` to your `@Setup` prompt |
| Copilot not picking up the issue | Ensure the issue is assigned to the `copilot` user (the workflow does this automatically on label) |
