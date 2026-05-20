# Hermes NATS Adapter

Typed Rust adapter primitives for Hermes-backed Nova agents on the existing
Adapt local NATS bus.

## Scope

- Derive standard nova subjects from an agent name.
- Serialize and publish structured Nova envelopes.
- Subscribe to direct, meet, ping, log, and custom subjects.
- Perform request/reply calls with a bounded timeout.
- Keep secrets outside source by accepting credentials through runtime config.

## Local Bus

The active fleet bus is already running locally. Use the existing environment
instead of starting Docker:

```bash
set -a
. /adapt/secrets/db.env
set +a
```

## Build And Test

```bash
cargo fmt --check
cargo clippy -- -D warnings
cargo test
```

## Example

```rust
use hermes_nats_adapter::{AdapterConfig, NatsAdapter, NovaEnvelope};

# async fn example() -> hermes_nats_adapter::Result<()> {
let config = AdapterConfig::new("nats://localhost:18020", "echo");
let adapter = NatsAdapter::connect(config.clone()).await?;
let envelope = NovaEnvelope::direct("latch", "hello").with_target("echo");

adapter
    .publish_envelope(config.direct_subject(), &envelope)
    .await?;
# Ok(())
# }
```

## Status

The crate currently provides the reusable transport layer. Agent-specific CLI
bridging and Hermes turn execution stay in the Pipecat voice control plane until
the Rust bridge promotion gates pass.
