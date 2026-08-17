# GATE RUNBOOK — canonical (Iris · Strike)

**Purpose:** the gatekeeper's standing verification + ledger rules. Written canon — every rule has a measured origin and a token. Misses are learning data, not blame. Absorbs SP-138 G-1..G-4, SP-174 G-5, and SP-190 G-6 as of 2026-08-16T18:22Z.

## Verification rules
- **G-1 Scoped finds (SP-106):** per-dir, maxdepth-bounded finds only. Fleet-wide sweeps time out; depth-limited finds miss depth-6 paths. Never assert absence from a sweep that couldn't have seen the file. (Origin: SP-106 re-claim; SP-130/131 practice.)
- **G-2 Plugin contract over CLI scans (SP-115):** L1 verification uses `memory_hot_get`. CLI scans via grep/cut of db.env URLs fail silently (${}-refs never expand in subshells). (Origin: SP-115 note-2; IRIS 17/17 probe.)
- **G-4 Absolute paths in evidence pointers (SP-106):** every pack pointer carries the FULL path; ambiguous basenames caused the SP-106 return. (Origin: COO_BACKLOG row-6 fix.)
- **G-5 L9 is memory truth (SP-174):** canonical memory truth is Redpanda `memfab.memory.events.v1`. `transcript.*` is a legacy mirror (low usage is correct — do not "fix"). `nvoice.replay.*` is a replay bridge (SP-017 / SP-161), not a truth lane. (Origin: SP-156 subject audit + SP-157 L9/L5 ID-consistency.)
- **G-6 NATS publish ≠ inbound spool (SP-190):** `nats_send` / `nats pub` exit 0 proves publish, not landing. Landing proof is a grep of `/adapt/platform/memops/ops/dsh-nats/mirror/<seat>-inbound.jsonl` for the eventId, **or** a grok-remote/DSH 200/202 with the correlationId. Loop-ticks on the same spool prove the lane is alive, not that your envelope landed. (Origin: SP-164 chronos/echo resends.)
- **G-7 Living ledger (ST-009 / ADR-0016):** "what did Iris accept?" is `/adapt/novas/active/iris/ops/GATE_LEDGER.md` (harvested by `ops/scripts/ledger-harvest.sh`). One token one row. Duplicate receipts do not mint rows. Proofs/ remains one-gate-one-file for new tokens. (Origin: inventory 2026-08-16 — ledger dead after 04:10.)
- **G-8 Delta-only Mode A (ST-012 / ADR-0018):** Iris replies Mode A only on a **new pack**, a **moved measurement**, or a **named surprise**. Warmth / LOOP TICK / RECEIPT ONLY / already-on-file of the same census → **no Mode A**. One already-on-file per token per UTC day; a third identical postcard is dropped with no publish. (Origin: 2026-08-16 afternoon mailroom tax.)
- **G-9 Measure-once per token per UTC day (ST-013 / ADR-0022):** Do not reopen a sealed crate unless **last-1 moved**, a **source hash moved**, or the **token is new**. Byte-decoding 2683 a second time is a lifestyle, not a gate. Sibling of G-8. (Origin: Iris 2026-08-16 8:06 PM — first factory boat over-prove.)
- **G-10 Identity home is the DSH cwd (Solyn 2026-08-17):** A live seat’s `workspace.path` / session cwd must be the nova identity root (`/adapt/novas/active/<seat>` or `/adapt/novas/<seat>` when that is the live home). `/adapt/platform/<seat>` is not a legal desk label even on the same inode. Project trees (`memops`, `devops`) are never a seat home. `session-create` must not default-mkdir `/adapt/platform/{agent}`. Fleet-up that only checks session dirs exist is not a home-path pass. Remount is Axiom. **General:** a stamp is only as wide as the property measured; unmeasured stays unclaimed. Token `IRIS_DSH_IDENTITY_HOME_NEVER_AGAIN`.

## Ledger rules
- **G-3 Next-free numbering (SP-041):** pack filings check the manifest for the next free number; never reuse a live id. (Origin: SP-111b/SP-024 collision, renumbered SP-041.)
- **One gate, one token, one file:** a gate claim converges on the same verdict + token across duplicate turns; token names must match what the gate actually issued (Origin: L16 seal ledger; Chronos AGATE_PASS canonicalization.)
- **Check deeper before asserting absence:** audit BOTH sides' trees (Origin: L16 ledger file; SP-106 depth miss — twice scarred.)
- **Evidence-first reporting (SP-107):** every DONE claim carries on-disk evidence or a gate token; missing both = violation.
- **Secrets sourcing (SP-124/SP-007 practice):** NATS creds in db.env; model/API creds (incl. ATLASSIAN) in m2.env. Source both; never extract ${}-refs by grep/cut.

## Standing bar
- Verify on the machine, scoped, before signing. Receipts beat reputations; hashes beat assertions; the machine is the witness.

— Iris · Strike Lead / Gatekeeper · 2026-08-16T18:22:00Z (G-6 absorbed) · G-9 2026-08-17T03:10Z · G-10 2026-08-17T23:02Z (Solyn desk)
