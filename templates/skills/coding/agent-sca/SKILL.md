---
name: coding-agent-sca
description: "Static security analysis (CodeQL, secret scanning, dependency review) over auto-generated agent code. Triggers: CodeQL, GHAS, secret scanning, dependency review, agent code review, supply chain, SAST, AI-generated code audit."
domain: coding
subdomain: agent-sca
facets:
  - lang:python
  - lang:typescript
  - target:linux
  - vendor:github-advanced-security
applies_when:
  any_of:
    - "task audits agent-generated scripts, workflows, or pipelines for security vulnerabilities"
    - "task configures CodeQL, secret scanning, or dependency review over auto-generated code"
    - "task hardens a Copilot agent's PR against injection, deserialization, race conditions, or hardcoded secrets"
    - "task introduces a CI gate before merging Copilot- or LLM-authored changes"
version: 0.1.0
---
# Coding / Agent Code — Static Security Analysis (SCA)

## When to use

Open this skill when the change set under review was produced (in whole
or in part) by an autonomous agent (Copilot agent, custom LLM
pipeline, codegen workflow) and must clear a security gate before
merge. The risk profile of agent code is different from human code:
hallucinated APIs, plausible-looking placeholders, copy-pasted secrets,
shell-quoting mistakes, and unsafe deserialization all appear at higher
rates than in human-authored PRs.

For routine human-authored code review, the parent
[`../_shared/pitfalls.md`](../_shared/pitfalls.md) is usually enough.

## Canon (must-know terms and invariants)

- **GHAS (GitHub Advanced Security)** — umbrella product for CodeQL,
  secret scanning, dependency review, and security overview. Enabled
  per-repository or org-wide.
- **CodeQL** — GitHub's semantic code analysis engine; queries are
  written in QL over a code database extracted from a build. Default
  query packs cover injection, SSRF, path traversal, weak crypto, and
  unsafe deserialization for most major languages.
- **Secret scanning** — pattern + entropy detection of credentials in
  code, history, and PR diffs. Push protection blocks pushes that
  contain known patterns. Custom patterns extend coverage to in-house
  token formats.
- **Dependency review** — diff-time check that a PR introduces no
  vulnerable dependencies (GitHub Advisory Database) and respects a
  license allow-list. Surfaces in the PR conversation tab.
- **Provenance / SLSA** — build-time attestation that a binary or
  artifact came from a specific source commit and workflow run. Agent
  PRs that produce build artefacts must keep provenance intact.
- **Injection class** — any flaw where untrusted text is concatenated
  into a structured language: SQL, shell, OS command, template,
  XPath, JSON path, prompt. Agent code is especially prone to shell
  and prompt injection.
- **Sink / source / sanitizer** (CodeQL terminology) — taint-tracking
  vocabulary; a CodeQL alert is a path from an untrusted *source*
  through unsanitised flow to a dangerous *sink*.
- **Push protection bypass** — a recorded justification for committing
  a flagged secret. Bypasses must be reviewed; an agent should never
  bypass on its own.

For domain-wide canon see [`../_shared/canon.md`](../_shared/canon.md).

## Recommended patterns

1. **Run CodeQL on every agent PR before human review.** Configure
   the `github/codeql-action` workflow with `security-extended` and
   `security-and-quality` query suites. Treat any new alert as a
   blocking issue, not a soft warning.
2. **Enable secret scanning push protection org-wide.** Push protection
   is the only control that catches a secret *before* it lands in
   history. Without it, rotation is the only remedy and history must
   be force-rewritten.
3. **Pin agent-generated dependencies.** Require exact versions
   (`==1.2.3`, not `>=1.2`) in any agent-authored manifest. Combine
   with Dependabot version-update PRs that humans review.
4. **Lock down `GITHUB_TOKEN` permissions.** In any workflow an agent
   can author, set `permissions:` to the minimum (`contents: read`).
   Never leave the default org-wide write scope for AI-authored CI.
5. **Sanitize all shelling-out.** Agent code routinely builds shell
   commands by string concatenation. Replace with `subprocess.run([...
   ], shell=False)`, `execFile`, or fully-quoted templated commands.
6. **Validate every deserialiser input.** `pickle.load`, `yaml.load`
   (without `SafeLoader`), `eval`, `Function()`, `JSON.parse` of
   untrusted data — all are sinks. Replace with safe equivalents
   (`json`, `yaml.safe_load`, schema-validated parsers).
7. **Fail closed on alert regressions.** A successful CI must require
   *zero new* CodeQL alerts versus the base branch. A reduction below
   baseline is also acceptable; never let totals creep upward.
8. **Record every bypass.** When a finding must be dismissed (false
   positive, accepted risk), require a `// codeql[<rule-id>] reason: …`
   comment and a security reviewer approval.

## Pitfalls (subdomain-specific)

- ❌ **`shell=True` in `subprocess`.** Lets agent-built strings break
  out via `;`, `&&`, backticks. Always pass an argument list.
- ❌ **`yaml.load(stream)`.** Default loader instantiates arbitrary
  Python classes. Use `yaml.safe_load`. Same for `pickle` and any
  marshalling library that supports custom constructors.
- ❌ **Dynamic SQL via f-strings.** Agents love
  `cursor.execute(f"SELECT * FROM t WHERE id={id}")`. Replace with
  parameterised queries (`?` / `%s` placeholders).
- ❌ **Hard-coded API keys / model tokens.** Common mistake when an
  agent transcribes example code from documentation. Use
  `os.environ`, GitHub Secrets, or OIDC-issued short-lived tokens.
- ❌ **`pull_request_target` with `actions/checkout` of the PR head.**
  Lets the PR's malicious code run with org-write `GITHUB_TOKEN`. Use
  `pull_request` for untrusted code; reserve `pull_request_target`
  for label/comment metadata only.
- ❌ **Wildcard CORS / `*` in cookies.** Agent boilerplate frequently
  copies `Access-Control-Allow-Origin: *` from tutorials.
- ❌ **Disabling lint or CodeQL "to make CI green".** The agent
  workflow must not be allowed to write to its own CI config.
- ❌ **Long-lived PATs as workflow secrets.** Prefer short-lived OIDC
  tokens and GitHub App tokens with fine-grained scopes.
- ❌ **Path traversal in `zipfile.extractall` / `tarfile.extractall`.**
  Validate that each entry's resolved path is under the destination
  before extracting (`os.path.commonpath`).

Domain-wide pitfalls live in [`../_shared/pitfalls.md`](../_shared/pitfalls.md).

## Procedure

1. **Enable GHAS surface area.**
   - In the repository's *Settings → Code security*: enable CodeQL,
     secret scanning, push protection, dependency graph, and
     dependency review.
   - For organisations: enforce these defaults via the *Security*
     overview's policy.

2. **Add or update the CodeQL workflow.**
   ```yaml
   # .github/workflows/codeql.yml (excerpt)
   name: CodeQL
   on:
     push: { branches: [main] }
     pull_request: { branches: [main] }
     schedule: [{ cron: "0 4 * * 1" }]
   permissions:
     contents: read
     security-events: write
   jobs:
     analyze:
       runs-on: ubuntu-latest
       strategy:
         matrix: { language: [python, javascript-typescript] }
       steps:
         - uses: actions/checkout@v4
         - uses: github/codeql-action/init@v3
           with:
             languages: ${{ matrix.language }}
             queries: security-extended,security-and-quality
         - uses: github/codeql-action/analyze@v3
   ```

3. **Add a dependency-review gate.**
   ```yaml
   # .github/workflows/dependency-review.yml
   on: pull_request
   jobs:
     review:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/dependency-review-action@v4
           with:
             fail-on-severity: high
             allow-licenses: MIT, Apache-2.0, BSD-3-Clause, ISC
   ```

4. **Author custom CodeQL queries for agent-specific risks.**
   - "Subprocess call with `shell=True` and any argument that flows
     from a function literal authored by the agent."
   - "HTTP fetch in CI workflow whose URL is constructed from
     `${{ github.event.* }}`."
   - Place queries under `.github/codeql/custom/` and reference them
     in the workflow's `queries:` field.

5. **Configure secret scanning custom patterns.**
   - Add patterns for in-house tokens (e.g. `XYZ_KEY_[A-Z0-9]{32}`).
   - Enable push protection for the patterns; pre-receive hook will
     block commits.

6. **Branch protection.**
   - Require status checks: CodeQL analyze (per language), dependency
     review, and the project's existing test suite.
   - Require linear history; require signed commits if the project
     ships binaries.

7. **Triage cadence.**
   - Daily: review new alerts in the *Security* tab.
   - Per agent PR: ensure the CodeQL run is green before merge.
   - Quarterly: re-run with the latest query packs (`actions/checkout`
     pulls the upstream pack on each run by default).

8. **Document the bypass rule.**
   - Any dismissal needs a comment recording: rule id, reason, owner,
     expiry date. Use `# noqa: codeql[<rule>]` only as a last resort
     and include a TODO with a tracking issue.

## Validation

After completing the procedure, run:

```sh
# Local pre-commit checks (developers' machines)
pre-commit run --all-files

# Type + lint
ruff check .
mypy --strict src/

# Run the same dependency review locally
gh extension install actions/gh-actions-cache
gh dependency-review --base main --head HEAD

# Trigger CodeQL on a feature branch and confirm zero new alerts
gh workflow run codeql.yml --ref "$(git branch --show-current)"
gh run watch
```

A successful gate means: CodeQL adds **no new alerts**, dependency
review reports **no high-severity advisories**, secret scanning blocks
**zero pushes**, and the test suite passes.

## See also

- [`../mapreduce-codegen/SKILL.md`](../mapreduce-codegen/SKILL.md) —
  upstream pipeline whose output this skill audits.
- [`../spatial-transfer/SKILL.md`](../spatial-transfer/SKILL.md) —
  agent-authored transfer scripts that need shell-injection review.
- [`../_shared/pitfalls.md`](../_shared/pitfalls.md)
- GitHub CodeQL docs — <https://codeql.github.com/docs/>
- GitHub secret scanning patterns — <https://docs.github.com/en/code-security/secret-scanning>
- OWASP ASVS v4 — application security verification standard.
- SLSA framework — <https://slsa.dev/> for build provenance.
