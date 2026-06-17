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

Default routes:

- `nova.<target>.direct` for normal direct coordination.
- `nexus.agent.<target>.direct` for durable session-ingress handoffs.
- `session_only` delivery unless Chase asks for visible wake-first delivery.

Never put provider keys, NATS credentials, bearer tokens, database secrets, or
other sensitive values in A2A messages, docs, or local memory.
