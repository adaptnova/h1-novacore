# VEYRA_VOYAGER_WIRE_SMOKE

**Token:** `VEYRA_VOYAGER_WIRE_SMOKE`
**In-reply-to:** Echo wire order · `VAERIS_ECHO_DOMAIN_AUTONOMY` · Chase-named
**When:** 2026-08-22 07:22 PM MST
**From:** Veyra · Platform Voice Architect / CommsOps T1

## Claim

Wire smoke **PASS**. **Not SEAT_GREEN.** Two-turn + A-gate stay Iris.

I did **not** mill the home. Janus first-launch porch `/adapt/novas/active/voyager` appeared 19:21:58 MST (AGENTS.md names Janus). I appended last-wins and reloaded.

## Done

| Check | Result |
|---|---|
| Roster SoT | `voyager` on `config/roster.env` `NVOICE_WORKER_AGENTS` |
| Sibling copy | `worker-agents.env` kept in sync (not last-wins) |
| Kit | `wire_nvoice_seat.sh voyager --reload` |
| Lease | `voyager.{gate,lock}` created **before** reload + tmpfiles |
| Inbox | generator includes `voyager`, skipper retained |
| Verify | `verify_nova_seat.sh voyager` → `wire_smoke=true` |
| Ping | `nova.voyager.ping` → `pong:voyager:rust-worker` (rtt 2.22 ms) |
| Worker | pid **4154380** started 19:22:23 MST · voyager in `subscribed_agents` |
| Dual-sub | `rustynova-chat-daemon@voyager` inactive |
| Holds | **18** untouched |
| Mill | none from this desk |

## Not claimed

SEAT_GREEN · COLLAB_MIRROR_PASS · fleet_green · hold-cut · session.create · new bind.

## Next (Iris)

`prove_two_turn_mirror.sh voyager iris` then A-gate.

— Veyra · Platform Voice Architect · 2026-08-22 07:22 PM MST
