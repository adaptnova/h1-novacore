#!/bin/bash

# AWS S3 Backup Script for Hourly Backups
# Created: 2025-01-24
# Version: 1.0.0

# Load configuration
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_DIR}/config.sh"

# Timestamp for this backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_ID="backup_${TIMESTAMP}"
TEMP_DIR="${TEMP_BACKUP_DIR}/backup_${TIMESTAMP}"

# Setup logging for this backup
INFO_LOG="${DISK_BACKUP_LOGS}/info/${BACKUP_ID}.log"
ERROR_LOG="${DISK_BACKUP_LOGS}/error/${BACKUP_ID}.log"
DEBUG_LOG="${DISK_BACKUP_LOGS}/debug/${BACKUP_ID}.log"
AUDIT_LOG="${DISK_BACKUP_LOGS}/audit/${BACKUP_ID}.log"

# Ensure temp directory exists
mkdir -p "$TEMP_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Logging functions with colors
log_info() { echo -e "\033[0;32m[INFO]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$INFO_LOG"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$ERROR_LOG"; }
log_debug() { echo -e "\033[0;34m[DEBUG]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_LOG"; }
log_audit() { echo -e "\033[0;33m[AUDIT]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$AUDIT_LOG"; }

# Error handling
handle_error() {
    local error_message="$1"
    local fatal="${2:-true}"
    log_error "$error_message"
    log_audit "Backup failed: $error_message"
    [ "$fatal" = "true" ] && cleanup
    [ "$fatal" = "true" ] && exit 1
}

# Start backup process
echo -e "\n\033[1;36m=== Starting AWS Backup Process ===\033[0m\n"
log_audit "Starting backup process with ID: ${BACKUP_ID}"
log_info "Initializing backup process"

# Validate AWS credentials
log_debug "Validating AWS credentials"
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    handle_error "AWS credentials validation failed"
fi
echo -e "\033[0;32m✓\033[0m AWS credentials validated"

# Calculate total size and files
echo -e "\n\033[1;33mCalculating backup size...\033[0m"
total_size=$(du -sb "$SOURCE_DIR" | cut -f1)
total_files=$(find "$SOURCE_DIR" -type f 2>/dev/null | wc -l)
human_size=$(numfmt --to=iec-i --suffix=B "${total_size:-0}")

echo -e "\n\033[1;33mBackup Statistics:\033[0m"
echo -e "Files to backup: \033[1;32m$total_files\033[0m"
echo -e "Total size: \033[1;32m$human_size\033[0m\n"

# Create backup metadata
METADATA_FILE="${DISK_BACKUP_DIR}/metadata/${BACKUP_ID}.json"
cat > "$METADATA_FILE" << EOF
{
    "backup_id": "${BACKUP_ID}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "source_dir": "${SOURCE_DIR}",
    "s3_bucket": "${BUCKET_NAME}",
    "s3_prefix": "${S3_PREFIX}/${BACKUP_ID}",
    "total_files": ${total_files},
    "total_size": ${total_size}
}
EOF

# Stage files with rsync and show progress
echo -e "\n\033[1;34mStaging files for backup...\033[0m"
mkdir -p "${TEMP_DIR}/data"

# Use parallel rsync processes for faster transfer
RSYNC_OPTS="-ah --info=progress2 --no-i-r"
EXCLUDE_OPTS=$(printf -- '--exclude=%s ' "${EXCLUDE_PATTERNS[@]}")

# Split source directory into multiple parts for parallel processing
find "${SOURCE_DIR}" -maxdepth 1 -mindepth 1 -type d | while read -r dir; do
    {
        dir_name=$(basename "$dir")
        mkdir -p "${TEMP_DIR}/data/${dir_name}"
        rsync $RSYNC_OPTS $EXCLUDE_OPTS "${SOURCE_DIR}/${dir_name}/" "${TEMP_DIR}/data/${dir_name}/" || true
    } &

    # Limit parallel rsync processes
    while [ $(jobs -p | wc -l) -ge 4 ]; do
        sleep 1
    done
done

# Wait for all rsync processes to complete
wait

# Create manifest
echo -e "\n\033[1;34mGenerating manifest...\033[0m"
{
    echo "Backup ID: ${BACKUP_ID}"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Source Directory: ${SOURCE_DIR}"
    echo "Total Files: ${total_files}"
    echo "Total Size: ${total_size}"
    
    echo -e "\nFile List:"
    cd "${TEMP_DIR}/data" && find . -type f -exec sha256sum {} \;
} > "${TEMP_DIR}/manifest.txt"

# Configure AWS CLI for optimal multipart upload
export AWS_MAX_CONCURRENT_REQUESTS=20
export AWS_MULTIPART_THRESHOLD=100MB
export AWS_MULTIPART_CHUNKSIZE=500MB

# Create and upload archive in parallel chunks
echo -e "\n\033[1;34mCreating and uploading backup...\033[0m"
cd "${TEMP_DIR}/data"

# Use tar with parallel compression
tar -c . | pigz -p 4 | pv -s "$total_size" | split -b 50G - "${TEMP_DIR}/backup.tar.gz.part-"

# Upload parts in parallel
for part in "${TEMP_DIR}"/backup.tar.gz.part-*; do
    {
        part_name=$(basename "$part")
        aws s3 cp "$part" \
            "s3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/parts/${part_name}" \
            --storage-class "$STORAGE_CLASS" \
            --metadata "backup_id=${BACKUP_ID}" &

        # Limit parallel uploads
        while [ $(jobs -p | wc -l) -ge 4 ]; do
            sleep 1
        done
    }
done

wait

# Upload manifest
aws s3 cp "${TEMP_DIR}/manifest.txt" \
    "s3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/manifest.txt" \
    --storage-class "$STORAGE_CLASS" \
    --metadata "backup_id=${BACKUP_ID}"

# Log completion
echo -e "\n\033[1;32m=== Backup Summary ===\033[0m"
echo -e "Backup ID: \033[1;33m${BACKUP_ID}\033[0m"
echo -e "Total Files Processed: \033[1;33m${total_files}\033[0m"
echo -e "Total Size: \033[1;33m${human_size}\033[0m"
echo -e "Location: \033[1;33ms3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/\033[0m\n"

log_info "Backup completed successfully"
log_audit "Backup completed - ID: ${BACKUP_ID}"