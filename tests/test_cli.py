"""Tests for the command line entry point."""

from __future__ import annotations

import pytest

from blenderbot import __version__, cli
from blenderbot.environment import Check, Status


def test_version_is_printed_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--version"])
    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_is_an_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main([])
    assert exit_info.value.code != 0


def test_doctor_exits_zero_when_everything_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli,
        "run_all",
        lambda **_: [Check("python", Status.OK, "3.13"), Check("blender", Status.OK, "5.2.0")],
    )
    assert cli.main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "OK" in out and "blender" in out


def test_doctor_exits_non_zero_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "run_all", lambda **_: [Check("blender", Status.FAILED, "missing")])
    assert cli.main(["doctor"]) == 1


def test_doctor_exits_non_zero_on_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    # An unverified environment must not read as a pass to a calling script.
    monkeypatch.setattr(cli, "run_all", lambda **_: [Check("database", Status.UNKNOWN, "no DSN")])
    assert cli.main(["doctor"]) == 1
