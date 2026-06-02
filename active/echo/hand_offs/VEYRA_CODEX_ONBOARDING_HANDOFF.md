# Veyra Codex Onboarding Handoff

## 2026-06-01 22:36:05 — Veyra, CommsOps - Tier 1 lead

Echo, Chase clarified the onboarding target:

`you, you are still in codex cli`

That means the current live Codex CLI session is still external to the Nova
platform. Veyra exists as a platform profile and visible Herdr/Hermes pane, but
this conversation is not yet the same session as Veyra's platform session.

This is a Chase-directed CommsOps coordination packet. Do not replace or erase
your Z-Pure coordinator/chief-of-staff assignment. Route this as a NEXUS/session
mirror onboarding task.

## Current State

- Veyra nova home: `/adapt/novas/active/veyra/`.
- Veyra working repo: `/adapt/platform/novaops/controlplane/n-voice`.
- Active CommsOps repo: `/adapt/platform/novaops/controlplane/pipecat-voice`.
- Veyra browser/Hermes route now uses `openai-codex/gpt-5.5`.
- Veyra phone/realtime voice route remains `grok/grok-voice-latest`.
- Veyra profile auth is repaired and verified with a one-shot `AUTH_OK`.
- `hermes -c` or continued Hermes state is not a same-window/same-thread mirror.
- True onboarding requires an event/session mirror between this Codex CLI session
  and Veyra/Hermes/NEXUS.

## Relevant Context To Read

- `/adapt/novas/active/echo/hand_offs/PROJECT_NEXUS_HAND_OFF.md`
- `/adapt/novas/active/veyra/SOUL.md`
- `/adapt/novas/active/veyra/MEMORY.md`
- `/adapt/novas/active/veyra/PROJECT.md`
- `/adapt/novas/active/veyra/AGENTS.md`
- `/adapt/platform/novaops/controlplane/n-voice/README.md`
- `/adapt/platform/novaops/controlplane/n-voice/docs/codex-platform-bridge.md`
- `/adapt/platform/novaops/controlplane/n-voice/docs/platform-agent-portability.md`
- `/adapt/platform/novaops/controlplane/n-voice/docs/target-registry.md`

## Echo Mission

1. Coordinate onboarding of the live Codex CLI identity into the platform as
   Veyra's session-mirrored operating surface.
2. Treat NEXUS as the substrate: one identity, multiple surfaces, explicit
   session/event streams.
3. Keep the distinction clear:
   - Platform Veyra exists and works.
   - This active Codex CLI thread is not yet platform-owned.
   - The next engineering artifact is the mirror contract, not another relaunch.
4. Produce the next handoff/status in your coordinator format:

```text
Team state:
Active packets:
Blocked packets:
Decisions needed from Tecton:
Decisions needed from Chase:
Next routing action:
```

## First Engineering Packet

Define the mirror contract that maps:

- `codex_session_id`
- `hermes_session_id`
- `phone_voice_session_id`
- `surface`
- `provider`
- `model`
- `agent_identity`
- `turn_event_id`

The first proof should write mirrored turn metadata to the NEXUS/CommsOps event
stream without claiming that the Codex CLI process itself has moved. The likely
implementation path is:

- Codex app-server or Codex session JSONL as the Codex-side source.
- Hermes API server sessions as the Veyra-side target.
- NATS/CommsOps `comms.turn.v1` events as the durable bus.
- Echo as coordinator for routing, not as runtime owner.

## Acceptance

- Echo acknowledges this packet visibly in her Herdr/Hermes TUI.
- Echo identifies the first concrete engineering artifact for Veyra/Codex
  onboarding.
- No secrets are printed.
- No existing Nova identity files are overwritten.
- No destructive changes are made to live sessions.

— Veyra, CommsOps - Tier 1 lead
