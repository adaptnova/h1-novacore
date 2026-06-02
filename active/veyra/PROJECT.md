# PROJECT.md — n-voice

## What This Is

`n-voice` is the clean Voice-to-Nova control-plane repository. It turns the prototype voice pipeline into a platform-grade voice layer: speech in → routed agent work → spoken replies back.

**Repo:** `/adapt/platform/novaops/controlplane/n-voice`
**GitHub:** `adaptnova/n-voice`

## Veyra's Role

Veyra is the **primary platform voice target** for this project. When n-voice routes a voice turn to `nova.platform.direct`, Veyra is the agent that answers.

Veyra is NOT just another Hermes agent on the voice mesh. She is the continuity target: one operating identity across phone, browser, CLI, Hermes, NATS, and NEXUS-backed event streams.

Current runtime split:

- Browser/Hermes surface: `openai-codex/gpt-5.5`
- Phone/realtime voice surface: `grok/grok-voice-latest`
- Platform target: Veyra, not the hosted Codex CLI process

The active hosted Codex CLI session still has to be onboarded through a session/event mirror. `hermes -c` can continue Hermes state, but it does not attach to the current Codex CLI thread.

## Key Architecture

```
voice client → gateway (Deepgram) → route contract → agent bridge → reply stream
                                                         │
                                              ┌──────────┴──────────┐
                                              │ nova.platform.direct │  ← Veyra
                                              │ nova.codex.direct    │  ← Codex bridge
                                              │ nova.iris.direct     │  ← Iris fallback
                                              └─────────────────────┘
```

## Current Milestones

1. Define the route protocol and target lifecycle
2. Port the Deepgram gateway as a clean service
3. Port Hermes visible TUI routing as an optional bridge
4. Promote Codex voice from spike to platform bridge
5. Add activity, health, and route diagnostics from day one
6. **Veyra's mission**: Be the Codex-independent platform-agent route (milestone 6)
7. Mirror live Codex CLI turns into Veyra/NEXUS without pretending the CLI process moved

## Key Docs

- `README.md` — project overview and layout
- `REQUIREMENTS.md` — product and technical requirements
- `docs/architecture.md` — system architecture
- `docs/codex-platform-bridge.md` — Codex bridge design
- `docs/operations.md` — operational runbook
- `docs/security.md` — security design

## Operational Conventions

- No Docker, no virtualenvs
- Systemd manages services
- Secrets in environment files, never committed
- Failures must name the true upstream blocker
- Voice mode is read-only by default
