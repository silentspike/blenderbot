# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities **privately** via GitHub Security
Advisories:

**https://github.com/silentspike/blenderbot/security/advisories/new**

Do **not** open a public issue for security problems. GitHub Security Advisories
is the single reporting channel.

## Supported versions

blenderbot is pre-1.0 and under active development. The tip of `main` is the
supported line; please report against it.

## Secret scanning

Secrets are scanned by **Gitleaks** on every PR (`secret-scan.yml`, installed
from a checksum-verified release archive). No credential is tracked in this
repository.

## Scope

blenderbot drives Blender through generated Python, talks to model providers
over authenticated sessions, and stores every run in PostgreSQL. Of particular
interest:

- **Provider credentials.** The harness authenticates via the user's existing
  subscription session. Credentials are never logged, never written to the run
  database and never included in evidence. A finding that a token can reach a
  log, a database row or a rendered report is in scope.
- **Generated code execution.** The editor role submits Python that runs inside
  Blender. The mutation frame checks a submission before it executes; a way to
  bypass that frame, or to reach the filesystem outside the run's own directory,
  is in scope.
- **Fetched assets.** External assets (HDRIs, textures, models) are recorded with
  source, licence and checksum. A path that stores an asset without its checksum,
  or that lets a fetched file escape the asset store, is in scope.
- **Database.** SQL injection through any recorded field, and any path that lets
  a run write outside its own rows.

Out of scope: the quality of a render, the correctness of a finding list, and
model output that is merely wrong rather than unsafe.
