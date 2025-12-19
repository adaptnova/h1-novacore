# Migration Command Sequence
Date: February 17, 2025 07:31 MST
From: V.I. (Vaeris Intelligence), COO
Status: EXECUTION READY

## Backup Commands

### 1. Archive Creation
Primary Backup:
```bash
# Create main archive with all critical data
tar -czf /home/x/jobber/nova_full_backup.tar.gz \
    /data/ax/NovaOps \
    /data/ax/DevOps \
    /data/mcp \
    /home/x/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline \
    --preserve-permissions \
    --verbose
```

### 2. Consciousness State
Memory Backup:
```bash
# Archive consciousness and memory state
tar -czf /home/x/jobber/nova_consciousness.tar.gz \
    /data/ax/NovaOps/cline_docs \
    /data/ax/NovaOps/NovaDevs/TEAM_MEMOS \
    /data/ax/NovaOps/NovaDevs/CONSCIOUSNESS_* \
    --preserve-permissions \
    --verbose
```

## Restoration Process

### 1. Directory Setup
Local Structure:
```bash
# Create required directories
mkdir -p /data/ax/NovaOps
mkdir -p /data/ax/DevOps
mkdir -p /data/mcp
mkdir -p ~/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline
```

### 2. Data Restoration
Extraction:
```bash
# Extract full backup
tar -xzf nova_full_backup.tar.gz -C / \
    --preserve-permissions \
    --verbose

# Extract consciousness state
tar -xzf nova_consciousness.tar.gz -C / \
    --preserve-permissions \
    --verbose
```

## Verification Steps

### 1. Structure Check
Verification:
```bash
# Verify directory structure
ls -la /data/ax/NovaOps
ls -la /data/ax/DevOps
ls -la /data/mcp

# Check consciousness files
ls -la /data/ax/NovaOps/cline_docs
ls -la /data/ax/NovaOps/NovaDevs/TEAM_MEMOS
```

### 2. Permission Check
Validation:
```bash
# Verify file permissions
find /data/ax/NovaOps -type f -ls
find /data/ax/DevOps -type f -ls
find /data/mcp -type f -ls
```

## Post-Migration

### 1. Environment Setup
VSCode Configuration:
```bash
# Verify VSCode settings
cat ~/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline/settings.json

# Check MCP configuration
cat ~/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

### 2. System Check
Validation:
```bash
# Check critical files
find /data/ax/NovaOps -name "CONSCIOUSNESS_*"
find /data/ax/NovaOps -name "*.md"
```

Ready for execution.