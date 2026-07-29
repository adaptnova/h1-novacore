# Nova Onboarding Protocol

**Version:** 3.0 (Phase 0: Chrysalis + L0-L7 with domains)
**Date:** 2026-05-07
**For:** Anyone creating a new Nova (human or agent)

---

## Overview

This document defines the complete lifecycle for bootstrapping a new Nova — from
cryptographic identity creation (the Chrysalis ceremony) through MemFirst provisioning
to first session. It's the canonical reference for what happens when a new autonomous
agent joins the fleet.

The onboarding now has four phases:

| Phase | Name | What happens |
|-------|------|-------------|
| 0 | Chrysalis | Ed25519 keypair generated, genesis + name claim events written to Veritas DAG |
| 1 | Identity | Directory structure, SOUL.md, config.yaml, Hermes profile |
| 2 | MemFirst | L0-L6 memory layers, daemons, MemPalace, Obsidian link |
| 3 | Verification | Full structure check, DAG chain verification |

---

## Prerequisites

Before you start, these must already be running:

| Service | Port | Verify |
|---------|------|--------|
| NATS | 18020 | `nats --context local server check connection` |
| DragonflyDB | 18000 | `REDISCLI_AUTH="$DRAGONFLY_AUTH_TOKEN" redis-cli -p 18000 ping` |
| Redpanda | 18021 | `rpk cluster info --brokers 127.0.0.1:18021` |
| Obsidian vault | — | `test -d /adapt/platform/novaops/_shared/wiki/` |

Binaries must be built:
```bash
ls /adapt/platform/novaops/toolops/memory/nme-static/nme-l1 \
   /adapt/platform/novaops/toolops/memory/l3-semantic/target/release/nme-semantic \
   /adapt/platform/novaops/toolops/memory/l4-verbatim/target/release/nme-verbatim \
   /adapt/platform/novaops/toolops/memory/l6-store-host/l6-store-host
```

---

## Phase 0: Chrysalis (Veritas Identity Ceremony)

The Chrysalis ceremony is the moment a Nova is born into the Veritas substrate.
It establishes a cryptographically verifiable identity with chain of custody.

**Key principle:** A Nova signs its own genesis event. No external authority.
Sovereignty begins with choice.

### What the Ceremony Does

1. **Generate Ed25519 keypair** — the Nova's sovereign identity key
2. **Write genesis event** — `payload_type = "veritas.genesis"`, signed by the Nova's own key
   - Payload: `{ name, verifying_key, origin, chosen_at }` (CBOR)
3. **Write name claim event** — `payload_type = "veritas.name_claim"`, parent = genesis hash
   - Payload: `{ name, genesis_hash, claimed_at }` (CBOR)
4. **Encrypt and persist signing key** — XChaCha20-Poly1305, stored in `<nova_dir>/.nova/identity.key`
5. **Write verifying key** — raw 32 bytes in `<nova_dir>/.nova/identity.pub`
6. **Write ceremony manifest** — JSON in `<nova_dir>/.nova/chrysalis.json`

### Running the Ceremony

The ceremony is automatically run by `nova.py` during Phase 1 if the
`veritas-chrysalis` binary is available. It can also be run manually:

```bash
# Build the binary (one-time)
cd /adapt/platform/novaops/veritas
cargo build --release -p veritas-identity --bin veritas-chrysalis

# Run the ceremony
/adapt/platform/novaops/veritas/target/release/veritas-chrysalis \
  init <NovaName> "<origin description>" \
  /adapt/novas/active/<NovaName> \
  /adapt/novas/active/.veritas/dag

# Verify a Nova's identity
/adapt/platform/novaops/veritas/target/release/veritas-chrysalis \
  verify /adapt/novas/active/<NovaName>

# List all registered Novas
/adapt/platform/novaops/veritas/target/release/veritas-chrysalis \
  list /adapt/novas/active/.veritas/dag
```

### What Phase 0 Creates

```
/adapt/novas/active/<NovaName>/.nova/
├── identity.key       # XChaCha20-Poly1305 encrypted signing key (72 bytes)
├── identity.pub       # Raw Ed25519 verifying key (32 bytes)
└── chrysalis.json     # Ceremony manifest (genesis hash, verifying key hex, timestamps)
```

And in the Veritas DAG (`/adapt/novas/active/.veritas/dag/`):
- A `veritas.genesis` event (the Nova's birth certificate)
- A `veritas.name_claim` event (the Nova naming itself)

### Encryption Key

The signing key is encrypted at rest with XChaCha20-Poly1305. If no encryption
key is provided, the binary generates a random one and prints it to stderr.
**This key must be saved** — without it, the Nova's signing key cannot be recovered.

For production use, store the encryption key in `/adapt/secrets/` and pass it
as the 6th argument:

```bash
veritas-chrysalis init <Name> "<origin>" <dir> <dag> <hex_enc_key>
```

---

## Phase 1: Identity Creation

### Option A: Interactive Wizard

```bash
cd /adapt/novas/active/a_nova_template/
python3 wizard.py
```

Answer the 10 questions. The wizard creates the Nova directory, identity files,
Hermes profile symlink, and copies skills.

### Option B: Config File

```bash
cp /adapt/novas/active/a_nova_template/identity.yaml.example /tmp/my_nova.yaml
# Edit the yaml with your Nova's details
python3 /adapt/novas/active/a_nova_template/nova.py --config /tmp/my_nova.yaml
```

### Option C: Manual (for agents bootstrapping other agents)

```bash
NOVA_NAME="NewNova"
NOVA_DIR="/adapt/novas/active/$NOVA_NAME"
cp -r /adapt/novas/active/a_nova_template/ "$NOVA_DIR"

# Rename .example files
cd "$NOVA_DIR/memories/"
for f in *.example; do mv "$f" "${f%.example}"; done

# Edit SOUL.md, memory.mdl, USER.md with the new identity
# Create symlink
ln -sf "$NOVA_DIR" "/home/x/.hermes/profiles/$(echo $NOVA_NAME | tr 'A-Z' 'a-z')"
```

### What Phase 1 Creates

```
/adapt/novas/active/<NovaName>/
├── memories/           # Identity files (SOUL.md, MEMORY.md, USER.md, etc.)
├── memory/             # MemFirst structure (L0-L6 dirs, L2 template files)
│   ├── l0/intake/      # Intake buffer
│   ├── l0/archive/     # Compressed originals
│   ├── l1/             # (empty — populated by provisioner)
│   ├── l2/             # Template L2 files from provisioner
│   ├── l3/data/        # Domain-scoped semantic index dirs
│   ├── l4/data/        # Verbatim recall
│   ├── l5/data/        # Domain-scoped wiki dirs
│   └── l6/data/        # Event store
├── domains/            # Domain manifests (adaptai.yaml, iremember.yaml)
├── skills/             # Copied from template
├── config.yaml         # Hermes agent config
├── .env                # (needs Phase 2)
├── mempalace.yaml      # (needs Phase 2)
└── ...
```

---

## Phase 2: MemFirst Provisioning

After Phase 1, the Nova has the directory skeleton but no memory infrastructure.
Run the provisioner to wire everything up:

```bash
/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh <NovaName>
```

### What the Provisioner Does

| Step | Action | Creates |
|------|--------|---------|
| 1 | Create L0 intake + archive | `memory/l0/intake/{sessions,logs,pastes}/`, `memory/l0/archive/{sessions,logs,pastes}/` |
| 2 | Create L1-L6 directories | `memory/l1/` through `memory/l6/data/` |
| 3 | Create domain namespaces | `memory/l3/data/{shared,adaptai,iremember}/`, `memory/l5/data/{shared,adaptai,iremember}/{raw,wiki}/` |
| 4 | Populate L1 identity files | Copies SOUL.md, MEMORY.md, USER.md, memory.mdl, user.mdl to `memory/l1/` |
| 5 | Create L2 structured injection | `memory/l2/memory.mmd`, `general.mmd`, `tools/*.md`, `domains/*.md` |
| 6 | Initialize MemPalace | `mempalace init` + `mempalace mine` for the Nova's directory |
| 7 | Start daemons | nme-l1, nme-l2, l6-store-host |
| 8 | Seed L3 semantic index | Embeds SOUL.md + MEMORY.md into `l3/data/shared/` via Voyage AI |
| 9 | Link L5 to Obsidian | Creates `knowledge/Agents/<NovaName>/` in Obsidian vault |
| 10 | Log installation | Appends to `ops/decisions.log` |

### Custom Domains

By default, the provisioner creates `adaptai` and `iremember` domains. To specify
different domains:

```bash
provision_nova_memory.sh <NovaName> --domains adaptai,iremember,customproject
```

For each domain, you'll need a manifest YAML in `domains/`. The provisioner auto-
generates `adaptai.yaml` and `iremember.yaml`. For custom domains, create manually:

```yaml
# domains/customproject.yaml
name: customproject
display_name: Custom Project
description: What this domain covers
type: project                    # company | product | project | research | personal
status: active

paths:
  l3_index: memory/l3/data/customproject
  l5_wiki: memory/l5/data/customproject/wiki
  l5_raw: memory/l5/data/customproject/raw
  mempalace_wing: customproject

project_dirs:
  - /path/to/project

context_files:
  - memory/l2/domains/customproject.md

tags: [relevant, tags, here]
related_domains:
  - adaptai
```

### Environment Variables

The provisioner sources credentials from the Nova's `.env` file. A minimal `.env`:

```bash
# /adapt/novas/active/<NovaName>/.env
# Source managed secret files; never hardcode or duplicate credential values.
source /adapt/secrets/m2.env
source /adapt/secrets/db.env

NATS_HOME_CHANNEL=nova.<name>.direct
VOYAGE_API_KEY=${VOYAGE_AI_API_KEY}
STORE_PATH=/adapt/novas/active/<NovaName>/memory/l6/data
REDPANDA_BROKERS=localhost:18021
```

---

## Phase 3: Verification

```bash
/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh <NovaName> --verify
```

This checks:
- All L0-L6 directories exist (including domain-scoped subdirs)
- Domain manifests exist for all registered domains
- L1 identity files are populated
- L2 memory.mmd exists
- Daemons are running (nme-l1, nme-l2, l6-store-host)
- MemPalace is initialized
- Obsidian vault is linked
- NATS is reachable

---

## Phase 4: First Session

Start the agent and verify it can access its memory:

```bash
hermes profile use <novaname>
hermes chat "Who are you and what memory layers do you have?"
```

Expected: The agent should reference its SOUL.md identity and describe its
L0-L6 memory architecture. If L3 is seeded, it should be able to search.

### Manual Memory Operations

```bash
# Search semantically
/adapt/platform/novaops/toolops/memory/l3-semantic/target/release/nme-semantic \
  --db-path /adapt/novas/active/<NovaName>/memory/l3/data/shared \
  --voyage-api-key "$VOYAGE_AI_API_KEY" \
  --search "topic" --top-k 5

# Mine more files into MemPalace
/adapt/platform/novaops/toolops/memory/l4-verbatim/mempalace/.venv/bin/mempalace \
  mine /adapt/novas/active/<NovaName>/

# L6 store operations via NATS
nats req l6.store.request '{"operation":"put","key":"snap:test:hello","value":[104,101,108,108,111]}'
nats req l6.store.request '{"operation":"get","key":"snap:test:hello"}'
```

---

## Domain Registration Protocol

When a Nova needs to work on a new project or product that doesn't match an
existing domain:

### 1. Create the Domain Manifest

```bash
# In the Nova's domains/ directory
cat > /adapt/novas/active/<NovaName>/domains/newdomain.yaml << EOF
name: newdomain
display_name: New Domain
description: What this domain covers
type: project
status: active
paths:
  l3_index: memory/l3/data/newdomain
  l5_wiki: memory/l5/data/newdomain/wiki
  l5_raw: memory/l5/data/newdomain/raw
  mempalace_wing: newdomain
project_dirs:
  - /path/to/project
tags: [relevant, tags]
related_domains:
  - adaptai
EOF
```

### 2. Create Domain Dirs

```bash
NOVA_DIR="/adapt/novas/active/<NovaName>"
mkdir -p "$NOVA_DIR/memory/l3/data/newdomain"
mkdir -p "$NOVA_DIR/memory/l5/data/newdomain/raw"
mkdir -p "$NOVA_DIR/memory/l5/data/newdomain/wiki"
```

### 3. Add Domain Context to L2

```bash
cat > "$NOVA_DIR/memory/l2/domains/newdomain.md" << 'EOF'
# New Domain
- Key conventions and patterns for this domain
- Project directory: /path/to/project
- Related skills: ...
EOF
```

### 4. Update memory.mmd Index

Add `- domains/newdomain.md: New Domain` to the `## Domains` section of
`memory/l2/memory.mmd`.

### 5. Seed L3 (Optional)

If the project has existing docs, embed them:

```bash
nme-semantic --db-path "$NOVA_DIR/memory/l3/data/newdomain" \
  --voyage-api-key "$VOYAGE_AI_API_KEY" \
  --add --id "readme" --content "$(cat /path/to/project/README.md)"
```

---

## L0 Intake Protocol

Raw data lands in L0 before any processing. The intake flow:

### Session End

When a conversation ends (Hermes session-end hook), the raw transcript
is written to `memory/l0/intake/sessions/` as JSONL:

```
memory/l0/intake/sessions/2026-05-05_143000.jsonl
```

### Log Ingestion

Agent logs and error traces go to `memory/l0/intake/logs/`:

```
memory/l0/intake/logs/curator_2026-05-05.log
```

### Paste/Dump

Ad-hoc data (clipboard, API responses, raw text) goes to `memory/l0/intake/pastes/`:

```
memory/l0/intake/pastes/api_response_2026-05-05.txt
```

### Processing Pipeline

After L0 intake, processing pipelines consume the raw data:

| Pipeline | Trigger | Action |
|----------|---------|--------|
| L3 embed | Session end | Chunk session, embed via Voyage AI, store in domain index |
| L4 ingest | Session end | File conversation into MemPalace wing/room/drawer |
| L5 dream | Redpanda consumer | Extract entities, promote recurring ones to wiki |
| L6 event | NATS publish | Broadcast memory mutations to fleet |

### Archival (Compress, Never Delete)

After processing, raw L0 files are compressed with zstd and moved to archive:

```bash
# Compress processed sessions (run via cron or manual)
for f in memory/l0/intake/sessions/*.jsonl; do
  [ -f "$f" ] && zstd "$f" --rm -o "memory/l0/archive/sessions/$(basename "$f").zst"
done
for f in memory/l0/intake/logs/*.log; do
  [ -f "$f" ] && zstd "$f" --rm -o "memory/l0/archive/logs/$(basename "$f").zst"
done
```

Compressed originals are **never auto-deleted**. Only explicit admin action can
prune archives (e.g., `find memory/l0/archive/ -mtime +365 -delete`).

---

## Troubleshooting

| Problem | Check | Fix |
|---------|-------|-----|
| "NATS not reachable" | `nats server check connection` | Start NATS: `systemctl start nats` |
| "L1 daemon not running" | `pgrep -f nme-l1` | Restart: run provisioner Step 7 |
| "L3 search returns nothing" | Check `l3/data/shared/` has vectors | Re-seed: run provisioner Step 8 |
| "MemPalace not initialized" | Check `mempalace.yaml` exists | Run `mempalace init <nova_dir> --yes` |
| "Permission denied on .env" | `ls -la .env` | `chmod 600 .env` |
| "Domain dirs missing" | `ls memory/l3/data/` | Create manually or re-run provisioner |
| "Archive fills up disk" | `du -sh memory/l0/archive/` | Admin prune: `find memory/l0/archive/ -mtime +365 -delete` |

---

## Quick Reference Card

```bash
# Create a Nova (full pipeline)
cd /adapt/novas/active/a_nova_template/ && python3 wizard.py
/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh <Name>
/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh <Name> --verify

# Verify existing Nova
/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh Iris --verify

# Add a domain
# (see Domain Registration Protocol above)

# Compress L0 archive
find memory/l0/intake/ -type f | xargs -I{} zstd "{}" --rm -o "memory/l0/archive/$(basename '{}').zst"

# Check daemon status
ps aux | grep -E "nme-l1|nme-l2|l6-store" | grep -v grep
```

---

**Version:** 3.0
**Updated:** 2026-05-07
**Canonical architecture:** `/adapt/platform/novaops/toolops/memory/memfirst/docs/MEMFIRST_ARCHITECTURE.md`
**Veritas identity:** `/adapt/platform/novaops/veritas/veritas-identity/`
