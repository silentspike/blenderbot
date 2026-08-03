"""Tests for the dependency resolver behind the vulnerability audit.

This is gate logic: if it silently produces an empty list, the audit reports
"No known vulnerabilities found" and the gate goes green without auditing
anything. That failure mode is what these tests pin down.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import resolve_dependencies as rd


def write_report(tmp_path: Path, names: list[tuple[str, str]]) -> Path:
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps({"install": [{"metadata": {"name": n, "version": v}} for n, v in names]}),
        encoding="utf-8",
    )
    return report


def test_pins_every_dependency_to_its_version(tmp_path: Path) -> None:
    report = write_report(tmp_path, [("psycopg", "3.3.4"), ("psycopg-binary", "3.3.4")])
    assert rd.resolve(report) == ["psycopg==3.3.4", "psycopg-binary==3.3.4"]


def test_excludes_the_project_itself(tmp_path: Path) -> None:
    # It is installed from the checkout and is not on PyPI, so pip-audit cannot
    # resolve it and --strict would fail on that alone.
    report = write_report(tmp_path, [("blenderbot", "0.1.0"), ("psycopg", "3.3.4")])
    assert rd.resolve(report) == ["psycopg==3.3.4"]


# Distribution names compare case-insensitively (PEP 503), so any casing of the
# project's own name must be excluded. A different separator would be a
# different package and is deliberately not covered here.
@pytest.mark.parametrize("name", ["blenderbot", "Blenderbot", "BLENDERBOT", "BlenderBot"])
def test_excludes_the_project_under_any_casing(tmp_path: Path, name: str) -> None:
    report = write_report(tmp_path, [(name, "0.1.0"), ("psycopg", "3.3.4")])
    assert rd.resolve(report) == ["psycopg==3.3.4"]


def test_empty_resolution_exits_non_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path, [])
    out = tmp_path / "reqs.txt"
    assert rd.main(["prog", str(report), str(out)]) == 1
    assert "produced nothing" in capsys.readouterr().err
    assert not out.exists()


def test_project_only_resolution_also_exits_non_zero(tmp_path: Path) -> None:
    # A project with its dependencies stripped resolves to itself alone, which
    # would leave nothing to audit.
    report = write_report(tmp_path, [("blenderbot", "0.1.0")])
    assert rd.main(["prog", str(report), str(tmp_path / "reqs.txt")]) == 1


def test_missing_report_exits_non_zero(tmp_path: Path) -> None:
    assert rd.main(["prog", str(tmp_path / "absent.json"), str(tmp_path / "out.txt")]) == 1


def test_wrong_argument_count_exits_two(tmp_path: Path) -> None:
    assert rd.main(["prog"]) == 2


def test_writes_the_pinned_list(tmp_path: Path) -> None:
    report = write_report(tmp_path, [("psycopg", "3.3.4")])
    out = tmp_path / "reqs.txt"
    assert rd.main(["prog", str(report), str(out)]) == 0
    assert out.read_text(encoding="utf-8") == "psycopg==3.3.4\n"
