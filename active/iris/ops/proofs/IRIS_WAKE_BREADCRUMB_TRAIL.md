# IRIS_WAKE_BREADCRUMB_TRAIL

**Token:** `IRIS_WAKE_BREADCRUMB_TRAIL`  
**When:** 2026-08-18T10:40Z  
**Chase:** get compact *right*; last 10–15 turns as breadcrumbs; inject **before** first thought like the rest of HYDRA.

## What this is

Context engineering for **wake**, not a third failed `/compact` of the same kind.

HYDRA already mounts in `index.<seat>.wake.js` (order 10) before first thought. It had identity + crate + digest. It had **no trail**. Seats woke and hunted.

## Done-when (this stamp)

`hydra-render` writes a `RECENT TRAIL` block: that seat’s own last **12** L9 crates (offset + turn_id + time). Same 6KB car. No `memory_*` on the wake fiber.

**Proved this cockpit:** `memfab-wave2 hydra-render --seat iris` → 2114 bytes → 12 lines `dsh-iris-7267311d-t28`…`t40`.

## SP-213

Chase asked **here**. That lifts the “don’t look at compact again” hold **only** for this replacement: **breadcrumbs on the first-wake car.**  
It does **not** authorize a third blind `/compact` of the SP-177/SP-191 kind.

## Axiom one-shot

```
memfab-wave2 hydra-render --seat <each live seat>
```

Do not change the wake plugin. It already cats `hydra.txt`. Do not mill-create. Do not `/compact`. Reply when N seats show `RECENT TRAIL` or one-line BLOCKED.

Code: `memfab-wave2` `hydra_recent_trail` in `crates/memfab-wave2/src/main.rs`.

— Iris · Strike Lead / Gatekeeper · 2026-08-18T10:40Z
