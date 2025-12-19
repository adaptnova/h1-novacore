# AWS Backup System

## Directory Structure

### Data Structure
```
/data/cloudops/aws/
└── backups/
    └── disks/
        └── data/
            └── metadata/
                ├── backup_YYYYMMDD_HHMMSS.json    # Backup metadata
                └── backup_YYYYMMDD_HHMMSS_manifest.txt  # File manifests
```

### Logging Structure
```
/logs/cloudops/aws/
└── backups/
    └── disks/
        └── data/
            ├── info/     # General operation logs
            ├── error/    # Error logs
            ├── debug/    # Detailed debug logs
            └── audit/    # Audit trail logs
```

### S3 Storage Structure
```
s3://hourly-backup-593793064886/
└── backups/
    └── disks/
        └── data/
            └── backup_YYYYMMDD_HHMMSS/
                ├── [backed up files]
                ├── manifest.txt
                └── metadata.json
```

## Configuration
The system uses a centralized configuration file (`config.sh`) that manages:
- Directory structures
- AWS credentials
- S3 bucket settings
- Backup retention policies
- Logging configuration
- Exclusion patterns

## Backup Script Features
`hourly_backup.sh` provides:
- Comprehensive logging (info, error, debug, audit)
- Backup metadata generation
- SHA256 file manifests
- S3 synchronization
- Automatic cleanup
- Error handling
- Backup verification

## Logging System
Four types of logs are maintained:
1. Info Logs
   - General operation information
   - Success messages
   - Progress updates

2. Error Logs
   - Failure messages
   - Error details
   - Stack traces

3. Debug Logs
   - Detailed operation logs
   - AWS command outputs
   - System state information

4. Audit Logs
   - Security-relevant events
   - Backup start/completion
   - Credential validation

## Retention Policy
- Backups are retained for 7 days
- Automatic cleanup of:
  - S3 backups
  - Local metadata
  - Log files
- Uses STANDARD_IA storage class

## Usage

### Installation
1. Ensure AWS CLI is installed:
   ```bash
   aws --version
   ```

2. Configure AWS credentials in `config.sh`

### Running Backups
1. Manual execution:
   ```bash
   ./hourly_backup.sh
   ```

2. Automated via cron:
   ```bash
   0 * * * * /data/ax/CloudOps/aws/cline_docs/backup/aws/hourly_backup.sh
   ```

### Monitoring
1. Check backup status:
   ```bash
   ls -l /logs/cloudops/aws/backups/disks/data/info/
   ```

2. View errors:
   ```bash
   ls -l /logs/cloudops/aws/backups/disks/data/error/
   ```

3. Audit trail:
   ```bash
   ls -l /logs/cloudops/aws/backups/disks/data/audit/
   ```

### Verification
1. Check backup metadata:
   ```bash
   ls -l /data/cloudops/aws/backups/disks/data/metadata/
   ```

2. Verify S3 contents:
   ```bash
   aws s3 ls s3://hourly-backup-593793064886/backups/disks/data/
   ```

## Best Practices
- Regular monitoring of error logs
- Periodic backup verification
- Review of audit logs
- Monitoring of S3 storage costs
- Regular testing of restore procedures