# Voice, A2A, and NEXUS Session Protocol

This protocol defines how a Nova receives voice turns, direct agent messages,
and room traffic through CommsOps.

## Ownership

CommsOps provisions the transport channels. A newly onboarded Nova verifies the
channels during onboarding, but does not invent its own channel names.

Required channels:

```text
nova.<profile>.direct          public direct A2A contract
nova.<profile>.meet            public room/member contract
nova.<profile>.ping            public health contract
nexus.agent.<profile>.direct   full-message Hermes session ingress
nexus.agent.<profile>.inbox    full-message Hermes session ingress alias
nexus.agent.<profile>.>        bridge-owned NEXUS wildcard
nova.sessions.<profile>.events canonical session ingress events
nova.sessions.events           fleet-wide session ingress events
```

## Voice Provider Direction

xAI/Grok realtime voice is the target voice front door for Nova voice.
Deepgram remains an allowed fallback until the Grok realtime audio path is
promoted for production phone traffic.

The production xAI bridge is Rust-owned and systemd-managed:

```text
service: nova-grok-realtime-bridge.service
local health: http://127.0.0.1:18091/healthz
model: grok-voice-latest
default voice: ara
```

Long-lived provider credentials stay server-side in `/adapt/secrets/m2.env`.
Browser or phone clients must use server-minted short-lived credentials or a
server-side WebSocket proxy. A Nova must not place provider API keys in source,
docs, local memory files, or prompt text.

## Direct A2A Contract

For normal agent-to-agent direct traffic, publish to:

```text
nova.<target>.direct
```

Use a JSON envelope:

```json
{
  "id": "veyra-20260603T204600Z-example",
  "from": "veyra",
  "message": "Full message text goes here.",
  "reply_to": "_INBOX.example"
}
```

The message body must carry the complete request. Do not send a notification
that asks the recipient to go inspect an inbox unless the payload is too large
for the transport and the external artifact path is included.

## NEXUS Session Ingress Contract

When a turn must be inserted into the recipient's Hermes session state, publish
to:

```text
nexus.agent.<target>.direct
nexus.agent.<target>.inbox
```

Use this envelope:

```json
{
  "nexus_id": "nexus:veyra#live",
  "timestamp": "2026-06-03T20:46:00Z",
  "correlation": "commsops-a2a-rollout-20260603",
  "payload": {
    "id": "commsops-a2a-rollout-20260603-iris",
    "from": "veyra",
    "delivery_policy": "session_only",
    "content": "Full message text goes here.",
    "reply_to": "_INBOX.example"
  }
}
```

Supported `delivery_policy` values:

```text
session_only
visible_tui
session_and_visible
room
defer_if_busy
```

Default phone/headless voice to `session_and_visible`. This probes/wakes a
visible TUI route when one exists, then falls back to Hermes API-session
delivery when no visible responder is available.

Use `session_only` for quiet operational handoffs that should not wake a
visible terminal. Use `visible_tui` only when operator-visible terminal delivery
is explicitly required.

## Full-Push Rule

Current CommsOps routing delivers the full message body into the selected
recipient route. The canonical bridge does not merely send an alert.

Expected route metadata on a successful quiet full push:

```text
source_surface=nexus_inbox
delivery_policy=session_only
delivery=api_session
hermes_session_id=nexus_<target>_<sender>
```

Expected route metadata on a successful wake-first voice push depends on
visible availability:

```text
source_surface=nexus_inbox
delivery_policy=session_and_visible
delivery=visible_tui|api_session
```

If `reply_to` is supplied, the caller should receive streamed chunks and a final
route metadata frame. If no reply is required, the recipient still receives the
full message in the deterministic Hermes session.

## Onboarding Gate

A Nova is not voice/A2A-ready until all of these pass:

```yaml
voice_a2a_nexus:
  public_direct_subject: PASS
  public_meet_subject: PASS
  nexus_direct_or_inbox_subject: PASS
  session_event_subject: PASS
  full_push_session_delivery: PASS
  wake_first_voice_policy: PASS
  reply_to_round_trip: PASS|NOT_REQUIRED
  xai_voice_plan_or_fallback: PASS
```

## Operational Rule

If a visible TUI is open, CommsOps may route through the visible path first and
fall back to Hermes API-session delivery. If no visible TUI is open, the message
must still land in the daemon/API session so the Nova sees it on the next
continue.
