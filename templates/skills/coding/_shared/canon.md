# Coding — Shared Canon

Terminology and invariants common to every `coding/*` subdomain.

## Invariants

- **Source of truth is the test suite.** A change is not done until tests cover the new behavior.
- **Smallest correct diff wins.** Prefer surgical edits over rewrites.
- **Public API stability** is a contract. Breaking changes require explicit version bumps.
- **Errors are values, not control flow.** Encode failure in return types where the language allows.

## Terminology

- **Hot path** — code on the critical execution path; optimization candidate.
- **Cold path** — rarely executed; readability beats performance.
- **Yak shaving** — incidental work that is not part of the requested change. Defer or split.

## Cross-cutting practices

1. Read tests before reading implementation.
2. Reproduce the bug with a failing test before fixing it.
3. Keep functions focused; if a function needs a section header comment, split it.
