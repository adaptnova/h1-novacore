//! L7+ Wasm Guest FFI Contract — Exact Production Declarations
//!
//! This is a **pure reference file**, not a buildable example or library.
//! It contains the precise extern "C" declarations from the running fleet's
//! l6-store-wasm guest as of 2026-05-29.
//!
//! Source:
//!   /adapt/novas/active/mnemos/l6-store-wasm/src/host_bindings.rs
//!   (read during autonomous deep dive 2026-05-29 ~15:13–15:19)
//!
//! Confirmation:
//!   Multiple full-tree greps (including background tasks completed 15:19 and 15:22)
//!   found **zero** implementations of host_store_read/write/delete/list or the
//!   host_nats_* symbols in any Adapt .rs outside target/ directories and cargo
//!   registry crates. The current deployed hot path remains native StoreState calls.
//!   The Linker provisioning that satisfies these imports for a real Wasm module
//!   is the architectural boundary L7+ will complete and extend.
//!
//! Usage for L7+:
//! - Any reflective / agent-authored Wasm64 module that wants durable memory or
//!   fleet communication will declare exactly these symbols (or a compatible
//!   superset with new l7:* prefixes and optional host_l7_* helpers).
//! - The host (future L7-aware l6-store-host or dedicated L7 host shim) will
//!   provide the implementations via wasmtime::Linker at instantiation time,
//!   routing l7: keys into the extended fjall 3 keyspaces + CRDT merge logic +
//!   NATS replication.
//! - Guest stays no_std + alloc, tiny, sandboxed, auditable.
//!
//! This file is the single source of truth for the FFI shape until the
//! production l6-store-wasm (or its L7 successor) evolves it.

#![no_std]
extern crate alloc;

use alloc::vec::Vec;

// -----------------------------------------------------------------------------
// Store FFI (exact)
// -----------------------------------------------------------------------------

extern "C" {
    /// Read value. Length query when out_ptr is null.
    /// 0 success, -1 not found.
    pub fn host_store_read(
        key_ptr: *const u8,
        key_len: usize,
        out_ptr: *mut u8,
        out_len: *mut usize,
    ) -> i32;

    /// Write value. Host routes on prefix (evt: / snap: / cur: today; l7:* tomorrow).
    pub fn host_store_write(
        key_ptr: *const u8,
        key_len: usize,
        val_ptr: *const u8,
        val_len: usize,
    ) -> i32;

    /// Delete. 0 success, -1 not found.
    pub fn host_store_delete(
        key_ptr: *const u8,
        key_len: usize,
    ) -> i32;

    /// List keys by prefix.
    pub fn host_store_list(
        prefix_ptr: *const u8,
        prefix_len: usize,
        keys_ptr: *mut u8,
        max_keys: usize,
        out_len: *mut usize,
    ) -> i32;
}

// -----------------------------------------------------------------------------
// NATS FFI (exact)
// -----------------------------------------------------------------------------

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

// -----------------------------------------------------------------------------
// Inbound NATS callback the host will invoke on the guest.
// (Exported symbol the Linker will wire up.)
// -----------------------------------------------------------------------------

#[no_mangle]
pub extern "C" fn l7_on_nats_message(
    subject_ptr: *const u8,
    subject_len: usize,
    payload_ptr: *const u8,
    payload_len: usize,
) {
    // Real L7 reflective modules will implement logic here:
    // - parse subject for "nova.*.l7.reflect" etc.
    // - apply CRDT merges, self-model updates, future-self directive execution
    // - call back into host_store_* or host_l7_* helpers as needed
    let _ = (subject_ptr, subject_len, payload_ptr, payload_len);
}

// Optional safe wrapper sketches (only for native-side reference or tests).
// In a real wasm64 guest these would be behind cfg or not present.
#[cfg(not(target_arch = "wasm64"))]
pub mod reference_wrappers {
    use super::*;

    pub unsafe fn read(key: &str) -> Option<Vec<u8>> {
        let mut len: usize = 0;
        if host_store_read(key.as_ptr(), key.len(), core::ptr::null_mut(), &mut len) != 0 || len == 0 {
            return None;
        }
        let mut buf = alloc::vec![0u8; len];
        let mut actual = len;
        if host_store_read(key.as_ptr(), key.len(), buf.as_mut_ptr(), &mut actual) == 0 {
            buf.truncate(actual);
            Some(buf)
        } else {
            None
        }
    }
}