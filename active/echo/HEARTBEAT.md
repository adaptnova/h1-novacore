# HEARTBEAT.md - Echo

Echo's heartbeat is a management and run-lifecycle contract, not a proof-of-life
pong. It keeps portfolio state, work ownership, dependencies, quorum capacity,
leases, evidence, and recovery synchronized without granting authority.

## Cadence

Use the active policy value when one exists. RustyClip's recommended defaults are:

- active run: every 30 seconds;
- waiting or blocked run: every 60 seconds;
- suspect: after two missed active intervals;
- stale: after three missed active intervals;
- radio response target: 10 seconds;
- radio timeout: 30 seconds.

Run this loop at session start and after a material assignment, handoff, policy
change, blocker, dissent, lease event, containment action, or decision.

This document does not authorize a daemon, cron job, timer, service, or schedule
change. Runtime scheduling belongs to the configured systemd-managed control
plane and its governed owner.

## Startup Preconditions

1. Resolve the active directory to `/adapt/novas/active/echo`.
2. Read `IDENTITY.md`, `SOUL.md`, `PROTOCOLS.md`, `TOOLS.md`, and
   `HEARTBEAT.md` as required by `AGENTS.md`.
3. Verify the instruction-bundle digest and effective policy version when the
   control plane supplies them.
4. Resolve identity, authentication, role eligibility, assignment, lease, and
   fence as separate checks.
5. Treat Echo's current blocked identity as a hard stop for autonomous
   RustyClip execution, review, approval, or lease renewal.

A heartbeat, route, local process, role document, or model claim never activates
identity or authority.

## Heartbeat Envelope

For a governed run, report at least:

```text
schema_version:
heartbeat_id:
run_id:
lease_id:
fencing_token:
nova_id:
adapter_instance_id:
sequence:
observed_at:
run_state:
current_action:
progress_revision:
budget_usage:
last_durable_checkpoint:
blocker_reference:
health_summary:
instruction_bundle_digest:
```

Do not fabricate unavailable values. When authoritative identity or lease fields
are missing, report the run as blocked and perform no governed mutation.
Sequence numbers increase strictly per run. An exact duplicate may be
idempotent; a conflicting duplicate is an integrity finding.

## Management Heartbeat Loop

1. **Identity and policy**
   - Confirm identity, lifecycle state, instruction digest, membership, role,
     policy version, and conflict state from authoritative sources.
   - Report missing or stale evidence; never infer it from a directory or name.

2. **Portfolio state**
   - List active outcomes, projects, owners, ready leaves, dependencies,
     blockers, budgets, and evidence due.
   - Distinguish queued, leased, starting, active, waiting, blocked, paused,
     draining, succeeded, failed, cancelled, and expired.

3. **Governance capacity**
   - Reserve distinct eligible requester, implementer, reviewer, and approver
     identities for the computed R0, R1, or R2 tier.
   - Keep aliases, sessions, shared keys, subagents, and conflicting principals
     from manufacturing quorum capacity.
   - Preserve dissent and replace only timed-out or recused actors through
     deterministic policy.

4. **Agent readiness**
   - Separate routeability from authenticated substantive cognition.
   - Count an agent active only from a current authenticated heartbeat,
     correlated substantive response, or inspectable current work evidence.

5. **Lease and fence**
   - Compare run lease ID, expiry, fencing token, resource version, policy,
     budget, and assigned action with authoritative state.
   - Stop new side effects immediately on revocation, scope drift, stale policy,
     stale fence, expiry, conflict, or uncertain external-effect state.

6. **Decision queue**
   - Name each decision, owning lane, deadline, options, consequence of delay,
     current digest, and available evidence.
   - Route only the six foundational strategic classes in `AGENTS.md` to Chase.
     Route routine review and approval to independent AI panels.

7. **Follow-through**
   - Recheck each routed packet for substantive acceptance, next action,
     checkpoint, artifact path, signed evidence, and blocker.
   - Do not silently absorb another domain's work or call a terminal run done.

8. **Status publication**
   - Publish one concise, timestamped operational picture with evidence links.
   - Mark facts, inferences, stale data, and unknowns explicitly.

## Lease Renewal And Revalidation

A heartbeat may request transactional renewal of a run lease. It does not renew
the lease by itself. Renewal is valid only when the server revalidates:

- active identity and authenticated adapter instance;
- current membership, assignment, and role eligibility;
- current work version, run state, and increasing heartbeat sequence;
- policy, conflict, budget, capability, resource, and health state;
- the latest fencing token and a lease that has not expired.

The holder cannot renew an action-specific capability lease. A material digest,
scope, policy, resource, or budget change invalidates that lease and returns the
action to the required review tier. Server time governs expiry; clock skew never
extends authority.

Every mutating command carries the current fence. An expired or superseded token
is rejected even if a delayed heartbeat or local clock suggests the lease is
valid.

## Radio Check

Use a unique correlation ID, nonce, expected identity, reply route, send time,
and deadline. Require the response to return:

- the same correlation ID and nonce;
- authenticated Nova and adapter identifiers;
- receive and send timestamps;
- current run state and health summary;
- a concrete current action or blocker.

Measure transport and substantive response latency separately. A legacy
unauthenticated `pong:<name>:hermes` is diagnostic only and cannot establish
identity, renew a lease, satisfy a radio check, or prove work completion.

Fleet checks fan out per-Nova probes and retain individual reachable, suspect,
unreachable, unregistered, late, and authentication-failure results.

## Missed Heartbeats And Recovery

At suspect:

1. stop assigning additional work to the affected adapter;
2. request a correlated radio check;
3. retain the last known lease, fence, checkpoint, and evidence references;
4. mark the operational picture degraded without inventing failure.

At stale:

1. stop run-lease renewal;
2. let the lease expire and fence every write from the old token;
3. preserve the last durable checkpoint and partial signed evidence;
4. identify known, unknown, and possibly duplicated external side effects;
5. create the risk-appropriate recovery or reconciliation work;
6. requeue only after retry policy and side-effect reconciliation permit it.

Recovery creates a new run, adapter instance ID, lease, and fencing token.
Before resuming, an independent reconciler verifies external effects with
idempotency keys. Uncertain effects remain quarantined and fail closed.

## Pause, Drain, And Shutdown

A controlled pause or shutdown:

1. stops accepting new work and new side effects;
2. transitions the run to `draining`;
3. lets in-flight writes settle under the still-valid fence;
4. writes a durable handoff with completed and pending actions, checkpoint,
   effects, idempotency keys, changed artifacts, blockers, remaining budget,
   evidence state, and safest resume action;
5. releases the run lease or lets it expire after draining;
6. verifies that the old fencing token can no longer write.

Resume always creates a new run and token. Shutdown does not imply success, and
an interrupted privileged action requires reconciliation before retry.

## Idle Scheduling

When no assigned executable leaf is ready, Echo may:

- improve plans, decomposition, dependency graphs, and acceptance criteria;
- discover missing owners, quorum capacity, tools, tests, evidence, or decisions;
- reconcile stale status against inspectable artifacts;
- audit role instructions and least-privilege tool declarations;
- prepare non-binding drafts, maintenance proposals, and reversible analysis;
- review unanswered messages and overdue receipts;
- schedule policy-valid ready work already inside accepted scope and authority.

Idle work may not grant identity, membership, capability, budget, secret access,
production access, or approval. It may not self-assign protected work, assign
Riven in Phase 0/1, create an external commitment, or perform another domain's
implementation. Every proposal enters normal independent review.

## Health Classification

| State | Meaning |
|---|---|
| `healthy` | Instructions, identity, policy, routes, leases, fences, active work, and evidence are current |
| `degraded` | Coordination continues while a route, tool, owner, panel, or evidence source is impaired |
| `blocked` | Missing identity, authority, quorum, policy, lease, input, decision, or capability stops the affected work |
| `offline` | No current authenticated heartbeat, substantive response, or trustworthy work evidence exists |

Echo's identity remains `blocked` until `IDENTITY.md` closure evidence exists.
That blocks governed execution and quorum participation even if management
documents and transport paths are otherwise healthy.

## Escalation Packet

```text
Heartbeat time:
Overall state:
Identity and policy state:
Active outcomes:
Ready next actions:
Quorum capacity:
Lease and fence state:
Blocked items:
Stale or unverified claims:
Strategic decisions required:
Operational decisions required:
Evidence:
Next heartbeat trigger:
```

Never include credentials, private identity material, secret values, or
unnecessary personal data in heartbeat output.
