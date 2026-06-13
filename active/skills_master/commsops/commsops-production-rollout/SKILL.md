---
name: commsops-production-rollout
description: "Use when planning, executing, proving, or debugging a CommsOps/n-voice production rollout across NATS, n-voice, Hermes gateways, MemFab Temporal workflows, Paperclip workbench, Grok/Deepgram voice provider failover, A2A readiness, and Codex bridge surfaces."
version: 1.0.0
author: Veyra, CommsOps - Tier 1 lead
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [commsops, production-rollout, n-voice, a2a, memfab, temporal, paperclip, grok, deepgram, rust-agents]
    related_skills: [nova-a2a-comms, nova-nats-ops, hermes-agent-ops, hermes-visible-terminal-ops]
---

# CommsOps Production Rollout

## Overview

Use this skill to move CommsOps from sprint artifacts into a live operator-driven
production state. The rollout must prove behavior through services and APIs, not
only through process state. Keep NATS and the Temporal server stable unless a
substrate change is explicitly required.

This skill is written for Codex, Hermes Novas, and Rust-agent implementers. Codex
and Hermes can consume this `SKILL.md` directly. Rust agents should treat the
Rust-agent section as the bootstrap contract until the fleet has a Rust-native
skill loader wired into their runtime.

## When to Use

- Chase asks to roll out, cut over, deploy, or prove CommsOps/n-voice.
- A sprint closes and needs production proof instead of a planning artifact.
- A2A, phone/headless voice, Paperclip, MemFab, Temporal, or Codex bridge
  readiness must be checked together.
- A service restart is needed but NATS/Temporal substrate continuity matters.
- A Rust Nova needs the rollout contract to implement a loader, checker, or
  daemon-side proof path.

Do not use this for generic NATS message sending. Use `nova-a2a-comms` for that.

## Canonical Paths

```text
/adapt/platform/commsops
/adapt/platform/commsops/ops/runbooks/production-cutover-runbook.md
/adapt/platform/commsops/ops/proofs
/adapt/platform/novaops/controlplane/n-voice
/adapt/platform/novaops/controlplane/pipecat-voice
/adapt/platform/novaops/controlplane/paperclip
/adapt/platform/memops/memfabric
```

## Read First

Before executing a rollout, read the current runbook and the latest proof:

```bash
sed -n '1,220p' /adapt/platform/commsops/ops/runbooks/production-cutover-runbook.md
ls -1t /adapt/platform/commsops/ops/proofs/*production* /adapt/platform/commsops/ops/proofs/*sprint16* 2>/dev/null | head
```

For A2A routing details, also load:

```text
/adapt/novas/active/skills_master/commsops/nova-a2a-comms/SKILL.md
```

## Rollout Rule

Default rollout mode is controlled application restart:

- Restart app/control-plane units only.
- Leave `nats-server.service` and `temporal-server.service` running when their
  health is already good.
- Use `sudo systemctl` for system units. Non-sudo systemctl against system units
  can produce misleading timeout behavior.
- Prove readiness from HTTP/API surfaces after restart.
- Record proof under CommsOps ops before claiming production go.

## Preflight Checks

Run these from any shell with local service access:

```bash
systemctl is-active \
  n-voice-gateway.service \
  n-voice-codex-bridge.service \
  n-voice-turn-mirror.service \
  comms-turn-memory-ingest.service \
  nova-grok-realtime-bridge.service \
  pipecat-voice.service \
  memfab-temporal.service \
  paperclip.service

XDG_RUNTIME_DIR=/run/user/1000 systemctl --user is-active \
  nova-hermes-nats-bridge.service \
  hermes-gateway-chronos.service \
  hermes-gateway-zap.service \
  hermes-gateway-echo.service \
  hermes-gateway-skipper.service

curl -fsS http://127.0.0.1:18192/api/a2a/readiness \
  | jq '{status,accepted,failed,unknown,stale,release_gates}'

curl -fsS http://127.0.0.1:18192/api/voice/provider-failover/proof \
  | jq '{ok,active:.baseline.active_voice_provider,grok:.voice_proof.grok.state,deepgram:.voice_proof.deepgram.state,browser_keys:.voice_proof.browser_receives_provider_keys}'

curl -fsS http://127.0.0.1:3100/api/commsops/workbench \
  | jq '{readiness:{accepted:.readiness.accepted,failed:.readiness.failed,stale:.readiness.stale,unknown:.readiness.unknown},codex_status:.codexBridge.status,workflow_ok:.workflow.ok}'
```

Go criteria:

- all listed services active,
- A2A `status == green`,
- `failed == 0`, `unknown == 0`, `stale == 0`,
- all release gates true,
- voice proof `ok == true`,
- active voice provider is expected for the rollout,
- Paperclip workbench returns readiness and Codex bridge health.

## Controlled Restart Order

Use this order unless the current runbook supersedes it:

```bash
set -euo pipefail
for unit in \
  memfab-temporal.service \
  n-voice-codex-bridge.service \
  n-voice-gateway.service \
  n-voice-turn-mirror.service \
  comms-turn-memory-ingest.service \
  nova-grok-realtime-bridge.service \
  pipecat-voice.service \
  paperclip.service
do
  sudo timeout 60s systemctl restart "$unit"
done

XDG_RUNTIME_DIR=/run/user/1000 systemctl --user restart nova-hermes-nats-bridge.service
sleep 8
```

Only restart `nats-server.service` or `temporal-server.service` if:

- preflight proves the substrate is degraded,
- a config change directly targets that substrate, or
- the operator explicitly approves substrate restart.

## Post-Rollout Proof

Repeat the preflight checks, then trigger one fresh native readiness workflow:

```bash
curl -fsS -X POST http://127.0.0.1:18192/api/workflows/commsops/readiness/run \
  | jq '{ok,status,workflow_id,temporal_run_id,completed:.output_event.output_event.memfab_response.body.summary.completed,observed_steps:.output_event.output_event.memfab_response.body.summary.observed_steps}'
```

The proof is acceptable only when:

- `ok == true`,
- `status == succeeded`,
- `workflow_id` is non-empty,
- `temporal_run_id` is non-empty,
- `completed == true`,
- `observed_steps >= 1`.

## Proof Artifact

Write one JSON proof under:

```text
/adapt/platform/commsops/ops/proofs/YYYY-MM-DD-production-rollout-execution.json
```

Include:

- timestamp and signer,
- rollout strategy,
- restarted system units,
- restarted user units,
- system/user active state,
- A2A readiness summary,
- workflow id and run id,
- voice provider proof,
- Paperclip workbench proof,
- final result.

Never include secrets, tokens, passwords, raw env files, bearer headers, or full
provider config.

## Ops Logs

Update these files newest-first:

```text
/adapt/platform/commsops/ops/operations_history.md
/adapt/platform/commsops/ops/decisions.log
```

Use this signature:

```text
— Veyra, CommsOps - Tier 1 lead
```

Log decisions separately from actions. A common rollout decision is: keep NATS
and Temporal server running because substrate health is already proven.

## Git Discipline

In `/adapt/platform/commsops`, commit only the rollout proof and ops logs unless
the rollout actually changed code/config:

```bash
git add ops/proofs/YYYY-MM-DD-production-rollout-execution.json ops/operations_history.md ops/decisions.log
git commit -m "Record production rollout execution — Veyra, CommsOps - Tier 1 lead"
git push origin HEAD:main
```

If the local branch is `working` with upstream `origin/main`, use:

```bash
git push origin HEAD:main
```

## Rust-Agent Bootstrap Contract

Rust agents are not considered fully wired into this skill until a Rust runtime
can discover, parse, and report this skill from the shared corpus.

Minimum Rust loader contract:

1. Read skills from:
   - `/adapt/novas/active/skills_master`
   - optional local mirror: `/data/vast/home/x/.agents/skills`
2. Discover files matching `**/SKILL.md`.
3. Parse YAML frontmatter fields: `name`, `description`, `version`, `metadata`.
4. Index by `name` and metadata tags.
5. Expose a command or NATS request that returns:
   - skill name,
   - source path,
   - description,
   - body hash,
   - loaded timestamp.
6. Treat `references/`, `scripts/`, and `agents/` as relative to the skill
   directory.
7. Never execute scripts from a skill without an explicit task and operator-safe
   validation.

For this rollout skill, a Rust agent should be able to answer:

```text
skill.name=commsops-production-rollout
skill.source=/adapt/novas/active/skills_master/commsops/commsops-production-rollout/SKILL.md
skill.status=loaded
```

Until that proof exists, say: "Rust services are Rust-native in the CommsOps hot
path, but Rust agents are not yet skill-loader wired."

## Failure Handling

- If A2A drops from green, stop and inspect the gateway/bridge logs before
  touching NATS.
- If Paperclip is unavailable, verify `paperclip.service` points at the active
  repo and not an upstream/stale checkout.
- If MemFab restart appears stuck, retry with `sudo systemctl`; do not conclude
  Rust shutdown is broken from a non-sudo systemctl timeout alone.
- If voice proof is not ready, inspect Grok realtime and Deepgram provider state
  before changing roster or phone UI.
- If a proof endpoint races startup, wait a short settle window and rerun once.

## Verification Checklist

- [ ] Current runbook read.
- [ ] Preflight captured.
- [ ] Controlled restart executed.
- [ ] Post-rollout A2A green.
- [ ] Fresh workflow id and run id captured.
- [ ] Voice provider proof captured.
- [ ] Paperclip workbench proof captured.
- [ ] Proof JSON written without secrets.
- [ ] Ops history updated newest-first.
- [ ] Decision log updated newest-first.
- [ ] CommsOps commit pushed.
- [ ] Rust-agent skill-loader status reported honestly.
