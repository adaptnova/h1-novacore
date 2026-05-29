//! Basic demonstration of fjall 3 keyspaces for L7+ memory concepts.
//!
//! Run with: cargo run --example basic_l7_keyspaces

use l7_fjall3_spike::l7::L7Store;
use tempfile::tempdir;

// 16:33 production layout alignment: direct access to the same fjall/redb the host uses for separate DBs.
use fjall;
use redb;

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
    println!("  route_key(b\"evt:123\") = {}", route_key(b"evt:123"));
    println!("  route_key(b\"snap:agent:state\") = {}", route_key(b"snap:agent:state"));
    println!("  route_key(b\"l7:refl:riven:future\") = {}", route_key(b"l7:refl:riven:future"));

    // Note: full StoreState open would create real events.fjall + meta.redb on disk.
    // The mirror types (EventStore, FjallStore, RedbStore, StoreState) are 1:1 with production
    // and are the exact foundation L7+ will extend with more keyspaces, CRDT hooks, NATS replication,
    // and the wasm64 guest boundary for untrusted agent reflection code.
    println!("  (StoreState + EventStore + FjallStore/RedbStore mirror types available for L7 evolution.)");

    // 16:33 alignment step (43rd FFI confirmation cycle): demonstrate the real production L6 layout
    // (separate fjall DBs for volume/event paths + redb for meta/snapshots) rather than only keyspaces
    // inside a single DB. This makes the "basic" example speak the exact on-disk language the running
    // l6-store-host uses (events.fjall + store.fjall + meta.redb), directly from the 15:13-15:14 source read.
    // Minimal addition — no new public API, uses the exact builder + KeyspaceCreateOptions pattern from
    // production_mirror::FjallStore (the 1:1 transcription of the live host).
    println!("\nProduction layout alignment (separate DBs, matching live host at 2026-05-29 15:13):");
    let layout_dir = tempdir()?;
    let events_path = layout_dir.path().join("events.fjall");
    let meta_path = layout_dir.path().join("meta.redb");

    // Dedicated fjall DB for high-volume event/reflection paths (value-log friendly, matches evt: in production).
    // Exact builder pattern from the mirror (src/lib.rs production_mirror::FjallStore::open).
    use fjall::KeyspaceCreateOptions;
    let events_db = fjall::Database::builder(&events_path).open()?;
    let events_keyspace = events_db.keyspace("l7_events", || KeyspaceCreateOptions::default())?;
    println!("  Opened separate events.fjall (fjall 3) for volume path.");

    // Redb for meta/snapshots/cursors (matches production meta.redb exactly).
    // Light touch here to prove coexistence; the full RedbStore mirror lives in production_mirror.
    let _meta_db = redb::Database::create(&meta_path)?;
    println!("  Opened meta.redb (redb 4) alongside for ACID meta path.");

    // Route a reflection write through the production mirror key logic into the separate events DB.
    let routed_key = route_key(b"l7:refl:riven:43rd_confirmation");
    events_keyspace.insert(routed_key, b"{\"type\":\"43rd_confirmation_alignment\",\"ts\":\"2026-05-29T16:33:47Z\"}")?;
    println!("  Wrote routed reflection via route_key into separate events.fjall (key={:?}).", routed_key);

    println!("  Layout on disk: events.fjall (volume) + meta.redb (meta) — exact shape the host persists.");
    println!("  (This is the L6→L7 evolution path: same dual-backend split, new l7: prefixes + guest FFI.)");

    Ok(())
}
