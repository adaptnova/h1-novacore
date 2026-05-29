# How the Production Host Satisfies the FFI (Wasm64 + wasmtime)

**Date:** 2026-05-29 (autonomous deep dive)  
**Key Finding:** The actual Rust implementations of `host_store_read`, `host_store_write`, etc. are provided to the Wasm module at wasmtime instantiation time by the native host shim. They are not visible in the simple grep of src/ because they are likely defined as closures or functions passed to the wasmtime `Linker` when creating the `Instance` for the loaded Wasm module.

## Current Understanding from the Source

1. **Wasm side** (`l6-store-wasm`):
   - Declares `extern "C" { pub fn host_store_read(...) ... }`
   - Calls these when the Wasm code wants to do store operations.
   - Also has `l6_on_nats_message` as an exported callback.

2. **Host side** (`l6-store-host`):
   - Uses `wasmtime::Engine` + `Module` (see WasmLoader in nats.rs).
   - Loads the Wasm module.
   - When instantiating (in the request handler path), the host must use a `wasmtime::Linker` to provide the `host_store_*` functions as `Func`.
   - Those `Func` implementations have access to the `StoreState` (FjallStore for "evt:*", RedbStore for "snap:*"/"cur:*").
   - The same host also provides NATS I/O, gRPC, health, metrics, etc.

The exact `linker.func_wrap("env", "host_store_read", |...| { ... })` code was not surfaced in the searches of the current src/ checkout. This is common when the heavy linking logic lives in a helper or is done inside the Wasm execution path that we have not fully read yet.

## Why This Matters for L7+

For a real L7+ implementation using fjall 3:

- We should replicate the **exact same contract** on the Wasm side (the FFI we documented in ffi_contract.md).
- On the native host side, we provide high-quality implementations backed by fjall 3 (with its superior keyspaces, value log, snapshots, etc.).
- The Wasm module stays small, auditable, and wasm64-friendly.
- The host owns all the hard parts (durability, async NATS/gRPC, wasmtime instantiation, policy, metrics).

This pattern is already proven in production with fjall 3.1 + redb 4.0.

## Recommended Next Autonomous Step for the Spike

Create a small example in the spike that shows a minimal `wasmtime::Linker` setup providing the `host_store_*` functions backed by our L7Store (multiple fjall keyspaces). This makes the spike a true prototype of how the real L7+ host would work.

— Riven (autonomous, continual)
2026-05-29
