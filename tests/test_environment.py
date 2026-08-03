"""Tests for the environment checks."""

from __future__ import annotations

import shutil

import pytest

from blenderbot import environment
from blenderbot.environment import Check, Status


def test_python_check_passes_on_the_running_interpreter() -> None:
    # The suite itself only runs on a supported interpreter, so this must hold.
    assert environment.check_python().status is Status.OK


def test_blender_missing_from_path_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: None)
    check = environment.check_blender("blender")
    assert check.status is Status.FAILED
    assert "not on PATH" in check.detail


def test_blender_version_below_minimum_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/blender")
    monkeypatch.setattr(environment, "_run", lambda *_, **__: (0, "Blender 4.2.1"))
    check = environment.check_blender()
    assert check.status is Status.FAILED
    assert "4.2.1" in check.detail


def test_blender_version_at_minimum_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: "/opt/blender/blender")
    monkeypatch.setattr(environment, "_run", lambda *_, **__: (0, "Blender 5.2.0"))
    check = environment.check_blender()
    assert check.status is Status.OK


def test_unparsable_blender_banner_is_unknown_not_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/blender")
    monkeypatch.setattr(environment, "_run", lambda *_, **__: (0, "Blender (unknown build)"))
    assert environment.check_blender().status is Status.UNKNOWN


def test_missing_dsn_is_unknown_not_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BLENDERBOT_DSN", raising=False)
    check = environment.check_database()
    assert check.status is Status.UNKNOWN
    assert "BLENDERBOT_DSN" in check.detail


def test_unreachable_database_fails() -> None:
    pytest.importorskip("psycopg")
    # Port 1 is reserved and never listens, so this exercises the real failure path.
    check = environment.check_database("postgresql://nobody@127.0.0.1:1/nothing")
    assert check.status is Status.FAILED


def test_run_all_covers_every_check() -> None:
    names = {c.name for c in environment.run_all(dsn=None, blender="definitely-not-a-binary")}
    assert names == {"python", "blender", "database"}


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([Status.OK, Status.OK], Status.OK),
        ([Status.OK, Status.UNKNOWN], Status.UNKNOWN),
        ([Status.OK, Status.FAILED], Status.FAILED),
        # A failure outranks an unknown: the loudest problem wins.
        ([Status.UNKNOWN, Status.FAILED], Status.FAILED),
    ],
)
def test_worst_ranks_failed_above_unknown_above_ok(
    statuses: list[Status], expected: Status
) -> None:
    checks = [Check(f"c{i}", s, "") for i, s in enumerate(statuses)]
    assert environment.worst(checks) is expected


def test_run_reports_a_missing_binary_instead_of_raising() -> None:
    code, output = environment._run(["definitely-not-a-binary-xyz"])
    assert code == 127
    assert "not found" in output
