#!/bin/bash

# Enhanced AWS S3 Parallel Backup Script with Error Tolerance
# Version: 2.1.0

# Load configuration
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_DIR}/config.sh"

# Timestamp for this backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_ID="${BACKUP_ID:-backup_${TIMESTAMP}}"
TEMP_DIR="${TEMP_BACKUP_DIR}/backup_${TIMESTAMP}"
FAILED_FILES_LOG="${TEMP_DIR}/failed_files.log"

# Setup logging
INFO_LOG="${DISK_BACKUP_LOGS}/info/${BACKUP_ID}.log"
ERROR_LOG="${DISK_BACKUP_LOGS}/error/${BACKUP_ID}.log"
DEBUG_LOG="${DISK_BACKUP_LOGS}/debug/${BACKUP_ID}.log"
AUDIT_LOG="${DISK_BACKUP_LOGS}/audit/${BACKUP_ID}.log"

# Ensure temp directory exists
mkdir -p "$TEMP_DIR"

# Cleanup function
cleanup() {
    if [ -f "$FAILED_FILES_LOG" ]; then
        cp "$FAILED_FILES_LOG" "${DISK_BACKUP_LOGS}/error/failed_files_${BACKUP_ID}.log"
    fi
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Enhanced logging functions
log_info() { echo -e "\033[0;32m[INFO]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$INFO_LOG"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$ERROR_LOG"; }
log_debug() { echo -e "\033[0;34m[DEBUG]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_LOG"; }
log_audit() { echo -e "\033[0;33m[AUDIT]\033[0m [$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$AUDIT_LOG"; }
log_failed() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$FAILED_FILES_LOG"; }

# Array of available NICs
NICS=(eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7)
declare -A NIC_STATUS

# Initialize NIC status
for nic in "${NICS[@]}"; do
    NIC_STATUS[$nic]="available"
done

# Function to get next available NIC
get_available_nic() {
    for nic in "${NICS[@]}"; do
        if [[ "${NIC_STATUS[$nic]}" == "available" ]]; then
            NIC_STATUS[$nic]="busy"
            echo "$nic"
            return 0
        fi
    done
    echo ""
    return 1
}

# Function to release NIC
release_nic() {
    local nic=$1
    NIC_STATUS[$nic]="available"
}

# Start backup process
echo -e "\n\033[1;36m=== Starting Enhanced Parallel AWS Backup Process ===\033[0m\n"
log_audit "Starting parallel backup process with ID: ${BACKUP_ID}"

# Validate AWS credentials for all NICs
working_nics=0
for nic in "${NICS[@]}"; do
    log_debug "Validating AWS credentials for $nic"
    if ! aws sts get-caller-identity --profile "${nic}_profile" > /dev/null 2>&1; then
        log_error "AWS credentials validation failed for $nic"
        NIC_STATUS[$nic]="failed"
    else
        log_info "✓ AWS credentials validated for $nic"
        ((working_nics++))
    fi
done

if [ $working_nics -eq 0 ]; then
    log_error "No working NICs available. Aborting backup."
    exit 1
fi

# Calculate total size and files
echo -e "\n\033[1;33mCalculating backup size...\033[0m"
total_size=$(du -sb "$SOURCE_DIR" 2>/dev/null | cut -f1)
total_files=$(find "$SOURCE_DIR" -type f 2>/dev/null | wc -l)
human_size=$(numfmt --to=iec-i --suffix=B "${total_size:-0}")

# Stage files with parallel rsync
echo -e "\n\033[1;34mStaging files for backup...\033[0m"
mkdir -p "${TEMP_DIR}/data"

RSYNC_OPTS="-ah --info=progress2 --no-i-r --ignore-errors"
EXCLUDE_OPTS=$(printf -- '--exclude=%s ' "${EXCLUDE_PATTERNS[@]}")

# Split source directory for parallel processing
find "${SOURCE_DIR}" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | while read -r dir; do
    {
        dir_name=$(basename "$dir")
        mkdir -p "${TEMP_DIR}/data/${dir_name}"
        if ! rsync $RSYNC_OPTS $EXCLUDE_OPTS "${SOURCE_DIR}/${dir_name}/" "${TEMP_DIR}/data/${dir_name}/" 2>/dev/null; then
            log_failed "Failed to sync directory: ${dir_name}"
        fi
    } &

    # Limit parallel rsync processes
    while [ $(jobs -p | wc -l) -ge $(nproc) ]; do
        sleep 1
    done
done

wait

# Create manifest of successfully copied files
echo -e "\n\033[1;34mGenerating manifest of successful files...\033[0m"
{
    echo "Backup ID: ${BACKUP_ID}"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Source Directory: ${SOURCE_DIR}"
    echo "Total Files Attempted: ${total_files}"
    echo "Total Size Attempted: ${total_size}"
    
    echo -e "\nSuccessfully Copied Files:"
    cd "${TEMP_DIR}/data" && find . -type f -exec sha256sum {} \; 2>/dev/null
} > "${TEMP_DIR}/manifest.txt"

# Create archive chunks
echo -e "\n\033[1;34mCreating backup chunks...\033[0m"
cd "${TEMP_DIR}/data"

# Use tar with parallel compression and split into smaller chunks
tar -c . 2>/dev/null | pigz -p $(nproc) | pv -s "$total_size" | split -b 1G - "${TEMP_DIR}/backup.tar.gz.part-"

# Upload chunks using all available NICs
echo -e "\n\033[1;34mUploading backup chunks using multiple NICs...\033[0m"
upload_chunk() {
    local part=$1
    local part_name=$(basename "$part")
    local nic=$(get_available_nic)
    local retries=3
    
    if [ -z "$nic" ]; then
        log_error "No NICs available for upload of $part_name"
        return 1
    }
    
    while [ $retries -gt 0 ]; do
        log_info "Uploading $part_name using $nic (attempts remaining: $retries)"
        if aws s3 cp "$part" \
            "s3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/parts/${part_name}" \
            --storage-class "$STORAGE_CLASS" \
            --metadata "backup_id=${BACKUP_ID}" \
            --profile "${nic}_profile" 2>/dev/null; then
            log_info "Successfully uploaded $part_name using $nic"
            release_nic "$nic"
            return 0
        fi
        ((retries--))
        sleep 5
    done
    
    log_error "Failed to upload $part_name after all retries"
    log_failed "Failed to upload chunk: $part_name"
    release_nic "$nic"
    return 1
}

# Upload all chunks in parallel
failed_chunks=()
for part in "${TEMP_DIR}"/backup.tar.gz.part-*; do
    {
        if ! upload_chunk "$part"; then
            failed_chunks+=("$part")
        fi
    } &

    # Limit parallel uploads to number of working NICs
    while [ $(jobs -p | wc -l) -ge $working_nics ]; do
        sleep 1
    done
done

wait

# Upload manifest using any available NIC
nic=$(get_available_nic)
aws s3 cp "${TEMP_DIR}/manifest.txt" \
    "s3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/manifest.txt" \
    --storage-class "$STORAGE_CLASS" \
    --metadata "backup_id=${BACKUP_ID}" \
    --profile "${nic}_profile"
release_nic "$nic"

# Copy failed files log to S3 if it exists
if [ -f "$FAILED_FILES_LOG" ]; then
    nic=$(get_available_nic)
    aws s3 cp "$FAILED_FILES_LOG" \
        "s3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/failed_files.log" \
        --storage-class "$STORAGE_CLASS" \
        --profile "${nic}_profile"
    release_nic "$nic"
fi

# Log completion
echo -e "\n\033[1;32m=== Backup Summary ===\033[0m"
echo -e "Backup ID: \033[1;33m${BACKUP_ID}\033[0m"
echo -e "Total Files Attempted: \033[1;33m${total_files}\033[0m"
echo -e "Total Size Attempted: \033[1;33m${human_size}\033[0m"
echo -e "Location: \033[1;33ms3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/\033[0m"

if [ -f "$FAILED_FILES_LOG" ]; then
    echo -e "\n\033[1;31mSome files failed to backup. Check failed_files.log for details.\033[0m"
    echo -e "Failed files log: s3://${BUCKET_NAME}/${S3_PREFIX}/${BACKUP_ID}/failed_files.log\n"
fi

log_info "Backup completed with some files skipped"
log_audit "Backup completed - ID: ${BACKUP_ID}"

# Return 1 if there were any failures, 0 if completely successful
[ -f "$FAILED_FILES_LOG" ] && exit 1 || exit 0