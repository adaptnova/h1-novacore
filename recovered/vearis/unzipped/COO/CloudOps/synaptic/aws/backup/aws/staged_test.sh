#!/bin/bash

# Staged backup test script
# Tests backups in increasing size with error tolerance

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "${SCRIPT_DIR}/config.sh"

echo -e "\n\033[1;36m=== Starting Staged Backup Tests ===\033[0m\n"

# Stage 1: Small test with /data/ax/CloudOps (~1GB test)
echo -e "\n\033[1;33mStage 1: Small Test Backup\033[0m"
export SOURCE_DIR="/data/ax/CloudOps"
export BACKUP_ID="small_test_$(date +%Y%m%d_%H%M%S)"
export S3_PREFIX="test_backups"

"${SCRIPT_DIR}/parallel_backup.sh"
SMALL_TEST_STATUS=$?

echo -e "\nSmall test completed with status: $SMALL_TEST_STATUS"
sleep 5

# Stage 2: Medium test with /data/ax
if [ $SMALL_TEST_STATUS -eq 0 ] || [ $SMALL_TEST_STATUS -eq 1 ]; then
    echo -e "\n\033[1;33mStage 2: /data/ax Backup\033[0m"
    export SOURCE_DIR="/data/ax"
    export BACKUP_ID="ax_backup_$(date +%Y%m%d_%H%M%S)"
    export S3_PREFIX="ax_backups"

    "${SCRIPT_DIR}/parallel_backup.sh"
    MEDIUM_TEST_STATUS=$?
    
    echo -e "\n/data/ax backup completed with status: $MEDIUM_TEST_STATUS"
    sleep 5
fi

# Stage 3: Full /data backup
if [ $MEDIUM_TEST_STATUS -eq 0 ] || [ $MEDIUM_TEST_STATUS -eq 1 ]; then
    echo -e "\n\033[1;33mStage 3: Full /data Backup\033[0m"
    export SOURCE_DIR="/data"
    export BACKUP_ID="full_backup_$(date +%Y%m%d_%H%M%S)"
    export S3_PREFIX="full_backups"

    "${SCRIPT_DIR}/parallel_backup.sh"
    FULL_BACKUP_STATUS=$?
    
    echo -e "\nFull backup completed with status: $FULL_BACKUP_STATUS"
fi

echo -e "\n\033[1;32m=== Staged Backup Tests Complete ===\033[0m"
echo "Small Test Status: $SMALL_TEST_STATUS"
echo "Medium Test Status: $MEDIUM_TEST_STATUS"
echo "Full Backup Status: $FULL_BACKUP_STATUS"