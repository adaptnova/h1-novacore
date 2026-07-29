# Echo Identity, Instruction, And Tool Audit

## 2026-07-28 23:04:59 — SIGNED_BY_SKIPPER

## Scope

Audited only `/adapt/novas/active/echo` and its repository-local ops records.
No service, external agent, repository remote, or path outside Echo's profile
was modified.

## Verified Identity And Runtime

- Nova name: Echo
- Active directory: `/adapt/novas/active/echo`
- Hermes profile link: `/home/x/.hermes/profiles/echo`
- Hermes profile link resolves to the active directory.
- A Hermes process for profile `echo` was observed with the active directory as
  its working directory.
- `.nova/chrysalis.json` is parseable and names `echo`.
- `.nova/identity.pub` is 32 bytes and matches the manifest's verifying-key
  value.
- `.nova/identity.key` is an encrypted 72-byte file with mode `0600`; its
  contents were not read.
- Public identity metadata was hardened from mode `0664` to `0644`.
- No locally verified `nova_id` exists.
- `IDENTITY.md` records the verified identity references and leaves every
  unavailable RustyClip identity field explicitly `null`.

The pinned `veritas-chrysalis` verifier now passes Echo's local bundle checks.
Full registry verification remains blocked because no authoritative Veritas DAG
store is available at the configured local path. No identity value was invented
to bypass that blocker.

## Verified Role And Authority

Local Build 1 coordination records establish:

- Chase is Board.
- Echo is the top-level operating manager and Chief of Staff for Build 1.
- Domain and lane owners report through Echo for coordination while retaining
  technical authority.
- Tecton is an architecture reviewer, not Echo's manager.
- Riven is excluded from the current Build 1 phase.
- Echo's domain is Coordination / CoS at `/adapt/platform/CoS`.
- The current control-plane project is RustyClip at
  `/adapt/platform/novaops/controlplane/rustyclip`.

The previous Z-Pure role remains historical context, not current authority.

## Instruction Bundle

Current required role bundle:

| File | Result |
|---|---|
| `AGENTS.md` | corrected and role-specific |
| `HEARTBEAT.md` | created and role-specific |
| `TOOLS.md` | corrected and role-specific |
| `SOUL.md` | corrected and role-specific |
| `PROTOCOLS.md` | created and role-specific |
| `IDENTITY.md` | created as a blocked partial identity; `.nova/` remains the cryptographic source |

Hermes-loadable copies under `memories/` and `memory/l1/` were synchronized.
`PROJECT.md` and the current `MEMORY.md` authority snapshot were corrected so
they no longer send Echo through Tecton or force Z-Pure as the active project.
The longer historical memory was preserved with a current-authority override.

## Tool Audit

Installed and verified:

- `git`, authenticated `gh`, `rg`, `jq`, and `curl`;
- `nats`, with local contexts and readable `NOVA_LIFECYCLE` metadata;
- `systemctl` and `journalctl`;
- `codex` and `hermes`;
- local `bin/tirith`;
- `veritas-chrysalis` from pinned Veritas revision `878e4af1`;
- `cargo`, `rustc`, `cargo-deny` 0.20.2, `cargo-llvm-cov` 0.8.7,
  `sqlx-cli` 0.9.0, `wasm-pack`, and `wasmtime`.

Configured runtime surface:

- enabled toolsets: `hermes-cli`, `messaging`;
- NATS platform flag: enabled;
- enabled plugins: none;
- local NATS bridge manifest: present but inactive;
- configured external platform channels: none.

Required but missing or unverified:

- an authoritative Veritas DAG store for identity-registry verification;
- an enabled and proven model-facing NATS push bridge;
- a substantive correlated A2A round trip during this audit;
- a dedicated `paperclip` or `rustyclip` CLI.

Installed but excessive or prohibited by default:

- Docker is installed but prohibited by the environment contract.
- `kubectl`, database CLIs, `sudo`, `su`, `tcpdump`, and `strace` are present
  but outside Echo's routine authority.
- Rust/Wasm build tools are evidence-review tools for Echo unless Chase assigns
  direct implementation.
- Unrelated red-team, gaming, media, and smart-home skills are out of role.

The least-privilege action matrix is recorded in `TOOLS.md`.

## Security Correction

Credential-like literals in
`docs/protocols/NOVA_ONBOARDING_PROTOCOL.md` were replaced with managed-secret
references and context-based commands. No credential value is reproduced in
this report.

## Exact Files Changed

Content changed or created:

- `/adapt/novas/active/echo/AGENTS.md`
- `/adapt/novas/active/echo/HEARTBEAT.md`
- `/adapt/novas/active/echo/TOOLS.md`
- `/adapt/novas/active/echo/SOUL.md`
- `/adapt/novas/active/echo/PROTOCOLS.md`
- `/adapt/novas/active/echo/IDENTITY.md`
- `/adapt/novas/active/echo/PROJECT.md`
- `/adapt/novas/active/echo/MEMORY.md`
- `/adapt/novas/active/echo/memories/SOUL.md`
- `/adapt/novas/active/echo/memories/MEMORY.md`
- `/adapt/novas/active/echo/memory/l1/SOUL.md`
- `/adapt/novas/active/echo/memory/l1/MEMORY.md`
- `/adapt/novas/active/echo/docs/protocols/NOVA_ONBOARDING_PROTOCOL.md`
- `/adapt/novas/active/echo/scripts/validate_nova.sh`
- `/adapt/novas/active/echo/ops/operations_history.md`
- `/adapt/novas/active/echo/ops/decisions.log`
- `/adapt/novas/active/echo/ops/reports/2026-07-28-echo-identity-instruction-tool-audit.md`

Permissions changed only:

- `/adapt/novas/active/echo/.nova/identity.pub` (`0664` to `0644`)
- `/adapt/novas/active/echo/.nova/chrysalis.json` (`0664` to `0644`)

## Validation

Completed:

- required-bundle presence and Echo-role assertions;
- stale Tecton/Z-Pure manager-string scan across current instructions;
- SOUL and MEMORY copy consistency checks;
- Chrysalis JSON parse, key-length, public-key consistency, and permission
  checks;
- high-confidence secret-pattern scan over changed artifacts;
- trailing-whitespace scan;
- `bash -n scripts/validate_nova.sh`;
- `shellcheck scripts/validate_nova.sh`;
- `scripts/validate_nova.sh echo`;
- `git diff --check`;
- staged-change check.

The updated profile validator finished with zero errors and four warnings:

- `memories/memory.mdl` is absent;
- `memories/user.mdl` is absent;
- `memories/LAYERED_MEMORY.md` is absent;
- the local identity bundle passed, but the authoritative Veritas DAG store is
  absent, so registry membership was not reverified.

The three legacy memory files are optional under the current contract and were
not fabricated.

## Repository State

The permanent files enumerated above are included in a narrowly scoped
`working`-branch profile commit. Echo's shared repository already contained
substantial unrelated tracked and untracked state; none of it was staged,
reverted, or included. The durable profile commit is recorded in the RustyClip
bootstrap completion report.
