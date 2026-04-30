---
name: coding-api-design
description: "Designing public and internal HTTP/gRPC APIs: resource modelling, versioning, errors, pagination, idempotency, schema evolution. Triggers: REST, OpenAPI, gRPC, Protobuf, API design, versioning, pagination, idempotency, OAS."
domain: coding
subdomain: api-design
facets:
  - lang:python
  - lang:typescript
  - lang:go
  - target:network
applies_when:
  any_of:
    - "task designs a new HTTP, REST, or gRPC API surface"
    - "task introduces or evolves an OpenAPI / Protobuf schema"
    - "task adds versioning, pagination, idempotency, or error semantics to an existing API"
    - "task reviews API ergonomics, naming, or backward compatibility"
version: 0.1.0
---
# Coding / API Design

## When to use

Open this skill when the deliverable is an API surface (or a change
to one): public REST endpoints, internal gRPC, webhook contracts, or
schema evolution. For runtime IO performance, use
[`../network/SKILL.md`](../network/SKILL.md). For SDK code generation
from a finished spec, this skill applies up to the point the spec
is frozen.

If activation hints don't match, return to [`../INDEX.md`](../INDEX.md).

## Canon (must-know terms and invariants)

- **Resource vs RPC modelling** — REST favours nouns and a small
  verb set (`GET/POST/PUT/PATCH/DELETE`); RPC favours named methods.
  Pick one style per service and stay consistent.
- **Idempotent vs safe** — *safe* methods (`GET`, `HEAD`) have no side
  effects; *idempotent* methods (`PUT`, `DELETE`) can be repeated
  without changing state beyond the first call. `POST` is neither
  unless an idempotency key makes it so.
- **Versioning** — major version in the URL (`/v1/`) for public APIs
  is unambiguous; header-based (`Accept: application/vnd.acme.v2+json`)
  is cleaner but harder for caches and humans.
- **Pagination** — *offset-based* (simple but breaks under
  concurrent writes); *cursor-based* (stable, opaque token); always
  document `next_cursor` semantics and a hard upper bound on `limit`.
- **Error envelope** — RFC 7807 `application/problem+json` for HTTP;
  `google.rpc.Status` for gRPC. Always include a stable, machine-
  readable `code` plus a human `message`; never leak stack traces.
- **Backwards compatibility** — additive changes are safe (new
  optional fields, new methods); removing or repurposing fields
  breaks clients. Reserve removed Protobuf tags forever.
- **HATEOAS / link relations** — embedding navigation in responses;
  controversial but valuable when consumers iterate on resources.
- **Field selection / sparse fieldsets** — `?fields=` to limit
  payload; saves bandwidth without breaking schema.
- **OAS / Protobuf as the source of truth** — generate code, docs,
  and tests from the spec; never hand-edit generated artefacts.
- **Idempotency-Key header** — RFC 9457 (proposed) / Stripe-style;
  enables safe retries on `POST` endpoints.

## Recommended patterns

1. **Spec-first.** Author OpenAPI 3.1 (REST) or `.proto` (gRPC)
   before writing handlers. Generate server stubs and client SDKs
   from the spec.
2. **Pin the major version in the path** for public APIs
   (`/v1/things`); use semver for the implementation behind it.
3. **Use cursor pagination by default.** Return `next_cursor` plus
   `has_more`; make cursors opaque (base64-wrap the underlying
   keyset).
4. **One canonical error envelope** across the entire surface.
   Include `code` (kebab-case), `message`, `details[]`, optional
   `request_id`. Map to standard HTTP / gRPC status codes.
5. **Idempotency keys on every mutating endpoint.** Client supplies
   `Idempotency-Key`; server stores `(key, body_hash) → response`
   for ≥ 24 h.
6. **Resource-scoped permissions, not endpoint-scoped.** "Read this
   project" generalises across endpoints; "GET /projects/:id" does
   not.
7. **Reserve breaking changes for major versions.** Within a major,
   only additive: new optional fields, new endpoints, new error
   codes. Document a `Deprecation` header for sunset paths.
8. **Standardise long-running operations.** Either return `202` +
   a status URL (REST), or follow Google AIP-151 LRO pattern
   (gRPC). Don't invent per-endpoint conventions.
9. **Field naming consistency.** `snake_case` everywhere in JSON or
   `camelCase` everywhere — pick one, document, lint.
10. **Document the rate-limit envelope.** `X-RateLimit-Limit`,
    `-Remaining`, `-Reset` (or `Retry-After`); don't make clients
    discover limits via 429 alone.
11. **Author contract tests** that round-trip OpenAPI/Protobuf
    examples through the live server.

## Pitfalls (subdomain-specific)

- ❌ **`GET` with side effects.** Caches, prefetchers, and crawlers
  will trigger them.
- ❌ **Repurposing a field's meaning** within a major version.
  Even renaming a string enum value breaks clients that switch on
  it.
- ❌ **Returning an array as the top-level JSON body.** Hard to
  evolve (cannot add metadata); wrap in `{ "items": [...] }`.
- ❌ **Mixing 4xx and 5xx semantics.** `400 Bad Request` for client
  errors only; never for "I don't have data for that yet" (404 or
  202).
- ❌ **Different error shapes per endpoint.** Clients can't write
  one handler.
- ❌ **Offset pagination on data with concurrent writes.** Items
  appear twice or skip; use cursors.
- ❌ **Reusing Protobuf field tags.** Wire format is positional;
  re-using a removed tag corrupts every old client silently.
- ❌ **Returning timestamps as local time.** Always RFC 3339 UTC
  (`2025-01-02T03:04:05Z`); accept zoned input but normalise.
- ❌ **Coupling the public schema to the database schema.** Any
  refactor of the DB becomes a public breaking change.
- ❌ **No `request_id` in error responses.** Production debugging
  becomes impossible.
- ❌ **Trailing-slash inconsistency.** Either always or never; pick
  one and redirect 301 the other.
- ❌ **Unbounded list endpoints.** Always cap; document the cap.

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Identify the resource model.** What nouns? What relationships?
   What lifecycle states? Sketch as a small ER-like diagram.
2. **Pick the protocol and style** (REST + JSON, gRPC, or both via
   gRPC-Gateway). Consider clients, latency budget, streaming
   needs.
3. **Author the spec** (OpenAPI 3.1 or `.proto`). Include examples
   in the spec; lint with `spectral` / `buf lint`.
4. **Define the error envelope** and a starter set of error codes.
   Document mapping to HTTP / gRPC status.
5. **Define versioning + deprecation policy.** Write it in
   `docs/api-policy.md`; commit with the spec.
6. **Generate code & SDKs** from the spec; treat generated code as
   build output.
7. **Write contract tests** that exercise every endpoint with the
   spec's examples; fail closed on schema violation.
8. **Run a backwards-compatibility check** against the previous
   release artefact (`oasdiff`, `buf breaking`).
9. **Document with examples**, not just schema. Curl + SDK
   snippets per endpoint.

## Validation

After completing the procedure, run:

```sh
# Spec lint
spectral lint openapi.yaml --ruleset .spectral.yaml          # OAS
buf lint && buf format --diff && buf breaking \
    --against ".git#branch=main"                             # Protobuf

# Generated SDK build
openapi-generator generate -i openapi.yaml -g typescript-axios \
    -o sdks/ts && (cd sdks/ts && npm ci && npm run build)
buf generate    # for protobuf

# Contract tests (server)
schemathesis run openapi.yaml --base-url http://localhost:8080 \
    --checks all --hypothesis-derandomize

# Backwards-compat
oasdiff breaking previous.yaml openapi.yaml
buf breaking --against ".git#branch=main"
```

## See also

- [`../network/SKILL.md`](../network/SKILL.md) — runtime concerns
  (timeouts, retries, idempotency execution).
- [`../observability/SKILL.md`](../observability/SKILL.md) — for
  RED metrics and OpenTelemetry conventions on the API surface.
- [`../databases/SKILL.md`](../databases/SKILL.md) — when API
  schemas wrap data stores; keep them decoupled.
- OpenAPI 3.1 specification — <https://spec.openapis.org/oas/v3.1.0>
- Protobuf style guide — <https://protobuf.dev/programming-guides/style/>
- Google AIP design rules — <https://google.aip.dev/>
- RFC 7807 (problem+json), RFC 9457 (idempotency-key proposal).
