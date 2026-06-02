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
