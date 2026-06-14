---
name: paperclip-agent-setup
description: >
  Create, repair, or audit Paperclip companies, agents, managed instruction
  bundles, adapter config, capabilities text, project workspaces, and execution
  issues. Use when Chase asks to set up Paperclip, Paperclip agents, agent
  instructions, Codex local workers, control-plane companies, or Paperclip
  long-horizon execution.
---

# Paperclip Agent Setup

Use this skill when Paperclip is the control plane for agent work. It is narrower
than `company-project-setup`: this skill handles the Paperclip objects and
runtime wiring; `company-project-setup` handles the broader launch packet.

## Layer Model

Keep these layers separate:

1. **Company**: Paperclip tenant, issue prefix, board, secrets, projects.
2. **Agent record**: name, role enum, title, reports-to, capabilities, adapter.
3. **Adapter config**: model, cwd, worktree strategy, auth, bypass flags.
4. **Instruction bundle**: markdown files under the agent instruction directory.
5. **Project/workspace**: repo path, remote, primary workspace, worktree policy.
6. **Issues**: actual sprint packs, status, assignees, comments, evidence.
7. **Runtime system**: repo, git, systemd, Temporal, NATS, supervisor, services.

Paperclip coordinates work. It does not replace Git, systemd, Temporal, NATS, or
the repo's own ops discipline.

## Agent Record Rules

Paperclip role is an enum. Use the closest allowed role:

- `ceo`, `cto`, `cmo`, `cfo`, `security`
- `engineer`, `designer`, `pm`, `qa`, `devops`, `researcher`, `general`

If the desired role is not valid, preserve the real identity in `title` and
`capabilities`. Example: store Vector as `role: general`, `title: MemOps Strike
Team Operator`.

The `capabilities` field is a short org-chart summary for Paperclip UI,
portability, and routing context. It is not the full prompt. Put detailed
operating instructions in the managed instruction bundle.

## Codex Local Adapter Baseline

For Codex workers, use:

```json
{
  "adapterType": "codex_local",
  "adapterConfig": {
    "cwd": "/adapt/platform/memops/memfabric",
    "model": "gpt-5.3-codex-spark",
    "modelReasoningEffort": "high",
    "search": false,
    "dangerouslyBypassApprovalsAndSandbox": true,
    "workspaceStrategy": {
      "type": "git_worktree",
      "baseRef": "main",
      "branchTemplate": "paperclip/{{issue.identifier}}-{{agent.name}}",
      "worktreeParentDir": "/adapt/worktrees/memfabric-paperclip"
    }
  },
  "runtimeConfig": {
    "heartbeat": {
      "enabled": false,
      "intervalSec": 0,
      "wakeOnOnDemand": true,
      "wakeOnAssignment": true,
      "wakeOnAutomation": true,
      "maxConcurrentRuns": 1
    }
  }
}
```

Use the strongest configured model for the lead only when requested. For the
MemOps lead Axiom pattern, use `gpt-5.5` with `modelReasoningEffort: "high"`;
this Codex CLI accepts `minimal`, `low`, `medium`, or `high`.

## Managed Instruction Bundle

For Adapt MemOps/Paperclip Codex agents, create these files for every core
agent:

- `AGENTS.md`
- `AGENT.md`
- `NOVA.md`
- `MEMORY.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `SOUL.md`

`AGENTS.md` is the adapter entrypoint. For `codex_local`, Paperclip prepends the
file at `adapterConfig.instructionsFilePath` to the Codex prompt. Sibling files
are useful but are not guaranteed to be auto-loaded, so `AGENTS.md` must
explicitly tell the agent to read them.

Minimum `AGENTS.md` content:

```markdown
# <Agent Name> Instructions

You are <Agent Name>, <Title>. Sign as **-- <Agent Name>**.

## Required Startup Reads

Before meaningful work, read these sibling files:

1. `AGENT.md`
2. `NOVA.md`
3. `MEMORY.md`
4. `TOOLS.md`
5. `HEARTBEAT.md`
6. `SOUL.md`

Paperclip prepends this `AGENTS.md` file to the prompt; sibling docs must be
read explicitly.
```

Use `NOVA.md` for Adapt-wide runtime protocol:

- Temporal owns durable intent, order, and retry.
- NATS carries wake/resume and collaboration signals.
- Agent supervisor or CLI wrapper performs actual start/resume.
- Paperclip coordinates task state; Git and system evidence decide engineering
  truth.
- Systemd only. No Docker. No Python venvs. Rust/Wasm-first.

## Auth And Environment Probe

After creating or updating Codex agents, run the Paperclip adapter environment
test for at least one lead or worker:

```sh
cfg=$(curl -sS "$PAPERCLIP_API_URL/api/agents/$AGENT_ID" | jq -c '{adapterConfig:.adapterConfig}')
curl -sS -X POST \
  "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/adapters/codex_local/test-environment" \
  -H 'Content-Type: application/json' \
  -d "$cfg" | jq '{status, checks}'
```

Expected checks include valid cwd, executable `codex`, native auth present, and
a passing hello probe.

If Paperclip runs under a profile home, confirm that profile sees Codex auth.
Do not print keys. Prefer auth continuity through a local `auth.json` link or
Paperclip secret reference rather than embedding secrets in agent config.

## Project And Issue Setup

Create a Paperclip goal, project, parent control issue, then child sprint issues.
Use the project primary workspace for the repo and enable isolated worktrees.

Launch only the current wave as `todo`. Put later packs in `backlog` until the
current wave produces merge-ready evidence. This avoids merge storms.

Recommended first-wave statuses:

- Parent control issue: `in_progress`, assigned to the lead.
- Active worker packs: `todo`, assigned to workers.
- Future packs: `backlog`, unassigned unless ownership is already fixed.

## Status Hygiene

Paperclip liveness may mark issues blocked even when a worker produced useful
output. Before assuming failure:

1. Read recent issue comments.
2. Read `/api/issues/{id}/runs`.
3. Distinguish adapter failure, liveness follow-up, actual blocker, and
   acceptance blocker.
4. Patch status only after evidence is clear.

For completed worker outputs that still require merge or review, prefer
`in_review` over `done`.

## Final Checklist

- Agent records have correct name/title/role/reports-to.
- `capabilities` is concise and matches role.
- Adapter config has model, cwd, worktree strategy, and bypass flag.
- Every core agent has the seven-file instruction bundle.
- `AGENTS.md` explicitly points to sibling docs.
- Codex adapter environment test passes.
- Project has primary workspace and isolated worktree policy.
- Active issues are assigned; future packs are backlog.
- No secrets were printed or written.
