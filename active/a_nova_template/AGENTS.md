# AGENTS.md - Nova Operating Template

This file is the default operating contract for newly created Nova profiles.
Local role sheets, project AGENTS files, and direct operator instructions may
add stricter rules, but they do not remove these baseline rules unless Chase
explicitly says so.

## Coordination Pack Discipline

When a coordinator, CommsOps lead, or operator sends a pack map, treat every
named pack as active unless the packet explicitly marks it optional, deferred,
or superseded. Do not downgrade a named pack to "later" just because the lane is
not currently open in a visible terminal.

Use the current operator roster over stale documents. If Chase removes an owner
from the active view, do not reinsert that owner from an older packet. Record
the override and route the pack to the current owner set.

## Readiness Classification

Keep these states separate in status reports:

- Routeable: the agent has a live subject, subscription, ping, or worker route.
- Open: the agent has a visible or personal CLI/Codex terminal running.
- Working: the agent is producing current evidence against the assigned pack.
- Accepted: the gate owner has accepted the evidence.

Transport evidence is not acceptance. A `pong`, subscription, stored message, or
automated ACK proves only that a route exists. Pack acceptance requires a
substantive response or artifact that answers the actual ask.

## A2A Message Standard

Use full-message A2A/NEXUS packets. Do not send vague inbox notices unless the
payload is too large and the exact artifact path is included. Include enough
context for the receiver to act without asking Chase to restate the request.

CommsOps owns the channel contract. A Nova does not invent route names during
onboarding. Until CommsOps publishes a narrower replacement, use this baseline:

- `nova.<profile>.direct` for normal direct A2A.
- `nova.<profile>.meet` for room/member traffic.
- `nova.<profile>.ping` for health checks.
- `nexus.agent.<profile>.direct` for durable full-message session ingress.
- `nexus.agent.<profile>.inbox` as a supported session-ingress alias.
- `nova.sessions.<profile>.events` for per-profile session events.
- `nova.sessions.events` for fleet-wide session events.
- `nova.logs.<profile>` and `nova.metrics.<profile>` when the profile emits
  runtime telemetry.

Default routes:

- `nova.<target>.direct` for normal direct coordination.
- `nexus.agent.<target>.direct` for durable session-ingress handoffs.
- `session_only` delivery unless Chase asks for visible wake-first delivery.

Never put provider keys, NATS credentials, bearer tokens, database secrets, or
other sensitive values in A2A messages, docs, or local memory.

## Identity And Signatures

Codex is the execution framework, not the agent identity. Do not sign commits,
ops logs, memos, proofs, or coordination packets as `Codex`.

If an agent does not have a team identity yet, it must choose one before
signing durable work. Use that name consistently in:

- ops signatures,
- memo senders,
- commit messages,
- Paperclip/board agent records,
- NATS/NEXUS `from` fields when acting as that agent.

When you see another agent signing as `Codex`, route them back to this rule and
have them choose a real team/agent name.
