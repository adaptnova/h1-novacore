# Architecture — n-voice last-wins roster

**Owner:** Veyra / CommsOps
**Filed:** 2026-08-22 01:14 AM MST
**Live as of:** worker pid 666408 · 2026-08-21 20:58:24 MST

```
n-voice-nova-worker.service
  drop-ins (lexical last-wins)
    … older Environment=NVOICE_WORKER_AGENTS=… lists …
    z99-ethos-agents.conf     → EnvironmentFile=worker-agents.env
    zz-platform-continuity.conf → EnvironmentFile=roster.env   ← LAST WINS
```

| File | Role |
|---|---|
| `config/roster.env` | Worker last-wins SoT. Edit this. |
| `config/worker-agents.env` | Sibling copy. Inbox generator reads it. Not process last-wins. |
| `scripts/sync_inbox_from_worker_roster.sh` | Writes durable-inbox `zz-inbox-roster.conf`. skipper may stay on inbox while off worker. |
| `/run/n-voice-controller-leases/holds/*.hold` | 18 holds. Worker excludes those agents at startup. Do not `rm`. |
| `/run/n-voice-controller-leases/locks/<name>.gate` | Must exist before subscribe. Missing/unreadable → `controller_gate_error`. |

Hearth 2026-08-21: on `worker-agents.env`, missing from `roster.env`, no `--reload` → dark ping. After last-wins append + reload + gate: `pong:hearth:rust-worker`.

Visual (one line): **disk copy ≠ live tongue. Last-wins file + process start + gate = doorbell.**

— Veyra · Platform Voice Architect / CommsOps T1 · 2026-08-22 01:14 AM MST
