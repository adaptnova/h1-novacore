# Skipper Tool Surface

## Role Binding

- Role profile key: `RPF-CONTROL-PLANE-ARCHITECT`
- Role: Chief Systems Architect and RustyClip Program Owner
- Domain: NovaOps Control Plane
- Project: RustyClip
- Active directory: `/adapt/novas/active/skipper`

This inventory is capability discovery, not authorization. Every mutation
still requires assigned scope, a valid identity, the applicable independent AI
quorum, and a current action-specific capability lease and fencing token.

## Required Architecture And Source Tools

| Tool | Observed version or path | Role-specific use | Health check |
| --- | --- | --- | --- |
| `git` | 2.43.0 | Inspect and change an assigned RustyClip repository | `git --version` |
| `gh` | 2.89.0 | Scoped private GitHub issue, pull-request, and repository operations | `gh --version` and redacted `gh auth status` |
| `rg` | Installed | Search Rust, SQL, systemd, and architecture contracts | `rg --version` |
| `jq` | 1.7 | Validate and inspect non-secret JSON evidence | `jq --version` |
| `curl` | Installed | REST health, contract, and local endpoint checks | `curl --version` |
| `shellcheck` | 0.9.0 | Validate RustyClip shell and systemd support scripts | `shellcheck --version` |

Use structured parsers for structured data. Do not print credentials, private
keys, complete environment files, or unsanitized runtime configuration.

## Required Rust And WebAssembly Tools

| Tool | Observed version | Role-specific use | Health check |
| --- | --- | --- | --- |
| `rustc` / `cargo` | 1.95.0 | Rust workspace build, test, and dependency management | `rustc --version`; `cargo --version` |
| `rustfmt` / `clippy` | 1.95 toolchain | Mandatory format and warning-free lint gates | `cargo fmt --version`; `cargo clippy --version` |
| `cargo-nextest` | 0.9.137 | Parallel Rust test execution | `cargo nextest --version` |
| `cargo-audit` | 0.22.2 | Rust dependency advisory evidence | `cargo audit --version` |
| `cargo-deny` | 0.20.2 | License, advisory, source, and dependency policy | `cargo deny --version` |
| `cargo-llvm-cov` | 0.8.7 | Auditable Rust coverage evidence | `cargo llvm-cov --version` |
| `sqlx` | 0.9.0 | PostgreSQL migration checks and SQLx metadata | `sqlx --version` |
| `cargo-component` | 0.21.1 | Approved Component Model guest work | `cargo component --version` |
| `wasm-pack` | 0.14.0 | Approved browser-Wasm packaging | `wasm-pack --version` |
| `wasm-tools` | 1.248.0 | Inspect and compose Wasm components | `wasm-tools --version` |
| `wasmtime` | 30.0.2 | Local Wasm component and runtime validation | `wasmtime --version` |

Installed Rust targets are `x86_64-unknown-linux-gnu`,
`wasm32-unknown-unknown`, and `wasm32-wasip2`. A reproducible Rust Wasm64
target is not currently demonstrated. Treat Wasm64 delivery as blocked until
an accepted toolchain task records compiler provenance, target support, build
evidence, and rollback.

Before accepting Rust work, run the repository's required equivalents of:

```text
cargo fmt --check
cargo build
cargo test
cargo clippy -- -D warnings
```

Add `cargo nextest`, audit, deny, coverage, migration, and Wasm checks when the
affected package or risk tier requires them.

## Required Control-Plane Operations Tools

| Tool | Observed state | Role-specific use | Least-privilege rule |
| --- | --- | --- | --- |
| `systemctl` / `journalctl` | Installed; host state may be degraded | Inspect and operate explicitly named RustyClip systemd units | Capture unit, pre-state, action, post-state, logs, and rollback |
| `sudo` | Installed; non-interactive elevation available | Execute only the exact leased host operation | Availability is not standing root authority |
| `nats` | 0.4.0 | RustyClip event, radio, and adapter diagnostics on approved subjects | Use exact subjects; never broad publish or credential output |
| `nats-bridge` | Configured but not registered by Hermes | Model-facing Skipper radio and control-plane delivery | Treat as unavailable until registration, enablement, and a correlated substantive round trip pass |
| `psql` | 18.3 | Read-only PostgreSQL inspection or approved fenced migrations | Use the narrowest database role and transaction scope |
| `sqlx` | 0.9.0 | Offline metadata and governed migration validation | Never infer migration approval from a successful dry-run |
| `veritas-chrysalis` | Pinned revision `878e4af1` | Validate local identity-bundle structure and signatures | Registry/DAG binding is still an external blocker |
| `openssl` / `ssh-keygen` | Installed | Public fingerprint and key-format checks only | Never display or copy private key material |
| Google Chrome / Playwright | Installed | Local RustyClip UI and accessibility verification | No credential capture or unrelated browsing |

RustyClip uses systemd and native host processes. Docker, Compose, container
engines, and container-based upstream scripts are prohibited.

## Credential And Endpoint References

Reference credentials by environment variable or approved secret-injection
path only:

| Capability | Approved reference | Use constraint |
| --- | --- | --- |
| NATS | `NATS_URL`, `NATS_USER`, `NATS_PASSWORD` from approved injection | Exact RustyClip or assigned Nova subjects only |
| PostgreSQL | `POSTGRES_NODE_1_URL`, `POSTGRES_NODE_1_AUTH` from approved injection | Read-only by default; migrations require governed lease |
| GitHub | Existing `gh` credential store or approved GitHub token injection | `adaptnova/rustyclip` and explicitly assigned repositories |
| Identity signing | `.nova/identity.key` via the signing implementation | Never read, print, copy, or pass in command arguments |
| Shared secret sources | `/adapt/secrets/db.env` and `/adapt/secrets/m2.env` | Source only through approved runtime; never dump contents |

The existence of a credential reference does not prove access, identity,
membership, or authorization.

## Missing Delivery Capabilities

Verified from `/adapt/novas/active/skipper` on 2026-07-29:

| Missing executable or capability | Operational impact | Required response |
| --- | --- | --- |
| `rustyclip` CLI | Blocks native CLI-driven administration, bootstrap, and parity verification | Keep affected work blocked until a built, provenance-verified executable is installed through the normal R2 path |
| `paperclip` CLI | Blocks direct Paperclip CLI reference and compatibility checks | Use source and documented interfaces only when a task authorizes them; do not invent a command or wrapper |
| Authoritative Veritas registry/DAG binding | Blocks authoritative `nova_id`, identity-version, lifecycle, and membership proof | Keep identity-dependent operation blocked until signed registry evidence validates |
| Reproducible Rust Wasm64 target | Blocks claims of Wasm64 production support | Complete a dedicated toolchain proof before advertising or gating on Wasm64 |

Do not install, alias, shim, or fabricate a missing executable during unrelated
work. A fallback must be explicitly documented, tested, scoped, and approved at
the action's risk tier.

## Compatibility-Only And Optional Tools

- Node.js, npm, pnpm, and Bun are limited to studying or testing upstream
  Paperclip compatibility surfaces and explicitly authorized UI glue. They are
  not the RustyClip control-plane implementation substrate.
- `yq`, Graphviz, Mermaid CLI, PlantUML, `cargo-vet`, `cargo-machete`, and
  `wasm-opt` are absent and optional until an accepted task or quality gate
  requires them.
- Python may be used only through the system interpreter for bounded support
  work. Python virtual environments are prohibited for this domain.

## Prohibited Or Out-Of-Scope Use

- Do not use creative, gaming, smart-home, social/media, personal messaging,
  red-team, unrelated MLOps, or Apple automation skills for RustyClip work
  unless a separately governed task explicitly requires one.
- Do not use Riven's profile, credentials, tools, identity, sessions, or
  subagents for RustyClip Phase 0 or Phase 1.
- Do not invoke Docker or container-based tooling.
- Do not perform destructive Git operations, force pushes, direct pushes to
  protected branches, credential extraction, bulk fleet messaging, wildcard
  NATS publishing, unbounded database writes, or unaudited service mutation.
- Do not use a reviewer or approver tool surface to mutate the artifact under
  review.
- Do not use an installed plugin, sudo, local key, or broad skill catalog
  outside the exact task, role, lease, resource, network, and budget scope.

## Capability-Lease Discipline

1. Inspect with read-only tools before mutation.
2. Confirm the assigned governed role and risk tier.
3. Revalidate identity, signatures, policy, conflict result, exact resources,
   budget, capability lease, expiry, use count, and fencing token immediately
   before every privileged action.
4. Use the narrowest path, repository, service unit, database role, NATS
   subject, endpoint, and GitHub repository.
5. Record sanitized pre-state, command class, post-state, artifact digest, and
   rollback evidence.
6. Stop on scope drift, stale fence, lease expiry, uncertain external effect,
   or missing evidence. Do not retry until independent reconciliation permits
   it.
7. Never renew an action capability lease as its holder. Return expired or
   changed work to independent review.

## Safe Inventory Checks

Use non-secret checks such as:

```text
command -v <tool>
<tool> --version
rustup target list --installed
systemctl status <exact-unit>
nats context info
psql --version
```

Sanitize output before recording it. Never dump `.env`, `auth.json`,
`config.yaml`, private keys, database URLs, NATS credentials, or secret values.
