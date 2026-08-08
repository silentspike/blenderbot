# Contributing to blenderbot

All development is done by the silentspike org. This document describes how the
project is developed and what every change has to clear.

**External pull requests are not accepted.** Repository settings restrict pull
request creation to collaborators. `external-pr-guard.yml` is a second layer
that closes and redirects any external PR that still reaches the repository.

**Suggestions and bug reports are welcome**, and they are read in the separate
[blenderbot feedback tracker](https://github.com/silentspike/blenderbot-feedback/issues/new/choose).
Repository settings restrict this product tracker to collaborators, so external
feedback cannot enter the implementation pool. `external-issue-guard.yml` is a
second layer if that setting drifts. For a security problem, use a private
security advisory rather than either public issue tracker.

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

## Parallel agent delivery

Codex is the only orchestration role. Interactive Claude sessions are the
default implementation workers. This choice is an execution policy, not product
architecture: blenderbot itself must remain able to use either supported model
provider or both.

Every worker lane obeys these rules:

- A GitHub issue is the work authority. Transport delivery, a running process or
  a model response is not proof that work was claimed or completed.
- A worker claims exactly one foreground mutation issue and works in one
  persistent, project-bound worktree. The claim records the issue, role,
  worktree, branch, session and generation.
- Worker-to-worker messages are denied. Workers send semantic acknowledgements,
  evidence, blockers and results to the Codex orchestrator; the orchestrator
  schedules all follow-up work.
- A delivered message is not an acknowledgement. The worker must acknowledge
  the message identifier and restate the issue, branch and intended action.
- Parallel ownership is semantic. Two issues may touch the same file only when
  their owned symbols or sections are disjoint and named in both issues.
- Shared migrations, generated contracts, flow specifications and release
  branches use short, exclusive effect lanes. A worker releases its ordinary
  slot while waiting for such a lane.
- Blocked, review-only and merge-ready work is parked so another independent
  issue can use the worker slot.
- The public issue and repository must contain every requirement needed for the
  task. Private plans, prior chats and local paths are never implementation
  dependencies.
- Completion requires a semantic result plus GitHub and repository readback:
  exact commit, executed checks, evidence location and remaining limitations.

The durable control ledger and the owner-facing control room are projections of
these facts. Neither is allowed to invent completion from terminal activity.
