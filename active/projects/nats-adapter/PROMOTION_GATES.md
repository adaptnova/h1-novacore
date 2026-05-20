# Hermes NATS Adapter Promotion Gates

## 2026-05-19 — SIGNED_BY_AGENT

The Rust adapter remains an isolated transport candidate. It must not own live
fleet subjects until all promotion gates below pass and a later task explicitly
approves the ownership change.

## Current Scaffold

- Crate: `/adapt/novas/active/projects/nats-adapter`
- Type surface: `AdapterConfig`, `NovaEnvelope`, `NatsAdapter`, `AdapterError`
- Supported primitives: derived subjects, JSON envelope publish, text publish,
  subscribe, request/reply JSON, timeout handling
- Existing live owners:
  - `nova.echo.direct`: `echo-tui-nats-bridge.service`
  - `nova.skipper.direct`: `skipper-tui-nats-bridge.service`

## Required Promotion Gates

1. Correlation ID: every request must carry a stable `NovaEnvelope.id`, and the
   reply must echo the same ID.
2. Reply inbox: every live-owner candidate must support NATS request/reply or an
   explicit `reply_to` field without losing final response capture.
3. Logs: every handled request must emit a structured log on a non-secret
   `nova.logs.<name>` subject.
4. Duplicate-owner prevention: proof subjects must be isolated until promotion;
   no adapter process may subscribe to `nova.echo.direct` or
   `nova.skipper.direct` during this gate.
5. Rollback: if duplicate ownership appears, stop the adapter proof process and
   restart the current TUI bridge owner for the affected subject.
6. Timeout behavior: request paths must fail closed with bounded timeouts rather
   than leaving orphan waits.
7. Secret handling: runtime NATS credentials come from environment variables;
   no secrets are logged or committed.

## Isolated Proof

Run from the crate directory:

```bash
set -a
. /adapt/secrets/db.env
set +a
cargo run --example isolated_proof
```

Default proof subjects:

- Direct proof: `nova.adapter-proof.direct`
- Log proof: `nova.logs.adapter-proof`

Expected output:

```text
proof id=<id> status=ok route=isolated-adapter-proof subject=nova.adapter-proof.direct log_subject=nova.logs.adapter-proof
```

## Go/No-Go

Current decision: no-go for live subject ownership.

Reason: the Rust adapter can prove typed isolated request/reply and logs, but it
does not yet execute a Hermes visible CLI turn or replace the existing
answer-capturing TUI bridges. Promotion to a live owner requires a later task
that proves visible-session delivery, final answer capture, and duplicate-owner
protection against the current bridge services.
