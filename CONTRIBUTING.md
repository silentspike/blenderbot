# Contributing to blenderbot

This document describes how blenderbot changes are proposed, tested and landed.

**External pull requests require an accepted feedback issue.** First open an
issue in the public
[blenderbot feedback tracker](https://github.com/silentspike/blenderbot-feedback/issues/new/choose).
After the repository owner applies `status:accepted`, the same author may open a
PR and add `Feedback: silentspike/blenderbot-feedback#123` to its body.
`external-pr-guard.yml` validates that relationship without checking out the PR.
GitHub requires explicit approval before any external contributor's workflow
jobs run.

**Suggestions and bug reports are welcome**, and they are read in the separate
[blenderbot feedback tracker](https://github.com/silentspike/blenderbot-feedback/issues/new/choose).
This product repository does not use public issues as its planning backlog.
`external-issue-guard.yml` redirects accidental public intake. For a security
problem, use a private security advisory rather than either public issue tracker.

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

Promotion is explicit and PR-only. A completed release candidate moves from
`dev` to `staging`; an authorized candidate moves from `staging` to `main`.
No merge into `dev` starts an automatic release cascade, and `main` does not
publish a release by itself.

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

## Work references and authority

Internal planning remains private. A public implementation PR contains exactly
one neutral reference such as `Work item: BB-S0.1`; it must not link, quote or
reveal internal issue content. A neutral ID proves only correlation. Required
checks and the authorized merge path still decide whether the exact PR head may
land.

Each implementation change uses one feature branch and targets `dev`. Promotion
and release are different operations with different authorization. A PR, check,
message or commit never grants its author permission to merge, promote or
publish a release.
