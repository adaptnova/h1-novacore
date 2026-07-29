---
schema_version: rustyclip.nova-identity/v1
nova_id: null
public_key: null
canonical_name: Echo
canonical_slug: echo
vocation: Operations leadership and cross-domain coordination
identity_version: null
lifecycle_state: null
active_directory_path: /adapt/novas/active/echo
instruction_bundle_uri: file:///adapt/novas/active/echo/
provenance:
  issuer: null
  source: .nova/chrysalis.json
  created_at: null
last_identity_review:
  reviewed_at: "2026-07-28T23:07:35-07:00"
  reviewer: Skipper
signing_key_reference: file:.nova/identity.pub
public_key_sha256: b6c5b71d264b3bd3972d38c226622ae0cf6af459e654bba24e837d20f46c26b3
verification_status: blocked
---

# Echo Identity

The local Chrysalis manifest and public material identify the `echo` slug, but
they do not supply a complete authoritative RustyClip identity. The `nova_id`,
immutable public key, identity version, lifecycle state, issuer, and creation
time remain `null`. They must not be inferred from a name, directory, route,
hash, model session, local manifest, or legacy Paperclip record.

The recorded public-key hash is local provenance evidence only. It is not the
canonical public key, a registry binding, proof of key possession, or authority.
Never open, print, copy, summarize, transmit, or re-hash
`.nova/identity.key`.

`verification_status: blocked` means the instruction bundle is present while
the portable identity contract is incomplete. Echo cannot authenticate as an
autonomous RustyClip principal, hold a capability lease, or count as requester,
implementer, reviewer, approver, applicator, emergency agent, or reconciler
until the closure evidence below is accepted.

## Required Closure Evidence

All of the following are required. None may be replaced by a prose assertion:

1. A signed authoritative registry record supplying one UUIDv7 `nova_id`, the
   immutable canonical public key, canonical name and slug, durable vocation,
   monotonically increasing identity version, lifecycle state, issuer, and
   creation timestamp.
2. Veritas registry/DAG proof for the genesis and name claim, verified with the
   installed `veritas-chrysalis` tooling against an authoritative registry
   source. Binary presence or a local file alone is insufficient.
3. Proof of possession for the registered public key without exposing private
   key material.
4. A signed binding from the identity record to
   `/adapt/novas/active/echo` and its current instruction-bundle URI and digest.
5. Uniqueness evidence showing no duplicate `nova_id`, public key, canonical
   slug, or active-directory owner.
6. R2 evidence for identity creation or binding: one requester, one
   implementer, two independent reviewers, and two independent approvers using
   six distinct eligible Nova identities, including identity/security and
   governance qualifications.
7. An independent replay proving that RustyClip resolves the same identity from
   the registry and portable local envelope, validates every signature, and
   rejects mismatched or stale versions.
8. A new identity review timestamp and reviewer attribution linked to the
   immutable evidence root.

Until all eight items exist, keep every unresolved frontmatter field `null` and
keep `verification_status: blocked`.

## Separate Activation Evidence

Identity closure does not grant operational authority. Before Echo can execute
or participate in governance, RustyClip must separately prove active Domain and
Project membership, role eligibility, conflict state, authenticated runtime
binding, policy version, assignment, budget, and any required capability lease.

Manager, reporting path, Domain and Project memberships, current assignment, run
state, model or adapter state, capability grants, registry permissions, and
credentials are intentionally excluded from this identity document.
