# copilot-agent-template

> 🌐 [日本語](./README.ja.md)

A generalized VS Code GitHub Copilot agent customization kit. Given any project repository, the `@Setup` agent reads the codebase and generates a tailored customization package: root `AGENTS.md`, workspace `.github/` files, `.vscode/settings.json`, and an optional GitHub Actions event trigger so that labeling a GitHub issue is enough to start a fully autonomous coding run.

Designed for **pay-per-token environments**: the pipeline minimizes inference cost through model routing, inter-phase state compression, and circuit-breaker retry control — without sacrificing code quality.

## Autonomous coding loop

This template replicates the three-layer autonomous pattern used by [claw-code](https://github.com/ultraworkers/claw-code):

| Layer                        | claw-code             | Copilot equivalent                                                              |
| ---------------------------- | --------------------- | ------------------------------------------------------------------------------- |
| **Execution loop**           | OmX / oh-my-codex     | `<project>.agent.md` — explore → plan → implement → verify                      |
| **Event trigger**            | clawhip               | `copilot-autoassign.yml` — label issue → Copilot opens PR                       |
| **Multi-agent coordination** | OmO / oh-my-openagent | Agent handoffs with lane-state JSON, Reflexion-guided recovery, circuit-breaker |

**Human interface**: file a GitHub issue and add the `copilot` label — from a browser, phone, or CLI. The agents handle the rest.

## What it generates

```
<your-project>/
├── AGENTS.md                          # Project constraints + file map
├── .vscode/
│   └── settings.json                  # Agent handoff + skill location settings
└── .github/
    ├── copilot-instructions.md        # Always-on workspace instructions + env awareness
    ├── schema/
    │   ├── lane-state.schema.json     # Inter-phase state object (Trajectory Reduction)
    │   ├── reflexion.schema.json      # Structured failure diagnosis for targeted fixes
    ├── workflows/
    │   └── copilot-autoassign.yml     # Event trigger: label → direct assign → Copilot opens PR
    ├── agents/
    │   ├── <project>.agent.md         # Autonomous pipeline agent (orchestrator)
    │   ├── explore.agent.md           # Read-only exploration  [model: Claude 4.6 Haiku]
    │   ├── plan.agent.md              # Task planning          [model: Claude 4.6 Sonnet]
    │   ├── implementer.agent.md       # Executes plan          [model: Claude 4.6 Sonnet]
    │   └── verification.agent.md      # Lint / build / tests   [model: Claude 4.6 Haiku]
    ├── instructions/
    │   ├── src-coding.instructions.md
    │   └── testing.instructions.md
    ├── prompts/
    │   ├── plan-change.prompt.md
    │   ├── implement-change.prompt.md  # Point-to-Point diffs only
    │   └── verify-workspace.prompt.md
    ├── hooks/
    │   ├── pre-tool-use.json          # Advisory confirmation before destructive commands
    │   └── post-tool-use.json         # Audit log after tool calls
    ├── scripts/
    │   ├── guard-dangerous-command.sh
    │   ├── run-project-checks.sh
    │   ├── create_skill.py            # Meta-tool: agent creates a new skill at runtime
    │   ├── refactor_skills.py         # Nightly consolidation of overlapping skills
    │   └── security/
    │       ├── codeql-scan.sh         # SAST wrapper (CodeQL → gh CLI → ESLint fallback)
    │       └── sast-api.py            # Unified Python SAST adapter (semgrep/codeql/eslint)
    └── skills/
        └── <domain>/
            ├── SKILL.md
            └── [optional bundled assets]
```

## Cost optimization architecture

Seven strategies to minimize token cost on pay-per-token APIs while maintaining code quality:

### 1. Per-agent model routing

Each agent file carries a fixed `model:` frontmatter field.

| Phase     | Model               |
| --------- | ------------------- |
| explore   | `Claude 4.6 Haiku`  |
| plan      | `Claude 4.6 Sonnet` |
| implement | `Claude 4.6 Sonnet` |
| verify    | `Claude 4.6 Haiku`  |

Claude Code users: the orchestrator also passes `model:` to `Agent` tool calls at runtime using the same names.

### 2. Trajectory Reduction — compress state between phases

The orchestrator never passes raw conversation history between phases. Instead, each phase transition serializes only what the next phase needs into a compact `LaneState` JSON object (schema: `.github/schema/lane-state.schema.json`):

```json
{
  "phase": "explore",
  "task": "Add login button",
  "relevant_files": ["src/auth/login.ts"],
  "plan_steps": [],
  "changed_files": [],
  "retry_count": 0,
  "error_fingerprints": []
}
```

This eliminates the exponential input-token growth that occurs when conversation history is forwarded across 5+ agent calls.

### 3. Point-to-Point editing — output only diffs

The Implementer agent is prohibited from using the Write tool to overwrite entire files. Every change is a Search/Replace edit — only the changed lines are generated, not the full file. For large files, this reduces output tokens by 10–100×.

### 4. Reflexion + circuit breaker — structured self-correction without loops

When verification fails, the Verification agent produces a `ReflexionReport` JSON (schema: `.github/schema/reflexion.schema.json`) instead of free-form error text:

```json
{
  "error_type": "test",
  "error_fingerprint": "test:TS2345_type_error_at_login",
  "root_cause": "login() return type changed from string to Promise<string>",
  "affected_files": [
    { "path": "src/auth/login.ts", "line": 42, "issue": "missing await" }
  ],
  "fix_plan": [
    {
      "file": "src/auth.test.ts",
      "search": "expect(login())",
      "replace": "expect(await login())",
      "rationale": "login is now async"
    }
  ],
  "safe_to_retry": true
}
```

The Implementer applies the `fix_plan` entries as Point-to-Point edits — no guessing.

**Circuit breaker**: if the same `error_fingerprint` appears twice in `lane_state.error_fingerprints[]`, the pipeline aborts immediately and escalates to the human rather than burning more tokens on a loop.

### 5. Shift-Left SAST — security checks during implementation

The Implementer calls `{{SAST_COMMAND}}` before marking each step complete. This catches security issues inline (when the fix is cheap) rather than discovering them in a later validation loop (when the fix is expensive).

Available wrappers (auto-selected by availability):

- `codeql` CLI
- `semgrep` (auto config)
- ESLint security plugin (JS/TS fallback)
- GitHub Advanced Security API (gh CLI fallback)

### 6. Voyager-pattern skill library — reuse instead of re-reason

`create_skill.py` distils successful implementations into `SKILL.md` files. `refactor_skills.py` merges overlapping skills nightly. New tasks query the skill library first — if a match exists, the agent applies the stored procedure directly instead of reasoning from scratch.

## Autonomous pipeline

```
[Workflow]  direct assign (label, 0 LLM calls)
                ↓
[Agent]     ▶ [LANE:explore]   → ✓ [LANE:explore:complete]    {Claude 4.6 Haiku}
            ▶ [LANE:plan]      → ✓ [LANE:plan:complete]       {Claude 4.6 Sonnet}
            ▶ [LANE:implement] → ✓ [LANE:implement:complete]   {Claude 4.6 Sonnet + SAST}
            ▶ [LANE:verify]    → ✓ [LANE:verify:complete]     {Claude 4.6 Haiku + Reflexion}
```

Between each phase: lane state JSON is serialized (conversation history is NOT forwarded).

A `✗ [LANE:{name}:blocked]` event means the lane failed and the pipeline is paused. The blocked agent reports the reason and, where possible, delegates back to the previous agent for self-correction. If the circuit breaker fires (`error_fingerprint` seen twice), the pipeline stops immediately and reports to the human.

For large tasks that span multiple sessions, the autonomous agent emits a `SESSION CHECKPOINT` block containing the current `lane_state` JSON so work can resume in a new session without re-running completed lanes.

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
    { "path": "/path/to/copilot-agent-template" },
  ],
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
2. Identify your tech stack, conventions, build/test commands, and domain constraints
3. Set `Claude 4.6 Haiku` and `Claude 4.6 Sonnet` as the models for lightweight and advanced phases
4. Configure `{{SAST_COMMAND}}` based on which security tools are installed (`codeql`, `semgrep`, or `eslint-plugin-security`)
5. Generate `AGENTS.md`, `.github/`, `.vscode/settings.json`, prompts, hooks, security scripts, and skills

The included PreToolUse hook is a convenience example, not a hard security boundary. If you need stronger protection, point the hook at a user-managed script outside the repository.

Shell-based helpers assume a POSIX `sh` runtime. Setup only generates them when the target project already relies on `sh`.

### 4. Close the template from the workspace (optional)

Once setup is done, you can remove this repo from the workspace.

### 5. Use the generated agents

**From VS Code Copilot Chat:**

```
@<ShortAgentName> implement X    # full autonomous run
@Plan             design an implementation plan
@Verification     run tests + lint
@Explore          read-only codebase exploration
```

Use prompt shortcuts from `.github/prompts/` (VS Code only):

- **Plan Change** — structured plan for a feature or bugfix
- **Implement Change** — full pipeline; enforces Point-to-Point edits and SAST check
- **Verify Workspace** — targeted lint/build/test run with Reflexion output on failure

**From any device (GitHub issue → autonomous PR):**

1. File or pick a GitHub issue describing the task
2. Add the label `copilot` (or the label configured during setup)
3. The workflow automatically classifies the issue (Level 1/2/3) and assigns to Copilot
4. Level 3 tasks pause for a human approval label before the pipeline starts
5. The agent runs the full pipeline and opens a PR — no local environment needed

**From GitHub.com (browser agent session):**

```
@copilot implement <task description>
@copilot plan <feature request>
```

Handoff buttons are not available in the browser; agents output the next step's prompt inline for continuation.

## Re-running setup

If the project structure changes significantly, re-run `@Setup` to refresh the customization files. The agent will detect existing customization files and summarize what will be created or updated.

## Template reference

See [`templates/`](./templates/) for the raw templates with `{{PLACEHOLDER}}` markers. The setup agent fills these in automatically from project analysis.

Key templates:

- `templates/agents/autonomous.template.agent.md` — full 4-phase pipeline with Trajectory Reduction and circuit breaker
- `templates/agents/explore.template.agent.md` — read-only exploration (`model: Claude 4.6 Haiku`)
- `templates/agents/plan.template.agent.md` — planning (`model: Claude 4.6 Sonnet`)
- `templates/agents/implementer.template.agent.md` — Point-to-Point implementation (`model: Claude 4.6 Sonnet`)
- `templates/agents/verification.template.agent.md` — verification with Reflexion output (`model: Claude 4.6 Haiku`)
- `templates/workflows/copilot-autoassign.template.yml` — direct-assignment workflow
- `templates/schema/lane-state.schema.json` — inter-phase state contract
- `templates/schema/reflexion.schema.json` — structured failure diagnosis contract
- `templates/scripts/security/codeql-scan.template.sh` — SAST shell wrapper
- `templates/scripts/security/sast-api.template.py` — Python SAST adapter

## Agent meta-tools: autonomous skill creation and nightly refactoring

Two Python scripts in `templates/scripts/` let an agent **grow its own skill library at runtime** — inspired by the [Voyager](https://voyager.minedojo.org/) self-improving agent architecture.

### `create_skill.py` — distil a solved task into a reusable skill

After an agent successfully completes a task it had not seen before, it calls this script to preserve the winning logic as a new `SKILL.md`:

```sh
python .agent/tools/create_skill.py \
  --name        "sort_scene_stream" \
  --description "Sort scene data by view-space depth" \
    --code_file   "temp_sort.ts" \
    --domain      "3dcg" \
  --subdomain   "scene-stream" \
    --facets      "lang:typescript,target:browser" \
    --skills_dir  ".agent/skills"
```

### `refactor_skills.py` — nightly consolidation of overlapping skills

Scans all accumulated `SKILL.md` files, detects overlapping skills via token-level similarity, and (with `--merge`) writes consolidated drafts for human inspection.

```sh
# Dry-run: report overlaps
python .agent/tools/refactor_skills.py --skills_dir .agent/skills

# Merge overlapping skills
python .agent/tools/refactor_skills.py --skills_dir .agent/skills --merge
```

### OJT loop

| Phase                  | What happens                                                |
| ---------------------- | ----------------------------------------------------------- |
| **1 Attempt**          | Agent queries skills DB, tries task with existing knowledge |
| **2 Explore & Search** | On failure, reads docs and updates code                     |
| **3 Verify**           | Runs tests; repeats Phase 2 until passing                   |
| **4 Distil & Store**   | Calls `create_skill.py` to save the winning implementation  |

## Schema reference

See [`schema/project-profile.md`](./schema/project-profile.md) for the full list of `{{PLACEHOLDER}}` extraction targets, including `Claude 4.6 Haiku`, `Claude 4.6 Sonnet`, `{{SAST_COMMAND}}`, and `{{PRIMARY_LANGUAGE_CODEQL}}`.

## Domain skills scaffold

`templates/skills/` ships a scaffold for domain-specific knowledge packs: coding (network, embedded), 3D CG (Blender, Houdini), CAD (parametric), machine learning (training, inference), and game engines (Unity, Unreal). Layout: **`<domain>/<subdomain>/SKILL.md`** with orthogonal axes expressed as `facets:` in the front-matter.

- [`templates/skills/README.md`](./templates/skills/README.md) — layering model and directory layout
- [`templates/skills/EXTENDING.md`](./templates/skills/EXTENDING.md) — how to add a new domain or subdomain
- [`templates/skills/SKILL_CATALOG.md`](./templates/skills/SKILL_CATALOG.md) — numbered catalog of all planned Generative Spatial Computing skills
