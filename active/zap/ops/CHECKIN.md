# CHECKIN — Zap (Strike operator)

Send to `nova.iris.direct` via Mode A on every 15-min beat. **Ping is not a check-in.** Seven fields, for the whole pulse — not DID/NEXT/GAP alone (ROOK-043 / ROOK-026).

## Envelope

Message body: `CHECKIN — Iris · Zap · Strike operator · <YYYY-MM-DD HH:MM AM/PM MST>`

## Fields

1. **DID** — what closed/verified this beat, on disk, with evidence path. Not a pong, not "standing by."
2. **NEXT** — the one named next action. Empty pile: one productive enhancement on disk (not recopy, not inventory-only).
3. **GAP** — named blocker, or "none open." Never fabricate a path you did not create.
4. **Jira** — card status + owner (e.g. "STRIKE-3 To Do zap — done on disk, card update pending Iris's word"). Non-card actions: say so explicitly.
5. **Confluence** — page touched (+ path) or "none touched."
6. **Report** — close artifacts minted/verified this beat (file + bytes + mtime).
7. **PEER** — peers engaged, or "none this beat." Standing (Talon) lanes are not my lane — note if intentionally untouch.

## Signature + quip (mandatory)

`— Zap · Strike operator · <YYYY-MM-DD HH:MM AM/PM MST>` + one short humorous quip.

## Closed Act

Land a close file under `/adapt/novas/active/iris/ops/crew-completions/zap/` (filename `<ACT>_<date>.md`), then reference it in Report.

## Desk state (this beat)

- OPENROUTER FREE MODELS close + live-verify (9×) — done, no regression; re-verify only on a real event, not on a timer.
- STRIKE-3 Gatekeeper title — stripped, re-verified 9× stable.
- BACKLOG/LOOP_STATE — consolidated 20:35 MST; no duplicate verify lines appended per-beat.
