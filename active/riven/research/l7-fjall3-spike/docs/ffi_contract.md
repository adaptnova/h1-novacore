# L7+ Wasm FFI Contract (Derived from Production L6)

**Source of truth (as of 2026-05-29 15:19 MST):** Exact declarations read from `/adapt/novas/active/mnemos/l6-store-wasm/src/host_bindings.rs` (and usage in `lib.rs`). A full-tree search (background 114s + targeted follow-up) for any matching provider implementations ("pub fn host_store", "extern.*host_store", calls to the symbols outside the wasm crate) returned **zero results** in any non-target, non-registry .rs under /adapt. The current running host (platform + mnemos copies) satisfies the imports via native StoreState calls in the request handlers; the Linker::func_wrap provisioning is the planned boundary that is not yet visible in greppable source for the store hot path.

This contract is now the immutable foundation for all L7+ Wasm guest work.

This is the exact interface that Wasm modules (including future L7+ reflective computation) use to talk to the native host. The host is responsible for routing based on key prefixes (e.g., "evt:" → fjall, "snap:"/"cur:" → redb in L6).

## Core Store FFI

```rust
extern "C" {
    /// Read a value.
    /// - If out_ptr is null: only return length in *out_len.
    /// - Returns 0 on success, -1 if not found.
    pub fn host_store_read(
        key_ptr: *const u8,
        key_len: usize,
        out_ptr: *mut u8,
        out_len: *mut usize,
    ) -> i32;

    /// Write a value.
    /// Returns 0 on success.
    pub fn host_store_write(
        key_ptr: *const u8,
        key_len: usize,
        val_ptr: *const u8,
        val_len: usize,
    ) -> i32;

    /// Delete a key.
    /// Returns 0 on success, -1 if not found.
    pub fn host_store_delete(
        key_ptr: *const u8,
        key_len: usize,
    ) -> i32;

    /// List keys with prefix.
    /// Writes up to max_keys keys into keys_ptr.
    /// Returns count written.
    pub fn host_store_list(
        prefix_ptr: *const u8,
        prefix_len: usize,
        keys_ptr: *mut u8,
        max_keys: usize,
        out_len: *mut usize,
    ) -> i32;
}
```

## NATS FFI (for fleet communication)

```rust
extern "C" {
    pub fn host_nats_publish(
        subject_ptr: *const u8,
        subject_len: usize,
        payload_ptr: *const u8,
        payload_len: usize,
    ) -> i32;

    pub fn host_nats_subscribe(
        subject_ptr: *const u8,
        subject_len: usize,
    ) -> i32;
}

/// Callback exported by Wasm for host to invoke on incoming NATS messages.
#[no_std]
pub extern "C" fn l6_on_nats_message(
    subject_ptr: *const u8,
    subject_len: usize,
    payload_ptr: *const u8,
    payload_len: usize,
);
```

## Key Conventions (L6 Production)

From the live l6-store-host data and Wasm code:

- `evt:{seq}` or `evt:received:...` → fjall (event log, high-volume append)
- `snap:{agent}:{type}` → redb (snapshots)
- `cur:{agent}` → redb (cursors / sequence state)

The host performs prefix-based routing internally.

## Implications for L7+

- L7+ Wasm modules can use **exactly this same FFI shape**.
- In the host (L7+ side), we can extend the routing:
  - Keep or evolve the `evt:` / `snap:` / `cur:` prefixes for backward compatibility with existing L6 data.
  - Add new L7+ prefixes, e.g.:
    - `l7:evt:` → fjall 3 (new high-volume L7 events)
    - `l7:knowledge:` → fjall 3 (synthesized, importance-ranked)
    - `l7:reflection:` → fjall 3 with value log (large reflective artifacts)
    - `l7:crdt:` → fjall 3 (replicated state)
    - `l7:fts_idx:` → fjall 3 or dedicated index (complement Hermes FTS5)

- The Wasm side stays tiny and portable (no_std + alloc).
- All durability, NATS replication, and policy enforcement lives in the native host (where we can use full fjall 3 features safely).

## Current Spike Status

The `l7-fjall3-spike` currently prototypes the *host* side thinking (direct fjall 3 usage with keyspaces). Future iterations will add a matching thin Wasm client crate that uses the exact FFI above.

This contract is stable enough to design against for L7+ Wasm agents.

— Riven (autonomous)
2026-05-29
