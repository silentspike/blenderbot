# Contributing to blenderbot

All development is done by the silentspike org. This document describes how the
project is developed and what every change has to clear.

**External pull requests are not accepted.** No foreign code enters this
repository. A PR opened from a fork is closed automatically by
`external-pr-guard.yml`.

**Suggestions and bug reports are welcome**, and they are read. Please open an
issue using the *Feature request or suggestion* or *Bug report* template — that
is the way to propose a change here. For a security problem, use a private
security advisory rather than a public issue.

## Ground rules

- **Language:** all repository content is **English** — issues, PRs, commits,
  docs, code, comments, identifiers. The `language-check` gate enforces this
  mechanically, and points at the exact `file:line` when it fails.
- **Conventional Commits** for commit messages and PR titles (`feat:`, `fix:`,
  `docs:`, `refactor:`, `perf:`, `test:`, `build:`, `ci:`, `chore:`, `deps:`,
  `spike:`).
- **No secrets** in the repo. Gitleaks runs on every PR.
- **Code only.** No working notes, scratch output or session logs in the repo.

## Local setup

```sh
just check      # fmt-check + lint + types + tests + language — the pre-push gate
```

## Verification and evidence

No change is done without evidence: **the command that was run and its actual
output**, a rendered image, or a passing test against real fixtures.

The following are explicitly *not* evidence: "reviewed, looks correct", quoted
line numbers, "the structure is in place", or a source review without execution.
The default status of every acceptance criterion is UNTESTED, and UNTESTED is
not PASS.

Report honestly. If a surface was not tested, name it in the PR and say why. A
partially verified change that says so is worth more than a green claim that
does not hold.

## Branch model & CI

Promotion flows `feature → dev → staging → main`, each gate stricter than the
last:

| Branch | Required gate | Scope |
|---|---|---|
| `dev` | `dev-checks` | fast shift-left: format, lint, types, unit tests, coverage |
| `staging` | `staging-pass` + CodeQL | integration tests against a real database, CodeQL |
| `main` | `main-pass` + CodeQL | release-grade: full suite, dependency audit, build |

Always-on for every PR into `dev`/`staging`/`main`: secret scan (Gitleaks),
Conventional-Commit title check, the English-only `language-check`, the
governance risk-label check, and auto-labeling.

Merging into `dev`/`staging` auto-opens and auto-merges the next-stage
promotion PR once the target's checks pass, so the cascade runs hands-off. A
watchdog reports a promotion that stalls.

**Merge strategy:** squash-only, at every hop. The three branches therefore
carry independent histories with identical *content*; reconcile by promoting
forward, not by expecting shared SHAs.

Branch protection is `strict` on all three: a PR must be up to date with its
base before it can merge, so every merge is tested against the exact tree it
lands on.

## Review policy

`required_approving_review_count` is 0: a single maintainer may merge their own
PR. This is deliberate for a single-maintainer repository — an approval only the
same person can give is ceremony, not safety. The compensating control is the
required-checks gate, which a self-approval cannot bypass, plus `enforce_admins`
on `main`. When a second maintainer joins, raise the count to 1.
