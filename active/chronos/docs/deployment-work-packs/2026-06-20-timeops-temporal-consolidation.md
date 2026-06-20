# TimeOps Temporal Consolidation

## 2026-06-20 15:52:13 — CHRONOS

Phase 0 consolidation is complete.

## What Changed

Created `/adapt/platform/timeops/temporal` as the Chronos/TimeOps-facing
Temporal.io surface.

The directory contains:

- `README.md`
- `PATH_MANIFEST.md`
- `systemd/live-unit-inventory.md`
- `runtime/README.md`
- compatibility symlinks into the live MemFabric Temporal workspace

## Compatibility Links

| TimeOps path | Live target |
|---|---|
| `/adapt/platform/timeops/temporal/memfabric` | `/adapt/platform/memops/memfabric` |
| `/adapt/platform/timeops/temporal/pc-bridge` | `/adapt/platform/memops/memfabric/ops/pc-bridge` |
| `/adapt/platform/timeops/temporal/crates/memfab-temporal` | `/adapt/platform/memops/memfabric/crates/memfab-temporal` |
| `/adapt/platform/timeops/temporal/crates/memfab-temporal-contract` | `/adapt/platform/memops/memfabric/crates/memfab-temporal-contract` |
| `/adapt/platform/timeops/temporal/proofs/durable-boundary` | `/adapt/platform/memops/memfabric/runtime/temporal-durable-boundary` |
| `/adapt/platform/timeops/temporal/proofs/live-signal-validation` | `/adapt/platform/memops/memfabric/runtime/temporal-live-signal-validation` |
| `/adapt/platform/timeops/temporal/tools/temporal` | `/home/x/.temporalio/bin/temporal` |
| `/adapt/platform/timeops/temporal/tools/ensure-memfab-temporal-namespace` | `/usr/local/sbin/ensure-memfab-temporal-namespace` |

## Safety Boundary

No live service roots were moved.

No systemd units were rewritten.

No runtime state directories were relocated.

Current live roots remain:

- `/adapt/platform/memops/memfabric`
- `/home/x/.temporalio/bin/temporal`
- `/var/lib/memfab/temporal`
- `/var/lib/memfab/runtime/memfab-temporal`
- `/var/log/memfab/runtime`

## Verification

Required verification commands:

```bash
find -L /adapt/platform/timeops/temporal -type l -print
systemctl is-active temporal-server.service memfab-temporal-namespace.service memfab-temporal.service nova-temporal.service
/adapt/platform/timeops/temporal/tools/temporal --version
readlink -f /adapt/platform/timeops/temporal/memfabric
readlink -f /adapt/platform/timeops/temporal/pc-bridge
```

## Next Phase

Phase 1 should update new Chronos/TimeOps references to use
`/adapt/platform/timeops/temporal`.

Phase 2 may rewrite systemd paths only under a dedicated restart window with
unit backups, rollback commands, and post-restart health checks.

— CHRONOS
