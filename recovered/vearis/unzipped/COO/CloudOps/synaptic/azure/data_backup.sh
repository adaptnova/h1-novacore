#!/bin/bash

# Data Backup Script
# Created: 2025-01-22
# Purpose: Backup /data to Azure Blob Storage

set -euo pipefail
trap 'cleanup_and_exit' ERR INT TERM

# Configuration
if [[ "${BACKUP_SOURCE_DIR}" == /* ]]; then
    # Absolute path - remove trailing slash
    SOURCE_DIR="${BACKUP_SOURCE_DIR%/}"
else
    SOURCE_DIR="${BACKUP_SOURCE_DIR:-/data}"
fi
SOURCE_NAME=$(basename "${SOURCE_DIR}")
STORAGE_ACCOUNT="${AZURE_STORAGE_ACCOUNT:-novadata1737534736}"
CONTAINER="${AZURE_STORAGE_CONTAINER:-databackup}"
SAS_TOKEN="${AZURE_SAS_TOKEN:-}"
LOG_DIR="${BACKUP_LOG_DIR:-/logs/backup}"
AZCOPY_WORK_DIR="${LOG_DIR}/azcopy"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/backup_${DATE}.log"

export AZCOPY_LOG_LOCATION="${AZCOPY_WORK_DIR}/logs"
# Environment setup
export AZCOPY_LOG_LOCATION="${AZCOPY_WORK_DIR}/logs" 
export AZCOPY_JOB_PLAN_LOCATION="${AZCOPY_WORK_DIR}/plans" 
export AZCOPY_TEMP_DIR="${AZCOPY_WORK_DIR}/tmp"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Cleanup function
cleanup_and_exit() {
    local exit_code=$?
    log "Cleaning up and exiting with code ${exit_code}"
    pkill -f azcopy || true
    exit "${exit_code}"
}

# Setup directories
setup_dirs() {
    log "Setting up directories"
    mkdir -p "${LOG_DIR}"
    chmod 750 "${LOG_DIR}"
    chown x:x "${LOG_DIR}"
    
    mkdir -p "${AZCOPY_WORK_DIR}/logs"
    mkdir -p "${AZCOPY_WORK_DIR}/plans"
    mkdir -p "${AZCOPY_WORK_DIR}/tmp"
    
    # Set proper ownership and permissions
    chown -R x:x "${AZCOPY_WORK_DIR}"
    chmod 750 "${AZCOPY_WORK_DIR}"
    chmod -R 750 "${AZCOPY_WORK_DIR}"
}

# Main backup function
do_backup() {
    log "Starting backup of ${SOURCE_DIR}"
    
    if [ -z "${SAS_TOKEN}" ]; then
        log "ERROR: AZURE_SAS_TOKEN environment variable is not set"
        exit 1
    fi
    
    log "Starting azcopy sync"
    
    # First, delete /data/configs from backup if it exists
    log "Removing /data/configs from backup (will free ~686G)..."
    azcopy rm "https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER}/configs?${SAS_TOKEN}" \
        --recursive \
        2>&1 | tee -a "${LOG_FILE}"
    
    local rm_status=${PIPESTATUS[0]}
    if [ $rm_status -eq 0 ]; then
        log "Successfully removed /data/configs from backup (Storage freed: ~686G)"
    else
        log "Note: /data/configs may not exist in backup or removal failed with status ${rm_status}"
    fi
    
    # Exclude patterns for sensitive/system directories
    local exclude_pattern="*/tmp/*;*/cache/*;*/proc/*;*/sys/*;*/dev/*;*/.env;*/__pycache__/*;*/node_modules/*;*/configs/*;*/logs/*"
    
    # Additional Docker-specific exclusions
    exclude_pattern="${exclude_pattern};\
*/docker/volumes/*;\
*/docker/overlay2/*;\
*/docker/containers/*;\
*/docker/image/*;\
*/docker/builder/*;\
*/docker/buildkit/*;\
*/docker/tmp/*;\
*/docker/swarm/*;\
*/minikube/*"
    
    azcopy sync "${SOURCE_DIR}" "https://${STORAGE_ACCOUNT}.blob.core.windows.net/${CONTAINER}/${SOURCE_NAME}/?${SAS_TOKEN}" \
        --recursive \
        --exclude-pattern="${exclude_pattern}" \
        --log-level=INFO \
        --output-type=text \
        --delete-destination=false \
        --cap-mbps=50 \
        --block-size-mb=100 \
        2>&1 | tee -a "${LOG_FILE}"
    
    local status=${PIPESTATUS[0]}
    if [ $status -eq 0 ]; then
        log "Backup completed successfully"
    else
        log "Backup failed with status ${status}"
        exit $status
    fi
}

# Cleanup old logs
cleanup_logs() {
    log "Cleaning up old logs"
    find "${LOG_DIR}" -type f -name "backup_*.log" -mtime +7 -delete
    find "${AZCOPY_WORK_DIR}/logs" -type f -mtime +7 -delete
    find "${AZCOPY_WORK_DIR}/plans" -type f -mtime +1 -delete
    find "${AZCOPY_WORK_DIR}/tmp" -type f -mtime +1 -delete
    find "${AZCOPY_WORK_DIR}" -type d -empty -delete
}

# Main execution
main() {
    setup_dirs
    do_backup
    cleanup_logs
}

# Run main function
main

exit 0