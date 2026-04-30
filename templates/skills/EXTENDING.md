# Extending the Skills Scaffold

This guide explains how to add a new domain or subdomain without breaking the layering model.

## Decision tree: domain or subdomain?

```
Is there an existing <domain>/ that shares the same canon and pitfalls?
├── Yes → add a NEW SUBDOMAIN under it
└── No  → add a NEW DOMAIN at the top level
```

Rules of thumb:

- **A domain** has a distinct *canon* (vocabulary, principles, evaluation criteria) and a distinct *pitfall set*. Examples: `coding`, `3dcg`, `cad`, `ml`, `gameengine`.
- **A subdomain** specializes a domain when a meaningful subset of patterns/pitfalls only applies to that area. Examples: `coding/embedded`, `3dcg/houdini`.
- **Anything orthogonal** (programming language, OS, vendor, scale) is a **facet**, not a folder. Put it in front-matter `facets:`.

If a candidate subdomain would have only 1–2 unique paragraphs versus its siblings, it does **not** justify a new folder; merge it into the parent or model it as a facet.

## Add a new subdomain

1. Pick the parent domain folder, e.g. `templates/skills/coding/`.
2. Copy the skeleton:
   ```sh
   cp templates/skills/_layout/SUBDOMAIN_SKILL.template.md \
      templates/skills/coding/<new-subdomain>/SKILL.md
   ```
3. Fill in the front-matter. Set `domain: coding`, `subdomain: <new-subdomain>`. Add `facets:` for any orthogonal axes.
4. (Optional) Add sibling files under the same folder when content grows beyond ~2 000 tokens:
   - `canon.md` — terminology, invariants
   - `patterns.md` — recommended approaches
   - `pitfalls.md` — known anti-patterns
   - `checklist.md` — pre-merge verification list
   - `examples/` — minimal runnable references
5. Update `<domain>/INDEX.md` so the decision tree references the new subdomain.
6. If your subdomain shares utilities with siblings, lift them to `<domain>/_shared/`.

## Add a new domain

1. Decide the domain name (lowercase, kebab-case, singular).
2. Create the folder and seed it from the layout templates:
   ```sh
   mkdir -p templates/skills/<new-domain>/_shared
   cp templates/skills/_layout/DOMAIN_INDEX.template.md \
      templates/skills/<new-domain>/INDEX.md
   ```
3. Add at least one initial subdomain (see above). A domain with zero subdomains is allowed only when it is intentionally flat — in that case place a single `SKILL.md` directly under the domain folder and skip the INDEX (link to the SKILL.md from this README).
4. Update `templates/skills/README.md` directory layout block.
5. Update the project-side `<TARGET_PROJECT>/.github/skills/` mapping if the `@Setup` agent needs to know about the new domain (see `.github/agents/setup.agent.md` Phase 1f).

## Naming conventions

| Element | Convention | Example |
|---|---|---|
| Domain folder | `kebab-case`, singular noun | `cad`, `gameengine` |
| Subdomain folder | `kebab-case`, noun or adjective | `embedded`, `parametric` |
| `name:` front-matter | `<domain>-<subdomain>` | `coding-network` |
| Facet keys | `axis:value` (lowercase) | `lang:rust`, `target:rtos`, `vendor:autodesk` |

## Anti-patterns to avoid

- ❌ Creating a folder per programming language (`coding/python/`, `coding/rust/`). Use `facets: [lang:python]`.
- ❌ Nesting beyond `<domain>/<subdomain>/`. If you feel the urge, you are encoding facets as folders.
- ❌ A subdomain that exists "for symmetry" but has no unique canon. Delete it.
- ❌ Duplicating the same canon paragraph across subdomains. Move it to `_shared/`.
- ❌ SKILL.md > 2 000 tokens. Split into sibling files.
- ❌ Forward-declaring empty subdomains for "future use". Add when needed (YAGNI).

## Checklist before opening a PR

- [ ] Front-matter has `name`, `description`, `domain`, `subdomain`, `version`.
- [ ] Folder depth ≤ 3 under `skills/`.
- [ ] Parent `INDEX.md` lists the new subdomain in its decision tree.
- [ ] No language/runtime appears as a folder level.
- [ ] `templates/skills/README.md` directory diagram is updated when adding a domain.
- [ ] Cross-references to `_shared/` resolve.
