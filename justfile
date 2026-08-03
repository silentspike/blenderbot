# blenderbot developer tasks. Run `just` for the list.
default:
    @just --list

fmt:
    ruff format src tests tools

fmt-check:
    ruff format --check src tests tools

lint:
    ruff check src tests tools

types:
    mypy

test:
    pytest

language:
    python3 tools/check_language.py

# Full pre-push gate — mirrors the required checks on `dev`
check: fmt-check lint types test language
