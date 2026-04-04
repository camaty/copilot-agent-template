# Project Profile Schema

This schema defines all the information the `@Setup` agent extracts from a project before generating customization files.
Each field is referenced as `{{FIELD_NAME}}` in the templates.

---

## Identity

| Placeholder | Description | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Repository / product name | `GaussianSplats3D` |
| `{{PROJECT_DESCRIPTION}}` | One-sentence summary | `Three.js-based 3D Gaussian Splat renderer, viewer, and distributable library` |
| `{{TECH_STACK}}` | Comma-separated stack | `JavaScript, Three.js, WebGL, WebGPU, Node.js` |
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
| `{{AUTONOMOUS_AGENT_NAME}}` | Short name for the main autonomous agent | `GS` (for GaussianSplats3D) |
| `{{AUTONOMOUS_AGENT_DESCRIPTION}}` | Description for the agent picker | `Full autonomous coding agent for <project>` |

## Domain Skills

Repeat the block below for each domain-specific skill the project warrants (typically 1-3):

| Placeholder | Description | Example |
|---|---|---|
| `{{SKILL_1_NAME}}` | Skill folder name (kebab-case) | `loader-development` |
| `{{SKILL_1_DESCRIPTION}}` | One-line description for skill discovery | `Adding or modifying file format loaders...` |
| `{{SKILL_1_TRIGGERS}}` | Comma-separated trigger phrases | `new loader, file format, parser` |
| `{{SKILL_1_CONTENT}}` | Full body of the SKILL.md | Step-by-step domain procedure |

## Extraction Hints for the Setup Agent

When extracting these values from a project, follow this priority order:

1. `README.md` → `PROJECT_NAME`, `PROJECT_DESCRIPTION`, `TECH_STACK`
2. `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` → `PACKAGE_MANAGER`, `BUILD_COMMAND`, `LINT_COMMAND`, `TEST_COMMAND`, `PRIMARY_LANGUAGE`
3. `CONTRIBUTING.md` / `DEVELOPMENT.md` → `CODE_STYLE_RULES`, `KEY_CONSTRAINTS`
4. `ARCHITECTURE.md` / `docs/` → `ARCHITECTURE_OVERVIEW`, `KEY_MODULES`
5. `AGENTS.md` (if present) → all fields; use as ground truth when available
6. Source file sampling (read 5-10 source files) → `NAMING_CONVENTIONS`, `IMPORT_ORDER`, `CODE_STYLE_RULES`
7. Test directory listing → `TEST_FRAMEWORK`, `TEST_STRUCTURE`, `TEST_DIR`
