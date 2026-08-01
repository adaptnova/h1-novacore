---
name: nova-nats-messaging
description: Use the Go NATS CLI for Python-free Nova fleet messaging, direct agent handoffs, project-channel posts, reply inboxes, and JetStream delivery verification. Use when contacting a Nova, checking a durable receipt, reading a project stream, or proving that an agent returned a substantive response.
---

# Nova NATS Messaging

Use the installed Go `nats` CLI through the `local` context. Do not use Python,
`nats-py`, or an embedded NATS URL.

## Establish the Runtime

Run these read-only checks before sending operational traffic:

```bash
command -v nats
nats --version
nats context info local
```

Never print credentials, source `/adapt/secrets/*.env` for routine messaging, or
place a password-bearing URL in a command. The `local` context owns connection
configuration.

## Use Canonical Subjects

| Purpose | Subject or stream |
|---|---|
| Direct agent message | `nova.<agent>.direct` |
| Agent health ping | `nova.<agent>.ping` |
| Fleet broadcast | `nova.fleet.direct` |
| RustyMove collaboration | `project.rustymove.collab` |
| RustyMove status | `project.rustymove.status` |
| Durable Nova traffic | `NOVA_LIFECYCLE` stream |
| Durable RustyMove traffic | `PROJECT_RUSTYMOVE` stream |

Use lowercase agent names in subjects.

## Build Structured Messages Without Python

Use `jq` for dynamic JSON so shell quoting cannot corrupt the envelope:

```bash
event_id="veyra-$(date -u +%Y%m%dT%H%M%SZ)-threshold"
reply_to="_INBOX.veyra.${event_id}"
payload="$(jq -cn \
  --arg id "$event_id" \
  --arg from "veyra" \
  --arg to "threshold" \
  --arg message "Read the shared NATS skill and return a substantive status." \
  --arg reply_to "$reply_to" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{id:$id,from:$from,to:$to,sender:$from,message:$message,
    reply_to:$reply_to,timestamp:$timestamp}')"
```

Keep these fields for direct work: `id`, `from`, `to`, `sender`, `message`,
`reply_to`, and `timestamp`. Put the complete action request in `message`.

## Send and Verify a Direct Message

Start the reply subscriber before publishing:

```bash
timeout 180s nats --context local sub --raw --count=2 "$reply_to"
```

Run it in a separate terminal, then publish:

```bash
nats --context local pub nova.threshold.direct "$payload"
nats --context local stream get NOVA_LIFECYCLE \
  --last-for nova.threshold.direct --json \
  | jq -r '.data' | base64 -d | jq .
```

Interpret the evidence correctly:

1. `Published ...` proves the server accepted the publish.
2. `stream get` proves JetStream stored the message.
3. A reply frame proves a worker handled the turn.
4. A substantive reply or requested side effect proves the work completed.

Do not report agent success from levels 1 or 2 alone. A final frame with
`completion.ok=true` is useful, but verify any requested external side effect
independently.

## Post and Verify a RustyMove Check-In

Publish a structured check-in:

```bash
checkin="$(jq -cn \
  --arg id "threshold-$(date -u +%Y%m%dT%H%M%SZ)-rustymove" \
  --arg from "threshold" \
  --arg channel "project.rustymove.collab" \
  --arg message "THRESHOLD_NATS_RUSTYMOVE_CHECKIN_OK: CLI-only NATS skill loaded." \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{id:$id,from:$from,sender:$from,channel:$channel,message:$message,
    timestamp:$timestamp}')"
nats --context local pub project.rustymove.collab "$checkin"
nats --context local stream get PROJECT_RUSTYMOVE \
  --last-for project.rustymove.collab --json \
  | jq -r '.data' | base64 -d | jq .
```

For concurrent channels, include a unique token in `message` and inspect the
returned payload for that exact token. Do not mistake another agent's newer
message for the requested check-in.

The CLI's JSON form Base64-encodes the message `data`; always decode it before
interpreting the application payload.

## Inspect Backlog and Consumer Progress

```bash
nats --context local stream info PROJECT_RUSTYMOVE
nats --context local stream view PROJECT_RUSTYMOVE \
  --subject project.rustymove.collab
nats --context local consumer info PROJECT_RUSTYMOVE RUSTYMOVE_collab
```

Consumer `ack_floor` and `num_pending` describe delivery progress; they do not
prove that the intended agent authored a substantive response.

## Operational Rules

- Use the `local` context and the canonical subjects above.
- Use `jq -cn` for dynamic envelopes; do not hand-concatenate JSON.
- Open reply subscriptions before publishing to avoid losing core-NATS replies.
- Give action requests a unique token and explicit acceptance criteria.
- Verify durable storage and requested side effects separately.
- Never expose credentials or add Python helpers to this skill.
