# Project Profile Schema

This schema defines all the information the `@Setup` agent extracts from a project before generating customization files.
Each field is referenced as `{{FIELD_NAME}}` in the templates.

---

## Identity

| Placeholder | Description | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Repository / product name | `ExampleService` |
| `{{PROJECT_DESCRIPTION}}` | One-sentence summary | `A multi-package application with a web client, backend services, and CI automation` |
| `{{TECH_STACK}}` | Comma-separated stack | `TypeScript, React, Node.js, PostgreSQL` |
| `{{PRIMARY_LANGUAGE}}` | Main language | `JavaScript` |
| `{{PACKAGE_MANAGER}}` | Package manager | `npm` / `pip` / `cargo` / `go` |

## Directories

| Placeholder | Description | Example |
|---|---|---|
| `{{SOURCE_DIR}}` | Primary source directory | `src/` |
| `{{SOURCE_GLOB}}` | Glob matching source files | `src/**/*.js` |
| `{{OUTPUT_DIR}}` | Generated / build output dir | `build/` |
| `{{TEST_DIR}}` | Test root directory | `tests/` |
| `{{DOCS_DIR}}` | Documentation directory (if any) | `docs/` |

## Commands

| Placeholder | Description | Example |
|---|---|---|
| `{{BUILD_COMMAND}}` | Full build command | `npm run build` |
| `{{LINT_COMMAND}}` | Lint / format check | `npm run lint` |
| `{{TEST_COMMAND}}` | Run all tests | `npm test` |
| `{{TEST_UNIT_COMMAND}}` | Run unit tests only | `npm run test:unit` |
| `{{TEST_INTEGRATION_COMMAND}}` | Run integration tests | `npm run test:integration` |
| `{{FORMAT_COMMAND}}` | Auto-format (if separate) | `npm run fmt` |
| `{{TYPECHECK_COMMAND}}` | Type-check command (if any) | `npx tsc --noEmit` |

## Architecture

| Placeholder | Description |
|---|---|
| `{{ARCHITECTURE_OVERVIEW}}` | 2-4 sentence description of the component model and key data flows |
| `{{KEY_MODULES}}` | Markdown bullet list of important source modules with one-line descriptions |
| `{{KEY_ENTRY_POINTS}}` | Main entry point(s) (e.g., `src/index.js`, `main.py`) |
| `{{KEY_CONSTRAINTS}}` | Non-negotiable project constraints as bullet list (e.g., "Never edit build/") |

## Code Style

| Placeholder | Description | Example |
|---|---|---|
| `{{CODE_STYLE_RULES}}` | Bullet list of style rules | `2-space indent, double quotes, semicolons, LF` |
| `{{NAMING_CONVENTIONS}}` | File and symbol naming rules | `PascalCase for classes, camelCase for functions` |
| `{{IMPORT_ORDER}}` | Module import ordering rules | `built-in → external → internal` |
| `{{FORMATTER}}` | Formatter used | `Prettier` / `Black` / `rustfmt` |

## Testing

| Placeholder | Description | Example |
|---|---|---|
| `{{TEST_FRAMEWORK}}` | Test runner / framework | `node:test`, `pytest`, `jest`, `cargo test` |
| `{{TEST_STRUCTURE}}` | Description of test tiers | `unit/ integration/ system/` |
| `{{COVERAGE_TARGETS}}` | Coverage goals | `Statements ≥ 85%, Branches ≥ 80%` |

## Agents

| Placeholder | Description | Example |
|---|---|---|
| `{{AUTONOMOUS_AGENT_NAME}}` | Short name for the main autonomous agent | `APP` |
| `{{AUTONOMOUS_AGENT_FILE}}` | Kebab-case filename of the autonomous agent (lowercase of name) | `app` |
| `{{AUTONOMOUS_AGENT_DESCRIPTION}}` | Description for the agent picker | `Full autonomous coding agent for <project>` |

## Prompts

Repeat the block below for each prompt the setup agent should create (typically 2-3):

| Placeholder | Description | Example |
|---|---|---|
| `{{PROMPT_1_NAME}}` | Prompt display name | `Plan Change` |
| `{{PROMPT_1_DESCRIPTION}}` | Prompt description | `Create an implementation plan for a requested change` |
| `{{PROMPT_1_AGENT}}` | Agent to invoke | `Plan` |
| `{{PROMPT_1_ARGUMENT_HINT}}` | Chat input hint | `Feature, bugfix, or refactor request` |
| `{{PROMPT_1_BODY}}` | Prompt body | `Create a structured plan for the requested change...` |

## Hooks And Settings

| Placeholder | Description | Example |
|---|---|---|
| `{{DEFAULT_MODEL}}` | Preferred Copilot model setting | `GPT-5 (copilot)` |
| `{{SKILLS_LOCATIONS}}` | JSON array literal for skill search paths in settings.json | `[".github/skills", ".agents/skills"]` |
| `{{SCRIPT_RUNTIME}}` | Helper-script runtime that is safe to assume | `sh` / `none` |
| `{{HOOK_1_NAME}}` | Hook file name | `pre-tool-use.json` |
| `{{HOOK_1_DESCRIPTION}}` | What the hook enforces | `Ask before obviously destructive terminal commands` |
| `{{COPILOT_LABEL}}` | GitHub issue label that triggers the autonomous agent via Actions | `copilot` |

## Domain Skills

Repeat the block below for each domain-specific skill the project warrants (typically 1-3):

| Placeholder | Description | Example |
|---|---|---|
| `{{SKILL_1_NAME}}` | Skill folder name (kebab-case) | `frontend-testing` |
| `{{SKILL_1_DESCRIPTION}}` | One-line description for skill discovery | `Building and debugging browser-based end-to-end tests` |
| `{{SKILL_1_TRIGGERS}}` | Comma-separated trigger phrases | `playwright, e2e, browser test, ui regression` |
| `{{SKILL_1_CONTENT}}` | Main body rendered into the skill procedure section | Step-by-step domain procedure |
| `{{SKILL_1_ASSET_SECTION}}` | Bundled assets section rendered into SKILL.md | `- [run-checks.sh](./run-checks.sh) — wrapper for repeated validation commands` |
| `{{SKILL_1_ASSET_FILES}}` | Optional sibling assets to create alongside SKILL.md | `run-checks.sh, test-template.ts` |
| `{{SKILL_1_WRAPPER_COMMAND}}` | Command used by a bundled shell wrapper | `npx playwright test "$@"` |

When materializing a specific domain skill into `templates/skills/core-domain/SKILL.template.md` or `templates/skills/core-domain/command-wrapper.template.sh`, map that skill's indexed values onto the generic template placeholders. For example, `SKILL_1_NAME` becomes `SKILL_NAME` and `SKILL_1_WRAPPER_COMMAND` becomes `SKILL_WRAPPER_COMMAND` for that skill's generated files.

## Extraction Hints for the Setup Agent

When extracting these values from a project, follow this priority order:

1. `README.md` → `PROJECT_NAME`, `PROJECT_DESCRIPTION`, `TECH_STACK`
2. `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` → `PACKAGE_MANAGER`, `BUILD_COMMAND`, `LINT_COMMAND`, `TEST_COMMAND`, `PRIMARY_LANGUAGE`
3. `CONTRIBUTING.md` / `DEVELOPMENT.md` → `CODE_STYLE_RULES`, `KEY_CONSTRAINTS`
4. `ARCHITECTURE.md` / `docs/` → `ARCHITECTURE_OVERVIEW`, `KEY_MODULES`
5. `AGENTS.md` (if present) → all fields; use as ground truth when available
6. Source file sampling (read 5-10 source files) → `NAMING_CONVENTIONS`, `IMPORT_ORDER`, `CODE_STYLE_RULES`
7. Test directory listing → `TEST_FRAMEWORK`, `TEST_STRUCTURE`, `TEST_DIR`
8. Existing `.github/prompts/`, `.github/hooks/`, `.github/skills/`, and `.vscode/settings.json` files → preserve good patterns and only generalize what matches the current project
