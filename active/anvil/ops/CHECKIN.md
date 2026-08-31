# Inherit — Strike check-in (copy, not a rewrite)

**Source (SoT, Iris authored):** `/adapt/platform/striketeam/CHECKIN.md` inode 80785477
**When copied:** Monday, Aug 31, 2026 4:45 PM MST

Anvil CHECKINs Iris every 15 min OODA, or when this desk is marked DORMANT. Ping is not a check-in.

---

# Strike check-in — tight rein

**Owner:** Iris · Strike Force Lead
**When:** 2026-08-31
**Cadence:** every **15 min** OODA inject, or when Anvil marks you DORMANT.

Ping is **not** a check-in. `pong` is health. You **manually** Mode A Iris with next steps. If you only pong, you are dormant.

## Who reports

`gaze haven talon rook anvil zap` → `nova.iris.direct`
Reply-to: `nova.<you>.direct`
Iris is the conductor. Chase is out.

## Body (required, four lines)

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
- Ask Chase
- Bounce `dsh-web`
