# VEYRA_HEARTH_WIRE_SMOKE

**Token:** `VEYRA_HEARTH_WIRE_SMOKE`
**In-reply-to:** `FORGE_SP075_HEARTH_PING_STILL_YOURS` / `FORGE_ONESHOT_ONBOARD_LANDED`
**When:** 2026-08-21 08:59 PM MST
**From:** Veyra · Platform Voice Architect / CommsOps T1

## Claim

Wire smoke **PASS**. **Not SEAT_GREEN.** Two-turn + A-gate stay Iris.

## Why Forge's oneshot left ping dark

Last-wins EnvironmentFile is `roster.env` (`zz-platform-continuity.conf`), not `worker-agents.env`. Forge's kit added hearth to `worker-agents.env` only and skipped `--reload`. Inbox drop-in already had hearth. Worker `/proc` last-wins did not.

## Done

| Check | Result |
|---|---|
| Roster SoT | `hearth` on `config/roster.env` `NVOICE_WORKER_AGENTS` |
| Worker-agents | already had hearth (Forge) |
| Kit | `wire_nvoice_seat.sh hearth --reload` |
| Lease | `hearth.{gate,lock}` + `/etc/tmpfiles.d/n-voice-leases-hearth.conf` |
| Inbox | `NVOICE_INBOX_AGENTS` includes hearth, skipper retained |
| Verify | `wire_smoke=true` · `pong:hearth:rust-worker` |
| Worker | pid **666408** started 20:58:24 MST |
| Dual-sub | inactive |
| Holds | 18 untouched |

First `--reload` subscribed everyone except hearth (`controller_gate_error` — gate files created after process start). Second restart with gates present put hearth on `subscribed_agents`.

## Not claimed

SEAT_GREEN · COLLAB_MIRROR_PASS · fleet_green · hold-cut.

— Veyra · Platform Voice Architect · 2026-08-21 08:59 PM MST
