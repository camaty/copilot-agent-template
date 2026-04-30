---
name: cad-api-harness
description: "Architecture patterns for wrapping CAD or CG APIs in a strict, schema-validated LLM action space with a deterministic geometry checker. Triggers: LLM harness, API harness, JSON Schema, OpenAPI, hallucinated geometry, deterministic checker, schema-validated, action space."
domain: cad
subdomain: api-harness
facets:
  - lang:python
  - lang:ts
  - vendor:llm
applies_when:
  any_of:
    - "task constrains an LLM to a strict OpenAPI specification or JSON Schema for 3D scene operations"
    - "task adds a deterministic checker or validator layer between an LLM and a CAD/CG API"
    - "task prevents hallucinated geometry by validating LLM output before execution"
version: 0.1.0
---
# CAD / API Harness

## When to use

Open this skill when an LLM (Copilot, GPT-4o, Claude, Gemini, or a local model) is the *producer* of CAD or CG operations and a downstream geometry engine or CAD system is the *consumer*. The harness sits between them: it enforces a schema-bounded action space and runs a deterministic geometry checker before any write reaches the CAD kernel.

For tasks that do *not* involve an LLM in the loop (e.g., direct scripted automation), use [`parametric/SKILL.md`](../parametric/SKILL.md) instead.

## Canon

- **Action space** — the closed set of operations the LLM is permitted to request (e.g., `create_box`, `extrude_face`, `add_mate`). Defined by an OpenAPI spec or JSON Schema; the LLM may not invent operations outside it.
- **Schema-validated call** — an LLM-produced JSON object that has been verified against the spec before being dispatched to the CAD kernel. Validation is structural and type-level only.
- **Deterministic checker** — a second, geometry-aware validation step that runs *after* schema validation. It evaluates whether the proposed operation is geometrically feasible (e.g., non-zero volume, valid topology, no degenerate faces) without executing a write.
- **Hallucinated operation** — an LLM output that passes schema validation but produces invalid or physically impossible geometry (e.g., a Boolean operation that yields an empty solid, self-intersecting faces, or a mate between non-existent references).
- **Dry-run mode** — executing the operation inside the CAD kernel's undo/preview scope, then asserting invariants, before committing the result.
- **Structured output / tool-call** — the LLM produces a typed function call or JSON object rather than free prose, greatly reducing parse surface and hallucination surface.

For shared CAD terminology see [`../_shared/canon.md`](../_shared/canon.md) (create when a second subdomain is added).

## Recommended patterns

1. **Schema-first design.** Define the full action space as an OpenAPI 3.1 `paths` or a JSON Schema `definitions` document before writing any LLM prompt. The schema is the contract; prompts are secondary.
2. **Two-layer validation.** Schema validation (Pydantic / ajv / zod) catches type and field errors cheaply. Geometry validation (CAD kernel dry-run or lightweight B-rep checks) catches semantic errors before commits.
3. **Closed-world action space.** Use LLM structured output (tool-calling / `response_format`) so the model can *only* emit operations in the schema. Reject completions that produce operations not in the schema immediately without retry.
4. **Idempotent write transactions.** Each harness call should be wrapped in a transaction that auto-rolls back on checker failure; never leave the model in a partially-written state.
5. **Operate on references, not coordinates.** Expose geometric entities (faces, edges, bodies) as opaque stable IDs rather than raw coordinates; this shrinks the LLM's decision space and eliminates floating-point hallucinations.
6. **Emit a structured audit log.** Record every (request, validation_result, action_taken) triple. This log is the primary debugging surface for hallucination root-cause analysis.

## Pitfalls

- ❌ **Letting the LLM propose arbitrary API methods.** Without a closed action space, the model invents plausible-sounding but non-existent operations.
- ❌ **Schema validation alone.** JSON Schema confirms shape, not geometric feasibility. A perfectly valid schema call can still produce degenerate geometry.
- ❌ **Relying on LLM self-correction.** Asking the model to "check your output" does not substitute for a deterministic checker; the model may confidently confirm broken geometry.
- ❌ **Passing raw mesh coordinates as LLM input.** Dense coordinate arrays exceed token budgets, degrade attention, and invite coordinate hallucination.
- ❌ **Mutable global CAD session state without transactions.** A failed harness call mid-sequence leaves the session dirty; all subsequent calls operate on corrupted state.
- ❌ **Unbounded retry loops on checker failure.** Set a hard retry cap (≤ 3); on exhaustion, surface the error to the caller rather than silently degrading.

## Procedure

1. **Enumerate the action space.** List every CAD operation the agent needs. Group them by risk (read-only, reversible write, irreversible write). Model your schema around this list; do not expose operations the agent does not need.
2. **Author the schema.** Write an OpenAPI 3.1 spec or JSON Schema that covers the enumerated actions. Validate the schema itself with a linter (`spectral`, `ajv`, `pydantic`).
3. **Configure structured LLM output.** Set `response_format` (OpenAI), `tool_choice` (Anthropic), or equivalent so the model only emits schema-conforming calls. Reject any completion that fails schema parse at the harness boundary — do not pass it to the checker.
4. **Implement the deterministic checker.** For each action type, write a checker function that runs the operation in a dry-run or preview scope and asserts post-conditions (non-empty result solid, no self-intersections, stable entity IDs). This function must have no side effects.
5. **Wrap writes in transactions.** Invoke the CAD kernel write only after both layers pass. On checker failure, roll back, log the failure triple, and return a structured error to the LLM for one retry.
6. **Test the harness independently.** Write unit tests that feed known-bad LLM outputs (schema-invalid, geometry-invalid, borderline) into the harness and assert the correct rejection behavior without a real LLM in the loop.

## Validation

```sh
# Python stack — adjust paths for your project layout
{{LINT_COMMAND}}      # e.g. ruff check src/ && mypy src/
{{BUILD_COMMAND}}     # e.g. pip install -e . --quiet
{{TEST_COMMAND}}      # e.g. pytest tests/harness/ -v

# TypeScript stack
# npx tsc --noEmit
# npx jest --testPathPattern=harness

# Schema validation
# npx @stoplight/spectral-cli lint openapi/cad-actions.yaml
# python -m pydantic validate --schema schema/cad-actions.json fixtures/sample_calls.json
```

## See also

- [`../parametric/SKILL.md`](../parametric/SKILL.md) — the downstream CAD target for harness-driven operations
- OpenAI Structured Outputs / Function Calling documentation — for configuring `response_format` and `tools`
- Pydantic (Python) / Zod (TypeScript) — for runtime schema validation
- OpenAPI Specification 3.1 (`https://spec.openapis.org/oas/v3.1.0`) — for authoring the action space schema
