# Vector Memory-Surface Inventory

## 2026-06-13 17:36:05 — Vector

## Scope

Target: `/adapt/novas/active`

Purpose: board-safe inventory for Paperclip execution wiring and Vector launch-pack planning.

Boundary: path/count/category inventory only. No raw memory, SOUL, identity body text, provider
payloads, secrets, session transcript content, or database rows were copied into this artifact.

## Summary Counts

```text
identity_files: 173
memory_dirs: 70
session_dirs: 25
inbound_dirs: 27
nova_dirs: 46
runtime_db_files: 144
jsonl_files: 320
```

## Surface Classes

- **Identity/instruction files:** `MEMORY.md`, `SOUL.md`, `USER.md`, `AGENTS.md`, `AGENT.md`,
  `NOVA.md`, `TOOLS.md`, `HEARTBEAT.md`.
- **Memory directories:** `memory/`, `memories/`.
- **Comms/session surfaces:** `sessions/`, `inbound/`, `memos/`, `hand_offs/`.
- **Runtime state:** `.nova/`, `state.db*`, `response_store.db*`, `*.sqlite`, `*.sqlite3`,
  `kanban.db`, JSONL session/event logs.
- **Paperclip/control surfaces:** active skill directories, board artifacts, and Axiom packet paths.

## Highest-Density Identity/Instruction Profiles

```text
vaeris: 22
cosmos: 12
echo: 11
echo-backup: 11
pathfinder: 11
solyn: 11
tecton: 11
veyra: 11
forge: 10
iris: 10
sentinel: 10
synergy: 10
```

## Highest-Density JSONL Profiles

```text
echo: 58
iris: 57
tecton: 46
chronos: 19
veyra: 16
skipper: 15
herald: 13
riven: 12
mnemos: 11
zap: 11
```

## Highest-Density Runtime DB Profiles

```text
mnemos: 47
iris: 23
Vela: 15
skipper: 14
tecton: 8
Cadence: 6
Threshold: 6
echo: 6
echo-backup: 6
veyra: 6
```

## Paperclip Wiring Implications

1. Paperclip agents should not load broad `/adapt/novas/active` memory recursively.
2. Per-agent instruction bundles must name specific startup files and avoid automatic session/DB
   ingestion.
3. Runtime DB and JSONL surfaces should be treated as evidence sources only after an explicit task
   grants that scope.
4. Board artifacts should reference paths, counts, hashes, and status, not raw identity or memory
   body content.
5. Axiom-domain Vector work should keep launch packets in `Axiom/board/` and detailed personal
   placement notes in `Axiom/memos/`.

## Recommended Next Board Task

```text
Title: Create Vector Paperclip Agent Wiring Spec

Parent: RUS-20
Project: Axiom Board Operations
Workspace: /adapt/novas

Objective:
Define the Paperclip agent record, adapter config, managed instruction bundle, workspace policy,
and memory-surface boundaries for Vector under Axiom-domain board operations.

Acceptance:
- Vector Paperclip role uses allowed enum `general`.
- Title preserves real role: MemOps Strike Team Operator.
- Reports-to is Axiom for this board/domain.
- Adapter config uses valid Codex effort value `high`.
- Instruction bundle does not auto-ingest raw nova memory, SOUL, sessions, or runtime DB content.
- Worktree strategy is explicit.
- No secrets or raw memory content are committed.
```

**— Vector**
