# Azure Backup System Templates

## Overview
These templates provide a foundation for setting up automated Azure Blob Storage backups using systemd and azcopy.

## Components

### 1. Systemd Service (`azure-backup.service.template`)
- Defines the backup service configuration
- Handles security and resource management
- Configures logging and error reporting

### 2. Systemd Timer (`azure-backup.timer.template`)
- Schedules backup execution every 15 minutes
- Includes randomized delay to prevent resource contention
- Ensures missed backups are executed

### 3. Backup Script (`backup_script.sh.template`)
- Handles the actual backup process
- Includes comprehensive error handling
- Manages logging and cleanup

## Setup Instructions

1. Prerequisites
```bash
# Install required tools
sudo apt-get update
sudo apt-get install -y azure-cli
curl -sL https://aka.ms/downloadazcopy-v10-linux | tar -xz
sudo mv ./azcopy_linux_amd64_*/azcopy /usr/local/bin/
```

2. Configure Azure Authentication
```bash
# Login to Azure
az login
azcopy login
```

3. Prepare Directory Structure
```bash
# Create necessary directories
sudo mkdir -p /logs/backup
sudo chown -R service_user:service_group /logs/backup
```

4. Configure Templates
```bash
# Copy and rename templates
cp azure-backup.service.template /etc/systemd/system/azure-backup.service
cp azure-backup.timer.template /etc/systemd/system/azure-backup.timer
cp backup_script.sh.template /path/to/backup_script.sh

# Make script executable
chmod +x /path/to/backup_script.sh
```

5. Customize Configuration
- Update paths in service file
- Configure backup source and destination in script
- Adjust timer settings if needed
- Set appropriate permissions

6. Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable azure-backup.timer
sudo systemctl start azure-backup.timer
```

## Customization Guide

### Service Configuration
- `User/Group`: Set appropriate service user
- `WorkingDirectory`: Update to script location
- `StandardOutput/StandardError`: Configure log paths

### Timer Configuration
- `OnCalendar`: Adjust schedule (default: every 15 minutes)
- `RandomizedDelaySec`: Modify delay window
- `AccuracySec`: Adjust timing precision

### Backup Script
- `SOURCE_DIR`: Set backup source path
- `BACKUP_CONTAINER`: Set Azure container name
- `STORAGE_ACCOUNT`: Set Azure storage account
- `LOG_DIR`: Configure log directory
- Customize exclude patterns
- Adjust retention policy

## Monitoring

### Check Status
```bash
# Check timer status
systemctl status azure-backup.timer

# Check service status
systemctl status azure-backup.service

# View logs
journalctl -u azure-backup.service
```

### Log Files
- Service output: /logs/backup/service-output.log
- Service errors: /logs/backup/service-error.log
- Backup logs: /logs/backup/backup_*.log

## Security Considerations

1. File Permissions
- Script: 750 (rwxr-x---)
- Log directory: 750 (rwxr-x---)
- Service files: 644 (rw-r--r--)

2. Azure Authentication
- Use managed identities when possible
- Regularly rotate credentials
- Use minimum required permissions

3. Data Protection
- Encrypt sensitive data
- Use secure paths
- Implement proper error handling

## Troubleshooting

1. Common Issues
- Permission denied: Check file/directory permissions
- Authentication failed: Verify Azure credentials
- Timer not triggering: Check systemd timer status

2. Debug Commands
```bash
# Check timer next run
systemctl list-timers azure-backup.timer

# Test backup script
/path/to/backup_script.sh

# View detailed logs
journalctl -u azure-backup.service -f
```

## Maintenance

1. Regular Tasks
- Monitor log files
- Check backup completion status
- Verify data integrity
- Update Azure credentials

2. Cleanup
- Old logs are automatically cleaned after 7 days
- Monitor disk usage
- Review backup retention policy

## Support
For issues or improvements:
- Check systemd logs
- Review Azure portal
- Monitor azcopy logs
- Check script exit codes