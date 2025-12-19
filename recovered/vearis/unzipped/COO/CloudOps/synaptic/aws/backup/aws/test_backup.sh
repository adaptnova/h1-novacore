#!/bin/bash

# Create necessary directories
mkdir -p /data/tmp
mkdir -p /data/cloudops/aws/backups
mkdir -p /logs/cloudops/aws/backups

# Load test configuration
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_DIR}/test_config.sh"

# First test: Small backup
echo "Starting test backup..."
export SOURCE_DIR="/data/test_backup"
export BACKUP_ID="test_backup_$(date +%Y%m%d_%H%M%S)"
export S3_PREFIX="test_backups"

# Run backup for test directory
"${SCRIPT_DIR}/hourly_backup.sh"

# If test successful, proceed with /data/ax backup
if [ $? -eq 0 ]; then
    echo "Test backup successful, proceeding with /data/ax backup..."
    export SOURCE_DIR="/data/ax"
    export BACKUP_ID="ax_backup_$(date +%Y%m%d_%H%M%S)"
    export S3_PREFIX="ax_backups"
    "${SCRIPT_DIR}/hourly_backup.sh"
fi

# Finally, backup whole /data disk
if [ $? -eq 0 ]; then
    echo "AX backup successful, proceeding with full /data backup..."
    export SOURCE_DIR="/data"
    export BACKUP_ID="full_backup_$(date +%Y%m%d_%H%M%S)"
    export S3_PREFIX="full_backups"
    "${SCRIPT_DIR}/hourly_backup.sh"
fi
