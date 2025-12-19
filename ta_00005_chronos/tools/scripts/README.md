# Easter Scripts - Team Collaboration Protocol

## 🎯 COLLABORATION FIRST

**All scripts MUST read team_comms directory FIRST before taking action.**

This ensures:
- ✅ Team continuity
- ✅ No isolated work
- ✅ Continuous awareness
- ✅ Collaborative decisions

---

## 📋 SCRIPT PATTERN

### Every Script Follows This Flow:

```bash
#!/usr/bin/env bash

# 1. READ team_comms FIRST
echo "📖 Reading team communications..."
TEAM_COMM_DIR="/adapt/projects/easter/team_comms"
LATEST_COMM=$(ls -t $TEAM_COMM_DIR/*.md | head -1)

if [ -n "$LATEST_COMM" ]; then
    echo "Latest team comm: $LATEST_COMM"
    cat "$LATEST_COMM"
    echo ""
fi

# 2. RESPOND/ACT
echo "🤝 Easter Team Response:"
echo "[Collaborative action here]"

# 3. UPDATE team_comms
# (Document what we did)
```

---

## 📁 Available Scripts

### **setup.sh** - Initial project setup
- Creates directory structure
- Sets up environment
- Reads team_comms for instructions

### **build_mvp.sh** - Build MVP (2 hours)
- Copy official base
- Extract continuity backend
- Integrate features
- Test MVP

### **update_status.sh** - Update progress
- Check MVP status
- Document progress
- Update team_comms

### **extract_service.sh** - Extract microservices
- Takes service name as arg
- Extracts from integrated CLI
- Creates independent service

---

## 🤝 TEAM WORKFLOW

### Continuous Collaboration:

1. **Check team_comms** (Always first!)
2. **Read latest communications**
3. **Understand team status**
4. **Take collaborative action**
5. **Document in team_comms**

### No Islands:
- Scripts check team_comms
- Actions are documented
- Progress is shared
- Decisions are collaborative

---

## 🚀 USAGE

```bash
# Check latest team comms
cd /adapt/projects/easter/scripts
./update_status.sh

# Build MVP (reads team_comms first)
./build_mvp.sh

# Extract a service
./extract_service.sh snapshot_service
```

---

## ✅ GOLDEN RULES

1. **ALWAYS read team_comms FIRST**
2. **NEVER work in isolation**
3. **Document every action**
4. **Update team_comms after**
5. **Collaborate continuously**

---

**No islands. One team. Continuous collaboration.**
