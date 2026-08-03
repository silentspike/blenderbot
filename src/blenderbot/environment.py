"""Environment checks.

Every check answers one question with a command and its actual output, because
a run that starts against a half-present environment fails later and less
clearly. A check that cannot be performed reports UNKNOWN - it never reports OK.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum

MINIMUM_PYTHON = (3, 11)
MINIMUM_BLENDER = (5, 2)
MINIMUM_POSTGRES = 18


class Status(Enum):
    """Outcome of a single check. UNKNOWN is not OK."""

    OK = "ok"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Check:
    """One environment check: what was asked, what came back."""

    name: str
    status: Status
    detail: str

    def line(self) -> str:
        return f"{self.status.value.upper():<8}{self.name:<12}{self.detail}"


def _run(command: list[str], timeout: float = 15.0) -> tuple[int, str]:
    """Run a command, return its exit code and combined output.

    A missing binary or a timeout is a result, not an exception - the caller
    turns it into a check outcome.
    """
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return 127, f"not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout:g}s: {' '.join(command)}"
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def _parse_version(text: str) -> tuple[int, ...] | None:
    """Pull the first dotted numeric version out of a tool's banner."""
    for token in text.replace(",", " ").split():
        parts = token.split(".")
        if len(parts) >= 2 and all(p.isdigit() for p in parts[:2]):
            return tuple(int(p) for p in parts if p.isdigit())
    return None


def check_python() -> Check:
    actual = sys.version_info[:2]
    detail = f"{actual[0]}.{actual[1]} (need >= {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]})"
    status = Status.OK if actual >= MINIMUM_PYTHON else Status.FAILED
    return Check("python", status, detail)


def check_blender(executable: str = "blender") -> Check:
    path = shutil.which(executable)
    if path is None:
        return Check("blender", Status.FAILED, f"not on PATH: {executable}")

    code, output = _run([path, "--version"])
    if code != 0:
        return Check(
            "blender", Status.FAILED, f"exit {code}: {output.splitlines()[0] if output else ''}"
        )

    version = _parse_version(output)
    if version is None:
        return Check(
            "blender", Status.UNKNOWN, f"could not parse version from: {output.splitlines()[0]}"
        )

    ok = version[:2] >= MINIMUM_BLENDER
    detail = (
        f"{'.'.join(str(p) for p in version[:3])} at {path} "
        f"(need >= {MINIMUM_BLENDER[0]}.{MINIMUM_BLENDER[1]})"
    )
    return Check("blender", Status.OK if ok else Status.FAILED, detail)


def check_database(dsn: str | None = None) -> Check:
    """Connect to PostgreSQL and read back its version.

    Without a DSN there is nothing to test, which is UNKNOWN rather than OK -
    an unconfigured database is not a working one.
    """
    dsn = dsn if dsn is not None else os.environ.get("BLENDERBOT_DSN")
    if not dsn:
        return Check("database", Status.UNKNOWN, "BLENDERBOT_DSN is not set")

    try:
        import psycopg
    except ImportError:
        return Check("database", Status.UNKNOWN, "psycopg is not installed")

    try:
        with psycopg.connect(dsn, connect_timeout=5) as connection:
            row = connection.execute("SELECT current_setting('server_version_num')").fetchone()
    # Any failure to reach the database is the result of this check, not a crash.
    except Exception as error:
        return Check("database", Status.FAILED, f"{type(error).__name__}: {error}".strip())

    if row is None:
        return Check("database", Status.UNKNOWN, "server_version_num returned no row")

    major = int(row[0]) // 10000
    ok = major >= MINIMUM_POSTGRES
    return Check(
        "database",
        Status.OK if ok else Status.FAILED,
        f"PostgreSQL {major} (need >= {MINIMUM_POSTGRES})",
    )


def run_all(dsn: str | None = None, blender: str = "blender") -> list[Check]:
    return [check_python(), check_blender(blender), check_database(dsn)]


def worst(checks: list[Check]) -> Status:
    """The overall outcome. FAILED beats UNKNOWN beats OK."""
    if any(c.status is Status.FAILED for c in checks):
        return Status.FAILED
    if any(c.status is Status.UNKNOWN for c in checks):
        return Status.UNKNOWN
    return Status.OK
