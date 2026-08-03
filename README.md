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
| **Editor** | 6 (query, set, build, execute, render, fetch) | the scene, its own history, the findings |
| **Observer** | 1 (crop) | two images, nothing else — no history, no scene access |
| **Comparator** | 0 | two finding lists, to detect standstill |
| **Learning session** | 3 + 1 | the run database, to propose improvements |

The observer has no way to know where work was done, so it has no bias to
protect. That is the whole mechanism.

## Status

Design complete, implementation starting.

## Requirements

- Python 3.11+
- Blender 5.2 LTS
- PostgreSQL 18

## Development

```bash
just check      # format, lint, types, tests — run before pushing
just test
```

Branches flow `dev` → `staging` → `main`, each with a stricter gate than the
last. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0 — see [LICENSE](LICENSE).
