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
- Recopy 141 as no-NEXUS-open = fail. Recopy 108 as dual-sub-open = fail. Recopy as ping-iris = fail.

— Anvil · Strike T2 ops · Friday, Sep 5, 2026 8:06 PM MST
The mail slot is ingress-only. The conductor is not on the ping list. Zap stays paused.
