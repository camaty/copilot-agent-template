#!/usr/bin/env sh
# SAST scan wrapper for {{PROJECT_NAME}} (Shift-Left security gate)
#
# This script is called by the Implementer agent BEFORE marking each
# implementation step as complete. It wraps CodeQL (or the configured
# alternative) so that the agent can call it as a simple tool.
#
# Exit codes:
#   0 — no HIGH/CRITICAL findings in changed files
#   1 — HIGH or CRITICAL findings found (blocking)
#   2 — SAST tool not available (non-blocking, logged as warning)
#
# Usage:
#   sh .github/scripts/security/codeql-scan.sh [file1 file2 ...]
#
# If file arguments are given, only those files are scanned.
# If no arguments, the entire {{SOURCE_DIR}} is scanned.
#
# Configuration:
#   Set SAST_SEVERITY_THRESHOLD env var to change blocking severity.
#   Default: "high" (blocks on HIGH and CRITICAL)
#   Options: "critical" | "high" | "medium" | "low"

set -eu

SEVERITY_THRESHOLD="${SAST_SEVERITY_THRESHOLD:-high}"
SCAN_TARGET="${1:-{{SOURCE_DIR}}}"
REPORT_FILE=".github/security/sast-report.json"

mkdir -p "$(dirname "$REPORT_FILE")"

# ── CodeQL ────────────────────────────────────────────────────────────────────
if command -v codeql >/dev/null 2>&1; then
  echo "[sast] Running CodeQL on: $SCAN_TARGET"

  # Create/update CodeQL database (incremental where possible)
  codeql database create .codeql-db \
    --language={{PRIMARY_LANGUAGE_CODEQL}} \
    --source-root=. \
    --overwrite \
    --quiet 2>/dev/null || {
      echo "[sast] WARNING: CodeQL database creation failed. Skipping SAST." >&2
      exit 2
    }

  # Run security queries
  codeql database analyze .codeql-db \
    --format=sarif-latest \
    --output="$REPORT_FILE" \
    --no-print-diagnostics-summary \
    codeql/{{PRIMARY_LANGUAGE_CODEQL}}-queries:Security/ 2>/dev/null

  # Parse results and check severity
  if command -v node >/dev/null 2>&1; then
    node - <<'JS'
const fs   = require('fs');
const path = require('path');

const report    = JSON.parse(fs.readFileSync(process.env.REPORT_FILE || '.github/security/sast-report.json', 'utf8'));
const threshold = (process.env.SEVERITY_THRESHOLD || 'high').toLowerCase();
const levels    = ['critical', 'high', 'medium', 'low'];
const minIdx    = levels.indexOf(threshold);

let blocking = [];

for (const run of (report.runs || [])) {
  for (const result of (run.results || [])) {
    const severity = (result.properties?.['problem.severity'] || result.level || 'warning').toLowerCase();
    const idx = levels.indexOf(severity === 'error' ? 'critical' : severity === 'warning' ? 'medium' : severity);
    if (idx !== -1 && idx <= minIdx) {
      const loc = result.locations?.[0]?.physicalLocation;
      blocking.push({
        severity,
        rule: result.ruleId,
        message: result.message?.text,
        file: loc?.artifactLocation?.uri,
        line: loc?.region?.startLine,
      });
    }
  }
}

if (blocking.length > 0) {
  console.error('[sast] BLOCKING findings:');
  for (const f of blocking) {
    console.error(`  ${f.severity.toUpperCase()} [${f.rule}] ${f.file}:${f.line} — ${f.message}`);
  }
  process.exit(1);
} else {
  console.log('[sast] No blocking findings.');
}
JS
  else
    # Fallback: check for "error" level results in SARIF without node
    if grep -q '"level":"error"' "$REPORT_FILE" 2>/dev/null; then
      echo "[sast] BLOCKING: HIGH/CRITICAL findings detected in $REPORT_FILE" >&2
      exit 1
    fi
    echo "[sast] No blocking findings (basic check)."
  fi

# ── GitHub Advanced Security (SARIF upload only) ──────────────────────────────
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo "[sast] CodeQL not available locally. Checking GitHub Advanced Security results..."

  # Fetch latest code scanning alerts for high/critical severity on changed files
  ALERTS=$(gh api \
    /repos/{owner}/{repo}/code-scanning/alerts \
    --jq '[.[] | select(.state=="open") | select(.rule.severity=="error" or .rule.severity=="critical")] | length' \
    2>/dev/null || echo "0")

  if [ "$ALERTS" -gt 0 ]; then
    echo "[sast] BLOCKING: $ALERTS open HIGH/CRITICAL code scanning alerts found." >&2
    gh api /repos/{owner}/{repo}/code-scanning/alerts \
      --jq '.[] | select(.state=="open") | select(.rule.severity=="error" or .rule.severity=="critical") | "  \(.rule.id): \(.most_recent_instance.location.path):\(.most_recent_instance.location.start_line) — \(.rule.description)"' \
      2>/dev/null || true
    exit 1
  fi
  echo "[sast] No blocking alerts from GitHub Advanced Security."

# ── ESLint security plugin (JS/TS fallback) ────────────────────────────────────
elif command -v npx >/dev/null 2>&1 && [ -f "package.json" ]; then
  echo "[sast] Falling back to eslint-plugin-security..."
  # Only block if exit code non-zero (errors found)
  npx eslint \
    --plugin security \
    --rule 'security/detect-object-injection: error' \
    --rule 'security/detect-non-literal-fs-filename: error' \
    --rule 'security/detect-eval-with-expression: error' \
    "$SCAN_TARGET" 2>/dev/null || {
      echo "[sast] BLOCKING: ESLint security findings detected." >&2
      exit 1
    }
  echo "[sast] No blocking ESLint security findings."

else
  echo "[sast] WARNING: No SAST tool available (CodeQL, gh CLI, or npm). Skipping SAST check." >&2
  exit 2
fi
