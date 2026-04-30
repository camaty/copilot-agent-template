# Coding — Shared Pitfalls

Anti-patterns that apply across every `coding/*` subdomain.

- ❌ **Silent catch-all.** `try { … } catch { /* ignore */ }` hides real failures.
- ❌ **God function.** A function over ~80 lines that mixes I/O, validation, and logic.
- ❌ **Premature abstraction.** Introducing an interface with one implementation "for the future".
- ❌ **Mutable global state.** Shared mutable singletons across modules.
- ❌ **Test-by-mock.** Tests that only assert calls to mocks without exercising real behavior.
- ❌ **Commit-message-as-spec.** Important design decisions buried in commit messages instead of code or docs.
- ❌ **Copy-paste evolution.** Two near-identical functions that drift independently.
