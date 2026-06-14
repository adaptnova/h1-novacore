---
name: paperclip-board-audit
description: >
  Audit Paperclip boards before execution: observe companies/projects/issues,
  classify blocked and stale work, decompose actionable tasks, write board-ready
  reports, and move work through checkout, completion, comments, commits, and
  push. Use when Chase or a lead asks to inspect board health, clean blocked
  tasks, create sprint packs from board state, or enforce observe-assess-execute
  discipline.
---

# Paperclip Board Audit

Use this skill when Paperclip is the operating board and the first job is to
understand the board before changing anything.

## Required Posture

1. Observe before adding, editing, closing, or assigning.
2. Assess evidence instead of trusting issue status alone.
3. Decompose work into an explicit Paperclip issue or subtask before execution.
4. Execute only after checkout or a clear board ownership trail exists.
5. Report through both artifacts and Paperclip comments.
6. Push committed artifacts when the repo is part of the work.

Use the `paperclip` skill for API mechanics and comments. This skill adds the
board-audit decision model.

## Fast Workflow

### 1. Observe

Collect the minimum complete board picture:

- companies, agents, and projects in scope;
- issue counts by status;
- active `todo`, `in_progress`, `in_review`, and `blocked` work;
- latest comments and active recovery actions for candidate issues;
- parent/child links, dependency blockers, and project/workspace ownership.

Do not create new tasks during observation unless the user explicitly gave the
task and there is no existing board lane for it.

### 2. Assess

Classify each candidate issue:

- `actionable_now`: clear next step and ownership exists;
- `needs_disposition`: successful or useful work exists but final state is
  missing;
- `stale_recovery`: adapter/runtime/retry failure is masking board state;
- `dependency_blocked`: downstream task correctly waits on another issue;
- `superseded`: replaced by newer accepted lane or commit evidence;
- `needs_human_decision`: authority or product direction is missing.

Prefer the newest accepted artifact, pushed commit, or completion report over
older comments.

### 3. Decompose

Before implementation, make the work board-visible:

- use an existing issue if it already names the work;
- otherwise create a focused issue under the right project;
- add child issues only for independently executable work;
- keep future work in `backlog` until the current gate is accepted.

Each task should have objective, scope, files/paths, validation, acceptance,
owner, and rollback or supersession criteria.

### 4. Execute

After checkout or confirmed ownership:

- keep edits path-scoped in dirty repos;
- avoid raw secrets, provider payloads, private memory, and SOUL content;
- write durable artifacts in the owning board/docs path;
- validate with syntax checks, link checks, API reads, or targeted tests;
- commit with the Paperclip co-author trailer when committing Paperclip work.

### 5. Report

Always produce a completion trail:

- board comment with status, artifacts, validation, commit, and next decision;
- completion report when the task produced durable artifacts;
- issue status update to `done`, `blocked`, or `in_review`;
- pushed branch/commit when version control applies.

If blocked, say who must act and what decision or evidence is needed.

## Audit Output Shape

Use this concise report shape unless the lead asks for another format:

```markdown
# Paperclip Board Audit

## Scope

## Board Summary

## Actionable Now

## Blocked Or Stale

## Superseded Or Done

## Decomposed Tasks

## Decisions Needed

## Recommendation

## Validation

## Completion Trail
```

## Loop Catalog

For ReACT, OODA, PDCA, and personal/domain-knowledge loops, read
`references/operating-loops.md` only when the task asks for loop design or
recurring workflow design.
