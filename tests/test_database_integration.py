"""Integration tests: these talk to a real PostgreSQL.

Selected with `-m integration` and skipped without BLENDERBOT_DSN, so the unit
suite stays runnable anywhere. The point of these is exactly what a mock cannot
prove: that the version query works against the server we actually target, and
that a wrong DSN fails the way the check claims it does.
"""

from __future__ import annotations

import os

import pytest

from blenderbot.environment import MINIMUM_POSTGRES, Status, check_database

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("BLENDERBOT_DSN"),
        reason="BLENDERBOT_DSN is not set",
    ),
]


def dsn() -> str:
    value = os.environ.get("BLENDERBOT_DSN")
    assert value is not None
    return value


def test_reaches_a_supported_postgres() -> None:
    check = check_database(dsn())
    assert check.status is Status.OK, check.detail
    assert f"PostgreSQL {MINIMUM_POSTGRES}" in check.detail or "PostgreSQL 1" in check.detail


def test_wrong_credentials_report_failed_not_unknown() -> None:
    # A rejected login is a definite negative, so it must not be reported as
    # "could not determine" - a caller distinguishes those.
    broken = dsn().replace("postgres:ci@", "postgres:wrong-password@")
    assert broken != dsn(), "the DSN did not contain the expected credentials"
    check = check_database(broken)
    assert check.status is Status.FAILED
    assert check.detail


def test_unreachable_host_reports_failed() -> None:
    check = check_database("postgresql://postgres@127.0.0.1:1/nothing")
    assert check.status is Status.FAILED
