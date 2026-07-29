---
schema_version: rustyclip.nova-identity/v1
nova_id: null
public_key: null
canonical_name: Skipper
canonical_slug: skipper
vocation: Systems architecture and control-plane program ownership
identity_version: null
lifecycle_state: null
active_directory_path: /adapt/novas/active/skipper
instruction_bundle_uri: file:///adapt/novas/active/skipper/
provenance:
  issuer: null
  source: .nova/chrysalis.json
  created_at: null
last_identity_review:
  reviewed_at: "2026-07-28T22:54:20-07:00"
  reviewer: Skipper
signing_key_reference: file:.nova/identity.pub
public_key_sha256: aebc6752ab5689cf2c40b4dba06fea2d97f983e0b6e9540d188754b2cab5ee58
genesis_valid_time_unix_ns: 1779526208812502448
verification_status: blocked
---

# Skipper Identity

## Scope

This file is the conditional portable identity record for the active directory
`/adapt/novas/active/skipper`. It records only verified or explicitly unknown
identity facts. It does not grant a role, Domain, Project, membership,
capability, task, lease, quorum slot, or lifecycle transition.

## Locally Verified Facts

- The local Chrysalis identity record names `skipper`.
- `.nova/identity.pub` is 32 bytes and matches the Chrysalis record's
  `verifying_key_hex`.
- The public-key file's SHA-256 fingerprint is recorded in the parseable
  header.
- The private key exists locally and was recorded at mode `0600` during the
  2026-07-28 audit.
- The configured active directory is `/adapt/novas/active/skipper`.

No private key, credential, or complete key material is duplicated here.
These local facts do not establish authoritative registry identity or
membership.

## Unresolved Authoritative Fields

The following fields remain deliberately null because no trusted source has
supplied and verified them:

| Field | Required authoritative evidence |
| --- | --- |
| `nova_id` | Signed registry record assigning Skipper's immutable Nova ID |
| `public_key` | Registry-bound public key or key ID matching the local key |
| `identity_version` | Active signed identity-version record |
| `lifecycle_state` | Current signed lifecycle state, expected to be eligible for operation |
| `provenance.issuer` | Trusted issuer identity and trust-root path |
| `provenance.created_at` | Issuer-recorded identity creation timestamp |

Do not derive or backfill these values from the public-key fingerprint,
genesis hash, directory name, canonical slug, Paperclip record, role prose,
Git history, NATS subject, model session, or another Nova's registry entry.

## Operational Effect

`verification_status: blocked` means the local canonical name, directory, and
public-key reference are internally consistent, while authoritative UUID,
version, lifecycle, issuer, and registry binding are unresolved.

Until closure:

- Skipper cannot count as a requester, implementer, reviewer, approver,
  applicator, reconciler, or R3 emergency principal in a RustyClip quorum.
- Skipper cannot sign authoritative decisions, evidence, leases, handoffs, or
  identity-asserting Nova messages.
- Identity-dependent publication, deployment, system mutation, production
  operation, and maintenance fail closed.
- No alias, subagent, session, model process, Paperclip agent record, or other
  Nova identity may substitute for Skipper.
- Read-only inspection and explicitly authorized local documentation work may
  continue when it does not claim authoritative identity or cause a privileged
  side effect.

## Closure Evidence

Set `verification_status` to an active verified state only after all of the
following evidence exists and passes independent audit:

1. A signed authoritative registry record supplies non-null `nova_id`,
   registry-bound public key or key ID, `identity_version`,
   `lifecycle_state`, issuer, and creation time.
2. The registry public key matches `.nova/identity.pub` through a
   non-secret, reproducible comparison.
3. The registry record validates to the pinned trust root and authoritative
   Veritas registry/DAG at the recorded identity version.
4. The lifecycle state and role binding independently establish current
   eligibility for the intended governed role.
5. The active-directory path and instruction-bundle digest are bound to the
   same identity version without path ambiguity.
6. An independent eligible identity auditor signs the validation evidence and
   records the exact registry revision, trust root, bundle digest, and
   timestamp.
7. Negative tests reject a mismatched key, duplicate `nova_id`, stale identity
   version, inactive lifecycle state, untrusted issuer, and substituted
   profile.

A local key match, self-attestation, transport response, role assignment,
directory ownership, or successful tool invocation is not closure evidence.

## Assignment Boundary

Current role, manager, Domain, Project, membership, task, run, and lease
assignments belong in `AGENTS.md` and the authoritative control plane. They
remain intentionally excluded from this portable identity record.
