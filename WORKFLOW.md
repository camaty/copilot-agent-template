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

The agent will go through 4 phases:

| Phase | What happens |
|-------|-------------|
| **0 — Confirm** | Lists existing `.github/` files; asks for confirmation |
| **1 — Analyze** | Reads README, package.json/pyproject.toml, source + test files |
| **2 — Generate** | Writes all `.github/` customization files |
| **3 — Validate** | Checks YAML syntax, line count, placeholder fill |
| **4 — Next steps** | Tells you what to do next |

Expected duration: 3-10 minutes depending on project size.

---

## Step 4 — Review generated files

Open each generated file and spot-check:

- `AGENTS.md` — does the file tree look right? Are the constraints accurate?
- `.github/copilot-instructions.md` — is the project summary accurate? Under 200 lines?
- `.github/agents/*.agent.md` — do the `description` fields have meaningful trigger phrases?
- `.github/instructions/*.instructions.md` — are `applyTo` globs correct for your codebase?
- `.github/skills/*/SKILL.md` — is the domain procedure correct?

Edit any file that needs tuning.

---

## Step 5 — Commit

```sh
cd your-project
git add AGENTS.md .github/
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

In a new Copilot Chat, try:

```
@Plan  Add support for <some feature>
```

```
@Explore  How does <subsystem> work?
```

```
@Verification  Run all tests
```

---

## Updating customization later

If the project structure changes significantly, re-run `@Setup` to refresh:

```
@Setup /path/to/my-project
```

The agent will compare against existing files and offer diffs.

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `@Setup` agent not visible | Ensure `copilot-agent-template` is in the VS Code workspace |
| Generated files look wrong | Run `@Setup` again with more context: *"The main language is Python, build tool is Make"* |
| `description` causes YAML error | Wrap the value in double quotes; escape inner `"` with `\"` |
| `applyTo` glob not matching | Test the glob in the VS Code file search to verify it matches |
| Agent not being discovered | Check that `description` contains the same keywords you type in chat |
