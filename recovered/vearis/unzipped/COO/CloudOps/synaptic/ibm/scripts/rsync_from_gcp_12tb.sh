#!/bin/bash

# rsync_from_gcp_12tb.sh - Script to rsync data from GCP 12TB disk to IBM Cloud
# Created by Synaptic on March 19, 2025

# Configuration
DESTINATION_DIR="/data-nova/gcp_migration/"
REMOTE_USER="x"
REMOTE_HOST="35.222.111.222"  # Replace with actual GCP instance IP
REMOTE_DIR="/mnt/disks/data-12tb/"
SSH_KEY="/root/.ssh/id_rsa"
LOG_FILE="/root/rsync_logs/rsync_from_gcp_12tb_$(date +%Y%m%d_%H%M%S).log"
EXCLUDE_FILE="/root/rsync_scripts/exclude_12tb.txt"
BANDWIDTH_LIMIT="50000"  # 50MB/s, adjust as needed

# Create log directory if it doesn't exist
mkdir -p /root/rsync_logs

# Create destination directory if it doesn't exist
mkdir -p "$DESTINATION_DIR"

# Create rsync exclude file
cat > "$EXCLUDE_FILE" << EOF
.Trash*
lost+found
*.tmp
*.temp
*.lock
*.part
.rsync-partial/
EOF

# Ensure the destination directory exists
if [ ! -d "$DESTINATION_DIR" ]; then
    echo "Error: Destination directory $DESTINATION_DIR does not exist or could not be created" | tee -a "$LOG_FILE"
    exit 1
fi

# Display start message
echo "Starting rsync from GCP 12TB disk to IBM Cloud at $(date)" | tee -a "$LOG_FILE"
echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR" | tee -a "$LOG_FILE"
echo "Destination: $DESTINATION_DIR" | tee -a "$LOG_FILE"
echo "Bandwidth limit: $BANDWIDTH_LIMIT KB/s" | tee -a "$LOG_FILE"

# Run rsync with progress, compression, bandwidth limiting, and logging
rsync -avz --progress --stats --partial --partial-dir=.rsync-partial \
    --bwlimit="$BANDWIDTH_LIMIT" \
    --exclude-from="$EXCLUDE_FILE" \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR" "$DESTINATION_DIR" 2>&1 | tee -a "$LOG_FILE"

# Check rsync exit status
RSYNC_EXIT_CODE=${PIPESTATUS[0]}
if [ $RSYNC_EXIT_CODE -eq 0 ]; then
    echo "Rsync completed successfully at $(date)" | tee -a "$LOG_FILE"
else
    echo "Rsync failed with exit code $RSYNC_EXIT_CODE at $(date)" | tee -a "$LOG_FILE"
fi

# Display summary
echo "Transfer summary:" | tee -a "$LOG_FILE"
echo "Exit code: $RSYNC_EXIT_CODE" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Calculate disk usage after transfer
echo "Disk usage after transfer:" | tee -a "$LOG_FILE"
df -h "$DESTINATION_DIR" | tee -a "$LOG_FILE"

exit $RSYNC_EXIT_CODE