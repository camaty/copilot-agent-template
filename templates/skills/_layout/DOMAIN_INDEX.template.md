---
# Domain INDEX template — copy to `<domain>/INDEX.md` and fill in.
# This file is NOT a SKILL.md; it has no `name:` field and is not loaded as a skill.
domain: {{DOMAIN}}
version: 0.1.0
---
# {{DOMAIN_HUMAN_NAME}} — Domain Index

> One-page entry point. Agents read this **first** when the active domain is `{{DOMAIN}}`.

## What this domain covers

{{DOMAIN_SCOPE_ONE_PARAGRAPH}}

## Subdomain decision tree

Pick the first matching row.

| If the task involves… | Open this subdomain |
|---|---|
| {{SIGNAL_1}} | [`{{SUBDOMAIN_1}}/SKILL.md`](./{{SUBDOMAIN_1}}/SKILL.md) |
| {{SIGNAL_2}} | [`{{SUBDOMAIN_2}}/SKILL.md`](./{{SUBDOMAIN_2}}/SKILL.md) |
| _none of the above_ | apply [`_shared/`](./_shared/) only and proceed with general practice |

## Facet vocabulary

Facets are orthogonal tags placed in each SKILL.md front-matter. Use only values from this list; add new ones here before using them.

| Axis | Allowed values |
|---|---|
| `lang:`   | {{LANG_VALUES}} |
| `target:` | {{TARGET_VALUES}} |
| `vendor:` | {{VENDOR_VALUES}} |

## Shared resources

- [`_shared/canon.md`](./_shared/canon.md) — terminology and invariants common to the whole domain
- [`_shared/pitfalls.md`](./_shared/pitfalls.md) — anti-patterns shared across all subdomains

## Related domains

- {{RELATED_DOMAIN_1}}: {{RELATION_NOTE_1}}
- {{RELATED_DOMAIN_2}}: {{RELATION_NOTE_2}}
