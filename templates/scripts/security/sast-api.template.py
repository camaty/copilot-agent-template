#!/usr/bin/env python3
"""
SAST/SCA API wrapper for {{PROJECT_NAME}} (Shift-Left security gate).

This script provides a unified Python interface for the Implementer agent
to call security analysis tools without knowing the underlying toolchain.
It can be invoked directly or used as a library by other agent scripts.

Exit codes:
    0 — pass (no blocking findings)
    1 — fail (HIGH or CRITICAL findings in scanned files)
    2 — tool unavailable (non-blocking warning)

Usage:
    python3 .github/scripts/security/sast-api.py [--files file1 file2] [--format json]
    python3 .github/scripts/security/sast-api.py --help

Configuration (environment variables):
    SAST_SEVERITY_THRESHOLD  Minimum severity to block on (default: high)
                             Values: critical | high | medium | low
    SAST_OUTPUT_FORMAT       Output format (default: text)
                             Values: text | json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

SeverityLevel = Literal["critical", "high", "medium", "low", "info"]

SEVERITY_ORDER: list[SeverityLevel] = ["critical", "high", "medium", "low", "info"]


@dataclass
class Finding:
    severity: SeverityLevel
    rule_id: str
    message: str
    file: str
    line: int | None = None
    tool: str = "unknown"

    def is_blocking(self, threshold: SeverityLevel) -> bool:
        threshold_idx = SEVERITY_ORDER.index(threshold)
        try:
            severity_idx = SEVERITY_ORDER.index(self.severity)
        except ValueError:
            severity_idx = len(SEVERITY_ORDER)
        return severity_idx <= threshold_idx


@dataclass
class SastResult:
    tool: str
    findings: list[Finding] = field(default_factory=list)
    available: bool = True
    error: str | None = None

    def blocking_findings(self, threshold: SeverityLevel) -> list[Finding]:
        return [f for f in self.findings if f.is_blocking(threshold)]


def run_command(cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=capture, text=True, timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout: {cmd}"


def scan_with_codeql(files: list[str]) -> SastResult:
    """Run CodeQL analysis."""
    if not shutil.which("codeql"):
        return SastResult(tool="codeql", available=False, error="codeql not in PATH")

    report_path = Path(".github/security/sast-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Create database
    rc, _, err = run_command([
        "codeql", "database", "create", ".codeql-db",
        f"--language={{PRIMARY_LANGUAGE_CODEQL}}",
        "--source-root=.", "--overwrite", "--quiet",
    ])
    if rc != 0:
        return SastResult(tool="codeql", available=False, error=f"DB creation failed: {err}")

    # Analyze
    rc, _, err = run_command([
        "codeql", "database", "analyze", ".codeql-db",
        "--format=sarif-latest",
        f"--output={report_path}",
        "--no-print-diagnostics-summary",
        "codeql/{{PRIMARY_LANGUAGE_CODEQL}}-queries:Security/",
    ])
    if rc != 0:
        return SastResult(tool="codeql", available=False, error=f"Analysis failed: {err}")

    findings = _parse_sarif(report_path, tool="codeql")
    return SastResult(tool="codeql", findings=findings)


def scan_with_semgrep(files: list[str]) -> SastResult:
    """Run Semgrep analysis."""
    if not shutil.which("semgrep"):
        return SastResult(tool="semgrep", available=False, error="semgrep not in PATH")

    targets = files if files else ["."]
    cmd = ["semgrep", "--config=auto", "--json", "--severity=ERROR", "--severity=WARNING"] + targets
    rc, stdout, err = run_command(cmd)

    if rc not in (0, 1):
        return SastResult(tool="semgrep", available=False, error=f"semgrep error: {err}")

    findings: list[Finding] = []
    try:
        data = json.loads(stdout)
        for r in data.get("results", []):
            extra = r.get("extra", {})
            severity_raw = extra.get("severity", "WARNING").lower()
            severity: SeverityLevel = "high" if severity_raw == "error" else "medium"
            findings.append(Finding(
                severity=severity,
                rule_id=r.get("check_id", "unknown"),
                message=extra.get("message", ""),
                file=r.get("path", ""),
                line=r.get("start", {}).get("line"),
                tool="semgrep",
            ))
    except (json.JSONDecodeError, KeyError):
        pass

    return SastResult(tool="semgrep", findings=findings)


def scan_with_eslint_security(files: list[str]) -> SastResult:
    """Run ESLint with security plugins (JS/TS projects)."""
    if not shutil.which("npx") or not Path("package.json").exists():
        return SastResult(tool="eslint-security", available=False, error="npx or package.json not found")

    targets = files if files else ["{{SOURCE_DIR}}"]
    cmd = [
        "npx", "eslint",
        "--plugin", "security",
        "--rule", "security/detect-object-injection: error",
        "--rule", "security/detect-non-literal-fs-filename: error",
        "--rule", "security/detect-eval-with-expression: error",
        "--format", "json",
    ] + targets
    rc, stdout, _ = run_command(cmd)

    findings: list[Finding] = []
    try:
        for file_result in json.loads(stdout):
            for msg in file_result.get("messages", []):
                if msg.get("severity", 0) >= 2:  # 2 = error
                    findings.append(Finding(
                        severity="high",
                        rule_id=msg.get("ruleId", "unknown"),
                        message=msg.get("message", ""),
                        file=file_result.get("filePath", ""),
                        line=msg.get("line"),
                        tool="eslint-security",
                    ))
    except (json.JSONDecodeError, KeyError):
        pass

    return SastResult(tool="eslint-security", findings=findings)


def _parse_sarif(path: Path, tool: str) -> list[Finding]:
    """Parse a SARIF report and return Finding objects."""
    findings: list[Finding] = []
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return findings

    severity_map = {"error": "critical", "warning": "medium", "note": "low"}

    for run in data.get("runs", []):
        for result in run.get("results", []):
            raw_level = result.get("level", "warning")
            severity = severity_map.get(raw_level, "medium")

            # Try problem.severity property (CodeQL)
            props_severity = (result.get("properties", {}) or {}).get("problem.severity", "")
            if props_severity:
                severity = props_severity.lower()

            loc = (result.get("locations") or [{}])[0]
            phys = loc.get("physicalLocation", {})
            uri = phys.get("artifactLocation", {}).get("uri", "")
            line = phys.get("region", {}).get("startLine")

            findings.append(Finding(
                severity=severity,
                rule_id=result.get("ruleId", "unknown"),
                message=(result.get("message") or {}).get("text", ""),
                file=uri,
                line=line,
                tool=tool,
            ))

    return findings


def run_all_scanners(files: list[str]) -> list[SastResult]:
    """Try all available scanners in priority order."""
    results: list[SastResult] = []
    for scanner in [scan_with_codeql, scan_with_semgrep, scan_with_eslint_security]:
        r = scanner(files)
        results.append(r)
        if r.available and r.findings is not None:
            # Found a working scanner — use it as primary (could run all if desired)
            break
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="SAST/SCA API wrapper")
    parser.add_argument("--files", nargs="*", default=[], help="Files to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--threshold",
        choices=SEVERITY_ORDER,
        default=os.environ.get("SAST_SEVERITY_THRESHOLD", "high"),
    )
    args = parser.parse_args()

    results = run_all_scanners(args.files)
    threshold: SeverityLevel = args.threshold  # type: ignore[assignment]

    all_blocking: list[Finding] = []
    available_tools: list[str] = []

    for r in results:
        if not r.available:
            print(f"[sast] {r.tool}: unavailable — {r.error}", file=sys.stderr)
            continue
        available_tools.append(r.tool)
        blocking = r.blocking_findings(threshold)
        all_blocking.extend(blocking)

    if not available_tools:
        msg = "[sast] WARNING: No SAST tool available. Install CodeQL, Semgrep, or eslint-plugin-security."
        if args.format == "json":
            print(json.dumps({"status": "unavailable", "message": msg, "findings": []}))
        else:
            print(msg, file=sys.stderr)
        return 2

    if args.format == "json":
        output = {
            "status": "fail" if all_blocking else "pass",
            "threshold": threshold,
            "tools_used": available_tools,
            "blocking_count": len(all_blocking),
            "findings": [
                {
                    "severity": f.severity,
                    "rule_id": f.rule_id,
                    "message": f.message,
                    "file": f.file,
                    "line": f.line,
                    "tool": f.tool,
                }
                for f in all_blocking
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        if all_blocking:
            print(f"[sast] BLOCKING: {len(all_blocking)} findings at or above '{threshold}' severity:")
            for f in all_blocking:
                loc = f"{f.file}:{f.line}" if f.line else f.file
                print(f"  {f.severity.upper()} [{f.rule_id}] {loc} — {f.message}")
        else:
            print(f"[sast] PASS: No blocking findings (threshold: {threshold}).")

    return 1 if all_blocking else 0


if __name__ == "__main__":
    sys.exit(main())
