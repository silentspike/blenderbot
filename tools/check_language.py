#!/usr/bin/env python3
"""English-only gate: fail if German text leaks into the repo.

The repository is English-only. This check scans tracked text files for German
signals and fails with an actionable report so a change can be fixed and
re-submitted.

Detection (kept deliberately low-false-positive):
  * any word containing an umlaut or an eszett;
  * a curated set of unambiguous German function words - words with no common
    English meaning, which appear in essentially any German sentence.

Legitimate non-English text is allowlisted two ways:
  * tools/lang_allowlist.txt - "glob:<pattern>" exempts whole files; any other
    non-comment line is an allowed substring (a line containing it is skipped);
  * an inline `lang-allow` marker comment on a line or the line above it.

Exit code 1 on any unallowed occurrence, 0 otherwise.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST = ROOT / "tools" / "lang_allowlist.txt"

TEXT_EXT = {
    ".py",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".sql",
    ".html",
    ".css",
    ".js",
    ".txt",
    ".cfg",
    ".service",
    ".sh",
    ".env",
}

# Unambiguous German function words - no common English meaning. Whole-word and
# case-insensitive. Deliberately excludes German words that collide with English
# (die, war, also, hat, man, will, fast, in, an, so, ...) and words that merely
# look German but are English (harness, phase, station, ...): listing those would
# fail ordinary English prose.
#
# Function words carry the check: German text without any of them is vanishingly
# rare, and the umlaut rule catches most of the rest.
GERMAN_WORDS = {
    "und",
    "oder",
    "nicht",
    "sind",
    "wird",
    "werden",
    "auch",
    "sehr",
    "diese",
    "dieser",
    "dieses",
    "kann",
    "muss",
    "soll",
    "beim",
    "vom",
    "zum",
    "zur",
    "wenn",
    "wurde",
    "wurden",
    "keine",
    "kein",
    "noch",
    "schon",
    "durch",
    "gegen",
    "ohne",
    "sowie",
    "jede",
    "jeder",
    "jedes",
    "eine",
    "einen",
    "einem",
    "eines",
    "wieder",
    "immer",
    "damit",
    "dann",
    "wie",
    "nur",
    "aber",
    "sich",
    "dass",
    "weil",
    "bereits",
    "jedoch",
    "etwa",
    "dabei",
    "hier",
}

WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+")
UMLAUT_RE = re.compile(r"[ÄÖÜäöüß]")


def load_allowlist() -> tuple[list[str], list[str]]:
    globs: list[str] = []
    subs: list[str] = []
    if ALLOWLIST.exists():
        for raw in ALLOWLIST.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("glob:"):
                globs.append(line[len("glob:") :].strip())
            else:
                subs.append(line)
    return globs, subs


def tracked_text_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [rel for rel in out.splitlines() if Path(rel).suffix.lower() in TEXT_EXT]


def is_german(tok: str) -> bool:
    return bool(UMLAUT_RE.search(tok)) or tok.lower() in GERMAN_WORDS


def main() -> int:
    globs, subs = load_allowlist()
    hits: list[tuple[str, int, int, str, str]] = []
    for rel in tracked_text_files():
        if any(fnmatch.fnmatch(rel, g) for g in globs):
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        lines = text.splitlines()
        for lineno, line in enumerate(lines, start=1):
            prev = lines[lineno - 2] if lineno >= 2 else ""
            if "lang-allow" in line or "lang-allow" in prev:
                continue
            if any(sub in line for sub in subs):
                continue
            for m in WORD_RE.finditer(line):
                if is_german(m.group(0)):
                    hits.append((rel, lineno, m.start() + 1, m.group(0), line.strip()[:120]))
                    break

    if hits:
        print(
            f"language-check: FAIL - {len(hits)} German text occurrence(s); "
            f"the repo is English-only.\n"
        )
        for rel, lineno, col, tok, ctx in hits:
            print(f"  {rel}:{lineno}:{col}: German token '{tok}'")
            print(f"      | {ctx}")
        print("\nResolve each occurrence by either:")
        print("  - translating the text to English (repo content is English-only), or")
        print("  - if it is legitimate (a test fixture or an encoding-coverage note), add an")
        print("    inline `lang-allow` marker comment on that line or the line directly above,")
        print("    or add the file glob / substring to tools/lang_allowlist.txt.")
        return 1

    print("language-check: OK - no German text in tracked English-only files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
