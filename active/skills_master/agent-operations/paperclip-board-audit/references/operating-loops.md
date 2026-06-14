# Operating Loops

Use loops deliberately. A loop should reduce recurring uncertainty, not add
ritual.

## Board Execution Loop

Use for Paperclip-controlled implementation:

```text
Observe -> Assess -> Decompose -> Checkout -> Execute -> Validate -> Report -> Push -> Close
```

Best for: board hygiene, sprint packs, code/doc changes, recovery work.

Exit condition: pushed evidence and a Paperclip disposition.

## ReACT Loop

Use when reasoning and tool action need to alternate:

```text
Reason -> Act -> Observe -> Update Belief -> Repeat
```

Best for: debugging, API discovery, unknown board state, incident response.

Guardrails:

- keep each action small enough to learn from;
- record belief changes when they alter the plan;
- stop when evidence supports a disposition.

## OODA Loop

Use when the environment changes quickly:

```text
Observe -> Orient -> Decide -> Act
```

Best for: live ops, multi-agent coordination, dashboard incidents, auth/runtime
failures.

Guardrails:

- orient with current owners, blast radius, and time sensitivity;
- choose a reversible action first when uncertainty is high.

## PDCA Loop

Use for process improvement:

```text
Plan -> Do -> Check -> Act
```

Best for: skill quality, CI hardening, release discipline, recurring board
audits.

Exit condition: new standard, checklist, or automation merged into the workflow.

## Domain Knowledge Loop

Use for building durable expertise:

```text
Question -> Gather -> Distill -> Link -> Apply -> Review
```

Best for: MemFabric, NATS, WASI, Rust agents, model/provider behavior, company
operating knowledge.

Artifacts:

- short memo with sources and decisions;
- glossary or concept map;
- task links showing where the knowledge changed execution.

## Personal Renewal Loop

Use for sustaining agent/human operating quality without pretending rest is
implementation work:

```text
Notice -> Name -> Reduce Load -> Recover -> Re-enter
```

Best for: fatigue, context overload, repeated failed attempts, escalating
frustration, or long overnight runs.

Artifacts:

- brief pause note or handoff;
- reduced-scope next action;
- explicit re-entry condition.

## Meta Loop

Use when the workflow itself is failing:

```text
Detect Friction -> Extract Pattern -> Change Protocol -> Test On Next Task
```

Best for: repeated missing dispositions, poor handoffs, duplicated work,
unclear authority, or stale board states.

Rule: if the same failure appears three times, make it a protocol, skill,
script, or board automation.
