#!/bin/bash

# Backup script for /data directory using AzCopy
# Author: Nova
# Last modified: 2025-01-24
# Description: Efficient incremental backup using MD5 hash comparison and progress monitoring

# Exit on error, but allow error handling
set -e
trap 'handle_error $? $LINENO' ERR

handle_error() {
    local exit_code=$1
    local line_no=$2
    echo "[$(date)] Error occurred in script at line: $line_no with exit code: $exit_code"
}

# Environment setup
LOG_DIR="./logs"  # Use local logs directory by default
AZCOPY_WORK_DIR=${LOG_DIR}/azcopy
AZCOPY_LOG_LOCATION=${AZCOPY_WORK_DIR}/logs
AZCOPY_JOB_PLAN_LOCATION=${AZCOPY_WORK_DIR}/plans

# Export for azcopy to use
export AZCOPY_LOG_LOCATION
export AZCOPY_JOB_PLAN_LOCATION

# Source and destination
SOURCE_DIR=${1:-"/data"}  # Allow override for testing
STORAGE_ACCOUNT="novadata1737534736"
CONTAINER="databackup"
SOURCE_NAME=$(basename "${SOURCE_DIR}")

# SAS Token with full permissions
SAS_TOKEN="se=2025-01-30T06%3A00%3A00Z&sp=racwdl&sv=2022-11-02&sr=c&skoid=d4026ca4-a97d-4856-b4ad-6a64a5dafe78&sktid=d568f95a-a48a-4e42-8acf-0ba8c93c300f&skt=2025-01-23T06%3A00%3A38Z&ske=2025-01-30T06%3A00%3A00Z&sks=b&skv=2022-11-02&sig=YxpO4OYQQgl%2BqbvZ%2B45FX6CKjYkBWle6ILwhcl9Ioeo%3D"

# Ensure directories exist
mkdir -p "${LOG_DIR}" "${AZCOPY_WORK_DIR}" "${AZCOPY_LOG_LOCATION}" "${AZCOPY_JOB_PLAN_LOCATION}"

# Set permissions
chmod -R 750 "${LOG_DIR}"

# Create exclude pattern file
cat > "${LOG_DIR}/exclude_patterns.txt" << 'EOF'
*/configs/*
*/tmp/*
*/cache/*
*/proc/*
*/sys/*
*/dev/*
*/.env
*/__pycache__/*
*/node_modules/*
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
EOF

# Read exclusion patterns
EXCLUDE_PATTERN=$(tr '\n' ';' < "${LOG_DIR}/exclude_patterns.txt")

# Generate timestamp for log files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="${LOG_DIR}/backup_${TIMESTAMP}.log"
CHANGES_LOG="${LOG_DIR}/changes_${TIMESTAMP}.log"

# Verify azcopy is installed
if ! command -v azcopy &> /dev/null; then
    echo "[$(date)] Error: azcopy is not installed" | tee -a "${BACKUP_LOG}"
    exit 1
fi

# Verify source directory exists
if [ ! -d "${SOURCE_DIR}" ]; then
    echo "[$(date)] Error: Source directory ${SOURCE_DIR} does not exist" | tee -a "${BACKUP_LOG}"
    exit 1
fi

# Log start
echo "[$(date)] Starting incremental backup of ${SOURCE_DIR}" | tee -a "${BACKUP_LOG}"
echo "[$(date)] Using log directory: ${LOG_DIR}" | tee -a "${BACKUP_LOG}"
echo "[$(date)] AzCopy work directory: ${AZCOPY_WORK_DIR}" | tee -a "${BACKUP_LOG}"

# Execute AzCopy sync with MD5 hash comparison and improved monitoring
AZCOPY_COMMAND="azcopy sync \"${SOURCE_DIR}\" \"https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER}/${SOURCE_NAME}/?${SAS_TOKEN}\" \
    --recursive \
    --exclude-pattern=\"${EXCLUDE_PATTERN}\" \
    --delete-destination=false \
    --cap-mbps=50 \
    --put-md5 \
    --log-level=INFO \
    --output-type=json \
    --block-size-mb=100"

echo "[$(date)] Executing command: ${AZCOPY_COMMAND}" | tee -a "${BACKUP_LOG}"

eval ${AZCOPY_COMMAND} 2>&1 | while IFS= read -r line; do
    echo "[$(date)] $line" | tee -a "${BACKUP_LOG}"
    # Extract and log changed files from JSON output
    if echo "$line" | grep -q '"MessageType":"UPLOAD"' 2>/dev/null; then
        echo "$line" | jq -r '.Source' >> "${CHANGES_LOG}" 2>/dev/null || true
    fi
done

BACKUP_EXIT_CODE=${PIPESTATUS[0]}

# Log completion and statistics
if [ -f "${CHANGES_LOG}" ]; then
    CHANGED_FILES=$(wc -l < "${CHANGES_LOG}")
    echo "[$(date)] Changed files in this backup: ${CHANGED_FILES}" | tee -a "${BACKUP_LOG}"
fi

echo "[$(date)] Backup completed with exit code ${BACKUP_EXIT_CODE}" | tee -a "${BACKUP_LOG}"

# Cleanup old logs (keep last 7 days)
find "${LOG_DIR}" -name "backup_*.log" -mtime +7 -delete 2>/dev/null || true
find "${LOG_DIR}" -name "changes_*.log" -mtime +7 -delete 2>/dev/null || true

# If backup failed, show the last few lines of the log
if [ ${BACKUP_EXIT_CODE} -ne 0 ]; then
    echo "[$(date)] Backup failed. Last 10 lines of log:"
    tail -n 10 "${BACKUP_LOG}"
fi

exit ${BACKUP_EXIT_CODE}