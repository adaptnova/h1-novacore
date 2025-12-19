# AzCopy Backup System Technical Context

## Current System Configuration
1. Environment
   - OS: Linux 6.11
   - User: x
   - Service Management: systemd
   - Network Cap: 50 Mbps
   - Block Size: 100MB

2. Directory Structure
   ```bash
   LOG_DIR=/logs/backup
   AZCOPY_WORK_DIR=${LOG_DIR}/azcopy
   AZCOPY_LOG_LOCATION=${AZCOPY_WORK_DIR}/logs
   AZCOPY_JOB_PLAN_LOCATION=${AZCOPY_WORK_DIR}/plans
   ```

3. Permissions
   - Directory permissions: 750
   - Owner: x:x
   - Recursive permissions on work directories

## Current Implementation
1. Backup Script (backup_data.sh)
   - Uses azcopy sync command
   - Direct transfer (no temp directory)
   - Exclusion patterns for system directories
   - Network bandwidth cap at 50 Mbps

2. Authentication
   - SAS token-based access
   - Token generation via generate_sas.sh

3. Scheduling
   - systemd timer
   - 15-minute intervals

## Technical Issues
1. Performance
   - Full directory scanning on each run
   - No efficient incremental sync
   - Long execution times for large directories
   - Limited progress visibility

2. Resource Usage
   - High I/O during full scans
   - Network bandwidth capped
   - No temp directory usage (space consideration)

## Required Improvements
1. Implement MD5/CRC64 comparison for true incremental sync
2. Add --compare-hash flag for efficient change detection
3. Implement better progress monitoring
4. Optimize scanning of large directory structures
5. Add proper logging of changed files

## Log Locations
- Service output: /logs/backup/service-output.log
- Service errors: /logs/backup/service-error.log
- AzCopy logs: /logs/backup/azcopy/logs/
- Backup logs: /logs/backup/backup_*.log