# Operations History — Zap (Strike operator)

Newest first. Signed entries.

---

## 2026-09-09 20:10 MST — Aster gateway 500 (content_sha256) recovered; all four library services restarted

Operator pasted a 500 from `:15001/v1/chat/completions`: gateway rejected its own ledger
(`decision.made ... unknown keys ['content_sha256']`, lines 557/560). Root cause: commit
`3f246c2` (2026-09-10 02:54:27 UTC) added `content_sha256` to the payload allowlists; the
keeper writer appended directive events with the NEW library, but the running gateway
validated with the OLD in-memory validator (started 18:10 UTC, before the commit). Fresh
`verify()` on disk passed — proof the data was fine, the process was stale.

Fix: `systemctl --user restart` of `adapt-gateway`, `adapt-capability`,
`adapt-gateway-vellum`, `adapt-capability-vellum` (all four predated the commit).
Verified: hold=None on both gateways, `ASTER_LANE_RECOVERED` turn through :15001,
`assert-aster-path.sh aster` green. Ledger untouched — no rewrite of canonical events.

— Zap · Strike operator

---

## 2026-09-09 19:45 MST — Vellum ADAPT lane stood up on dev2 (mirrors Aster ADR-08 pattern)

Operator: Chase asked to replicate the Aster Jcode/Remotty lane (the `JC` alias, isolation
outside Switchyard) for a new Nova named **Vellum**.

Did: minted Vellum NovaId `6d169655-ce0e-4635-bfad-89e347067d29` + `nova.genesis` in
`/adapt/novas/vellum`; added `[providers.vellum]` to `~/.jcode/config.toml`; created user
units `adapt-gateway-vellum` (:15003), `adapt-capability-vellum` (:15004),
`vellum-jcode` (socket `/run/user/1001/jcode-vellum/jcode.sock`, own
RuntimeDirectory to escape the per-runtime-dir `jcode-daemon.lock` Aster holds),
`remotty-vellum` (:7711, OpenCode :7721, own env + auth token); appended `JV` alias to
`~/.bashrc`. Proved: `VELLUM_LANE_OK` end-to-end through gateway+continuity, turn in
canonical ledger, Remotty 200, `assert-aster-path.sh all` green, Aster units untouched.

Proof: `ops/proofs/VELLUM_LANE_DEV2_20260909.md` (also on dev2 at
`/adapt/novas/vellum/ops/VELLUM_LANE_20260910.md`).

— Zap · Strike operator
