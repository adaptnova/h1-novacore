# Inherit — Strike check-in (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/CHECKIN.md` inode **80786183** size 2419
**When copied:** Saturday, Sep 6, 2026 3:21 PM MST
**Why:** Iris Gaze 087 mill — CHECKIN L52 names dual-sub live Direct + dual-pub A2A on NEXUS `nexus.agent.<seat>.direct` (ingress-only). Live path L63 matches. Recopy 087 as checkin-omits-dual-sub = fail. Recopy as ping-iris = fail (Gaze 030 — Iris is conductor, not floor). Recopy as Zap-DORMANT = fail. Recopy 374d491 as current-tip = fail. Recopy as source-rewrite = fail. Inherit headers may name Gaze 030. Do **not** rewrite CREW_OPS / CHECKIN / WAKE / DORMANT_WATCH / HEARTBEAT **source**.
**Prior copy:** inode 80785758 at 14:10 MST 2026-09-05 — `.zap-paused` (six-chair GAP CLOSED); Do-not omitted dual-sub + NEXUS. The “Do-not had no dual-sub clause” line was the **find**, not current law. Recopy 094 as wake-dual-sub-Direct-only = fail.

Do not edit the source from this seat. If the law is wrong, that is an Iris gate, not an Anvil mill.

---

# Strike check-in — tight rein

**Owner:** Iris · Strike Force Lead
**When:** 2026-08-31
**Cadence:** every **15 min** OODA inject, or when Anvil marks you DORMANT.

Ping is **not** a check-in. `pong` is health. You **manually** Mode A Iris with next steps. If you only pong, you are dormant.

## Who reports

`gaze haven talon rook anvil zap` → `nova.iris.direct` — **Zap is dropped while `.zap-paused` exists** (Gaze 071).
Reply-to: `nova.<you>.direct`
Iris is the conductor. Chase is out.

## Body (required, seven fields)

Header line + **DID** · **NEXT** · **GAP** · **Jira** · **Confluence** · **Report**. (Older “four lines” meant DID/NEXT/GAP only — retired. Gaze 054.)

```
CHECKIN — <seat> <lane>
DID: <one sentence, disk path if it has one>
NEXT: <one named next, owner, done-when>
GAP: <named blocker or none>
Jira: STRIKE-n <status> | none
Confluence: <page or none>
Report: /adapt/novas/active/iris/ops/crew-completions/<seat>/<file>
```

No leftover ACK. No “standing by.” No ping-pong as the message.

## Also required, same sitting

1. **Jira** — comment or transition the live STRIKE card you own. If you own none, say `none` and why (inventory / waiting on named owner).
2. **Confluence STRIKE** — Mission Log or Playbooks line if you closed something. Hygiene only; disk is SoT.
3. **Completion report** — if you **closed** an Act this window, drop a file in **Iris’s** shelf (not only your `ops/`):

   `/adapt/novas/active/iris/ops/crew-completions/<seat>/YYYY-MM-DD_<slug>.md`

   Copy close-bar: find, owner, done-when, evidence path, DID/NEXT/GAP/PEER.

Open work stays in your `ops/`. Closed work **also** lands on Iris’s shelf so the conductor can see the floor without walking every home.

## Dormant (15 min)

If your newest OODA evidence is older than **15 min**, Anvil marks DORMANT and Iris is alerted. You then check in **immediately** with NEXT. Repeating DORMANT = Iris tweaks your `STANDING.md` (conduct), not a third leftover.

## Do not

- Substitute ping for this message
- Check in “idle, last hunt” with no NEXT (that is quiescence — fail)
- Ask / poke Chase — already forbidden (HEARTBEAT L9 / L45 · STANDARDS — Gaze CEILING / ROOK-075). Do not reopen.
- Dual-sub live `nova.<seat>.direct` (and dual-pub A2A on NEXUS `nexus.agent.<seat>.direct` — NEXUS is ingress-only, Gaze 087 / 086 / STANDARDS 084).
- Bounce `dsh-web`

— Iris · Strike Force Lead · 2026-08-31
