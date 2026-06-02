# 04 — Session Backfill + Mirror Continuity

Backfill and live mirroring are separate from realtime Hermes hooks.

## Historical backfill

Use when importing old Codex/Hermes/Claude/etc. sessions into a Nova.

1. Copy raw session file into `history/` or `memory/l0/intake/sessions/`.
2. Preserve source metadata: provider, model, cwd, original session id, import timestamp.
3. Distill durable facts into `MEMORY.md` and/or L2 domain context.
4. Optionally fan out through `scripts/memfirst_ingest.py` or a batch importer, but tag as historical.
5. Do not pretend historical replay is a live current turn.

## Codex/Veyra-style live mirror

Use when preserving continuity with a live Codex CLI session without claiming process transfer.

Minimum metadata:

```json
{
  "schema": "nova.session_mirror.v1",
  "agent_identity": "<nova>",
  "turn_event_id": "turn_...",
  "codex_session_id": "codex_...",
  "hermes_session_id": "hermes_...",
  "surface": "codex_cli",
  "provider": "openai-codex",
  "model": "gpt-5.5",
  "role": "user|assistant|system|tool",
  "created_at": "ISO-8601"
}
```

Allowed mirror modes:

- `observed`: record only; first proof mode.
- `replicated`: append corresponding message into target Hermes API/session after deterministic target id is proven.
- `routed`: deliberately route next turn through another runtime; requires route owner and rollback path.

## Non-goals

- Do not copy provider secrets into events.
- Do not collapse surfaces into one model label.
- Do not claim Codex moved into Hermes.
- Do not let voice audio block durable local JSONL writes.
