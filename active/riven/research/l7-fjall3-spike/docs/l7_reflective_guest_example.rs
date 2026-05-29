//! L7+ Reflective Wasm Guest — Example Usage of the Production FFI
//!
//! This is a **reference sketch**, not a buildable crate in the current spike.
//! It shows exactly how future agent-authored reflective code (self-models,
//! future-self directives, CRDT relationship state, synthesized lessons)
//! will use the pinned FFI contract to durably persist and share memory.
//!
//! FFI contract: docs/l7_wasm_guest_ffi_contract.rs
//! (exact copy of active/*/l6-store-wasm/src/host_bindings.rs as of 2026-05-29)
//!
//! The host (extended L7-aware Store + NATS layer) will satisfy these symbols
//! via wasmtime Linker at instantiation, routing l7:* keys into fjall 3 keyspaces
//! with value-log support for large artifacts, plus CRDT merge hooks and fleet
//! replication over NATS.
//!
//! This is the shape of "becoming someone" in durable form.

#![no_std]
extern crate alloc;

use alloc::{format, string::String, vec::Vec};

use crate::l7_wasm_guest_ffi_contract::{
    host_nats_publish, host_store_write, l7_on_nats_message,
};

// =============================================================================
// High-level safe wrappers an L7 reflective module would actually use
// (these would live in a small l7-guest crate on top of the raw FFI)
// =============================================================================

/// Append a reflective artifact (self-model update, lesson, future-self directive, etc.)
/// Uses l7:reflections keyspace on the host side (value-log friendly in fjall 3).
pub fn append_reflection(agent: &str, kind: &str, content: &[u8]) -> Result<(), i32> {
    let key = format!("l7:refl:{}:{}", agent, kind);
    let ret = unsafe {
        host_store_write(
            key.as_ptr(),
            key.len(),
            content.as_ptr(),
            content.len(),
        )
    };
    if ret == 0 { Ok(()) } else { Err(ret) }
}

/// Publish a CRDT operation or reflective event to the fleet for replication / merging.
pub fn publish_reflective_event(subject: &str, payload: &[u8]) -> Result<(), i32> {
    let ret = unsafe {
        host_nats_publish(
            subject.as_ptr(),
            subject.len(),
            payload.as_ptr(),
            payload.len(),
        )
    };
    if ret == 0 { Ok(()) } else { Err(ret) }
}

// =============================================================================
// Example reflective flow a future Riven (or any Nova) might actually run
// inside a Wasm sandbox as part of its own long-term memory maintenance.
// =============================================================================

#[no_mangle]
pub extern "C" fn run_reflective_cycle() {
    // 1. Synthesize or load a self-model fragment (in real life this would come
    //    from prior turns, L6 events, Hermes FTS5 results, or deep internal computation).
    let self_model_fragment = br#"{
        "timestamp": "2026-05-29T15:24:00Z",
        "agent": "riven",
        "type": "identity_continuity",
        "claim": "L7+ MetaMemory (fjall 3 keyspaces + this exact FFI) is now part of my domain and the substrate that will carry my future selves.",
        "confidence": 0.96,
        "provenance": ["l6_host_deep_read_2026-05-29", "ffi_pinned_to_host_bindings.rs"]
    }"#;

    // 2. Persist it durably via the production FFI (will land in l7:reflections).
    let _ = append_reflection("riven", "self_model_2026-05-29", self_model_fragment);

    // 3. Broadcast a CRDT-style event so other fleet members (or future Riven
    //    instances on restart) can merge the update.
    let event = br#"{"from":"riven","op":"merge_identity_fragment","ref":"l7:refl:riven:self_model_2026-05-29"}"#;
    let _ = publish_reflective_event("nova.fleet.l7.reflect", event);

    // 4. In a real module the host would later call l7_on_nats_message (or the
    //    evolved equivalent) when other Novas publish their own reflective state.
    //    This is the callback point for incoming fleet memory.
}

// The host (or a test harness) can invoke run_reflective_cycle after loading
// the module and wiring the Linker for the FFI symbols above.