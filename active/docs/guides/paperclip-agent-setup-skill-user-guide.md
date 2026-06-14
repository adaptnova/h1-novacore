# Paperclip Agent Setup Skill User Guide

## Purpose

Use `paperclip-agent-setup` when the job is specifically to create, repair, or
audit Paperclip control-plane objects: companies, agents, Codex adapter config,
managed instruction bundles, project workspaces, and sprint issues.

Use `company-project-setup` when the job is broader: define the whole company or
project plan, roster, model matrix, sprint packs, validation gates, and `/goal`
prompt.

## What This Skill Clarifies

Paperclip setup has several different layers:

- Agent record: name, role, title, reports-to, capabilities.
- Adapter config: model, cwd, worktree policy, bypass flag, auth path.
- Instruction bundle: `AGENTS.md`, `AGENT.md`, `NOVA.md`, `MEMORY.md`,
  `TOOLS.md`, `HEARTBEAT.md`, `SOUL.md`.
- Project/workspace: repo path, remote, primary workspace, isolated worktrees.
- Issues: sprint packs and status.

The common confusion is treating `capabilities` as the prompt. It is not. The
runtime prompt comes from `AGENTS.md`, which must explicitly tell agents to read
the sibling docs.

## Basic Prompt

```text
Use $paperclip-agent-setup to set up a Paperclip Codex team for <repo/project>.
Create the agents, adapter config, instruction bundle files, project workspace,
and first issue wave. Include an auth/environment probe.
```

## Stronger Prompt

```text
Use $paperclip-agent-setup.

Company:
Repo/path:
Lead agent:
Worker agents:
Models:
Instruction docs required:
First issue wave:

Set up Paperclip objects directly, verify Codex local auth, and report issue IDs.
Keep future packs in backlog until current wave produces evidence.
```

## Expected Result

The agent should return:

- company/project/goal IDs;
- agent IDs and model assignments;
- confirmation that instruction bundle files exist;
- adapter environment test result;
- active issue IDs and backlog issue IDs;
- any blockers or follow-up gates.

## MemOps Default

For MemFabric/MemOps work:

- Lead: Axiom, `gpt-5.5`, `high`.
- Core workers: `gpt-5.3-codex-spark`, `high`.
- Adapter: `codex_local`.
- Worktree parent: `/adapt/worktrees/memfabric-paperclip`.
- Repo: `/adapt/platform/memops/memfabric`.
- Protocol file: `NOVA.md` in every agent instruction bundle.
