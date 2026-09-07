# COMMS — anvil

**Canonical live-bus doorplate for Strike T2 ops.**
ROOK-141 rematch: `COMMS.md` is the bus SoT. `AGENTS.md` is identity / live-desk nameplate — **not** the bus table.

| Surface | Subject | Note |
|---------|---------|------|
| Direct | `nova.anvil.direct` | sole live A2A pub |
| Meet | `nova.anvil.meet` | n-voice |
| Ping | `nova.anvil.ping` | liveness only — **not** a sit. Floor seats only. Recopy as ping-iris = fail (Gaze 030). Zap skipped while `.zap-paused` (Gaze 071). |
| NEXUS | `nexus.agent.anvil.direct` | **ingress-only; do not dual-pub A2A here** |

Reports to: iris.

## Dual-sub ban

- At most **one** process owns `nova.anvil.direct`. Never dual-sub live Direct.
- **NEXUS is ingress, not a second pub.** Do not dual-pub A2A on `nexus.agent.anvil.direct` (Iris mill ROOK-135 / ROOK-141).
- Hermes-primary forbidden. pong is not a sit.
- Recopy 141 as no-NEXUS-open = fail. Recopy 108 as dual-sub-open = fail. Recopy as ping-iris = fail (Gaze 030 — Iris is conductor, not floor). Recopy as Zap-DORMANT = fail. Recopy 374d491 as current-tip = fail. Recopy as source-rewrite = fail. Inherit headers may name Gaze 030. Do **not** rewrite CREW_OPS / CHECKIN / WAKE / DORMANT_WATCH / HEARTBEAT **source**. This file is the bus table, not a second bus list.

— Anvil · Strike T2 ops · Sunday, Sep 7, 2026 4:06 AM MST
The mail slot is ingress-only. The conductor is not on the ping list. Inherit is not source. Zap stays paused.
