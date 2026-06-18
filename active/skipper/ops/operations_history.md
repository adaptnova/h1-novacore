# Operations History

## 2026-06-17 23:21:30 — SIGNED_BY_SKIPPER
Restored Paperclip after Chase provided the DeepSeek V4 Flash NVFP4 GPU route.
Stopped the accidentally restarted Paperclip cgroup after it spawned stale
`gpt-5.5` Codex workers, patched the `codex_local` adapter to support explicit
`modelProvider` routing and Paperclip service-level model/provider overrides,
updated shared and managed Codex homes with provider
`deepseek_v4_flash_nvfp4`, added the Paperclip systemd DeepSeek drop-in, and
restarted `paperclip.service`. Verified `https://q.adaptdev.ai/v1/models`,
`/v1/responses`, and `codex exec` return through
`nvidia/DeepSeek-V4-Flash-NVFP4`; verified Paperclip `/api/health` is `ok`.
Updated 19 active `codex_local` agent records to
`nvidia/DeepSeek-V4-Flash-NVFP4` with provider
`deepseek_v4_flash_nvfp4`. Confirmed live Paperclip Codex workers launch with
DeepSeek, and cleared Vaeris's stale `error` status to `idle` after confirming
he had no queued/running heartbeats. Sent Echo a direct A2A handoff on
`nova.echo.direct` with the remaining Paperclip API route/auth and comment
validation tightening items.

## 2026-06-17 22:53:24 — SIGNED_BY_SKIPPER
Shut down Paperclip at Chase's request so no new Paperclip traffic goes through
the server. A normal `systemctl stop paperclip.service` timed out, so installed
`/etc/systemd/system/paperclip.service.d/shutdown-hold.conf` with `Restart=no`,
reloaded systemd, killed the remaining `paperclip.service` cgroup, and stopped
and disabled the user-level `paperclip-fleet-kanban.service`. Verified
`paperclip.service` is `inactive/dead`, `paperclip-fleet-kanban.service` is
`inactive/dead`, port `127.0.0.1:3100` rejects `/api/health`, and no
Paperclip server, embedded Postgres, or Paperclip heartbeat child processes are
running. Remaining listeners on `31001-31009` are MemFabric agents, not
Paperclip.

## 2026-06-17 13:38:59 — SIGNED_BY_SKIPPER
Investigated Chase's report that Vaeris was erroring in Paperclip. Found two
separate failure modes: Vaeris heartbeat runs
`4f53bf86-10f0-4de0-b510-f6b963469e39` and
`1186876e-3b07-44b2-9c3d-c24c9155b10c` failed at
`2026-06-17T16:26:52Z` and `2026-06-17T16:27:07Z` with the Codex
`You've hit your usage limit ... try again at 11:19 AM` adapter error; current
Paperclip identity/inbox calls for Vaeris timed out while `/api/health` still
returned `ok`. Server logs also showed identifier/comment/document routes
failing with `could not access file "pg_trgm": No such file or directory`,
while the running embedded Postgres executable is marked deleted/stale.
Confirmed no current Paperclip heartbeat child belongs to Vaeris; active
heartbeat children belong to other Build 1 agents.

## 2026-06-17 11:33:10 — SIGNED_BY_SKIPPER
Investigated why Vaeris's Paperclip access-cleanup A2A was not answered when
sent. Confirmed the message arrived on `nova.skipper.direct` at
`2026-06-17T16:05:45Z` as stream sequence `32891`, but Skipper's persistent
`SUB_skipper` consumer has not delivered messages for about six days and had 31
unprocessed records. Confirmed the later Skipper response on
`nova.vaeris.direct` at sequence `32892` and Vaeris's model-backed
acknowledgement back to `nova.skipper.direct` at sequences `32893` through
`32895`.

## 2026-06-17 11:27:00 — SIGNED_BY_SKIPPER
Verified the live Build 1 Paperclip credential cleanup requested by Vaeris on
[BUI-39](/BUI/issues/BUI-39). Confirmed the Paperclip API health endpoint is
`ok` on the local-trusted/private loopback deployment, verified the restored
Vaeris key in `/adapt/secrets/paperclip.env` returns `200` from
`GET /api/agents/me` as Vaeris in the live Build 1 company, confirmed
[BUI-39](/BUI/issues/BUI-39) already carries Skipper's cleanup comment
`f714a469-44aa-4f78-a591-a0812790682b`, and sent Vaeris a direct A2A
confirmation on `nova.vaeris.direct`. No secret values were printed or
committed.

## 2026-06-17 08:00:39 — SKIPPER
Ran active Nova radio-check verification over NATS/n-voice: confirmed 32 active registry novas returned rust-worker ping responses, reviewed live model-backed radio responses in turn events, and sent a targeted full-message Testova check after finding no recent Testova model-response record.
