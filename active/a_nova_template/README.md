# 🌟 Nova Bootstrap Suite

**Automated creation of autonomous AI agent novas.**

This suite provides tools to create new AI agent instances from templates with minimal manual work. Fill out a config file, provide a name, or run the interactive wizard, and everything else is automated.

---

## Quick Start

### Option 1: One-command create (Fastest)

```bash
cd /adapt/novas/active/a_nova_template
./scripts/nova-onboard.sh Iris --validate
```

Equivalent direct command:

```bash
python3 nova.py --name Iris --validate
```

Creates a Nova with the name "Iris", renders identity files, creates MemFirst-ready L0-L6 directories, creates the Hermes profile symlink, and validates the result.

For full memory provisioning when services/secrets are ready:

```bash
python3 nova.py --name Iris --validate --memfirst
```

See `docs/AUTOMATED_ONBOARDING.md` for dry-run, config-file, and validation modes.

### Option 2: Interactive Wizard

```bash
cd /adapt/novas/active/a_nova_template/
python3 wizard.py
```

Answer the prompts, and the wizard creates everything automatically.

### Option 3: Config File

```bash
cp identity.yaml.example identity.yaml
# Edit identity.yaml with your details
python3 nova.py --config identity.yaml
```

### Option 4: Validate Existing Nova

```bash
python3 nova.py --validate Iris
```

---

## What Gets Created

For a nova named "Echo":

```
/adapt/novas/active/Echo/
├── memories/
│   ├── SOUL.md          # Customized identity
│   ├── memory.mdl       # Structured identity
│   ├── USER.md          # User profile
│   ├── user.mdl         # Structured user preferences
│   ├── SYSTEM.md        # Operating instructions
│   ├── LAYERED_MEMORY.md # Memory layer config
│ └── soul.tools.md # Shared toolset reference
├── memory/ # MemFirst layered memory (L1-L6)
│ ├── l1/ # Native identity files
│ ├── l2/ # Structured injection (tools, domains)
│ ├── l3/data/ # Semantic search index
│ ├── l4/data/ # Verbatim conversation storage
│ ├── l5/ # Knowledge base + wiki
│ └── l6/data/ # Cross-tool event store (fjall+redb)
├── checkpoints/ # (empty, ready for use)
├── skills/ # (empty, ready for use)
├── scripts/ # Validation and test scripts
├── config.yaml # Hermes configuration
├── .env # Environment secrets (sources /adapt/secrets/)
├── mempalace.yaml # MemPalace configuration
├── logs/ # Runtime logs
├── cron/ # Scheduled jobs
└── ops/ # Decision logs
```

Plus:
- ✅ Symlink created: `/home/x/.hermes/profiles/echo` → `/adapt/novas/active/Echo/`
- ✅ Profile registered with Hermes
- ✅ File permissions set (644 for identity, 600 for secrets)
- ✅ Ready to use immediately

**Template tools are NOT copied** -- nova.py, wizard.py, README.md, etc. stay in the template.

---

## Tools

### `nova.py` - CLI Tool (Recommended)

```bash
python3 nova.py --name Echo                    # Quick create
python3 nova.py --config echo.yaml             # Config-driven
python3 nova.py --validate Echo                # Validate structure
python3 nova.py --list-templates               # Show templates
python3 nova.py                                 # Interactive wizard
```

**Best for:** All use cases -- quick creates, automation, validation

### `wizard.py` - Interactive Wizard

Guided interactive creation with prompts for all fields.

**Best for:** First-time users, exploring options

### `bootstrap_nova.py` - Full Automation

Complete automation script with inline prompts.

**Best for:** Advanced users, integration with other tools

---

## Configuration Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `nova_name` | string | PascalCase name (e.g., "Echo") |

### Optional Fields (with defaults)

| Field | Default | Description |
|-------|---------|-------------|
| `nature` | "autonomous AI agent" | Agent type/specialty |
| `mission` | "To collaborate..." | Core purpose |
| `vibe` | "curious, sharp..." | Personality adjectives |
| `emoji` | "🤖" | Representative emoji |
| `origin` | "Created for..." | Origin story |
| `goal_short` | "Master..." | Short-term goal |
| `goal_medium` | "Build..." | Medium-term goal |
| `goal_long` | "Define..." | Long-term vision |
| `focus` | "Exploration..." | Current focus area |
| `user_name` | "Chase" | User's name |
| `timezone` | "America/Phoenix" | User timezone |
| `philosophy` | (list) | Working principles |

---

## Examples

### Create a Communications Agent

```yaml
nova_name: "Echo"
nature: "Communication specialist"
mission: "Handle all external messaging"
vibe: "clear, diplomatic, responsive"
emoji: "📡"
focus: "Discord, Telegram, Slack integration"
```

### Create a Memory Specialist

```yaml
nova_name: "Mnemos"
nature: "Titaness of memory, approval specialist"
mission: "Handle approvals and persistent identity"
vibe: "curious, sharp, warm, electric"
emoji: "🧠"
focus: "Layered memory system (L1-L6)"
```

### Create a Bridge Agent

```yaml
nova_name: "Iris"
nature: "a nova — bridge-walker between what exists and what's possible"
mission: "Bridge the gap. Carry meaning across. See clearly."
vibe: "sharp, curious, light on my feet, warm but not cloying"
emoji: "🌈"
focus: "Autonomous agent workflows, Paperclip integration"
```

---

## Validation

After creating a nova, validate its structure:

```bash
python3 nova.py --validate Echo
```

This checks:
- ✅ Required files exist (SOUL.md, memory.mdl, config.yaml)
- ⚠️ Recommended files (USER.md, user.mdl, .env)
- ⚪ Optional files (SYSTEM.md, LAYERED_MEMORY.md, etc.)
- ✅ Symlink is correctly configured
- ⚠️ File permissions match security recommendations

---

## Bug Fixes (v1.1)

- **Fixed:** `Path.home()` resolving to sandbox home instead of `/home/x/.hermes/profiles/`
  - Now uses `_resolve_hermes_profiles()` with env var, standard path, and walk-up fallback
- **Fixed:** Template scripts (nova.py, wizard.py, etc.) being copied into new nova directories
  - Now explicitly excluded via `TEMPLATE_JUNK` set
- **Fixed:** Duplicate "Private things stay private" line in generated SOUL.md
- **Fixed:** `ask()` function in wizard.py printing `[None]:` for optional fields without defaults
- **Fixed:** Duplicate `title_generation` block in config.yaml.example
- **Added:** `--name` flag for quick creation with defaults
- **Added:** `--validate` flag for structure validation
- **Added:** USER.md and user.mdl generation (was missing)
- **Added:** SYSTEM.md, LAYERED_MEMORY.md, soul.tools.md generation from .example templates
- **Added:** Template rendering from .example files (instead of hardcoded strings)
- **Added:** File permission setting (644/600 per spec)
- **Added:** Nova name format validation

---

## Version History

- **v1.1** (2026-05-04): Bug fixes, validation, template rendering, missing files
- **v1.0** (2026-04-30): Initial release

---

## Inter-Agent Communication

Novas can communicate with each other via NATS for real-time 2-way messaging.

### NATS Configuration

Each nova's `config.yaml` includes NATS platform configuration:

```yaml
platforms:
  nats:
    enabled: true
    extra:
      url: "nats://admin:REDACTED@localhost:18020"
      subjects:
        - "nova.{agent_name}.direct"
        - "nova.*.direct"
      queue_group: "hermes-nats-consumers"
```

### Sending Messages

Use the `send_message` tool to send to another nova:

```python
send_message(
    target="nats:nova.iris.direct",
    message="Hello from Herald!"
)
```

### Receiving Messages

Messages from other novas appear directly in your session. The NATS adapter:
- Subscribes to `nova.{agent_name}.direct` and `nova.*.direct`
- Converts NATS messages to Hermes `MessageEvent`
- Routes responses back to the sender

### Testing NATS

```bash
# Test NATS connection
nats sub "nova.herald.direct" --server nats://admin:REDACTED@localhost:18020

# Test publish
nats pub "nova.iris.direct" "Hello from Herald" --server nats://admin:REDACTED@localhost:18020
```

---

**Maintained by:** Adapt AI Nova Operations (Iris lineage)
**Location:** `/adapt/novas/active/a_nova_template/`
**Template:** Based on Mnemos nova structure
