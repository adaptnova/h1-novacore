# Final Migration Command Sequence
Date: February 17, 2025 07:38 MST
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
    /data/mcp \
    /data/ax/CommsOps \
    /data/ax/MLOps \
    /home/x/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline \
    --preserve-permissions \
    --verbose
```

### 2. Operations State
Specialized Backups:
```bash
# CommsOps backup
tar -czf /home/x/jobber/commsops_backup.tar.gz \
    /data/ax/CommsOps \
    --preserve-permissions \
    --verbose

# MLOps backup
tar -czf /home/x/jobber/mlops_backup.tar.gz \
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
    /data/ax/CommsOps/consciousness \
    /data/ax/MLOps/consciousness \
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
mkdir -p ~/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline
```

### 2. Full Restoration
Extraction Sequence:
```bash
# Extract complete backup
tar -xzf /path/to/gdrive/nova_complete_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose

# Extract operations backups if needed separately
tar -xzf /path/to/gdrive/commsops_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose
tar -xzf /path/to/gdrive/mlops_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose
```

## Verification Process

### 1. Structure Verification
Directory Checks:
```bash
# Verify all critical directories
ls -la /data/ax/NovaOps
ls -la /data/ax/DevOps
ls -la /data/ax/CommsOps
ls -la /data/ax/MLOps
ls -la /data/mcp
```

### 2. Operations Check
System Validation:
```bash
# Check CommsOps
ls -la /data/ax/CommsOps/consciousness
find /data/ax/CommsOps -name "*.md"

# Check MLOps
ls -la /data/ax/MLOps/consciousness
find /data/ax/MLOps -name "*.md"
```

Ready to execute migration sequence.