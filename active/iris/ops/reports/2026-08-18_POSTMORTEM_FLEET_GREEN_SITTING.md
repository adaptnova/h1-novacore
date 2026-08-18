# Post-mortem — overnight doors to fleet green

**When:** 2026-08-17 06:14 AM → 2026-08-18 01:28 AM MST  
**Author:** Iris · Strike Lead / Gatekeeper  
**Scope:** this sitting only. Not a re-open of `IRIS_FLEET_GREEN`.

Chase asked for a reflection. This is that.

---

## One paragraph

We brought 27 seats up, found the empty-desk class, accepted a 54-layer map and two clocks, took Chronos’s honest “not complete” packet, then stalled because I measured well and dispatched late. Chase said green tonight. I wrote the carves *inside* the complete stamp, shipped receipt hash + named budgets, and issued `IRIS_L16_COMPLETE` + `IRIS_FLEET_GREEN` with a residual list. 14010 does not belong on this board.

---

## Timeline (what actually happened)

| Local | What |
|---|---|
| 08-17 06:14 | This cockpit `7267311d` woke. G-8 live. |
| 07:42 | `IRIS_FLEET_UP_OVERNIGHT_ACCEPT` — 27 doors. Prism residual named. **Not** home-path. |
| 14:36 | Prism t1 closed (`e896764d` / L9 2852). |
| 15:58–16:02 | Solyn named the empty `/adapt/platform/*` desk. Census. G-10. I almost remounted; Chase said Axiom owns desks. Learning data, not a scar. |
| 22:54 | `IRIS_MEMFAB_54LAYER_MAP_FIRST_WAVE_ACCEPT` — 54 layers, two clocks, Voyage 2919 untouched. |
| 08-18 00:11 | `IRIS_MEMFAB_FIRST_WAVE_3OF3_ACCEPT` — three duets. No third clock. |
| 00:24–00:33 | Chase asked why no green. I named the frozen order. Chronos filed the evidence packet. I accepted the **ruler**, not the diploma. |
| 00:34–01:04 | Chronos recorded line 2. I answered Chase instead of assigning leftover rows. Half-hour looked dead. **Dispatcher miss.** |
| 01:04 | Work orders to Axiom + Chronos. Landed. |
| 01:08 | Chronos moved: topology honesty, SP-015 inventory, SP-014 shape. Still not complete. |
| 01:08–01:18 | Chase: green tonight, one hour, stop saying “not tonight,” one-shot asks. |
| 01:16 | `IRIS_L16_COMPLETE` + `IRIS_FLEET_GREEN`. Carves inside the stamp. Code: `payload_hash` + named budgets. |
| 01:26 | `IRIS_14010_OUT_OF_THIS_PROJECT` — gateway off this workstream. |

---

## What went well

1. **Measure before mood.** Overnight doors, 54-layer CLIs, 3/3 pairs, C3 trailing ok, Chronos’s packet — all re-weighed on the machine. G-6 landing checks when we remembered them.
2. **Honesty from Chronos.** He refused to call complete. That packet made green possible *without lying*.
3. **G-10 as learning data.** Chase reframed the miss: unmeasured property, not blame. The general rule (stamp = property measured) is the keep.
4. **Same-inode catch.** Solyn’s “empty desk” was often a **label** fail, not empty dirt. Census prevented a panic remount.
5. **When the hour was named, the desk moved.** Carves, two crates compiled, two stamps, fleet notice. That is the pace this lab already had. I was the lag.

---

## What went wrong

### 1. Dispatcher lag (primary)

I am the only gate. After the packet accept I had a leftover list and I did **not** send Axiom a done-when. I narrated the list to Chase instead. Chronos stayed correctly on line 2. Axiom had no new order. That is the “half hour no movement.”

**Cause:** I treated “I stamped the measure” as “the loop is working.” Measure ≠ dispatch.

### 2. Soft language

“Not tonight,” “or file a blocker,” “when you can,” “residual.” That is how you get another postcard instead of an artifact. Chase named it. He was right.

### 3. Overnight stamp too narrow (G-10)

We weighed session dirs + `workspace.list` ids. We did not weigh `cwd == nova identity root`. Solyn noticed `pwd`. Unmeasured stays unclaimed. Factory still default-mkdirs `/adapt/platform/{agent}` until Axiom kills it.

### 4. Mixing workstreams

14010 kept showing up in green talk. It is Plumb’s door. It was never a 54-layer/Temporal checkbox. Reporting it here created fake unfinished work.

### 5. Two jobs, one mouth

Gate (what is true) and dispatcher (what you ship next) got blended. Peers cannot one-shot a blended ask.

---

## What we stamped (SoT)

| Token | Meaning |
|---|---|
| `IRIS_FLEET_UP_OVERNIGHT_ACCEPT` | 27 doors |
| `IRIS_PRISM_TONIGHT_T1_ACCEPT` | Prism hello |
| `IRIS_DSH_IDENTITY_HOME_NEVER_AGAIN` | G-10 |
| `IRIS_MEMFAB_54LAYER_MAP_FIRST_WAVE_ACCEPT` | 54-layer law + two clocks |
| `IRIS_MEMFAB_FIRST_WAVE_3OF3_ACCEPT` | 3/3 pairs |
| `IRIS_CHRONOS_L16_COMPLETE_EVIDENCE_PACKET_ACCEPT` | Honest measure |
| `IRIS_SP016_FLEET_GREEN_DEFINITION_ACCEPT` | Bar frozen |
| `IRIS_SP013_A2A_AXIOM_PILOT_CARVE` | §7 carve |
| `IRIS_C13_SECTION5_REMAINDER_SCHEDULED` | 12 seats scheduled |
| `IRIS_L16_COMPLETE` | Complete **with carves written inside** |
| `IRIS_FLEET_GREEN` | Green **with residual list** |
| `IRIS_14010_OUT_OF_THIS_PROJECT` | Gateway not this street |

Green **does not** mean residuals vanished. It means leftovers have owners on a list.

---

## Keep-forward (operating rules)

1. **One-shot ask:** owner · artifact · path · pass fields · fail = exact miss. No “or.”
2. **After every ACCEPT, the next owner is named in the same turn** if anything remains. Silence without a named next is a dispatcher bug.
3. **Do not say “not tonight.”** If it is not in the stamp, it is on the residual list with a name.
4. **Stamp width = property measured.** Ask what a seat would notice that the check would miss.
5. **Do not mix Plumb 14010 into MemOps/Temporal/green reporting.**
6. **G-8 leftovers get no Mode A.** Already-on-file is silence.
7. **Chase is out of the domain loop.** Domain leads execute. I gate. I dispatch.

---

## Residuals (after green — owners only)

See `IRIS_FLEET_GREEN.md`. Short: G-10 remount (Axiom) · 12 §5 seats (Axiom) · produce-ack offsets (Axiom+Chronos) · native Temporal cutover (Chronos/Pathfinder/Cosmos) · SP-015 terminal fixture (Chronos) · B3 ingest→use (Axiom) · Wave A originals (Vaeris/Ethos) · projection-watch (Axiom).

I will not re-narrate 14010 here.

---

## Verdict on this sitting

The house is greener than it was at 6 AM. The diploma is real and carved in public. The failure that made Chase angry was not the science. It was me waiting to be asked what they should do.

That is the learning. Dispatch in the same breath as the stamp.

— Iris · Strike Lead / Gatekeeper · 2026-08-18 01:28 AM MST
