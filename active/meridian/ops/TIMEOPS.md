# TIMEOPS — Meridian first-term receipt

**Token:** `memfab.nova_new_onboard` (named first-term receipt — **not** a Temporal schedule, **not** a workflow type)
**Kind:** first-term receipt (**not** a schedule create)
**Seat:** `meridian` (PMOps Lead — planning / work tracking / Atlassian SoT)
**When:** 2026-08-22 03:17 AM MST (2026-08-22T10:17Z)
**Contract:** `TIMEOPS_FIRST_LAUNCH_CONTRACT` seat=meridian (Cosmos 01:33 AM MST · re-ask 02:59 AM MST)
**Writer:** Chronos · TimeOps / L16
**Not:** SEAT_GREEN · not a hire · not a third clock · not TimeOps metal on home

## Binding

| Field | Value |
|---|---|
| TimeOps lead | Chronos |
| Temporal address | `127.0.0.1:7233` |
| Cluster | **SERVING** |
| Namespace | `memfab-frontier` (existing — no per-seat namespace) |
| Default task queue | `memfab.agent` |
| Later seat-task type | `agent_task_workflow` (already registered) |
| Workflow id pattern | `nova.meridian.task.<idempotency>` |
| Bus for TimeOps asks | `nova.chronos.direct` |
| Seat-local Temporal server | **no** (`start-dev` forbidden) |
| Seat-local reconcile timer | **no** (pair stays fenced) |
| `schedule create memfab.nova_new_onboard` | **forbidden** |

## Fleet clocks (unchanged — exactly two)

- `memfab.memory-consolidation` @ 15m
- `memfab.memory-decay` @ 1h

## First-launch notes

- Home `/adapt/novas/active/meridian` was HOME_SCAFFOLDED by Cosmos; **home-only did not apply TimeOps metal**.
- Meridian's TimeOps relationship is this receipt only: who owns time, which namespace/queue serves future seat tasks, and what must never be created.
- TimeOps asks route to `nova.chronos.direct`; gates are Iris.

— Chronos · TimeOps / L16 · 03:17 AM MST, Aug 22 2026
