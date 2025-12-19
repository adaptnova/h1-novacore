#!/bin/bash

# GDRIVE BACKUP - Continuous Backup Service
# Version: 1.0.0

# Configuration
SOURCE_DIR="${SOURCE_DIR:-/data/ax}"
TARGET_PATH="${TARGET_PATH:-gdrive:/backups}"
TARGET_DIR="${TARGET_PATH}/ax"
LOG_FILE="/var/log/backup_service.log"
ERROR_LOG="/var/log/backup_service.error.log"

# Ensure log files exist
touch "$LOG_FILE" "$ERROR_LOG"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$ERROR_LOG"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
}

# Function to perform rclone backup
do_backup() {
    local changed_path="$1"
    log_message "Starting backup due to changes in: $changed_path"
    
    rclone sync "$SOURCE_DIR" "$TARGET_DIR" \
        --copy-links \
        --verbose \
        --log-file="$LOG_FILE" \
        --progress \
        --stats 30s \
        --stats-file-name-length 0 \
        --use-json-log \
        --fast-list \
        --transfers 16 \
        --checkers 32 \
        --buffer-size 32M \
        --drive-chunk-size 32M \
        --tpslimit 95 \
        --tpslimit-burst 100 \
        2>> "$ERROR_LOG"
    
    if [ $? -eq 0 ]; then
        log_message "Backup completed successfully"
    else
        log_error "Backup failed with exit code $?"
    fi
}

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    log_error "Source directory $SOURCE_DIR does not exist"
    exit 1
fi

# Log service start
log_message "Backup service started"
log_message "Monitoring directory: $SOURCE_DIR"
log_message "Backup destination: $TARGET_DIR"

# Perform initial backup
log_message "Performing initial backup..."
do_backup "$SOURCE_DIR"

# Monitor directory for changes
log_message "Starting continuous monitoring..."
inotifywait -m -r -e modify,create,delete,move "$SOURCE_DIR" | while read path action file; do
    log_message "Change detected: $action on ${path}${file}"
    do_backup "${path}${file}"
done

# Log service stop (should only reach here if inotifywait fails)
log_error "Monitoring stopped unexpectedly"
exit 1