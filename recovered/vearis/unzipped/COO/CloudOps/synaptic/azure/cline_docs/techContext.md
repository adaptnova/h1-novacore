# Azure Backup System - Technical Context

## Technologies Used

### Core Components
1. AzCopy
   - Version: Latest
   - Purpose: Efficient file transfer to Azure Blob Storage
   - Features: Resume support, parallel transfer

2. Systemd
   - Service: azure-backup.service
   - Timer: azure-backup.timer
   - Type: oneshot

3. Azure Blob Storage
   - Authentication: SAS Token
   - Container: databackup
   - Account: novadata1737534736

### Development Environment
1. Operating System
   - Linux 6.11
   - Bash shell

2. Directory Structure
   ```
   /data/ax/CloudOps/azure/
   ├── data_backup.sh
   ├── data-backup.service
   └── cline_docs/
   ```

3. Log Locations
   ```
   /logs/backup/
   ├── service-output.log
   ├── service-error.log
   └── backup_*.log
   ```

## Technical Constraints

### Security
1. Permissions
   - Directories: 750
   - Files: 640
   - Owner: x:x

2. Authentication
   - SAS token only
   - No stored credentials
   - Token expiry management

### Resource Limits
1. CPU
   - Policy: batch
   - Nice: 19

2. IO
   - Class: best-effort
   - Priority: 7

3. Network
   - Cap: 50 Mbps
   - Block size: 100MB

### Storage
1. Exclusions
   - Docker volumes and system files
   - Temporary and cache directories
   - Node modules and Python cache
   - /data/configs directory

2. Backup Location
   - Azure Blob Storage
   - Container: databackup
   - Hierarchical namespace: disabled

## Environment Variables
```bash
BACKUP_SOURCE_DIR=/data/
AZURE_STORAGE_ACCOUNT=novadata1737534736
AZURE_STORAGE_CONTAINER=databackup
AZURE_SAS_TOKEN=<token>
HOME=/logs/backup
BACKUP_LOG_DIR=/logs/backup
AZURE_CONFIG_DIR=/logs/backup/.azure
```

## Dependencies
1. System Requirements
   - Linux OS
   - systemd
   - azcopy
   - bash

2. Permissions Required
   - Read access to /data
   - Write access to /logs/backup
   - Execute permissions for scripts