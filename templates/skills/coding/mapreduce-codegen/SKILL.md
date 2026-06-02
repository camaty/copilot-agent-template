---
name: coding-mapreduce-codegen
description: "Map-Reduce orchestration where a planner model fans out coding subtasks to local executor models that write and verify code. Triggers: map-reduce, multi-agent codegen, orchestration, planner, executor, Qwen, local LLM, fan-out."
domain: coding
subdomain: mapreduce-codegen
facets:
  - lang:python
  - vendor:openai
  - vendor:qwen
applies_when:
  any_of:
    - "task distributes code generation across a planner model and multiple executor models"
    - "task uses a Map-Reduce pattern where a high-level model fans out subtasks to local models"
    - "task coordinates Qwen or similar local LLMs as executor agents"
version: 0.1.0
---
# Coding / Map-Reduce Multi-Agent Codegen

## When to use

Open this skill when the coding task is large enough that a single model pass would exceed its context window or produce low-quality results, and the work can be decomposed into independent or loosely coupled subtasks that different executor models can handle in parallel.

If the task is a routine single-file change, use the parent domain canon instead and skip this skill.

## Canon

- **Planner model** — a capable, high-context model (e.g. GPT-4o, o1) that reads the full requirement, produces a decomposition plan, and acts as the Map and Reduce controller.
- **Executor model** — a local, fast model (e.g. Qwen-Coder, Mistral Code) that receives one subtask and a layered reference package, then writes or modifies code for that subtask only.
- **Subtask spec** — a self-contained work unit emitted by the planner: target file(s), acceptance criteria, interface contract, and relevant context snippets.
- **Layered reference** — the minimal set of existing code, type stubs, and test fixtures bundled into each executor's prompt to ensure it can compile and test its output independently.
- **Reducer** — the planner model's second pass that merges executor outputs, resolves interface conflicts, and runs the global test suite.
- **Lane event** — a structured log entry (`[SKILL:mapreduce-codegen][MAP|REDUCE|VERIFY]`) emitted at each stage for traceability.

For terminology shared across the `coding` domain see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Decompose before you code.** Have the planner emit the full subtask list and confirm interfaces before any executor starts. Late interface changes cascade badly.
2. **Bundle layered references per subtask.** Each executor prompt must include type signatures, relevant imports, and the acceptance tests for its slice — nothing more. Over-bundling wastes context; under-bundling causes compile errors.
3. **Verify locally before reducing.** Each executor must run its own unit tests (`python -m pytest <slice>`) before returning output. A failing slice should be retried (up to N times) or flagged before the reducer sees it.
4. **Idempotent reduce pass.** The reducer should apply diffs, not full file replacements, so that two executors touching adjacent functions don't destroy each other's work.
5. **Gate on a global smoke test.** After reducing, always run the full test suite before declaring success; integration failures are expected and normal on the first reduce pass.
6. **Emit lane events at each stage** so the orchestrator can detect hung executors and retry or reassign.

## Pitfalls

- ❌ **Executors sharing mutable state.** If two executors write to the same module, define non-overlapping function-level boundaries before fan-out.
- ❌ **Planner hallucinating interfaces.** Always derive interface contracts from existing type stubs or run a type-check (`mypy --strict`) on the contract before fan-out.
- ❌ **Executor context overflow.** Keep each executor prompt under 80 % of its context limit; strip docstrings and comments from reference snippets when needed.
- ❌ **Ignoring executor retry budgets.** Without a hard retry cap (e.g. 3 retries per subtask), a stuck executor blocks the entire reduce pass indefinitely.
- ❌ **Reducing without diffing.** Concatenating full files from multiple executors produces conflicts. Use `difflib.unified_diff` or `git merge-file` to apply changes surgically.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Decompose (Planner → Map plan).**
   - Feed the full requirement to the planner model with a system prompt instructing it to output a JSON array of subtask specs.
   - Each spec must include: `id`, `description`, `target_files`, `interface_contract` (signatures), `acceptance_tests` (pytest ids or descriptions), `context_snippets` (file excerpts).
   - Validate the spec array with a schema check before proceeding.

2. **Bundle layered references.**
   - For each subtask, collect: the interface contract, the target file's current content (if any), directly imported modules' type stubs, and the acceptance test file.
   - Trim each bundle to fit comfortably within the executor model's context window.

3. **Fan-out (Map phase).**
   - Dispatch each subtask bundle to an executor model concurrently (e.g. via `asyncio.gather` with a semaphore for rate limiting).
   - Instruct each executor to: implement only the functions listed in the interface contract, run its acceptance tests, and return a unified diff against the original file.
   - Collect results; retry up to 3 times for any executor that returns a non-zero test exit code.

4. **Reduce (Reduce phase).**
   - Apply each executor's diff using `git apply --3way` or `difflib.patch`.
   - On conflict, send the conflicting hunks back to the planner model for arbitration.
   - After all diffs are applied, run `mypy --strict` (or equivalent type checker) on every changed file.

5. **Global validation.**
   - Run the full test suite: `python -m pytest --tb=short`.
   - If tests fail, feed the failure output back to the planner for a targeted fix cycle (limit to 2 fix cycles to avoid infinite loops).

6. **Emit completion event.**
   - Log `[SKILL:mapreduce-codegen][DONE] subtasks=N, retries=R, fix_cycles=F` for traceability.

## Validation

After completing the procedure, run:

```sh
mypy --strict <changed_files>
python -m pytest --tb=short
# If using ruff: ruff check <changed_files>
```

## See also

- [`../network/SKILL.md`](../network/SKILL.md) — if the orchestrator communicates with executors over HTTP/gRPC.
- [`../_shared/pitfalls.md`](../_shared/pitfalls.md)
- OpenAI Cookbook — Agents and multi-step reasoning patterns.
- Qwen-Coder model card — context limits and sampling recommendations for code tasks.
