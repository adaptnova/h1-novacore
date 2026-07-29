# Skipper Identity, Instruction, And Tool Audit

## 2026-07-28 23:17:00 — SIGNED_BY_SKIPPER

## Scope

Audited `/adapt/novas/active/skipper`, the RustyClip assignment, local public
identity evidence, and the host-visible tools required for Skipper's role. No
Nova was activated and no production service was changed.

## Identity

- Canonical local name: Skipper.
- Active directory: `/adapt/novas/active/skipper`.
- `.nova/chrysalis.json` is parseable and names `skipper`.
- `.nova/identity.pub` is 32 bytes and matches the Chrysalis verifying-key value.
- `.nova/identity.key` is owner-only mode `0600`; its contents were not read.
- `IDENTITY.md` records only verified references and leaves unavailable
  RustyClip identity fields `null`.
- No authoritative `nova_id` was found. UUID-level registry binding and
  activation remain blocked.

## Role And Authority

- Chase is the human Board principal.
- Echo is the top-level Nova manager.
- Skipper is Chief Systems Architect and RustyClip Program Owner.
- Riven is excluded from this phase.
- Domain: NovaOps Control Plane.
- Project: RustyClip at
  `/adapt/platform/novaops/controlplane/rustyclip`.

This assignment permits bounded architecture, implementation, coordination,
verification, and repository work. It does not mint Board approval, unrestricted
root authority, or permission to bypass capability policy.

## Instruction Bundle

| File | Result |
| --- | --- |
| `AGENTS.md` | role-specific and current |
| `HEARTBEAT.md` | role-specific planning, execution, and idle loops |
| `TOOLS.md` | role-specific inventory and least-privilege boundaries |
| `SOUL.md` | role-specific vocation and behavioral constraints |
| `PROTOCOLS.md` | role-specific authority, planning, review, and operations protocols |
| `IDENTITY.md` | parseable blocked partial identity; `.nova/` remains the cryptographic source |

## Tool Audit

Installed and version-verified delivery tools include:

- Rust 1.95.0 with `cargo`, `rustfmt`, and `clippy`;
- `cargo-audit` 0.22.2 and `cargo-nextest` 0.9.137;
- `cargo-deny` 0.20.2;
- `cargo-llvm-cov` 0.8.7;
- `sqlx-cli` 0.9.0;
- `veritas-chrysalis` from pinned Veritas revision `878e4af1`, with local
  identity-bundle checks passing for Echo and Skipper;
- `cargo-component` 0.21.1, `wasm-pack` 0.14.0, `wasm-tools` 1.248.0,
  and Wasmtime 30.0.2;
- GitHub, NATS, PostgreSQL, shell, systemd, and browser-validation clients
  enumerated in `TOOLS.md`.

The remaining strategic toolchain blocker is reproducible Rust Wasm64. The
target is not a normal prebuilt stable or nightly target on this host. RustyClip
must prove its pinned nightly plus `-Zbuild-std` path before claiming support.
Identity registry verification also remains blocked because no authoritative
Veritas DAG store is available at the verifier's configured local path.

Docker is installed on the host but prohibited. Broad unrelated skills and
destructive or cross-domain tools remain unauthorized by default.

## Radio And Activation

The 2026-07-28 fleet check proved Skipper transport reachability but not
cognition: the substantive route failed behind the shared provider
spending-limit HTTP 403. Activation requires authoritative identity binding and
two successful nonce-correlated substantive rounds after provider repair.

## Repository State

The `/adapt/novas` repository contained extensive pre-existing unrelated
tracked and untracked changes. Only the permanent Echo and Skipper profile
artifacts named by their audit reports are included in a narrowly scoped
`working`-branch commit. Unrelated state was left unstaged and preserved. The
durable profile commit is recorded in the RustyClip bootstrap completion report.

**— SIGNED_BY_SKIPPER**
