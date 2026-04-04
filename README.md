# copilot-agent-template

A generalized VS Code GitHub Copilot agent customization kit. Given any project repository, the `@Setup` agent reads the codebase and generates a full `.github/` customization folder — agents, instructions, skills, and prompts — tailored to that project.

## What it generates

```
<your-project>/.github/
├── copilot-instructions.md          # Always-on workspace instructions
├── AGENTS.md                        # Project constraints + file map
├── agents/
│   ├── <project>.agent.md           # Autonomous "do everything" agent
│   ├── explore.agent.md             # Read-only exploration
│   ├── plan.agent.md                # Task planning, outputs plan for approval
│   ├── implementer.agent.md         # Executes an approved plan
│   ├── reviewer.agent.md            # Security + quality auditor
│   └── verification.agent.md        # Runs lint / build / tests
├── instructions/
│   ├── src-coding.instructions.md   # Code style, patterns, conventions
│   └── testing.instructions.md      # Test pyramid + coverage targets
├── skills/
│   └── <domain>/SKILL.md            # Per-skill domain knowledge
└── prompts/
    └── <workflow>.prompt.md         # Reusable task prompts
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
1. Read your project's `README.md`, `package.json` / `pyproject.toml` / `Cargo.toml`, `CONTRIBUTING.md`, and source files
2. Identify your tech stack, conventions, build + test commands, and domain constraints
3. Generate all `.github/` customization files in your project
4. Ask for confirmation before writing

### 4. Close the template from the workspace (optional)

Once setup is done, you can remove this repo from the workspace. The generated `.github/` is self-contained.

### 5. Use the generated agents

In your project:

```
@<ProjectName>    # full autonomous agent
@Plan             # design an implementation plan
@Implementer      # execute a plan
@Reviewer         # audit code changes
@Verification     # run tests + lint
@Explore          # read-only codebase exploration
```

## Re-running setup

If the project structure changes significantly, re-run `@Setup` to update the customization files. The agent will diff against existing files and offer updates.

## Template reference

See [`templates/`](./templates/) for the raw templates with `{{PLACEHOLDER}}` markers. The setup agent fills these in automatically from project analysis.

## Schema reference

See [`schema/project-profile.md`](./schema/project-profile.md) for the full list of extraction targets. You can edit the generated `AGENTS.md` to tune what the agents know.
