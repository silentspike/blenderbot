#!/usr/bin/env python3
"""Fail closed when a public workflow crosses the repository's CI boundary."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

USES_RE = re.compile(r"^\s*-\s+uses:\s*([^\s#]+)", re.MULTILINE)
RUNNER_RE = re.compile(r"^\s*runs-on:\s*([^\s#]+)", re.MULTILINE)
PINNED_ACTION_RE = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?@[0-9a-f]{40}$"
)
GITHUB_HOSTED_RE = re.compile(r"^ubuntu-(?:latest|\d{2}\.\d{2})$")
FORBIDDEN_SECRET_RE = re.compile(
    r"secrets\.(?:PROMOTE_TOKEN|[A-Z0-9_]*APP(?:_|$)[A-Z0-9_]*(?:KEY|TOKEN|SECRET))"
)


@dataclass(frozen=True)
class Violation:
    path: Path
    message: str


def validate_workflows(root: Path) -> list[Violation]:
    workflow_dir = root / ".github" / "workflows"
    files = sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")))
    if not files:
        return [Violation(workflow_dir, "no public workflows found")]

    violations: list[Violation] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        uses = USES_RE.findall(text)
        runners = RUNNER_RE.findall(text)

        for action in uses:
            if action.startswith("./"):
                continue
            if PINNED_ACTION_RE.fullmatch(action) is None:
                violations.append(
                    Violation(path, f"action is not pinned to a full commit SHA: {action}")
                )

        for runner in runners:
            if GITHUB_HOSTED_RE.fullmatch(runner) is None:
                violations.append(
                    Violation(path, f"runner is not an allowed GitHub-hosted label: {runner}")
                )

        if "pull_request_target:" in text and any(
            action.startswith("actions/checkout@") for action in uses
        ):
            violations.append(
                Violation(path, "pull_request_target workflow must never check out PR code")
            )

        for secret in FORBIDDEN_SECRET_RE.findall(text):
            violations.append(Violation(path, f"private App credential is forbidden: {secret}"))

    return violations


def main(argv: list[str] | None = None) -> int:
    args = sys.argv if argv is None else argv
    root = Path(args[1]).resolve() if len(args) == 2 else Path(__file__).resolve().parent.parent
    if len(args) > 2:
        print("usage: validate_ci_policy.py [repository-root]", file=sys.stderr)
        return 2

    violations = validate_workflows(root)
    if violations:
        for violation in violations:
            print(f"{violation.path}: {violation.message}", file=sys.stderr)
        return 1
    print("ci-policy: OK - GitHub-hosted runners, pinned actions, no App credentials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
