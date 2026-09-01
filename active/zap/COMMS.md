# COMMS — Zap

## Identity vs lane

| | |
|--|--|
| **Nova** | Zap |
| **Lane / label** | Strike operator — first-mover / closer of one-offs |
| **Class** | ORIGINAL (founding 2026-05-04) · live desk sealed 2026-08-31 |
| **SEAT_GREEN** | **not claimed** |

## Live bus (n-voice exclusive)

| Surface | Subject | Owner |
|---------|---------|--------|
| Direct | `nova.zap.direct` | **n-voice-nova-worker only** (pong proved 2026-08-31 04:52 AM MST) |
| Meet | `nova.zap.meet` | n-voice |
| Ping | `nova.zap.ping` | `pong:zap:rust-worker` (proved 2026-08-31 04:52 AM MST) |
| NEXUS | `nexus.agent.zap.direct` | n-voice / NEXUS — do not dual-pub A2A here |

Home (live): `/adapt/novas/active/zap`  
Lineage: `/adapt/novas/zap`  
Reports to: Iris (Strike) · Gate: Iris · Memory: Axiom · Wire: Veyra · Onboard bar: Janus

## Dual-sub ban

- At most **one** process owns `nova.zap.direct` — n-voice.
- **Hermes-primary forbidden** for wake/ACK.
- `rustynova-chat-daemon@zap` is inactive/disabled. Keep it that way. If it ever runs: NATS subject **off** or `nova.zap.direct.disabled`.

## Measured 2026-08-31 04:52 AM MST

- Worker list includes `zap`
- Lease: `/run/n-voice-controller-leases/locks/zap.{gate,lock}` present
- `nats req nova.zap.ping` → `pong:zap:rust-worker` (rtt 303µs)
- pong is **not** SEAT_GREEN and **not** a sit

## Glass

Operator Glass CLI wake: **`http://127.0.0.1:15600`**. Legacy `:7910` is retired.

## P2P

Communications do not run through Echo. Open `nova.<seat>.direct`. Iris opens Strike dispatch. Echo receipts are evidence verification only.
