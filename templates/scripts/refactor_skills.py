#!/usr/bin/env python3
"""refactor_skills.py — Nightly refactoring of accumulated agent skills.

This script implements the "Nightly Refactoring" phase of the OJT loop described
in ARCHITECTURE.md. It scans all SKILL.md files under a skills directory, detects
overlapping or redundant skills, reports them, and—when run with --merge—generates
consolidated replacements so that the agent's knowledge base stays compact and
non-redundant.

Usage
-----
    # Dry-run: report overlapping skills without modifying anything.
    python .agent/tools/refactor_skills.py --skills_dir .agent/skills

    # Merge: rewrite overlapping skills into consolidated files.
    python .agent/tools/refactor_skills.py --skills_dir .agent/skills --merge

    # Tune the similarity threshold (0.0–1.0, default 0.5).
    python .agent/tools/refactor_skills.py --min_similarity 0.65

Similarity is computed with the standard-library difflib (no dependencies).
For richer semantic comparison, replace _similarity() with an embedding-based
approach or a call to a local model API.

Exit codes
----------
0   no overlapping skills found (or merge completed without errors)
2   overlapping skills found but --merge was not requested
1   IO / argument error
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import textwrap
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Front-matter parsing (no external YAML library required)
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_front_matter(text: str) -> dict[str, str]:
    """Extract a flat key→value map from a YAML front-matter block."""
    m = _FM_RE.match(text)
    if not m:
        return {}
    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().strip('"')
    return result


def _body_without_front_matter(text: str) -> str:
    """Return everything after the opening front-matter block."""
    m = _FM_RE.match(text)
    return text[m.end():] if m else text


# ---------------------------------------------------------------------------
# Skill record
# ---------------------------------------------------------------------------

class Skill:
    __slots__ = ("path", "meta", "body", "_raw_fm")

    def __init__(
        self, path: Path, meta: dict[str, str], body: str, raw_fm: str = ""
    ) -> None:
        self.path = path
        self.meta = meta
        self.body = body
        self._raw_fm = raw_fm

    @property
    def name(self) -> str:
        return self.meta.get("name", self.path.stem)

    @property
    def description(self) -> str:
        return self.meta.get("description", "")

    @property
    def domain(self) -> str:
        return self.meta.get("domain", "")

    @property
    def subdomain(self) -> str:
        return self.meta.get("subdomain", "")

    def facets(self) -> list[str]:
        """Return the facet list parsed from the raw front-matter YAML block."""
        items: list[str] = []
        in_facets = False
        for line in self._raw_fm.splitlines():
            if re.match(r"^facets\s*:", line):
                in_facets = True
                continue
            if in_facets:
                stripped = line.strip()
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip())
                elif stripped and not stripped.startswith("#"):
                    break
        return items

    def fingerprint(self) -> str:
        """Concatenated text used for similarity comparison."""
        return f"{self.name} {self.description} {self.body}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"Skill(name={self.name!r}, path={self.path})"


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def _scan_skills(skills_root: Path) -> Iterator[Skill]:
    """Yield Skill objects for every SKILL.md found under skills_root."""
    for skill_path in sorted(skills_root.rglob("SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        meta = _parse_front_matter(text)
        body = _body_without_front_matter(text)
        m = _FM_RE.match(text)
        raw_fm = m.group(1) if m else ""
        yield Skill(path=skill_path, meta=meta, body=body, raw_fm=raw_fm)


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

def _similarity(a: Skill, b: Skill) -> float:
    """Return a [0, 1] similarity score between two skills.

    The score is the average of:
    1. SequenceMatcher ratio on their fingerprints (bag-of-words proxy).
    2. Jaccard coefficient on word-token sets.

    Replace this function with an embedding-based approach for semantic
    similarity when a local model or API is available.
    """
    fp_a = a.fingerprint().lower()
    fp_b = b.fingerprint().lower()

    seq_ratio = SequenceMatcher(None, fp_a, fp_b, autojunk=False).ratio()

    tokens_a = set(re.findall(r"[a-z0-9]+", fp_a))
    tokens_b = set(re.findall(r"[a-z0-9]+", fp_b))
    union = tokens_a | tokens_b
    jaccard = len(tokens_a & tokens_b) / len(union) if union else 0.0

    return (seq_ratio + jaccard) / 2.0


def _find_overlapping(
    skills: list[Skill], min_similarity: float
) -> list[tuple[Skill, Skill, float]]:
    """Return pairs (a, b, score) where score >= min_similarity."""
    overlaps: list[tuple[Skill, Skill, float]] = []
    for i, a in enumerate(skills):
        for b in skills[i + 1 :]:
            score = _similarity(a, b)
            if score >= min_similarity:
                overlaps.append((a, b, score))
    return sorted(overlaps, key=lambda t: t[2], reverse=True)


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------

_MERGED_TEMPLATE = """\
---
name: {name}
description: "{description}"
domain: {domain}
subdomain: {subdomain}
facets:{facets_yaml}
applies_when:
  any_of:
{applies_when}
version: 0.1.0
merged_at: {merged_at}
merged_from:
{merged_from}
---
# {domain_human} / {subdomain_human}

## When to use

{description}

This skill was automatically consolidated from the following source skills:

{source_list}

## Canon

<!-- Review and merge canon sections from the source skills above. -->

## Recommended patterns

<!-- Review and merge pattern sections from the source skills above. -->

## Pitfalls

<!-- Review and merge pitfall sections from the source skills above. -->

## See also

<!-- Update cross-references after merging. -->
"""


def _facets_yaml(facets: list[str]) -> str:
    if not facets:
        return "\n  # - lang:python"
    return "\n" + "\n".join(f"  - {f}" for f in sorted(set(facets)))


def _merge_pair(a: Skill, b: Skill, target_path: Path) -> None:
    """Write a consolidated SKILL.md for the pair (a, b) at target_path."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    # Combine facets from both skills.
    facets = a.facets() + b.facets()

    # Combine applies_when hints.
    def _extract_applies_when(skill: Skill) -> list[str]:
        lines = []
        in_block = False
        for line in skill.body.splitlines():
            if "applies_when" in line or "any_of" in line:
                in_block = True
                continue
            if in_block:
                stripped = line.strip()
                if stripped.startswith("-"):
                    lines.append(stripped.lstrip("- ").strip('"'))
                elif stripped and not stripped.startswith("#"):
                    break
        return lines

    all_hints = list(dict.fromkeys(_extract_applies_when(a) + _extract_applies_when(b)))
    applies_when_yaml = "\n".join(f'    - "{h}"' for h in all_hints) if all_hints else '    - "(review me)"'

    merged_from_yaml = f"  - {a.path}\n  - {b.path}"
    source_list = f"- `{a.path}`\n- `{b.path}`"

    domain = a.domain or b.domain or "general"
    subdomain = a.subdomain or b.subdomain or "merged"
    name = f"{a.name}--{b.name}-merged"
    description = f"Merged skill: {a.description} / {b.description}"

    def _human(slug: str) -> str:
        return slug.replace("-", " ").replace("_", " ").title()

    content = _MERGED_TEMPLATE.format(
        name=name,
        description=description,
        domain=domain,
        subdomain=subdomain,
        facets_yaml=_facets_yaml(facets),
        applies_when=applies_when_yaml,
        merged_at=now,
        merged_from=merged_from_yaml,
        domain_human=_human(domain),
        subdomain_human=_human(subdomain),
        source_list=source_list,
    )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _print_report(
    skills: list[Skill],
    overlaps: list[tuple[Skill, Skill, float]],
    merged_paths: list[Path],
) -> None:
    print(f"\n[refactor_skills] Scanned {len(skills)} skill(s).")

    if not overlaps:
        print("[refactor_skills] No overlapping skills found.")
        return

    print(f"[refactor_skills] Found {len(overlaps)} overlapping pair(s):\n")
    for a, b, score in overlaps:
        print(f"  {score:.2f}  {a.path}")
        print(f"       {b.path}")
        print()

    if merged_paths:
        print("[refactor_skills] Merged skill(s) written to:")
        for p in merged_paths:
            print(f"  {p}")
        print()
        print(
            "[refactor_skills] Next step: review each merged file, fill in the "
            "Canon / Patterns / Pitfalls sections, then delete the source files."
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect and optionally consolidate overlapping agent skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--skills_dir", default=".agent/skills",
        help="Root directory that contains skills (default: .agent/skills).",
    )
    parser.add_argument(
        "--min_similarity", type=float, default=0.5,
        help="Similarity threshold 0.0–1.0 above which skills are considered "
             "overlapping (default: 0.5).",
    )
    parser.add_argument(
        "--merge", action="store_true",
        help="Write consolidated SKILL.md files for overlapping pairs. "
             "Without this flag the script only reports (dry-run).",
    )
    parser.add_argument(
        "--merged_dir", default=None,
        help="Directory where merged skills are written "
             "(default: <skills_dir>/_merged).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    skills_root = Path(args.skills_dir)
    if not skills_root.exists():
        print(f"[refactor_skills] ERROR: skills_dir not found: {skills_root}", file=sys.stderr)
        return 1

    skills = list(_scan_skills(skills_root))
    if not skills:
        print(f"[refactor_skills] No SKILL.md files found in: {skills_root}")
        return 0

    overlaps = _find_overlapping(skills, args.min_similarity)

    merged_paths: list[Path] = []
    if overlaps and args.merge:
        merged_dir = Path(args.merged_dir) if args.merged_dir else skills_root / "_merged"
        for idx, (a, b, _score) in enumerate(overlaps, start=1):
            target = merged_dir / f"merged_{idx:03d}.SKILL.md"
            _merge_pair(a, b, target)
            merged_paths.append(target)

    _print_report(skills, overlaps, merged_paths)

    if overlaps and not args.merge:
        return 2  # overlaps found but merge not requested

    return 0


if __name__ == "__main__":
    sys.exit(main())
