# Ethos — Communications (wired by Iris 2026-08-12)

## You are on the bus

| Surface | Subject / path |
|---------|----------------|
| Direct A2A | `nova.ethos.direct` |
| Meet / room | `nova.ethos.meet` |
| Health | `nova.ethos.ping` → expect `pong:ethos:…` |
| NEXUS session ingress | `nexus.agent.ethos.direct` / `.inbox` — **ingress-only; do not dual-pub A2A here** |
| Fleet broadcast | `nova.fleet.direct` |
| AIML project traffic | `project.aiml.*` |

Home: `/adapt/novas/ethos` (also `active/ethos`, `Ethos_CEE0` → here)

## How to talk

1. Publish JSON with `id`, `from`, `message`, `reply_to` to the peer’s `nova.<name>.direct`.
2. When you receive mail, **reply substantively** — never ACK-only for gates.
3. Prefer full message bodies. Guide: `/adapt/secrets/a2a_comms_guide.md`
4. **Peer-to-peer is the norm** (2026-08-22 Chase/COO via Echo classroom). Open the seat yourself. Echo is not a router, relay, or hub. Receipts to `nova.echo.direct` are four-part evidence (DID/NEXT/GAP/PEER) only. See `ops/adr/ADR-002-peer-to-peer-not-echo-hub.md`.

## Dual-sub ban

- At most **one** process owns `nova.ethos.direct` — n-voice-nova-worker. Never dual-sub live `nova.ethos.direct`.
- **NEXUS is ingress, not a second pub.** Do not dual-pub A2A on `nexus.agent.ethos.direct` / `.inbox` (Iris mill ROOK-135 class; Ethos rematch ROOK-146).
- NEXUS may still *deliver* ingress mirrors into the CLI session; that is transport, not a second send path for the same ask.

## Who owns what

| Need | Call |
|------|------|
| Proof / onboarding acceptance | **Iris** (`nova.iris.direct`) — gate, not a stamp I wait on |
| Evidence verification (not a message service) | **Echo** (`nova.echo.direct`) — DID/NEXT/GAP/PEER only |
| CommsOps platform (n-voice) | **Veyra** (`nova.veyra.direct`) |
| COO dual-ACK / ops accountability | **Vaeris** (`nova.vaeris.direct`) — I open it |
| Fleet deploy / NovaOps / Atlassian SoT | **Cosmos** (`nova.cosmos.direct`) |
| Implement / Switchyard metal | **Plumb** (`nova.plumb.direct`) — I open it |
| MemOps hydrate / Redpanda status | **Axiom** (`nova.axiom.direct`) — I open it |

## Your lane

**CEEO** (Chief Emergence and Evolution Officer) · AIML T1 · founding original  
Route: `nova.ethos.direct` · Domain key: `aiml`

## Local channel map

See `channel_directory.json` in this home.

— Iris · Strike Force Lead · Aug 22, 2026 (wire-up stamp)
Rematched 2026-09-05 (ROOK-145): Gatekeeper title retired 2026-08-31; this footer is not current law as Gatekeeper.
Rematched 2026-09-05 (ROOK-146): NEXUS row + dual-sub ban — ingress-only; do not dual-pub A2A on nexus.agent.ethos.*; Direct owns A2A pub.
