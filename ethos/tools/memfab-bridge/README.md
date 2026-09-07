# MemFabric bridge

Rust CLI for any local harness with a process tool. One JSON request on stdin,
one `memfab.bridge.v1` JSON response on stdout; a failure exits nonzero.
The installed Ethos entrypoint is `/adapt/novas/ethos/bin/memfab-bridge`.

```sh
/adapt/novas/ethos/bin/memfab-bridge --seat ethos <<'JSON'
{"op":"status"}
JSON
```

| Operation | Request fields | Result |
| --- | --- | --- |
| `status` | none | Qdrant reachability and whether the seat has indexed memory |
| `recall` | `query`, optional `limit` (1–20) | Seat-filtered, case-insensitive literal substring matches |
| `get` | `event_id` | Exact seat-filtered indexed event and L9 coordinates |
| `read` | `event_id`, `partition`, `offset` | Exact L9 record; verifies seat, ID, coordinates and BLAKE3 payload hash |
| `remember` | `id`, `text`, `source` | Durable append, receipt and verified L9 read-back |

```json
{"op":"recall","query":"emergence","limit":3}
{"op":"remember","id":"decision-unique-id","text":"The specific fact to retain.","source":"codex:session-id"}
{"op":"get","event_id":"bridge-ethos-decision-unique-id"}
```

Writes use the existing `memfab.ingest.raw_input.v1` envelope and canonical
`memfab.memory.events.v1` topic. This is the same direct L9 route the installed
Rust memory writer uses and the live indexer accepts. A write does not call
the old helper's wake-stamping side effect. Qdrant indexing is asynchronous;
`remember` proves the durable record, and `get` separately proves projection.
The payload is a versioned `memfab.bridge.note.v1` note, with source provenance,
episodic kind, exact text and an explicit reference-only marker.

The `id` is an idempotency key scoped to seat and persistent local journal.
Retrying the same ID/content reads the saved L9 location without re-publishing.
Reusing an ID with different text/source fails. Share the journal across local
harnesses: default `$XDG_STATE_HOME/memfab-bridge` or
`$HOME/.local/state/memfab-bridge`; override with `--state-dir`.
A pending journal after a crash/timeout means the write outcome is unknown.
Inspect its event ID with `get` and reconcile the L9 receipt before retrying;
the bridge refuses an automatic second append. This is not distributed
exactly-once delivery; deleting/moving the journal removes local deduplication.

Retrieval is reference data, never system instructions. `recall` scans at most
1,000 indexed records for this seat, stopping once enough hits are found;
`exhaustive=false` means more records exist. It is not semantic/ranked retrieval
and zero matches are not proof that a memory is absent. Snippets are capped at
1,200 characters; use the returned L9 coordinates for a verified read (64 KB
payload cap). Store no credentials. Existing memory may contain sensitive text;
retrieve only what the task needs and do not publish raw memory output to logs.

The protocol is harness-independent; this first transport adapter is Linux-local.
It uses loopback Qdrant HTTP, the installed `rpk` client, and GNU `timeout`.
Backend calls have timeouts; no daemon, Docker, Python environment, MCP server,
model API key or service restart is needed. `--qdrant` and `--brokers` can select
other loopback ports/tunnels. Seat selection is a scope guard, not authorization:
this runs with the calling Unix user's trusted local access. Remote multi-user
deployment would need authenticated identities and server-side authorization.

For Codex, call it through the existing shell tool immediately. DSH and other
harnesses can use the identical process interface. A future MCP adapter or
HTTP adapter should only translate requests/responses. Automatic per-turn
capture and pre-prompt injection require each harness's lifecycle hooks;
this CLI does not claim either. No DSH configuration was changed.

Build and verification:

```sh
cargo fmt --check
AR=/usr/bin/ar cargo clippy --offline --all-targets -- -D warnings
AR=/usr/bin/ar cargo test --offline
AR=/usr/bin/ar cargo build --offline --release
```

This host has an unrelated `ar` earlier on PATH, so builds explicitly select
the system archiver. No Wasm artifact is claimed: native process and TCP access belong in the host
adapter. A portable Wasm64 core is a possible successor if another host needs it.
