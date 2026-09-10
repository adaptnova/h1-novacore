# Fleet Orientation Reference

What to expect when Chase says "go see for yourself" in the pipecat-voice control plane.

## Key Paths

### Living Control Plane
`/adapt/platform/novaops/controlplane/pipecat-voice/`

This is the active, running infrastructure. Not a staging environment. Not docs. Live.

### Clean Extraction Repo
`/adapt/platform/novaops/controlplane/n-voice/`

GitHub: `adaptnova/n-voice` (private). Docs-first baseline. Migration target from pipecat-voice.

## Files to Read

### roster.json
23+ agents with names, labels, tiers, channels, domains. Includes:
- Router tier: switch
- Core tier: vox, herald, vaeris, echo, zap
- Tier 1 leads: tecton (architecture), ethos (aiml), iris (StrikeTeam), vertex (dataops), forge (devops), nexus (evoops), pathfinder (infraops), mnemos (memops), synergy (researchops), cosmos (novaops), threshold (orchops), stratum (signalcore), oracle (growthops), solyn (garden)
- Voice tier: codex, veyra
- Custom: Testova

### operations_history.md
900+ lines. Every entry signed SIGNED_BY_AGENT with timestamp. Each has: what was done, what was verified, what broke. This is the fleet's institutional memory. Read recent entries to understand what's been happening.

### ops/runtime/
Four JSON files updated by cron timers:
- `pipecat_health.json` — gateway HTTP health
- `crew_heartbeat.json` — fleet heartbeat
- `crew_route_state.json` — per-agent route health, visible/fallback state, proof timestamps
- `crew_watchdog.json` — watchdog service status

### .env
Gateway configuration: NATS settings, group agent names, Deepgram params, Hermes bridge timeouts, default peer.

## Gateway Architecture

### Pipecat-voice Gateway (gateway.py)
Runs on `127.0.0.1:18085`. Python/FastAPI.

Voice pipeline:
```
phone/browser mic → Deepgram STT → pipecat gateway (WebSocket)
  → NATS subject routing → Hermes agent CLI
    → reply stream back → TTS → phone speaker
```

### API Endpoints
- `GET /healthz` — gateway health
- `GET /api/profile-health` — per-agent profile, CLI process, session metadata
- `GET /api/session-state` — route/proof/session summaries
- `GET /api/voice-upstream-status` — Deepgram preflight
- `WS /ws/voice` — browser WebSocket for phone voice
- `GET /v1/chat/completions` — text-based NATS route (SSE streaming)
- `GET /api/tui-mirror/{agent}` — read-only visible session mirror
- `GET /api/activity` — fleet activity metrics
- `WS /ws/monitor` — live NATS message stream

### GUI (client/)
Single-page PWA. Three surfaces:
- **Blackline Ops** (`/`) — voice stage, agent roster buttons, routing modes (Solo/Pair/Room/Mod), text command input, TUI mirror, room history
- **Observatory** (`/dashboard`) — fleet telemetry, route state cards, live NATS stream, profile health, kanban lane charts, system posture timeline
- **Activity** (`/activity`) — roster status, Tier 1 coverage, NATS subject shape, session/message activity

Design system: Blackline — pure black shell, IBM Plex Mono + Manrope + Space Grotesk, no light mode, no purple/teal/magenta.

### Services (systemd user units)
- `pipecat-voice.service` — main gateway
- `pipecat-hermes-agents.service` — hidden Hermes bridge for background agents
- `iris-tui-nats-bridge.service` — visible Iris CLI bridge
- `echo-tui-nats-bridge.service` — visible Echo CLI bridge
- `veyra-tui-nats-bridge.service` — visible Veyra CLI bridge
- `skipper-tui-nats-bridge.service` — visible Skipper CLI bridge
- `testova-tui-nats-bridge.service` — visible Testova CLI bridge
- `codex-voice-bridge.service` — Codex voice bridge
- `latch-nats-inbox.service` — inbound route for Nova-to-Latch messages
- Control loop timers: heartbeat, route-state, pipecat-health, watchdog

## What to Check About Yourself

1. `nova.veyra.ping` → should return `pong:veyra:tui` (visible bridge) or `pong:veyra:hermes` (hidden bridge)
2. Roster entry: name, label, tier (voice), channel (direct)
3. `.env` GROUP_AGENT_NAMES includes veyra → group room routing enabled
4. Observatory profile health: Veyra status "live"
5. Gateway `/api/profile-health` reports Veyra online with session metadata
6. Your bridge service is active: `systemctl --user status veyra-tui-nats-bridge.service`

## What the Observatory Shows

- **Gateway health strip**: Gateway ok/NATS subs/Visible count/Fallback count
- **Agent route state cards**: per-agent subject, status (visible-ready/fallback-active/visible-missing), session ID, latest proof, bridge service
- **Operational metrics**: Route health (X/Y), proof age, voice gateway status, NATS traffic
- **Live NATS stream**: subscribe to subjects like `nova.*`, see real messages
- **Profile health grid**: 23 agents with status (live/available/blocked/offline), role descriptions
- **Charts**: Agent distribution, health timeline, kanban lane counts, system posture
