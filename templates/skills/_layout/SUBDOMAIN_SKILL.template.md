---
name: {{DOMAIN}}-{{SUBDOMAIN}}
description: "{{ONE_LINE_PURPOSE}}. Triggers: {{TRIGGER_KEYWORDS}}."
domain: {{DOMAIN}}
subdomain: {{SUBDOMAIN}}
facets:
  # Orthogonal tags. Choose values from the parent INDEX.md facet vocabulary.
  # Examples (delete unused, add per task):
  # - lang:python
  # - target:linux
  # - vendor:autodesk
applies_when:
  any_of:
    - "{{ACTIVATION_HINT_1}}"
    - "{{ACTIVATION_HINT_2}}"
version: 0.1.0
---
# {{DOMAIN_HUMAN_NAME}} / {{SUBDOMAIN_HUMAN_NAME}}

## When to use

{{WHEN_TO_USE_PARAGRAPH}}

If the task does not match the activation hints, return to [`../INDEX.md`](../INDEX.md) and pick another subdomain.

## Canon (must-know terms and invariants)

- **{{TERM_1}}** — {{DEFINITION_1}}
- **{{TERM_2}}** — {{DEFINITION_2}}

For terminology shared across the whole `{{DOMAIN}}` domain, see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. {{PATTERN_1_HEADLINE}} — {{PATTERN_1_BODY}}
2. {{PATTERN_2_HEADLINE}} — {{PATTERN_2_BODY}}

## Pitfalls (subdomain-specific)

- ❌ {{PITFALL_1}}
- ❌ {{PITFALL_2}}

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

If this skill includes bundled scripts or starter files (siblings of this `SKILL.md`), prefer those local assets over inline commands.

## Validation

After completing the procedure, run:

```sh
{{LINT_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
```

## See also

- {{RELATED_SKILL_1}}
- {{EXTERNAL_REFERENCE_1}}
