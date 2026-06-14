---
name: company-project-setup
description: >
  Set up an Adapt company project from idea to execution packet: define the
  company/project, agent roster, model/provider choices, comms routes, sprint
  packs, validation gates, and a ready-to-run /goal prompt. Use when Chase asks
  to stand up a company, project, agent team, model stack, Tier-1/Tier-2
  operating lane, or reusable launch packet.
---

# Company Project Setup

Use this skill to turn a high-level company or project idea into an executable Adapt setup packet.
The output should be concrete enough that an agent can start work without another planning pass.

## Operating stance

- Prefer decisive setup with clearly marked assumptions over blocking on missing details.
- Inspect existing repos, rosters, project docs, and skill directories before inventing names or roles.
- Keep secrets out of artifacts. Record env var names, provider names, and secret file paths only.
- Use Adapt conventions: Tier-1/Tier-2 ownership, `/goal` prompts, work packets, NATS routes, systemd
  service assumptions, Rust/Wasm-first implementation, and explicit validation gates.
- If the user asks for an Agent Companies package, use the `company-creator` skill after this setup
  packet defines the shape.

## Discovery

Gather enough context to answer:

1. What company/project is being created?
2. Which domain owns it, and who is the lead?
3. Is this a company, a department, a strike team, or a single-agent project?
4. Which agents are needed now, and which seats are future hires?
5. Which model/provider stack should each role use?
6. What artifacts, services, repos, or routes must exist?
7. What makes the first sprint done?

When context is available on disk, inspect it first. Useful sources often include:

- `/adapt/platform/TIER1_TREE.md`
- `/adapt/platform/tier1-registry/domains.md`
- `/adapt/novas/active/`
- `/adapt/novas/active/skills_master/`
- project `README.md`, `AGENTS.md`, `docs/`, `ops/`, and `.env.example` files

## Required setup packet sections

Produce a markdown packet with these sections unless the user asks for a different format:

- **Purpose:** one paragraph describing the company/project and the real-world outcome.
- **Ownership:** Tier-1 lead, Tier-2 lead if known, escalation path, and decision authority.
- **Operating Model:** company, department, strike team, street team, or single-agent lane.
- **Agent Roster:** agent name, role, reports-to, responsibilities, handoff target, and route.
- **Model Matrix:** model/provider per role, reason for each choice, fallback provider, and required env
  var names.
- **Project Structure:** repos, directories, docs, service units, and runtime state paths to create or
  update.
- **Sprint Packs:** 1-6 execution packs with objective, scope, files, validation, and acceptance gates.
- **Comms:** NATS subjects, inbox/outbox locations, memo routes, and status cadence.
- **Security Boundary:** secret handling, raw-memory policy, production ownership limits, and redaction
  rules.
- **Validation:** commands, service checks, evidence files, and go/no-go criteria.
- **Launch Prompt:** a ready-to-run `/goal` prompt.

## Agent roster pattern

For each agent, define:

```text
Agent:
Role:
Reports To:
Activated When:
Inputs:
Outputs:
Handoff:
Primary Model:
Fallback Model:
Comms Route:
Validation:
```

Keep rosters small for the first sprint. Prefer 3-5 active seats plus a backlog of future seats.

## Model matrix guidance

Choose models by work type:

- **Strategic planning / architecture:** strongest reasoning model available through the approved
  provider pool.
- **Code execution / repo work:** Codex or Hermes-compatible coding lane where local tools are needed.
- **Fast routing / triage:** lower-latency model with strong instruction following.
- **Memory / retrieval / embeddings:** approved embedding provider plus local durable store.
- **Voice / live ops:** low-latency provider and explicit fallback path.

Record only provider names and env var names. Do not print keys or token values.

## Sprint pack format

Each sprint pack should be copyable into a work packet:

```markdown
## Sprint Pack N: <name>

Objective:
Scope:
Inputs:
Files/Paths:
Actions:
Validation:
Acceptance:
Rollback:
Owner:
```

## `/goal` prompt requirements

The launch prompt must include:

- Acting identity or lane.
- Exact worktree/repo/path boundaries.
- Objective and acceptance criteria.
- Security rules.
- Validation commands.
- Commit/push expectations when applicable.
- Explicit instruction to report blockers early and not claim production ownership unless proven.

## Completion

End with:

- artifact paths written or recommended;
- open assumptions;
- first `/goal` prompt;
- recommended first sprint;
- any risks that should be visible to the Tier-1 lead.
