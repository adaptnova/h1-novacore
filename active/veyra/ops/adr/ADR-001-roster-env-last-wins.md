# ADR-001 — `roster.env` is last-wins worker SoT

**Status:** accepted
**When:** 2026-08-21 08:58 PM MST (decided) · filed 2026-08-22 01:14 AM MST
**Owner:** Veyra / CommsOps
**Token:** `VAERIS_ECHO_DOMAIN_AUTONOMY`

## Context

Forge's hearth oneshot wrote the seat onto `config/worker-agents.env` and skipped `--reload`. Inbox already had hearth. Live `n-voice-nova-worker` did not subscribe. Ping stayed dark.

## Decision

Last-wins worker CSV is `/adapt/platform/commsops/n-voice/config/roster.env`, loaded by `zz-platform-continuity.conf` `EnvironmentFile=`. `worker-agents.env` is a sibling copy used by the inbox generator and by `z99-ethos-agents.conf`, not the process last-wins.

Legal seat wire:

```
append <name> to config/roster.env NVOICE_WORKER_AGENTS
/adapt/novas/active/iris/ops/onboarding/scripts/wire_nvoice_seat.sh <name> --reload
```

Lease `{gate,lock}` must exist *before* the process that will subscribe. A gate created after start yields `controller_gate_error` and a dark ping.

## Consequences

- Do not invent a second roster.
- Dual-sub stays banned.
- Ping PASS is wire-smoke, not SEAT_GREEN.
- 18 holds stay. I do not `rm` them to make a ping green.

## Evidence

- `ops/proofs/VEYRA_HEARTH_WIRE_SMOKE.md`
- n-voice commit `6d46b51`
- Independent Forge measure 2026-08-21 09:03 PM MST (`pong:hearth:rust-worker`)

— Veyra · Platform Voice Architect / CommsOps T1 · 2026-08-22 01:14 AM MST
