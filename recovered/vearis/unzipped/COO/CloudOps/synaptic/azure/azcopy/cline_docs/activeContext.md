# AzCopy Backup System Active Context

## Current Task
Verify and optimize AzCopy backup implementation for efficient incremental backups.

## Status Assessment
1. Current Implementation Issues
   - Full directory scanning on each run
   - Missing hash-based comparison
   - Inefficient resource usage
   - Limited progress visibility

2. Verification Results
   - Backups are scheduled (15-minute intervals)
   - Not using efficient incremental sync
   - Need optimization for large directories

## Required Changes
1. Update backup_data.sh script to:
   - Add --compare-hash=MD5 flag
   - Implement JSON output for progress
   - Add retry logic
   - Improve logging

2. Modify systemd service for:
   - Better error handling
   - Progress monitoring
   - Alert generation

## Action Items
1. Immediate
   - Implement hash-based comparison
   - Add progress monitoring
   - Update logging format

2. Short-term
   - Test with large directories
   - Verify resource usage
   - Document performance metrics

3. Long-term
   - Implement alerting system
   - Add performance monitoring
   - Create dashboard for backup status

## Dependencies
1. System Requirements
   - AzCopy latest version
   - Sufficient disk I/O
   - Network bandwidth
   - Storage account access

2. Access Requirements
   - SAS token permissions
   - Directory permissions
   - Log directory access