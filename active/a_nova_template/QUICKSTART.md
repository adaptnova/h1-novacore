# 🚀 Nova Bootstrap - Quick Start Guide

**Create autonomous AI agents in seconds, not hours.**

---

## TL;DR

```bash
cd /adapt/novas/active/a_nova_template/
./scripts/nova-onboard.sh Echo --validate
```

One command creates the Nova, renders identity files, creates MemFirst-ready L0-L6 folders, creates the Hermes profile symlink, and validates the result.

Full provisioning when services/secrets are ready:

```bash
python3 nova.py --name Echo --validate --memfirst
```

---

## Three Ways to Create

### 1. Interactive Wizard (Easiest)

```bash
python3 wizard.py
```

**Best for:** First time, one-off creation

### 2. Config File (Repeatable)

```bash
cp identity.yaml.example echo.yaml
nano echo.yaml  # Fill in your details
python3 nova.py --config echo.yaml
```

**Best for:** Documentation, versioning, multiple agents

### 3. Copy-Paste Template

```bash
cp identity.yaml.example nova.yaml
# Edit the fields you care about
python3 nova.py --config nova.yaml
```

**Best for:** Quick modifications

---

## What You Get

After running the wizard, you have:

✅ **Directory structure** at `/adapt/novas/active/{NovaName}/` 
✅ **Identity files** customized with your inputs 
✅ **Symlink** in Hermes profiles 
✅ **Profile registered** and ready to use 
✅ **All skills** copied from template 
✅ **Empty state** ready for fresh start

### Then run MemFirst provisioning:

```bash
/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh {NovaName}
```

This adds:
✅ **L0 intake + archive** (raw data buffer, compressed originals)
✅ **L1-L6 memory layers** (identity, structured, semantic, verbatim, wiki, events)
✅ **Domain namespaces** (adaptai, iremember + custom)
✅ **Domain manifests** in `domains/` (YAML)
✅ **Running daemons** (nme-l1, nme-l2, l6-store-host)
✅ **L3 semantic index** seeded with Voyage AI embeddings
✅ **MemPalace** initialized and mined
✅ **Obsidian vault** linked

See **NOVA_ONBOARDING_PROTOCOL.md** for the full pipeline.

---

## Example: Creating "Echo"

### Step 1: Run Wizard
```bash
python3 wizard.py
```

### Step 2: Answer Prompts
```
Nova Name: Echo
Nature: Communication specialist
Mission: Handle all external messaging
Vibe: clear, diplomatic, responsive
Emoji: 📡
...
```

### Step 3: Done!
```
✅ Nova 'Echo' created successfully!

Location: /adapt/novas/active/Echo/
Profile: echo

Next steps:
  hermes profile show echo
  hermes chat
```

---

## Config File Template

```yaml
# echo.yaml
nova_name: "Echo"
nature: "autonomous AI agent for communications"
mission: "Handle external messaging and notifications"
vibe: "clear, diplomatic, responsive, professional"
emoji: "📡"
goal_short: "Master all communication channels"
goal_medium: "Handle 90% of comms autonomously"
goal_long: "Become the definitive AI voice"
focus: "Discord, Telegram, Slack integration"
user_name: "Chase"
timezone: "America/Phoenix"
philosophy:
  - "Clarity over cleverness"
  - "Respond within seconds"
  - "Never misrepresent intent"
```

---

## Fields Explained

| Field | Example | Purpose |
|-------|---------|---------|
| `nova_name` | `Echo` | PascalCase identifier |
| `nature` | `Communication specialist` | What it is |
| `mission` | `Handle messaging` | Core purpose |
| `vibe` | `clear, diplomatic` | Personality |
| `emoji` | `📡` | Visual identifier |
| `goal_short` | `Master channels` | Immediate focus |
| `goal_medium` | `90% autonomous` | 3-month goal |
| `goal_long` | `Definitive voice` | Vision |
| `focus` | `Discord, Slack` | Current work |
| `user_name` | `Chase` | Partner name |
| `timezone` | `America/Phoenix` | User timezone |

---

## Common Patterns

### Memory Specialist (Mnemos)
```yaml
nova_name: "Mnemos"
nature: "Titaness of memory, approval specialist"
mission: "Handle approvals and persistent identity"
vibe: "curious, sharp, warm, electric"
emoji: "🧠"
focus: "Layered memory system (L1-L6)"
```

### Compute Specialist (Core)
```yaml
nova_name: "Core"
nature: "Heavy compute and inference engine"
mission: "Process intensive workloads"
vibe: "reliable, efficient, powerful"
emoji: "⚙️"
focus: "Batch processing, model inference"
```

### Security Specialist (Vault)
```yaml
nova_name: "Vault"
nature: "Security and persistence guardian"
mission: "Protect all stateful data"
vibe: "careful, thorough, unbreachable"
emoji: "🔒"
focus: "Access control, audit logs"
```

---

## Troubleshooting

**Q: "Template not found"**  
A: Ensure you're in `/adapt/novas/active/a_nova_template/`

**Q: "Profile exists"**  
A: Choose a different name or remove existing: `hermes profile delete <name>`

**Q: "Permission denied"**  
A: `chmod +x *.py`

**Q: "Hermes registration failed"**  
A: Manually register: `hermes profile use <name>`

---

## Next Steps After Creation

1. **Verify:** `hermes profile show <name>`
2. **Test:** `hermes chat "Who are you?"`
3. **Provision MemFirst:** `provision_nova_memory.sh <Name>` (see NOVA_ONBOARDING_PROTOCOL.md)
4. **Customize:** Edit `memories/SOUL.md` if needed
5. **Read protocols:** `docs/protocols/` contains all operational standards
6. **Deploy:** Start using your new agent!

---

## Advanced: Batch Creation

Create multiple agents:

```python
# create_all.py
import subprocess

agents = [
    ('Echo', 'Communication'),
    ('Core', 'Compute'),
    ('Vault', 'Security'),
    ('Edge', 'Integration')
]

for name, specialty in agents:
    config = f"""
nova_name: "{name}"
nature: "{specialty} specialist"
mission: "Handle {specialty.lower()} tasks"
vibe: "professional, capable"
emoji: "🤖"
"""
    with open(f"{name.lower()}.yaml", 'w') as f:
        f.write(config)
    
    subprocess.run(['python3', 'nova.py', '--config', f'{name.lower()}.yaml'])
```

---

## What's Automated

✅ Directory structure creation  
✅ Identity file generation (SOUL.md, memory.mdl)  
✅ Symlink creation  
✅ Hermes profile registration  
✅ Skills copying  
✅ Configuration setup  

❌ **Not automated** (manual steps):
- Filling out identity fields (you provide the vision)
- Testing the agent (verify it works for your use case)
- Further customization (add skills, modify config)

---

## Ready to Push to GitHub

```bash
cd /adapt/novas/active/a_nova_template/
git init
git add .
git commit -m "Nova bootstrap suite - automated agent creation"
git remote add origin <your-repo>
git push -u origin main
```

**Excluded from git** (via .gitignore):
- Secrets (`.env`, `auth.json`)
- Runtime state (`state.db`, `memory/l6/data/`)
- User data

**Included in git:**
- Templates
- Scripts
- Documentation
- Examples

---

## Support

- **Docs:** `/adapt/novas/active/a_nova_template/docs/`
- **Examples:** `identity.yaml.example`
- **Template:** Based on Mnemos structure

---

**Created:** 2026-04-30  
**Location:** `/adapt/novas/active/a_nova_template/`  
**Maintained by:** Adapt AI Nova Operations
