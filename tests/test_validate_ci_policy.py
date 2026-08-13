"""Tests for the fail-closed public Actions policy."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import validate_ci_policy as policy

PIN = "3d3c42e5aac5ba805825da76410c181273ba90b1"


def write_workflow(root: Path, text: str) -> None:
    directory = root / ".github" / "workflows"
    directory.mkdir(parents=True)
    (directory / "test.yml").write_text(text, encoding="utf-8")


def test_current_repository_obeys_policy() -> None:
    root = Path(__file__).resolve().parent.parent
    assert policy.validate_workflows(root) == []


def test_accepts_sha_pinned_action_on_github_hosted_runner(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
        f"      - uses: actions/checkout@{PIN}\n",
    )
    assert policy.validate_workflows(tmp_path) == []


def test_rejects_floating_action_reference(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v6\n",
    )
    assert "not pinned" in policy.validate_workflows(tmp_path)[0].message


def test_rejects_self_hosted_runner(tmp_path: Path) -> None:
    write_workflow(tmp_path, "jobs:\n  test:\n    runs-on: self-hosted\n")
    assert "not an allowed GitHub-hosted" in policy.validate_workflows(tmp_path)[0].message


def test_rejects_app_private_key_secret(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "jobs:\n  test:\n    runs-on: ubuntu-latest\n    env:\n"
        "      KEY: ${{ secrets.CONTROL_APP_KEY }}\n",
    )
    assert "App credential is forbidden" in policy.validate_workflows(tmp_path)[0].message


def test_rejects_checkout_in_pull_request_target(tmp_path: Path) -> None:
    write_workflow(
        tmp_path,
        "on:\n  pull_request_target:\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        f"    steps:\n      - uses: actions/checkout@{PIN}\n",
    )
    messages = [violation.message for violation in policy.validate_workflows(tmp_path)]
    assert "pull_request_target workflow must never check out PR code" in messages


def test_missing_workflows_is_a_failure(tmp_path: Path) -> None:
    assert policy.validate_workflows(tmp_path)[0].message == "no public workflows found"
