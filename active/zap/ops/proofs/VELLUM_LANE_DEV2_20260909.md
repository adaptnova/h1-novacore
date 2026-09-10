# Vellum lane — ADAPT cockpit (mirrors Aster ADR-08 pattern)

**Done:** 2026-09-10 02:45 UTC (2026-09-09 19:45 MST) — Zap, Strike operator, on dev2.
**Requested by:** Chase (operator).

## What was built

A second Colony Three ADAPT lane for **Vellum**, isolated from Switchyard exactly like
Aster's (ADR-08 pattern: no router fabric between Nova and its gateway; continuity lives
in the gateway, not Switchyard).

| Piece | Aster lane | Vellum lane (new) |
|---|---|---|
| ADAPT gateway | :15001 (`adapt-gateway.service`) | **:15003** (`adapt-gateway-vellum.service`) |
| CapabilityPort | :15002 (`adapt-capability.service`) | **:15004** (`adapt-capability-vellum.service`) |
| jcode server | `colony3-jcode.service`, socket `/run/user/1001/jcode/jcode.sock` | **`vellum-jcode.service`**, socket `/run/user/1001/jcode-vellum/jcode.sock` |
| Remotty | :7710 (`remotty.service`, env `~/.config/remotty/`) | **:7711** (`remotty-vellum.service`, env `~/.config/remotty-vellum/`, OpenCode port 7721) |
| Shell entry | `JC` alias | **`JV` alias** |
| Provider profile | `[providers.adapt]` -> :15001 | **`[providers.vellum]`** -> :15003 (send_turn_metadata=true) |
| Nova home | `/adapt/novas/aster` | `/adapt/novas/vellum` |
| Brain | Flash-Next :11001 | Flash-Next :11001 (shared, as Aster's) |

- **NovaId (permanent):** `6d169655-ce0e-4635-bfad-89e347067d29` — minted 2026-09-10,
  `identity/novaid.md` + `nova.genesis` event in `memory/canonical/events.jsonl`.
- BrainPort invariant held: gateway brain = :11001 only; never 14010/14011/14100/15001/8001.
- `jcode-daemon.lock` is **per XDG_RUNTIME_DIR**: Vellum's server runs with its own
  `RuntimeDirectory=vellum-runtime` so both servers coexist (this was the one real
  obstacle; the Aster server holds the default runtime-dir lock).

## Verification (all passed)

1. `jcode run` via `JV`-style env -> socket -> :15003 -> Vellum continuity -> **VELLUM_LANE_OK**.
2. Turn landed in ledger: `exchange.completed` + activation events in `/adapt/novas/vellum/memory/canonical/events.jsonl` (5 events, verify ok).
3. `curl http://127.0.0.1:7711/remotty/` -> **200** (Remotty Vellum PWA; auth token in `~/.config/remotty-vellum/auth.env`).
4. `assert-aster-path.sh all` -> **all 4 assertions pass** — Aster lane and shared fabrics untouched.
5. `colony3-jcode`, `adapt-gateway`, `remotty` (Aster units) all still `active`.

## Files (dev2)

- `/adapt/novas/vellum/{AGENTS.md, identity/novaid.md, memory/canonical/events.jsonl, ops/}`
- `~/.config/systemd/user/{adapt-gateway-vellum,adapt-capability-vellum,vellum-jcode,remotty-vellum}.service` (enabled)
- `~/.config/remotty-vellum/{remotty.env,auth.env}` (mode 600)
- `~/.jcode/config.toml` — appended `[providers.vellum]` (backup `config.toml.bak-pre-vellum-*`)
- `~/.bashrc` — `JV` alias appended (backup `.bashrc.bak-pre-vellum-*`)

## Usage

- **Shell:** `ssh dev2` -> `JV` (opens jcode in Vellum home on the Vellum socket).
- **Mobile/PWA:** Remotty on `127.0.0.1:7711/remotty` (loopback, like Aster's; tunnel as needed).
- **Vellum identity:** AGENTS.md is a scaffold — role line awaits operator declaration.

## Deliberate non-changes

- `default_provider` in `~/.jcode/config.toml` stays `nova` — casual sessions never write
  into Vellum's ledger (same rule as Aster's `adapt` profile comment).
- Shared `jcode-serve.service` (system) untouched; ADR-08 drop-ins intact.
- No Switchyard/Plumb/TensorZero units touched.

— Zap · Strike operator · 2026-09-09 07:45 PM MST
