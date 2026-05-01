#!/usr/bin/env python3
"""create_skill.py — Meta-tool: create and save a new agent skill.

This script is the "tool-creating tool" from the OJT loop described in
ARCHITECTURE.md. After an agent solves a task it did not know how to handle
before, it distils the successful logic into a reusable SKILL.md file so that
future reasoning loops can call upon it directly.

Usage
-----
    python .agent/tools/create_skill.py \\
        --name      "sort_3dgs_splats" \\
        --description "3DGS Splatデータを深度でソートする" \\
        --code_file  "temp_sort.ts" \\
        [--domain    "3dcg"] \\
        [--subdomain "3dgs"] \\
        [--facets    "lang:typescript,target:browser"] \\
        [--skills_dir ".agent/skills"]

Positional outcome
------------------
A new SKILL.md is written at:
    <skills_dir>/<domain>/<subdomain>/SKILL.md

If the file already exists the new code block is *appended* as an additional
example section rather than overwriting the file.

Exit codes
----------
0   success
1   argument / IO error
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SKILL_TEMPLATE = """\
---
name: {name}
description: "{description}"
domain: {domain}
subdomain: {subdomain}
facets:{facets_yaml}
applies_when:
  any_of:
    - "task involves {name}"
version: 0.1.0
created_at: {created_at}
---
# {domain_human} / {subdomain_human}

## When to use

Use this skill when {description}

If the task does not match the activation hints, return to
[`../INDEX.md`](../INDEX.md) and pick another subdomain.

## Canon (must-know terms and invariants)

<!-- Add key terms and invariants here. -->

## Recommended patterns

<!-- Add recommended patterns here. -->

## Pitfalls (subdomain-specific)

<!-- Add known pitfalls here. -->

## Implementation

```{code_lang}
{code_body}
```

## Validation

```sh
# Add lint / build / test commands appropriate for this skill.
```

## See also

<!-- Add links to related skills or external references. -->
"""

_APPEND_TEMPLATE = """\

## Example: {name} (added {created_at})

```{code_lang}
{code_body}
```
"""


def _slugify(text: str) -> str:
    """Convert a skill name into a safe directory/file-name component."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _human(slug: str) -> str:
    """Turn a slug into a human-readable title."""
    return slug.replace("-", " ").replace("_", " ").title()


def _facets_yaml(facets_str: str) -> str:
    """Convert a comma-separated facet string to a YAML list block."""
    if not facets_str.strip():
        return "\n  # - lang:python"
    items = [f.strip() for f in facets_str.split(",") if f.strip()]
    return "\n" + "\n".join(f"  - {item}" for item in items)


def _detect_lang(path: str) -> str:
    """Guess a markdown code-fence language from a file extension."""
    ext_map = {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".rs": "rust",
        ".go": "go",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".wgsl": "wgsl",
        ".glsl": "glsl",
        ".hlsl": "hlsl",
        ".sh": "sh",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
    }
    suffix = Path(path).suffix.lower()
    return ext_map.get(suffix, "")


def _ensure_index(domain_dir: Path, domain: str) -> None:
    """Create a minimal INDEX.md if the domain directory has none."""
    index_path = domain_dir / "INDEX.md"
    if index_path.exists():
        return
    index_content = textwrap.dedent(f"""\
        ---
        domain: {domain}
        version: 0.1.0
        ---
        # {_human(domain)} — Domain Index

        ## Subdomain decision tree

        | If the task involves… | Open this subdomain |
        |---|---|
        | _(add rows as new subdomains are created)_ | |

        ## Facet vocabulary

        | Axis | Allowed values |
        |---|---|
        | `lang:` | _(add as needed)_ |
        | `target:` | _(add as needed)_ |
    """)
    index_path.write_text(index_content, encoding="utf-8")
    print(f"[create_skill] Created domain index: {index_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new agent skill from a code file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--name", required=True,
        help="Stable identifier for the skill, e.g. 'sort_3dgs_splats'."
    )
    parser.add_argument(
        "--description", required=True,
        help="One-line human description of what the skill does."
    )
    parser.add_argument(
        "--code_file", default=None,
        help="Path to a source file whose content is embedded in the skill."
    )
    parser.add_argument(
        "--domain", default=None,
        help="Domain folder name (e.g. '3dcg', 'coding'). Inferred from --name if omitted."
    )
    parser.add_argument(
        "--subdomain", default=None,
        help="Subdomain folder name (e.g. '3dgs'). Inferred from --name if omitted."
    )
    parser.add_argument(
        "--facets", default="",
        help="Comma-separated facet tags, e.g. 'lang:typescript,target:browser'."
    )
    parser.add_argument(
        "--skills_dir", default=".agent/skills",
        help="Root directory where skills are stored (default: .agent/skills)."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # Resolve domain / subdomain from name when not supplied.
    name_slug = _slugify(args.name)
    parts = name_slug.split("-")
    domain = args.domain or (parts[0] if parts else "general")
    subdomain = args.subdomain or (name_slug if len(parts) <= 1 else "-".join(parts[1:]) or name_slug)

    # Read code body.
    code_body = ""
    code_lang = ""
    if args.code_file:
        code_path = Path(args.code_file)
        if not code_path.exists():
            print(f"[create_skill] ERROR: code_file not found: {code_path}", file=sys.stderr)
            return 1
        code_body = code_path.read_text(encoding="utf-8")
        code_lang = _detect_lang(args.code_file)

    created_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    # Resolve target path.
    skills_root = Path(args.skills_dir)
    domain_dir = skills_root / domain
    subdomain_dir = domain_dir / subdomain
    skill_path = subdomain_dir / "SKILL.md"

    subdomain_dir.mkdir(parents=True, exist_ok=True)
    _ensure_index(domain_dir, domain)

    if skill_path.exists():
        # Append a new example block instead of overwriting.
        append_block = _APPEND_TEMPLATE.format(
            name=args.name,
            created_at=created_at,
            code_lang=code_lang,
            code_body=code_body or "# (no code provided)",
        )
        with skill_path.open("a", encoding="utf-8") as fh:
            fh.write(append_block)
        print(f"[create_skill] Appended example to existing skill: {skill_path}")
    else:
        content = _SKILL_TEMPLATE.format(
            name=args.name,
            description=args.description,
            domain=domain,
            subdomain=subdomain,
            facets_yaml=_facets_yaml(args.facets),
            created_at=created_at,
            domain_human=_human(domain),
            subdomain_human=_human(subdomain),
            code_lang=code_lang,
            code_body=code_body or "# (no code provided)",
        )
        skill_path.write_text(content, encoding="utf-8")
        print(f"[create_skill] Created new skill: {skill_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
