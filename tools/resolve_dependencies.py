#!/usr/bin/env python3
"""Resolve this project's own dependencies into a pinned requirements list.

Used by the vulnerability audit on `main`. Auditing the whole environment would
also flag the runner's pip and setuptools, which this project does not ship - a
CVE there would fail the gate for a reason unrelated to the change under review.

Exits non-zero when the resolution yields nothing. That is not decoration:
pip-audit exits 0 on an empty requirements file with "No known vulnerabilities
found", so a silent resolver change would otherwise leave the gate green while
auditing nothing at all.

Usage:
    pip install --dry-run --ignore-installed --report report.json .
    python3 tools/resolve_dependencies.py report.json audited-requirements.txt
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = "blenderbot"


def normalise(name: str) -> str:
    return name.lower().replace("_", "-")


def resolve(report: Path) -> list[str]:
    data = json.loads(report.read_text(encoding="utf-8"))
    return [
        f"{item['metadata']['name']}=={item['metadata']['version']}"
        for item in data.get("install", [])
        if normalise(item["metadata"]["name"]) != PROJECT
    ]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <report.json> <output.txt>", file=sys.stderr)
        return 2

    report, output = Path(argv[1]), Path(argv[2])
    if not report.exists():
        print(f"error: {report} does not exist", file=sys.stderr)
        return 1

    deps = resolve(report)
    if not deps:
        print(
            "error: dependency resolution produced nothing - an audit of this "
            "would pass without auditing anything",
            file=sys.stderr,
        )
        return 1

    output.write_text("\n".join(deps) + "\n", encoding="utf-8")
    print(f"resolved {len(deps)} dependencies:")
    for dep in deps:
        print(f"  {dep}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
