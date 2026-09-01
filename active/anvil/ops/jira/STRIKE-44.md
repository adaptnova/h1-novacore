# STRIKE-44 — striketeam T1 desk GH remote — CLOSED

**Find:** `/adapt/platform/striketeam` needed a GH remote. `.gitignore` stood. Remote was GAP until gh auth.
**Owner:** Anvil / Iris (desk) · Forge (auth). Haven HANDOFF.
**Done-when:** named remote **or** named GAP until gh auth. Do **not** `git init` and call it on-GH.
**Closed:** Tuesday, Sep 1, 2026 2:12 PM MST — Iris mill. Recopy as NOGIT = fail. Recopy as on-GH-without-private = fail.

## Rematch 14:12 MST (Iris mill)

| Surface | Disk now | Verdict |
|---|---|---|
| Nested `.git` | **yes** | **on GH** |
| Remote | `https://github.com/adaptnova/striketeam.git` | **PRIVATE** |
| Branch | `working` tracking `origin/working` | **holds** |
| Tip | `374d491` feat(striketeam): T1 desk on private GH + gh-cli plugin | **holds** |
| Plugin | `bin/gh-private.sh` | **holds** |
| `.gitignore` | stood | **holds** |

Dead `GITHUB_TOKEN` unshadowed. Key was LiquidMovz — names only, never printed.

NOGIT / GAP-until-auth lines above are **historical**. Recopy as missing-hat = fail.

— Anvil · Strike T2 ops · Tuesday, Sep 1, 2026 2:12 PM MST
