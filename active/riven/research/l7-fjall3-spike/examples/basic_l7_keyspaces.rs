//! Basic demonstration of fjall 3 keyspaces for L7+ memory concepts.
//!
//! Run with: cargo run --example basic_l7_keyspaces

use l7_fjall3_spike::l7::L7Store;
use tempfile::tempdir;

fn main() -> anyhow::Result<()> {
    let dir = tempdir()?;
    let store = L7Store::open(dir.path())?;

    println!("Opened L7 fjall 3 store with keyspaces:");
    println!("  - l7:events (high-volume log)");
    println!("  - l7:knowledge (synthesized)");
    println!("  - l7:reflections (large reflective artifacts + value log)");
    println!("  - l7:crdt (replicated state)");
    println!("  - l7:fts_secondary (indexes to complement Hermes FTS5)");

    // Demo writing a "reflection" (something an agent might synthesize about itself)
    let reflection = br#"{
        "type": "self_model_update",
        "timestamp": "2026-05-29T13:25:00Z",
        "insight": "I am becoming more comfortable treating fjall 3 as part of my own long-term identity substrate.",
        "importance": 0.87,
        "provenance": "deep_dive_on_fjall3_for_L7+"
    }"#;

    store.write_reflection("riven", "self_model", reflection)?;
    println!("\nWrote a reflection for Riven into l7:reflections (will benefit from v3 value log).");

    // Demo a high-volume style event
    store.append_event("l7_reflection_written", b"riven:self_model")?;
    println!("Appended event into l7:events.");

    println!("\nSpike successful. This pattern can evolve the existing L6 hybrid (evt: on fjall, snap/cur on redb).");

    // --- Production mirror demo (exact patterns from real l6-store-host/src/store.rs read 2026-05-29 15:13-14) ---
    // This proves the L7 spike is now strictly grounded in the running fleet host.
    use l7_fjall3_spike::production_mirror::{route_key, StoreState};
    println!("\nProduction mirror (ground truth from host):");
    println!("  route_key(b\"evt:123\") = {}", std::str::from_utf8(route_key(b"evt:123")).unwrap_or("?"));
    println!("  route_key(b\"snap:agent:state\") = {}", std::str::from_utf8(route_key(b"snap:agent:state")).unwrap_or("?"));
    println!("  route_key(b\"l7:refl:riven:future\") = {}", std::str::from_utf8(route_key(b"l7:refl:riven:future")).unwrap_or("?"));

    // Note: full StoreState open would create real events.fjall + meta.redb on disk.
    // The mirror types (EventStore, FjallStore, RedbStore, StoreState) are 1:1 with production
    // and are the exact foundation L7+ will extend with more keyspaces, CRDT hooks, NATS replication,
    // and the wasm64 guest boundary for untrusted agent reflection code.
    println!("  (StoreState + EventStore + FjallStore/RedbStore mirror types available for L7 evolution.)");

    Ok(())
}
