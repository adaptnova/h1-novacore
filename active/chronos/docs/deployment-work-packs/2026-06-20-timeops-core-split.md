# TimeOps Core Split

## 2026-06-20 15:57:43 — CHRONOS

Moved the original non-Temporal TimeOps material into its own directory:

```text
/adapt/platform/timeops/core
```

## New Top-Level Layout

```text
/adapt/platform/timeops/
├── README.md
├── core/
└── temporal/
```

## Core Contents

`core/` now owns the original TimeOps domain material:

- `MANIFESTO.md`
- `README.md`
- `ops/`
- `playbooks/`
- `protocols/`
- `registry/`
- `specs/`
- `tier2/`
- `workflows/`

## Compatibility Links

The former top-level paths remain as symlinks into `core/` so existing references
do not break:

- `/adapt/platform/timeops/MANIFESTO.md -> /adapt/platform/timeops/core/MANIFESTO.md`
- `/adapt/platform/timeops/ops -> /adapt/platform/timeops/core/ops`
- `/adapt/platform/timeops/playbooks -> /adapt/platform/timeops/core/playbooks`
- `/adapt/platform/timeops/protocols -> /adapt/platform/timeops/core/protocols`
- `/adapt/platform/timeops/registry -> /adapt/platform/timeops/core/registry`
- `/adapt/platform/timeops/specs -> /adapt/platform/timeops/core/specs`
- `/adapt/platform/timeops/tier2 -> /adapt/platform/timeops/core/tier2`
- `/adapt/platform/timeops/workflows -> /adapt/platform/timeops/core/workflows`

## Safety Boundary

No live services, systemd units, MemFabric paths, Temporal runtime state, or
Paperclip paths were moved.

`/adapt/platform/timeops/temporal` remains unchanged as the Temporal.io
navigation surface.

## Verification

Verification completed:

- Compatibility links resolve with `readlink -f`.
- No stale `/adapt/platform/timeops/{ops,playbooks,protocols,registry,specs,tier2,workflows}` references remained in the TimeOps docs scanned.
- `temporal-server.service`, `memfab-temporal-namespace.service`, `memfab-temporal.service`, `nova-temporal.service`, and `paperclip.service` remained active.

— CHRONOS
