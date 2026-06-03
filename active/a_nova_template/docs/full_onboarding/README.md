# Full Nova + Hermes Onboarding

This directory is the consolidated full onboarding pack. It plugs the old project-team checklist gap: MemFirst realtime hooks, L0 seed, L3/L4/L5/L6 fanout, historical backfill, and Hermes runtime/profile verification.

## Source order

0. `00_existing_docs_map.md` — routes every existing doc in `docs/` so old references do not compete with the full onboarding gate.
1. `01_full_onboarding_checklist.md` — operator checklist and acceptance gates.
2. `02_hermes_runtime.md` — Hermes profile/config/session/runtime setup.
3. `03_memfirst_realtime.md` — seed + realtime pre/post LLM memory ingestion/injection.
4. `04_session_backfill_and_mirror.md` — historical imports and Codex/Veyra mirror pattern.
5. `05_infra_channels_databases_monitoring.md` — NATS, Nexus, DragonflyDB, Redpanda, NebulaDB graph, vector DB, Hermes DBs, E2E trace, and playback monitoring.
6. `../protocols/VOICE_A2A_NEXUS_PROTOCOL.md` — required voice, direct A2A, and NEXUS session-ingress channel contract.
7. `verify_full_onboarding.py` — static verifier for generated Nova homes.
8. `verify_runtime_onboarding.py` — runtime verifier that creates/probes a Nova, exercises realtime hooks/fanout, records E2E trace/playback, and inventories Temporal.io touch points.

## Existing docs rule

Existing docs stay. They are scoped in `00_existing_docs_map.md` as architecture, protocol, migration, or historical references. If they conflict with this directory's acceptance criteria, `docs/full_onboarding/` wins for onboarding completion.

## Canonical command

```bash
cd /adapt/novas/active/a_nova_template
python3 nova.py --name Echo --validate
python3 docs/full_onboarding/verify_full_onboarding.py /adapt/novas/active/Echo
python3 docs/full_onboarding/verify_runtime_onboarding.py --name RuntimeOnboardProbe
```

`verify_runtime_onboarding.py` emits two top-level booleans:

```yaml
runtime_probe_ok: true   # verifier executed core hook/ingest/trace/playback path
production_gate_ok: true # all production substrate checks passed, including topics/vector/trace/Temporal inventory
```

A failed `production_gate_ok` with `runtime_probe_ok: true` means the runtime path works but production substrate is incomplete, usually missing durable topics, NebulaDB CLI/registration, or an external backend.

For an existing Nova:

```bash
python3 docs/full_onboarding/verify_runtime_onboarding.py \
  --nova-home /adapt/novas/active/Echo \
  --profile echo
```

For full MemFirst runtime provisioning, run preflight first:

```bash
python3 nova.py --preflight-runtime
python3 nova.py --name Echo --validate --memfirst
```

## Non-negotiable distinction

- Seed memory is birth context.
- Realtime ingestion is post-turn persistence.
- Realtime injection is pre-turn context loading.
- Historical backfill is separate import/replay.
- Hermes runtime verification proves the profile actually wakes as the intended Nova.
