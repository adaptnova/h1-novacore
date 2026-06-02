# 00 — Existing Docs Map

This map prevents the full onboarding pack from becoming another competing doc pile. Existing docs are retained, but their authority is scoped.

## Canonical routing

```yaml
new_nova_creation:
  primary: docs/AUTOMATED_ONBOARDING.md
  full_acceptance_overlay: docs/full_onboarding/
  verifier: docs/full_onboarding/verify_full_onboarding.py

full_lifecycle_architecture:
  primary: docs/protocols/NOVA_ONBOARDING_PROTOCOL.md
  note: includes Chrysalis/Veritas + MemFirst phases; older than realtime hook work

legacy_lifecycle_doc:
  path: docs/NOVA_ONBOARDING_PROTOCOL.md
  status: superseded by docs/protocols/NOVA_ONBOARDING_PROTOCOL.md
  use_for: historical comparison only

memory_architecture:
  primary: docs/MEMORY_ARCHITECTURE.md
  runtime_overlay: docs/full_onboarding/03_memfirst_realtime.md

memfirst_planning:
  primary: docs/MEMFIRST_INTEGRATION_PLAN.md
  status: planning/design reference, not acceptance checklist

hermes_profile_runtime:
  primary: docs/protocols/HERMES_PROFILE_PROTOCOL.md
  operational_overlay: docs/full_onboarding/02_hermes_runtime.md

nats:
  primary: docs/NATS_INTEGRATION.md
  related_protocols:
    - docs/protocols/INFRASTRUCTURE_PROTOCOL.md
    - docs/protocols/AGENT_COORDINATION_PROTOCOL.md
    - docs/protocols/MEMORY_OPERATIONS_PROTOCOL.md

secrets:
  primary: docs/protocols/SECRETS_AND_CREDENTIALS_PROTOCOL.md
  rule: examples must reference env vars/secret files, not hardcoded credentials

migration_suite:
  primary_index: docs/a__README.md
  files:
    - docs/a__migration_guide.md
    - docs/a__nova_naming.md
    - docs/a__nova_template.md
  status: migration reference; not the full onboarding source of truth

status_summary_docs:
  paths:
    - docs/TEMPLATE_v1.3.0_SUMMARY.md
    - docs/MNEMOS_GAP_ANALYSIS.md
    - docs/ARCHITECTURE.md
  status: historical/status/design context
```

## Existing docs inventory

| Doc | Role now | Action |
|---|---|---|
| `AUTOMATED_ONBOARDING.md` | Current create/validate commands | Keep, points to full overlay |
| `full_onboarding/` | Full acceptance pack | Canonical overlay |
| `protocols/NOVA_ONBOARDING_PROTOCOL.md` | Lifecycle architecture | Keep, update later for realtime hooks if desired |
| `NOVA_ONBOARDING_PROTOCOL.md` | Older lifecycle v2 | Superseded; do not use as canonical |
| `MEMORY_ARCHITECTURE.md` | L0-L6 architecture | Keep |
| `MEMFIRST_INTEGRATION_PLAN.md` | Design/integration plan | Keep as planning reference |
| `NATS_INTEGRATION.md` | NATS-specific integration | Keep |
| `protocols/HERMES_PROFILE_PROTOCOL.md` | Hermes profile protocol | Keep |
| `protocols/MEMORY_OPERATIONS_PROTOCOL.md` | Memory ops protocol | Keep |
| `protocols/INFRASTRUCTURE_PROTOCOL.md` | Infra prerequisites | Keep |
| `protocols/SECRETS_AND_CREDENTIALS_PROTOCOL.md` | Secrets policy | Keep; scrub examples if hardcoded secrets appear |
| `protocols/AGENT_COORDINATION_PROTOCOL.md` | Agent coordination | Keep |
| `protocols/ADAPT_OPERATING_PROTOCOL.md` | Operating norms | Keep |
| `protocols/CRISIS_PROTOCOL.md` | Crisis handling | Keep |
| `a__README.md` | Migration suite index | Keep |
| `a__migration_guide.md` | Migration guide | Keep |
| `a__nova_naming.md` | Naming conventions | Keep |
| `a__nova_template.md` | Template structure | Keep |
| `TEMPLATE_v1.3.0_SUMMARY.md` | Historical status | Keep as historical |
| `MNEMOS_GAP_ANALYSIS.md` | Historical gap analysis | Keep as historical/reference |
| `ARCHITECTURE.md` | Modularization/migration strategy | Keep as design reference |

## Rule

If a doc says something about onboarding that conflicts with `docs/full_onboarding/`, the full onboarding pack wins for acceptance criteria. The older doc can stay as architecture/history, but it is not the gate.
