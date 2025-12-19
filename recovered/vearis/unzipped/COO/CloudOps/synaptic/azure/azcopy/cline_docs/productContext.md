# AzCopy Backup System Product Context

## Purpose
Automated backup system for /data directory to Azure Blob Storage using AzCopy sync functionality.

## Key Components
- Source: /data directory
- Destination: Azure Blob Storage (novadata1737534736/databackup)
- Authentication: SAS token-based
- Scheduling: systemd timer (15-minute intervals)

## Business Requirements
1. Regular automated backups
2. Efficient handling of large data sets
3. Minimal system resource usage
4. Reliable data synchronization
5. Clear progress tracking

## Technical Goals
1. Implement true incremental backups
2. Optimize transfer performance
3. Maintain data integrity
4. Provide clear progress visibility
5. Efficient resource utilization