"""Command line entry point."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from blenderbot import __version__
from blenderbot.environment import Status, run_all, worst


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blenderbot",
        description="Iteratively match a Blender scene to a reference image.",
    )
    parser.add_argument("--version", action="version", version=f"blenderbot {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="check that the environment can run a job")
    doctor.add_argument("--dsn", default=None, help="PostgreSQL DSN (defaults to BLENDERBOT_DSN)")
    doctor.add_argument("--blender", default="blender", help="Blender executable to probe")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "doctor":
        checks = run_all(dsn=args.dsn, blender=args.blender)
        for check in checks:
            print(check.line())
        overall = worst(checks)
        print(f"\n{overall.value}")
        # UNKNOWN exits non-zero as well: an unverified environment is not a
        # working one, and a caller must not read it as a pass.
        return 0 if overall is Status.OK else 1

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
