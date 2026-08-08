# blenderbot

Closes the loop between a Blender scene and a reference image — and keeps the
model that does the work from being the one that judges it.

## The problem this solves

A single agent that edits a scene, renders it and then compares its own render
against the reference reliably reports success it has not achieved. Measured on
the same image pair, an editing agent's find count decays across rounds
(6, 4, 2, 2, 1, 1) while an agent that has never touched the scene finds 22
differences in the same pair. The editing agent is not lying; it cannot see past
the changes it just made.

blenderbot therefore separates the roles by construction rather than by
instruction:

| Role | Tools | Sees |
|---|---|---|
| **Editor** | 6 (`knowledge`, `set_value`, `build`, `execute`, `image`, `fetch`) | the scene, its own history, the findings |
| **Observer** | 1 (`crop`) | only the prepared image input and approved requirements for the job kind — no history or scene access |
| **Learning session** | 3 | retained run evidence, to propose measured improvements |

The observer has no way to know where work was done, so it has no bias to
protect. That is the whole mechanism.

## Status

The implementation program is being established. Product implementation has not
started. Release-candidate milestones and implementation contracts are tracked
in GitHub issues.

## Requirements

- Python 3.13
- Blender 5.2 LTS
- PostgreSQL 18

## Development

```bash
just check      # format, lint, types, tests — run before pushing
just test
```

Branches flow `dev` → `staging` → `main`, each with a stricter gate than the
last. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Feedback

Ideas and bug reports belong in the separate
[blenderbot feedback tracker](https://github.com/silentspike/blenderbot-feedback/issues/new/choose).
This repository's issues are reserved for approved implementation work, and
external pull requests are closed automatically.

## License

Apache-2.0 — see [LICENSE](LICENSE).
