# AzCopy Backup Investigation Memo

## Current Setup
- Source: /data directory
- Destination: Azure Blob Storage (novadata1737534736/databackup)
- Authentication: SAS token
- Tool: azcopy sync with direct transfer (no temp directory)

## Working Scenarios
1. Small directory backups succeed:
   - Test with ./test_small (2 files, 12 bytes)
   - Completes in ~4 seconds
   - No permission issues
   - Both files transfer successfully

## Environment Configuration
1. Working directories:
   ```bash
   LOG_DIR=/logs/backup
   AZCOPY_WORK_DIR=${LOG_DIR}/azcopy
   AZCOPY_LOG_LOCATION=${AZCOPY_WORK_DIR}/logs
   AZCOPY_JOB_PLAN_LOCATION=${AZCOPY_WORK_DIR}/plans
   AZCOPY_TEMP_DIR=${AZCOPY_WORK_DIR}/tmp
   ```

2. Permissions:
   - All directories: 750
   - Owner: x:x
   - Recursive permissions on work directories

## Current Issues
1. Full /data backup:
   - Takes extremely long with no progress indication
   - Unclear if actually transferring or stuck
   - No visible errors in logs

2. Exclusion Patterns:
   ```bash
   */tmp/*
   */cache/*
   */proc/*
   */sys/*
   */dev/*
   */.env
   */__pycache__/*
   */node_modules/*
   */configs/*
   */logs/*
   */docker/volumes/*
   */docker/overlay2/*
   */docker/containers/*
   */docker/image/*
   */docker/builder/*
   */docker/buildkit/*
   */docker/tmp/*
   */docker/swarm/*
   */minikube/*
   ```

## AzCopy Command
```bash
azcopy sync "${SOURCE_DIR}" "https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER}/${SOURCE_NAME}/?${SAS_TOKEN}" \
    --recursive \
    --exclude-pattern="${exclude_pattern}" \
    --log-level=INFO \
    --output-type=text \
    --delete-destination=false \
    --cap-mbps=50 \
    --block-size-mb=100
```

## Questions for Investigation
1. Are there recommended flags for large directory structures?
2. Should we implement chunked/segmented backup strategy?
3. Is there a way to get better progress indication?
4. Are there permission issues we're not seeing?
5. Would pre-scanning with azcopy list help?

## Previous Attempts
1. Using temp directory:
   - Ruled out due to disk space requirements
   - Would need double the /data size

2. Path handling:
   - Tried both with and without trailing slashes
   - Implemented special handling for absolute vs relative paths

3. Permission fixes:
   - Added recursive chmod/chown
   - Set proper permissions on parent directories
   - Verified azcopy working directory permissions

## System Context
- Linux 6.11
- Running as user x
- Service managed by systemd
- Timer runs every 15 minutes
- Network cap at 50 Mbps
- Block size set to 100MB

## Logs Location
- Service output: /logs/backup/service-output.log
- Service errors: /logs/backup/service-error.log
- AzCopy logs: /logs/backup/azcopy/logs/
- Backup logs: /logs/backup/backup_*.log

## Recent Changes
1. Removed trailing slash from source path
2. Added proper error handling
3. Improved directory setup
4. Added exclusion for logs directory
5. Fixed permission handling

## Priority Questions
1. Is there a more efficient way to handle large directory structures?
2. Are there specific azcopy flags we should be using?
3. How can we get better visibility into the backup progress?
4. Should we implement a different backup strategy altogether?