#!/bin/bash

# AWS S3 Backup Script for Hourly Backups
# Created: 2025-01-24
# Version: 1.0.0

# Configuration
BUCKET_NAME="hourly-backup-593793064886"
SOURCE_DIR="/data"
BACKUP_PREFIX="hourly/$(date +%Y-%m-%d)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/logs/backup"
LOG_FILE="${LOG_DIR}/hourly_backup_${TIMESTAMP}.log"
ERROR_LOG="${LOG_DIR}/error_${TIMESTAMP}.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    local error_message="$1"
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $error_message" >> "$ERROR_LOG"
    log "Error occurred: $error_message"
    exit 1
}

# Validate AWS credentials
log "Validating AWS credentials..."
aws sts get-caller-identity > /dev/null 2>&1 || handle_error "AWS credentials validation failed"

# Create backup manifest
log "Creating backup manifest..."
find "$SOURCE_DIR" -type f -print0 | xargs -0 sha256sum > "/tmp/backup_manifest_${TIMESTAMP}.txt"

# Perform backup
log "Starting backup to S3..."
aws s3 sync "$SOURCE_DIR" "s3://${BUCKET_NAME}/${BACKUP_PREFIX}/${TIMESTAMP}" \
    --storage-class STANDARD_IA \
    --metadata "timestamp=${TIMESTAMP}" \
    --exclude "*.tmp" \
    --exclude "*.log" \
    || handle_error "Backup sync failed"

# Upload manifest
log "Uploading backup manifest..."
aws s3 cp "/tmp/backup_manifest_${TIMESTAMP}.txt" \
    "s3://${BUCKET_NAME}/${BACKUP_PREFIX}/${TIMESTAMP}/manifest.txt" \
    || handle_error "Manifest upload failed"

# Cleanup old manifests
rm -f "/tmp/backup_manifest_${TIMESTAMP}.txt"

# Verify backup
log "Verifying backup..."
aws s3 ls "s3://${BUCKET_NAME}/${BACKUP_PREFIX}/${TIMESTAMP}/" > /dev/null 2>&1 \
    || handle_error "Backup verification failed"

# Log success
log "Backup completed successfully"
log "Backup location: s3://${BUCKET_NAME}/${BACKUP_PREFIX}/${TIMESTAMP}/"

# Cleanup old backups (keep last 7 days)
log "Cleaning up old backups..."
aws s3 ls "s3://${BUCKET_NAME}/hourly/" | while read -r line; do
    backup_date=$(echo "$line" | awk '{print $2}' | cut -d'/' -f1)
    if [[ $(date -d "$backup_date" +%s) -lt $(date -d "7 days ago" +%s) ]]; then
        aws s3 rm "s3://${BUCKET_NAME}/hourly/$backup_date" --recursive
        log "Cleaned up backup from $backup_date"
    fi
done

log "Backup process completed"