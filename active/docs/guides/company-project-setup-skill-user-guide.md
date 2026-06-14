# Company Project Setup Skill User Guide

## Purpose

The `company-project-setup` skill turns a loose company, project, or agent-team idea into an
execution-ready setup packet. It is meant for Adapt operator work where the output needs to include
agents, model choices, routes, sprint packs, validation gates, and a copyable `/goal` prompt.

## When To Use It

Use it when you want to:

- stand up a new company project;
- define a new agent or agent team;
- choose model/provider assignments for roles;
- create Tier-1/Tier-2 operating structure;
- build sprint packs before going offline;
- produce a launch prompt an agent can execute without another planning round.

## Basic Prompt

```text
Use $company-project-setup to set up a company project for <idea>.
Include the company/project purpose, agent roster, model matrix, sprint packs, security boundaries,
and a ready-to-run /goal prompt.
```

## Stronger Prompt

```text
Use $company-project-setup.

Company/project:
Domain owner:
Repo/path:
Known agents:
Preferred models/providers:
Runtime constraints:
First outcome needed:

Create the setup packet, sprint packs, and /goal prompt. Make reasonable assumptions and call out
anything that needs Tier-1 approval.
```

## Expected Output

The skill should produce:

- a short purpose statement;
- ownership and escalation path;
- operating model such as company, department, street team, strike team, or single-agent lane;
- agent roster with responsibilities and handoffs;
- model/provider matrix with fallback choices;
- project structure and files to create;
- sprint packs;
- comms routes and status cadence;
- security and redaction rules;
- validation commands and go/no-go gates;
- a launch-ready `/goal` prompt.

## Optional Fields

Useful optional inputs:

- codename, public name, or callsign, such as `Cincinnati`;
- preferred icon or identity notes;
- API/provider boundaries;
- NATS subject names;
- systemd service names;
- existing worktree path;
- planned launch date;
- whether the project is experimental, canary, shadow, or production.

## Example

```text
Use $company-project-setup to create a MemOps street-team project called Cincinnati.
It needs one lead, two specialist agents, model choices, NATS routes, four sprint packs, and a
/goal prompt. Keep secrets out of the artifact and assume Rust/Wasm-first implementation.
```

## Follow-On Skills

- Use `company-creator` when the setup packet should become a formal Agent Companies package.
- Use `adapt-agent-rosters` when the main need is ownership, Tier-1/Tier-2 mapping, or dispatch.
- Use `nova-nats-ops` when the packet needs live NATS routing or subject validation.

## Operator Notes

The skill should not claim production ownership just because a setup packet exists. Treat launch as
proposal or shadow/canary until validation proves the lane is ready.
