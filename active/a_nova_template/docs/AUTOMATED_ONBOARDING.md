# Automated Nova Onboarding

This is the canonical, anyone-can-run onboarding path for creating a new Nova from `a_nova_template`.

## Fast path

```bash
cd /adapt/novas/active/a_nova_template
./scripts/nova-onboard.sh Echo --validate
```

Equivalent direct command:

```bash
python3 /adapt/novas/active/a_nova_template/nova.py --name Echo --validate
```

## Config-file path

```bash
cp /adapt/novas/active/a_nova_template/identity.yaml.example /tmp/echo.yaml
# edit /tmp/echo.yaml
python3 /adapt/novas/active/a_nova_template/nova.py --config /tmp/echo.yaml --validate
```

## Full MemFirst provisioning

First check runtime readiness:

```bash
python3 /adapt/novas/active/a_nova_template/nova.py --preflight-runtime
```

When NATS/Dragonfly/Redpanda/secrets/binaries are ready:

```bash
python3 /adapt/novas/active/a_nova_template/nova.py --name Echo --validate --memfirst
```

`--memfirst` automatically runs the same full-runtime preflight before it calls the MemFirst provisioner.

Or provision later from inside the new Nova:

```bash
/adapt/novas/active/Echo/scripts/setup_memory_layers.sh --full
```

## Realtime memory hooks

Hooks and ingestion:

```text
plugins/memfirst-realtime
  pre_llm_call   -> injects compact L1/L2 + latest session memory into the next turn
  post_llm_call  -> calls scripts/memfirst_ingest.py for the completed turn

scripts/memfirst_ingest.py
  L0: appends JSONL to memory/l0/intake/sessions/<session>.jsonl
  mirror: appends JSONL to sessions/<session>.jsonl
  L3: adds the turn to semantic search when embedding keys are available
  L4: appends user/assistant messages to nme-verbatim
  L5: writes a raw session_turn source JSON
  L6: publishes memory.<profile>.session_turn over NATS
```

## Full onboarding overlay

The consolidated full Nova + Hermes + MemFirst checklist lives in:

```text
/adapt/novas/active/a_nova_template/docs/full_onboarding/
```

After creating a Nova, run the static full-onboarding verifier:

```bash
python3 /adapt/novas/active/a_nova_template/docs/full_onboarding/verify_full_onboarding.py /adapt/novas/active/Echo
```

This verifies Hermes config YAML, profile/plugin readiness, L0 onboarding seeds, realtime hook declarations, and identity mirror basics. Runtime L3/L4/L5/L6 fanout still needs the realtime probe when services/secrets are available.

Existing docs in `docs/` are routed by `docs/full_onboarding/00_existing_docs_map.md`; old architecture/protocol docs remain useful, but the full onboarding overlay is the acceptance gate.

## Safety / testing

Dry-run without writes:

```bash
python3 /adapt/novas/active/a_nova_template/nova.py --name DryRunNova --dry-run --skip-hermes-register
```

Validate existing Nova:

```bash
python3 /adapt/novas/active/a_nova_template/nova.py --validate-only Echo
```

## What gets created

- `/adapt/novas/active/<NovaName>/`
- root `SOUL.md`, `MEMORY.md`, `USER.md`
- `memories/` identity files rendered from `.example` templates
- MemFirst-ready `memory/l0` through `memory/l6` directories
- initial onboarding seed session in `memory/l0/intake/sessions/*_onboarding.jsonl` and `sessions/*_onboarding.jsonl`
- realtime MemFirst plugin in `plugins/memfirst-realtime/`
- turn ingestion script in `scripts/memfirst_ingest.py`
- config enables `plugins.enabled: [memfirst-realtime]` so Hermes hooks ingest turns automatically
- `memory/l1/{SOUL.md,MEMORY.md,USER.md}`
- `domains/`, `scripts/`, `docs/`, `configs/`, `ops/`, `workspace/`
- `config.yaml`
- `.env` that sources shared secrets from `/adapt/secrets/db.env` and `/adapt/secrets/m2.env`
- `mempalace.yaml`
- Hermes profile symlink under `/home/x/.hermes/profiles/<profile>` unless a custom `--profiles-dir` is provided

## Important flags

```text
--name NAME                 Quick create from defaults
--config FILE               Create from identity YAML/JSON
--validate                  Validate immediately after creation
--validate-only NAME        Validate existing Nova
--dry-run                   Print actions; write nothing
--memfirst                  Run full MemFirst provisioner after creation
--skip-hermes-register      Do not run hermes profile use
--base-dir DIR              Override /adapt/novas/active for tests
--profiles-dir DIR          Override Hermes profiles dir for tests
--force                     Replace generated files/symlink when target exists
```

## Verified

The automation was verified by creating and validating a temporary Nova under `/tmp` with a temporary Hermes profile directory, plus a dry run.
