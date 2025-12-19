# Master Project Documentation

## Azure Backup System

### Project Overview
- **Purpose**: Automated backup of /data directory to Azure Blob Storage
- **Created**: 2025-01-22
- **Status**: Active
- **Storage Freed**: ~686G (by removing /data/configs)

### Azure Configuration
- **Storage Account**: novadata1737534736
- **Container**: databackup
- **Location**: centralus
- **SKU**: Standard_LRS
- **Kind**: StorageV2

### SAS Token Management
#### Current Token
- **Generated**: 2025-01-22 22:59 MST
- **Expiry**: 2025-01-30 06:00 UTC
- **Permissions**: Read, Add, Create, Write, Delete, List (racwdl)
- **Token Details**:
  * Service Version (sv): 2022-11-02
  * Start Time (skt): 2025-01-23T06:00:38Z
  * End Time (ske): 2025-01-30T06:00:00Z
  * Permissions (sp): racwdl
  * Resource (sr): c (container)
  * Service Key Object ID (skoid): d4026ca4-a97d-4856-b4ad-6a64a5dafe78
  * Service Key Tenant ID (sktid): d568f95a-a48a-4e42-8acf-0ba8c93c300f
  * Service Key Version (skv): 2022-11-02
  * Service Key Type (sks): b
  * Generated: 2025-01-22 23:00 MST

### System Components
1. **Backup Script**
   - Location: /data/ax/CloudOps/azure/data_backup.sh
   - Permissions: 750 (rwxr-x---)
   - Owner: x:x
   - Features:
     * Error handling
     * Logging
     * Cleanup
     * Progress monitoring

2. **Systemd Service**
   - Service: /etc/systemd/system/azure-backup.service
   - Timer: /etc/systemd/system/azure-backup.timer
   - Schedule: Every 15 minutes
   - Type: oneshot

3. **Logging System**
   - Base Path: /logs/backup
   - Components:
     * service-output.log
     * service-error.log
     * backup_*.log
     * azcopy/
   - Retention: 7 days (logs), 1 day (plan files)

### Performance Settings
- Block Size: 100MB
- Bandwidth Cap: 50 Mbps
- MD5 Verification: Enabled
- Exclusion Patterns:
  * System: tmp, cache, proc, sys, dev
  * Development: .env, __pycache__, node_modules
  * Docker: volumes, overlay2, containers, image, builder, buildkit, tmp, swarm
  * Custom: configs

### Security Configuration
- Service User: x
- Service Group: x
- File Permissions:
  * Scripts: 750
  * Logs: 640
  * Directories: 750
- Systemd Security:
  * ProtectSystem=full
  * PrivateTmp=true
  * NoNewPrivileges=true
  * ProtectHome=true
  * RestrictRealtime=true
  * MemoryDenyWriteExecute=true

### Resource Management
- IOSchedulingClass: best-effort
- IOSchedulingPriority: 7
- CPUSchedulingPolicy: batch
- Nice: 19
- UMask: 0027
- LimitNOFILE: 65535

### Maintenance Schedule
1. **Daily Tasks**
   - Check backup logs
   - Monitor disk usage
   - Verify successful transfers
   - Check AzCopy directory permissions

2. **Weekly Tasks**
   - Review log rotation
   - Check system performance
   - Verify symlink integrity
   - Review Docker exclusions effectiveness

3. **Monthly Tasks**
   - Review SAS token expiration
   - Assess backup performance
   - Update documentation
   - Review environment variables

### Critical Dates
- SAS Token Renewal: Before 2025-01-30
- Next Performance Review: 2025-02-22
- Documentation Review: 2025-02-22

### Change History
1. 2025-01-22
   - Initial system implementation
   - Set up automated backups
   - Configured logging and monitoring
   - Removed /data/configs (~686G freed)
   - Enhanced AzCopy permissions
   - Improved Docker exclusions
   - Implemented environment variables

### Troubleshooting Guide
1. **Permission Issues**
   ```bash
   # Check AzCopy directories
   ls -la /logs/backup/azcopy
   # Fix permissions if needed
   sudo chown -R x:x /logs/backup/azcopy
   sudo chmod -R 750 /logs/backup/azcopy
   ```

2. **Service Issues**
   ```bash
   # Check service status
   systemctl status azure-backup.service
   # View logs
   journalctl -u azure-backup.service -n 50
   ```

3. **Backup Issues**
   ```bash
   # Check latest backup log
   tail -f /logs/backup/backup_*.log
   # Test backup manually
   sudo -u x /data/ax/CloudOps/azure/data_backup.sh
   ```

### Contact Information
- System Owner: Cloud Operations Team
- Infrastructure Management: System Administrators
- Documentation: Cloud Operations Team

### Related Documentation
- [Product Context](productContext.md)
- [System Patterns](systemPatterns.md)
- [Technical Context](techContext.md)
- [Active Context](activeContext.md)
- [Progress Tracking](progress.md)
- [Symlink Master](symlink_master.md)