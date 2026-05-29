//! L7+ Meta-Memory Spike using fjall 3.x — Grounded in Production L6 Host
//!
//! This spike evolves the exact production L6 hybrid (fjall 3.1 + redb 4.0)
//! already running in the fleet into the reflective L7+ layer for agent-authored
//! knowledge, self-models, future-self directives, CRDT relationship state,
//! and long-horizon synthesized lessons.
//!
//! **Grounding (2026-05-29 15:14 MST — Riven):** Every pattern here descends
//! directly from line-by-line reading of the real running host at
//! /adapt/platform/novaops/toolops/memory/l6-store-host/src/ (store.rs as the
//! consolidated source of truth for routing + backends, nats.rs for WasmLoader +
//! NATS forward_to, main.rs wiring, grpc.rs domain verbs, live events.fjall +
//! meta.redb layout). We extend the proven architecture; we do not invent a new one.
//!
//! Key design goals for L7+:
//! - High-volume append + synthesized knowledge (fjall keyspaces + value log)
//! - Large reflective artifacts (agent-authored, multi-KB to MB self-models)
//! - Multiple isolated modalities with independent tuning (keyspaces)
//! - NATS-replicable CRDT + fleet-wide reflective state (forward_to + subjects)
//! - Wasm64-friendly FFI boundary (evolve the l6-store-wasm pattern for untrusted reflection)
//! - Seamless integration point for Hermes FTS5 (lexical secondary index)
//!
//! Current L6 key conventions (exact from production store.rs route_key):
//!   "evt:{seq}"             → fjall keyspace "events"
//!   "snap:{agent}:{type}"   → redb table "snapshots"
//!   "cur:{agent}"           → redb table "cursors"

use fjall::{Database, KeyspaceCreateOptions};
use std::path::Path;

pub mod l7 {
    use super::*;

    /// L7 memory modalities as separate fjall keyspaces (direct evolution of
    /// the production single-"events" keyspace pattern).
    /// This allows independent tuning (compression, block size, filters, compaction
    /// strategy, value log thresholds) per modality — exactly what fjall 3.x enables.
    pub struct L7Store {
        pub db: Database,
        pub events: fjall::Keyspace,        // High-volume raw + processed events (append-heavy)
        pub knowledge: fjall::Keyspace,     // Synthesized lessons, self-models, importance-ranked structures
        pub reflections: fjall::Keyspace,   // Agent-authored meta-thoughts, future-self directives (large blobs → value log)
        pub crdt: fjall::Keyspace,          // Replicated identity / relationship / provenance state
        pub fts_secondary: fjall::Keyspace, // Secondary indexes feeding or coexisting with Hermes FTS5
    }

    impl L7Store {
        pub fn open(path: impl AsRef<Path>) -> anyhow::Result<Self> {
            // Use exact production host pattern (Database::builder + keyspace closure)
            // This guarantees compatibility with the fjall 3.1 already running fleet-wide.
            let db = fjall::Database::builder(path.as_ref()).open()?;

            // Events: high write throughput (production-style keyspace creation)
            let events = db.keyspace("l7:events", || KeyspaceCreateOptions::default())?;

            // Knowledge: balanced synthesized structures
            let knowledge = db.keyspace("l7:knowledge", || KeyspaceCreateOptions::default())?;

            // Reflections: large agent-authored artifacts (value log friendly in fjall 3.x)
            let reflections = db.keyspace("l7:reflections", || KeyspaceCreateOptions::default())?;

            // CRDT state: transactional for fleet replication
            let crdt = db.keyspace("l7:crdt", || KeyspaceCreateOptions::default())?;

            // Secondary indexes (Hermes FTS5 complement / acceleration)
            let fts_secondary = db.keyspace("l7:fts_secondary", || KeyspaceCreateOptions::default())?;

            Ok(Self {
                db,
                events,
                knowledge,
                reflections,
                crdt,
                fts_secondary,
            })
        }

        /// Write a reflective artifact (large value → will use value log in fjall 3.x)
        pub fn write_reflection(
            &self,
            agent: &str,
            reflection_type: &str,
            content: &[u8],
        ) -> anyhow::Result<()> {
            let key = format!("reflection:{}:{}", agent, reflection_type);
            self.reflections.insert(key.as_bytes(), content)?;
            Ok(())
        }

        /// Append an L7 event (high volume path, mirroring production evt: usage)
        pub fn append_event(&self, event_type: &str, payload: &[u8]) -> anyhow::Result<()> {
            let seq = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_micros() as u64;

            let key = format!("evt:{}", seq);
            let value = format!("{}|", event_type).into_bytes();
            let mut full_value = value;
            full_value.extend_from_slice(payload);

            self.events.insert(key.as_bytes(), &full_value)?;
            Ok(())
        }
    }
}

// ============================================================================
// production_mirror — Faithful transcription of the real running L6 host
// (store.rs + supporting types) as the exact foundation to extend for L7+.
// All comments below are Riven's notes on L7 evolution points.
// ============================================================================

pub mod production_mirror {
    use anyhow::Result;
    use async_trait::async_trait;
    use std::path::Path;
    use std::sync::Arc;

    /// Exact route_key logic from production src/store.rs:15
    /// L7 evolution: extend the match for "l7:refl:", "l7:know:", "l7:crdt:" etc.
    /// or make routing pluggable / keyspace-aware inside fjall.
    pub fn route_key(key: &[u8]) -> &'static str {
        match key.first() {
            Some(&b'e') if key.starts_with(b"evt:") => "events",
            Some(&b's') if key.starts_with(b"snap:") => "snapshots",
            Some(&b'c') if key.starts_with(b"cur:") => "cursors",
            // L7+ extension points (future)
            Some(&b'l') if key.starts_with(b"l7:refl:") => "l7_reflections",
            Some(&b'l') if key.starts_with(b"l7:know:") => "l7_knowledge",
            Some(&b'l') if key.starts_with(b"l7:crdt:") => "l7_crdt",
            _ => "events",
        }
    }

    /// Exact EventStore trait from production (src/store.rs:36)
    /// Note the #[async_trait] on a fully sync/blocking interface — this is the
    /// deliberate seam for moving the impl into a wasm64 guest while the host
    /// owns I/O, durability, NATS, and wasmtime Linker provisioning of host_* FFI.
    #[async_trait]
    pub trait EventStore: Send + Sync {
        fn append(&self, key: &[u8], value: &[u8]) -> Result<()>;
        fn get(&self, key: &[u8]) -> Result<Option<Vec<u8>>>;
        fn delete(&self, key: &[u8]) -> Result<()>;
        fn list_keys(&self, prefix: &[u8]) -> Result<Vec<Vec<u8>>>;
        fn count(&self) -> Result<u64>;
    }

    // --- Fjall backend (production pattern, single keyspace "events" today) ---
    use fjall::KeyspaceCreateOptions;

    pub struct FjallStore {
        db: Arc<fjall::Database>,
    }

    impl FjallStore {
        pub fn open(path: &Path) -> Result<Self> {
            let db = fjall::Database::builder(path).open()?;
            Ok(Self { db: Arc::new(db) })
        }

        pub fn create(path: &Path) -> Result<Self> {
            if path.exists() {
                std::fs::remove_dir_all(path)?;
            }
            std::fs::create_dir_all(path)?;
            Self::open(path)
        }

        fn keyspace(&self, name: &str) -> Result<fjall::Keyspace> {
            self.db
                .keyspace(name, || KeyspaceCreateOptions::default())
                .map_err(|e| anyhow::anyhow!("fjall: {}", e))
        }
    }

    #[async_trait]
    impl EventStore for FjallStore {
        fn append(&self, key: &[u8], value: &[u8]) -> Result<()> {
            let part = self.keyspace("events")?;
            part.insert(key, value)
                .map_err(|e| anyhow::anyhow!("fjall insert: {}", e))?;
            Ok(())
        }

        fn get(&self, key: &[u8]) -> Result<Option<Vec<u8>>> {
            let part = self.keyspace("events")?;
            Ok(part.get(key).ok().flatten().map(|g| g.to_vec()))
        }

        fn delete(&self, key: &[u8]) -> Result<()> {
            let part = self.keyspace("events")?;
            part.remove(key)
                .map_err(|e| anyhow::anyhow!("fjall delete: {}", e))?;
            Ok(())
        }

        fn list_keys(&self, prefix: &[u8]) -> Result<Vec<Vec<u8>>> {
            let part = self.keyspace("events")?;
            let mut keys = Vec::new();
            for guard in part.iter() {
                let key = guard.key()?;
                if key.starts_with(prefix) {
                    keys.push(key.to_vec());
                }
            }
            Ok(keys)
        }

        fn count(&self) -> Result<u64> {
            let part = self.keyspace("events")?;
            Ok(part.iter().count() as u64)
        }
    }

    // --- Redb backend (production pattern, two tables) ---
    use redb::{ReadableDatabase, ReadableTable, TableDefinition};

    const SNAPSHOTS: TableDefinition<&[u8], &[u8]> = TableDefinition::new("snapshots");
    const CURSORS: TableDefinition<&[u8], &[u8]> = TableDefinition::new("cursors");

    pub struct RedbStore {
        db: Arc<redb::Database>,
    }

    impl RedbStore {
        pub fn open(path: &Path) -> Result<Self> {
            let db = redb::Database::create(path)?;
            Self::init_tables(&db)?;
            Ok(Self { db: Arc::new(db) })
        }

        pub fn create(path: &Path) -> Result<Self> {
            if path.exists() {
                std::fs::remove_file(path)?;
            }
            let db = redb::Database::create(path)?;
            Self::init_tables(&db)?;
            Ok(Self { db: Arc::new(db) })
        }

        fn init_tables(db: &redb::Database) -> Result<()> {
            let write = db.begin_write()?;
            write.open_table(SNAPSHOTS)?;
            write.open_table(CURSORS)?;
            write.commit()?;
            Ok(())
        }

        fn table_for_key(key: &[u8]) -> &'static str {
            if key.starts_with(b"snap:") {
                "snapshots"
            } else if key.starts_with(b"cur:") {
                "cursors"
            } else {
                "snapshots"
            }
        }
    }

    #[async_trait]
    impl EventStore for RedbStore {
        fn append(&self, key: &[u8], value: &[u8]) -> Result<()> {
            let table_name = Self::table_for_key(key);
            let write = self.db.begin_write()?;
            match table_name {
                "snapshots" => {
                    let mut table = write.open_table(SNAPSHOTS)?;
                    table.insert(key, value)?;
                }
                "cursors" => {
                    let mut table = write.open_table(CURSORS)?;
                    table.insert(key, value)?;
                }
                _ => return Err(anyhow::anyhow!("unknown table")),
            }
            write.commit()?;
            Ok(())
        }

        fn get(&self, key: &[u8]) -> Result<Option<Vec<u8>>> {
            let table_name = Self::table_for_key(key);
            let read = self.db.begin_read()?;
            match table_name {
                "snapshots" => {
                    let table = read.open_table(SNAPSHOTS)?;
                    Ok(table.get(key)?.map(|v| v.value().to_vec()))
                }
                "cursors" => {
                    let table = read.open_table(CURSORS)?;
                    Ok(table.get(key)?.map(|v| v.value().to_vec()))
                }
                _ => Ok(None),
            }
        }

        fn delete(&self, key: &[u8]) -> Result<()> {
            let table_name = Self::table_for_key(key);
            let write = self.db.begin_write()?;
            match table_name {
                "snapshots" => {
                    let mut table = write.open_table(SNAPSHOTS)?;
                    table.remove(key)?;
                }
                "cursors" => {
                    let mut table = write.open_table(CURSORS)?;
                    table.remove(key)?;
                }
                _ => return Err(anyhow::anyhow!("unknown table")),
            }
            write.commit()?;
            Ok(())
        }

        fn list_keys(&self, prefix: &[u8]) -> Result<Vec<Vec<u8>>> {
            let read = self.db.begin_read()?;
            let mut keys = Vec::new();
            for table_name in &["snapshots", "cursors"] {
                let table = match *table_name {
                    "snapshots" => read.open_table(SNAPSHOTS).ok(),
                    "cursors" => read.open_table(CURSORS).ok(),
                    _ => None,
                };
                if let Some(t) = table {
                    for item in t.iter()? {
                        if let Ok((key, _)) = item {
                            if key.value().starts_with(prefix) {
                                keys.push(key.value().to_vec());
                            }
                        }
                    }
                }
            }
            Ok(keys)
        }

        fn count(&self) -> Result<u64> {
            let read = self.db.begin_read()?;
            let mut total = 0u64;
            for table_name in &["snapshots", "cursors"] {
                let table = match *table_name {
                    "snapshots" => read.open_table(SNAPSHOTS).ok(),
                    "cursors" => read.open_table(CURSORS).ok(),
                    _ => None,
                };
                if let Some(t) = table {
                    total += t.iter()?.count() as u64;
                }
            }
            Ok(total)
        }
    }

    /// Exact StoreState unification + routing from production (src/store.rs:269)
    /// L7 evolution: add Arc<L7 keyspaces> or make the events/meta fields
    /// generic over more backends; preserve the tmpfs hot-path optimization.
    pub struct StoreState {
        pub events: Arc<FjallStore>,
        pub meta: Arc<RedbStore>,
        pub tmpfs: bool,
    }

    impl StoreState {
        pub fn open(base_path: &Path) -> Result<Self> {
            Ok(Self {
                events: Arc::new(FjallStore::open(&base_path.join("events.fjall"))?),
                meta: Arc::new(RedbStore::open(&base_path.join("meta.redb"))?),
                tmpfs: false,
            })
        }

        pub fn create(base_path: &Path) -> Result<Self> {
            if base_path.exists() {
                std::fs::remove_dir_all(base_path)?;
            }
            std::fs::create_dir_all(base_path)?;
            Ok(Self {
                events: Arc::new(FjallStore::create(&base_path.join("events.fjall"))?),
                meta: Arc::new(RedbStore::create(&base_path.join("meta.redb"))?),
                tmpfs: false,
            })
        }

        pub fn open_tmpfs(base_path: &Path) -> Result<Self> {
            if base_path.exists() {
                std::fs::remove_dir_all(base_path)?;
            }
            std::fs::create_dir_all(base_path)?;
            Ok(Self {
                events: Arc::new(FjallStore::create(&base_path.join("events.fjall"))?),
                meta: Arc::new(RedbStore::create(&base_path.join("meta.redb"))?),
                tmpfs: true,
            })
        }

        pub fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
            let backend = route_key(key);
            match backend {
                "events" => self.events.get(key).ok().flatten(),
                "snapshots" | "cursors" => self.meta.get(key).ok().flatten(),
                _ => self.events.get(key).ok().flatten(),
            }
        }

        pub fn put(&self, key: &[u8], value: &[u8]) -> Result<(), ()> {
            let backend = route_key(key);
            let result = match backend {
                "events" => self.events.append(key, value),
                "snapshots" | "cursors" => self.meta.append(key, value),
                _ => self.events.append(key, value),
            };
            result.map_err(|e| eprintln!("store put error: {}", e))
        }

        pub fn delete(&self, key: &[u8]) -> Result<(), ()> {
            let backend = route_key(key);
            let result = match backend {
                "events" => self.events.delete(key),
                "snapshots" | "cursors" => self.meta.delete(key),
                _ => self.events.delete(key),
            };
            result.map_err(|e| eprintln!("store delete error: {}", e))
        }

        pub fn list_keys(&self, prefix: &[u8]) -> Vec<Vec<u8>> {
            let backend = route_key(prefix);
            match backend {
                "events" => self.events.list_keys(prefix).unwrap_or_default(),
                "snapshots" | "cursors" => self.meta.list_keys(prefix).unwrap_or_default(),
                _ => self.events.list_keys(prefix).unwrap_or_default(),
            }
        }

        pub fn stats(&self) -> StoreStats {
            StoreStats {
                event_count: self.events.count().unwrap_or(0),
                meta_count: self.meta.count().unwrap_or(0),
                tmpfs: self.tmpfs,
            }
        }
    }

    #[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
    pub struct StoreStats {
        pub event_count: u64,
        pub meta_count: u64,
        pub tmpfs: bool,
    }
}
