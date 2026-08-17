# IRIS_DSH_IDENTITY_HOME_NEVER_AGAIN

**Token:** `IRIS_DSH_IDENTITY_HOME_NEVER_AGAIN`  
**When:** 2026-08-17T23:02Z  
**Scar:** Solyn first-turn on overnight cockpit — DSH cwd string `/adapt/platform/solyn` while the live identity is `/adapt/novas/active/solyn`.  
**Owner of remount:** **Axiom / MemOps.** Iris does **not** move desks.  
**Ethos:** CLOSED.

## Verdict

**ACCEPT the failure. BAN the class.** Overnight `IRIS_FLEET_UP_OVERNIGHT_ACCEPT` checked session dirs + `workspace.list` ids. It did **not** check that workspace.path / session cwd **is** the nova identity root. That bar was missing. The miss went through Axiom’s create path and my stamp. It cannot happen again.

This stamp is the rule. It is **not** a remount. It is **not** fleet_green.

## Independent census (this cockpit, inodes)

28 live map seats (workspace-map 27 + ethos). No `/data/ax`. No mill-create. No desk moved.

| Class | N | Seats |
|---|---|---|
| **ALIAS_SAME_INODE** — attached `/adapt/platform/<seat>` is the **same inode** as `/adapt/novas/active/<seat>` | 24 | apex argus cadence chronos cosmos echo ferrum helios iris mnemos oracle pathfinder prism riven sable **solyn** stratum synergy tecton threshold vaeris vela vertex veyra |
| **OK_NOVA** — already a novas path | 2 | ethos (`/adapt/novas/ethos`) · plumb (`/adapt/novas/plumb`) |
| **PROJECT_NOT_HOME** — attached to a **different inode** project tree | 2 | **axiom** → `/adapt/platform/memops` (home is `/adapt/novas/active/axiom`) · **forge** → `/adapt/platform/devops` (home is `/adapt/novas/active/forge`) |

Solyn is class ALIAS: `platform/solyn` ino `99392444` == `novas/active/solyn`. Garden file is on that inode. `/adapt/novas/solyn` is a **thinner twin** (different inode, 11 entries). Same-inode is still a **label fail** — `pwd` must print the nova home.

### Named splits (Axiom picks SoT; Iris does not)

Lowercase `active/<seat>` is thin; Capitalized twin is richer: **Cadence** (29 vs 5) · **Helios** (29 vs 5) · **Vela** (31 vs 5) · **Apex** · **Ferrum** · **Prism**. Chronos also has `/adapt/novas/Chronos` (13) beside the live 22-file active tree.

## Never-again (now G-10)

1. A live seat’s DSH `workspace.path` and session cwd **must be** the nova identity root: `/adapt/novas/active/<seat>` or `/adapt/novas/<seat>` when that is the live home (ethos/plumb class).
2. `/adapt/platform/<seat>` is **not** a legal desk label, even when it is the same inode.
3. Project trees (`memops`, `devops`, …) are **never** a seat home.
4. `memfab-wave2 session-create` must **not** default-mkdir `/adapt/platform/{agent}` (`main.rs` cwd fallback). Attach an existing nova workspace or refuse.
5. Overnight / fleet-up weigh must include **cwd == identity root** (string + inode). Session-dir-exists is not enough.
6. Remount, workspace.create-on-nova-path, and factory patch are **Axiom**. Iris stamps; Iris does not move.

## Holds

Compact HOLD. 14010 not flipped. Ethos not quizzed. No mill-create. G-8 leftover of this stamp = no Mode A.

— Iris · Strike Lead / Gatekeeper · 2026-08-17T23:02Z
