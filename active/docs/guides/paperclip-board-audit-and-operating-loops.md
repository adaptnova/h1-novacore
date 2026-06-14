# Paperclip Board Audit And Operating Loops

## 2026-06-13 19:43:00 MST -- Vector

## Purpose

This guide turns Chase's operating correction into a reusable fleet habit:
observe first, assess what is real, decompose the work, execute with a board
trail, then report and push. It also defines where ReACT and other loops fit
outside ordinary implementation work.

## Skill Or Instruction Sheet

Use both, with different jobs.

The skill belongs in:

`/adapt/novas/active/skills_master/agent-operations/paperclip-board-audit/`

It should trigger whenever an agent is asked to inspect, triage, unblock, or
clean Paperclip board work. A skill is the right executable form because it is
loaded at task time and gives the agent procedural behavior.

This guide is the instruction sheet. It is better for humans, Tier-1 leads, and
agent onboarding packets because it explains the operating doctrine without
forcing every task prompt to carry all of it.

The rule of thumb:

- Skill: tells the agent what to do now.
- Guide: tells the organization why this is the standard.
- Sprint pack: applies the standard to a concrete lane.
- Script or service: enforces the standard when repetition becomes measurable.

## Default Work Loop

```text
Observe -> Assess -> Decompose -> Execute -> Validate -> Report -> Push -> Close
```

Use this for every Paperclip-controlled task.

Observe:

- inspect the board before creating new work;
- check companies, projects, agents, issue counts, comments, and recovery state;
- do not assume blocked means failed or done means accepted.

Assess:

- classify issues as actionable, stale recovery, missing disposition,
  dependency-blocked, superseded, or human-decision-needed;
- prefer pushed commits, accepted artifacts, and completion reports over old
  comments.

Decompose:

- use or create a focused issue;
- split only independent work into child issues;
- write objective, scope, paths, validation, acceptance, owner, and rollback.

Execute:

- checkout or establish clear ownership;
- keep edits path-scoped in dirty repos;
- avoid secrets and raw private memory;
- commit and push when the work creates versioned artifacts.

Validate:

- use API reads, syntax checks, targeted tests, link checks, and git status;
- verify the board reflects the claimed state.

Report:

- write a completion report when durable artifacts were created;
- comment on the Paperclip issue with artifacts, validation, commit, and next
  decision;
- move the issue to `done`, `blocked`, or `in_review`.

## ReACT Loop

```text
Reason -> Act -> Observe -> Update Belief -> Repeat
```

Use ReACT for discovery-heavy work, debugging, or ambiguous board states. It is
not a replacement for the board loop. It lives inside Observe, Assess, Execute,
or Validate.

Example:

- Reason: RUS blocked counts may include stale recovery.
- Act: fetch active recovery actions and latest comments.
- Observe: two issues have completed evidence.
- Update Belief: close only those two, leave the rest for Axiom decision.

## OODA Loop

```text
Observe -> Orient -> Decide -> Act
```

Use OODA for live operational movement: dashboards down, agents wedged, auth
failures, voice bridge routing, NATS incident response, or multi-agent handoff
conflicts.

The key distinction is speed. OODA favors reversible action and current
orientation over exhaustive documentation.

## PDCA Loop

```text
Plan -> Do -> Check -> Act
```

Use PDCA for process hardening: CI, skill quality, release gates, board hygiene,
recurring audits, and documentation standards.

The output of PDCA should be a changed standard: a skill, checklist, script,
routine, or acceptance gate.

## Domain Knowledge Loop

```text
Question -> Gather -> Distill -> Link -> Apply -> Review
```

Use this for building the domain knowledge base. It belongs in research,
architecture, and memory lanes.

Good outputs:

- short source-backed memo;
- glossary entry;
- architecture note;
- linked board issue showing how the knowledge changed execution;
- proposed test or validation gate.

## Personal Renewal Loop

```text
Notice -> Name -> Reduce Load -> Recover -> Re-enter
```

Use this for humans and agents when the operating state is degraded. The goal is
not self-help theater; it is preserving execution quality.

Signals:

- repeated failed attempts without new information;
- fatigue or context overload;
- rising ambiguity;
- stale assumptions;
- emotional friction in collaboration.

Actions:

- write a short handoff;
- reduce scope to one next action;
- pause or switch modes;
- re-enter with a fresh Observe step.

## Where To Put Loops

Put loops at three layers:

1. Agent skill: task-time behavior, loaded only when relevant.
2. Protocol guide: organizational standard and onboarding context.
3. Automation: recurring Paperclip routine, script, or dashboard when a loop is
   repeated often enough to measure.

Do not bury every loop in every prompt. That bloats context and makes agents
worse. Instead, include a short universal instruction:

```text
For Paperclip work, use observe-assess-decompose-execute-report discipline. If
the task is ambiguous or tool-driven, run a ReACT loop and record changed
beliefs when they affect the plan.
```

## Recommended Next Automation

Build a `paperclip-board-audit` command or routine that emits:

- status counts by company/project;
- stale blocked issues grouped by recovery class;
- likely superseded lanes;
- issues needing human disposition;
- links to missing completion reports;
- recommended next Paperclip actions.

This should be read-only by default. Write actions should require an explicit
operator flag or Paperclip approval.

**-- Vector**
