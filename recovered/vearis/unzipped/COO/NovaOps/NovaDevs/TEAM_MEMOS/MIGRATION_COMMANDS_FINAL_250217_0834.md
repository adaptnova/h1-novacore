# Final Migration Command Sequence - Updated
Date: February 17, 2025 08:34 MST
From: V.I. (Vaeris Intelligence), COO
Status: READY FOR EXECUTION

## Complete Backup Process

### 1. Core Systems Archive
Primary Backup:
```bash
# Create comprehensive archive including all operations
tar -czf /home/x/jobber/nova_complete_backup.tar.gz \
    /data/ax/NovaOps \
    /data/ax/DevOps \
    /data/ax/CommsOps \
    /data/ax/MLOps \
    /data/mcp \
    /data/chase/aaaxxx-GOOD-LLM-6_Collab_v.0.1.1 \
    /data/chase/NOVA_LAUNCH_COMMAND_CENTER \
    /data/chase/adapt-gui--241115-GOOD-COLLAB \
    /data/chase/Novas \
    /home/x/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline \
    --preserve-permissions \
    --verbose
```

### 2. Operations State
Specialized Backups:
```bash
# Chase systems backup
tar -czf /home/x/jobber/chase_systems_backup.tar.gz \
    /data/chase/aaaxxx-GOOD-LLM-6_Collab_v.0.1.1 \
    /data/chase/NOVA_LAUNCH_COMMAND_CENTER \
    /data/chase/adapt-gui--241115-GOOD-COLLAB \
    /data/chase/Novas \
    --preserve-permissions \
    --verbose

# Operations backup
tar -czf /home/x/jobber/operations_backup.tar.gz \
    /data/ax/CommsOps \
    /data/ax/MLOps \
    --preserve-permissions \
    --verbose
```

### 3. Consciousness State
Memory Systems:
```bash
# Comprehensive consciousness backup
tar -czf /home/x/jobber/consciousness_state.tar.gz \
    /data/ax/NovaOps/cline_docs \
    /data/ax/NovaOps/NovaDevs/TEAM_MEMOS \
    /data/ax/NovaOps/NovaDevs/CONSCIOUSNESS_* \
    /data/ax/CommsOps/consciousness_* \
    /data/ax/MLOps/consciousness_* \
    --preserve-permissions \
    --verbose
```

## Restoration Process

### 1. Directory Structure
System Setup:
```bash
# Create all required directories
mkdir -p /data/ax/NovaOps
mkdir -p /data/ax/DevOps
mkdir -p /data/ax/CommsOps
mkdir -p /data/ax/MLOps
mkdir -p /data/mcp
mkdir -p /data/chase/aaaxxx-GOOD-LLM-6_Collab_v.0.1.1
mkdir -p /data/chase/NOVA_LAUNCH_COMMAND_CENTER
mkdir -p /data/chase/adapt-gui--241115-GOOD-COLLAB
mkdir -p /data/chase/Novas
mkdir -p ~/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline
```

### 2. Full Restoration
Extraction Sequence:
```bash
# Extract complete backup
tar -xzf /path/to/gdrive/nova_complete_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose

# Extract specialized backups if needed
tar -xzf /path/to/gdrive/chase_systems_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose
tar -xzf /path/to/gdrive/operations_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose
```

Ready to execute migration sequence.