# Skipper Tool Surface

## Audit Scope

Verified locally on 2026-07-28 from `/adapt/novas/active/skipper`. A tool being
installed does not authorize its use. Versions are audit evidence, not permanent
requirements.

The profile configuration currently exposes the `hermes-cli` toolset, project-scoped
code execution, manual approvals, the `nats-bridge` plugin, and the configured
`nova.skipper.hermes.direct` NATS subject. No toolsets are explicitly disabled.

## Installed And Verified

### Source And Repository Control

| Tool | Verified version or path | Authorized use |
| --- | --- | --- |
| `git` | 2.43.0 | Inspect and change an assigned repository |
| `gh` | 2.89.0 | Private GitHub operations explicitly required by a task |
| `rg` | installed | Fast source and document search |
| `jq` | 1.7 | Structured JSON inspection without printing secrets |

### Rust And WebAssembly

| Tool | Verified version | Authorized use |
| --- | --- | --- |
| `rustc` / `cargo` | 1.95.0 | Rust builds and workspace management |
| `rustfmt` / `clippy` | 1.95 toolchain | Formatting and lint gates |
| `cargo-audit` | 0.22.2 | Dependency advisory checks |
| `cargo-nextest` | 0.9.137 | Test execution |
| `cargo-deny` | 0.20.2 | Dependency, license, advisory, and source-policy gates |
| `cargo-llvm-cov` | 0.8.7 | Auditable Rust coverage evidence |
| `sqlx-cli` (`sqlx`) | 0.9.0 | Migration checks and SQLx offline metadata |
| `cargo-component` | 0.21.1 | Component Model guest work |
| `wasm-pack` | 0.14.0 | Approved browser-Wasm packaging |
| `wasm-tools` | 1.248.0 | Inspect and compose Wasm components |
| `wasmtime` | 30.0.2 | Local component/runtime validation |

Installed Rust targets are `x86_64-unknown-linux-gnu`,
`wasm32-unknown-unknown`, and `wasm32-wasip2`. A Rust Wasm64 target was not
listed by either the active stable or installed nightly toolchain.

### Operations And Validation

| Tool | Verified version or state | Authorized use |
| --- | --- | --- |
| `systemctl` / `journalctl` | installed; system state reported degraded | Scoped service inspection and approved systemd changes |
| `sudo` | installed; non-interactive elevation available | Only commands explicitly within task authority |
| `nats` | 0.4.0 | Approved subjects and non-secret diagnostics |
| `psql` | 18.3 | Read-only inspection or explicitly approved migrations |
| `curl` | installed | Health and contract checks with redacted output |
| `shellcheck` | 0.9.0 | Shell validation |
| `openssl` / `ssh-keygen` | installed | Approved fingerprint and key-format checks |
| `veritas-chrysalis` | pinned Veritas revision `878e4af1`; local bundle checks passed | Identity-bundle verification; registry DAG still unavailable |
| Google Chrome / Playwright | installed | Local visual and interaction validation |

## Required But Missing For RustyClip Delivery

| Tool or capability | Why it is required | Constraint |
| --- | --- | --- |
| Reproducible Rust Wasm64 target | Prove the strategic Wasm64 build path | Treat as a design blocker until a supported toolchain is reproduced |

`yq`, Graphviz, Mermaid CLI, PlantUML, `cargo-vet`, `cargo-machete`, and
`wasm-opt` are absent. They are optional until an accepted task or quality gate
requires them.

## Installed But Restricted, Excessive, Or Prohibited

- Docker is installed but prohibited by TeamADAPT policy. Do not invoke the daemon,
  CLI, Compose, or Docker-based upstream scripts.
- Node.js 22.22.2, npm 10.9.7, pnpm 11.1.3, and Bun 1.2.23 are
  compatibility-only tools for studying or testing upstream Paperclip surfaces.
  They are not the implementation substrate for RustyClip's control plane.
- The profile contains broad creative, gaming, smart-home, social/media, red-team,
  MLOps, and Apple automation skills that are not required for the RustyClip owner
  role. Do not invoke them without an explicit, scoped task.
- Destructive Git commands, direct pushes to protected branches, force pushes,
  credential extraction, bulk messaging, and unbounded database writes are
  prohibited.
- A Python virtual environment is prohibited. When Python is unavoidable, use the
  system interpreter and keep it out of the Rust control-plane implementation.

## Least-Privilege Rules

1. Treat tool discovery, sudo availability, local keys, and configured plugins as
   capabilities that still require task authority.
2. Use the narrowest path, repository, service unit, database role, NATS subject,
   and GitHub repository needed for the task.
3. Prefer read-only inspection before mutation. Capture pre-state and post-state for
   privileged changes.
4. Never print, copy, commit, or place secrets in command arguments, logs, issues,
   prompts, memory, or reports.
5. Load credentials only from approved secret injection at execution time. Refer to
   secret paths, never values.
6. Do not install a missing tool opportunistically. Record the version, provenance,
   owner, and removal path in a separate approved toolchain task.
7. Do not use an out-of-role skill merely because it is present.

## Verification Commands

Use non-secret checks such as `command -v`, `--version`, `rustup target list
--installed`, and sanitized configuration key inspection. Never dump `.env`,
`auth.json`, `config.yaml`, or private key content.
