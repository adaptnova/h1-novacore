# Nova Bootstrap

Rust CLI for creating, validating, and auditing Adapt Nova profiles.

## Purpose

`nova-bootstrap` creates the filesystem profile, Hermes profile symlink,
baseline memories, config, identity files, and NATS metadata needed for a new
Nova agent. It is the starting point for PEA-driven fleet bootstrap work.

## System Requirements

- Rust toolchain with `cargo`
- System-level execution only
- Existing Adapt paths:
  - `/adapt/novas/active`
  - `/home/x/.hermes/profiles`
  - `/adapt/secrets/m2.env`
  - `/adapt/secrets/db.env`

This project does not use Docker and does not use Python virtual environments.

## Build

```bash
cargo fmt --check
cargo clippy -- -D warnings
cargo test
cargo build --release
```

## Create A Nova

```bash
./target/release/nova --name PEA-Test
```

The generated profile includes:

- `.env` with dotenv-safe pointers to shared model and infrastructure secret files
- `.nova/` identity metadata
- `AGENTS.md`
- `config.yaml`
- `memories/SOUL.md`
- `memories/USER.md`
- `memories/memory.mdl`
- `memories/user.mdl`

No API keys or infrastructure passwords are written directly into generated
profiles.

Launch wrappers or systemd units are responsible for loading
`/adapt/secrets/m2.env` and `/adapt/secrets/db.env` before starting Hermes.

## Validate A Nova

```bash
./target/release/nova --validate PEA-Test
```

## Audit

```bash
./target/release/nova --audit-all
./target/release/nova --paperclip-audit
```

## Paperclip Company Creation

```bash
./target/release/nova \
  --create-company "Example Company" \
  --company-description "Created by nova-bootstrap"
```

## Operational Model

The bootstrap flow is designed for the Adapt task system:

```text
ops/to_do -> ops/in_progress -> ops/completed
```

Meaningful operational changes should be logged in the control-plane ops logs
with timestamped, reverse-chronological entries signed by the acting agent.
