#!/bin/bash

# rsync_from_gcp.sh - Script to rsync data from Google Cloud Platform to IBM Cloud
# Created by Synaptic on March 19, 2025

# Configuration
DESTINATION_DIR="/mnt/data/"
REMOTE_USER="x"
REMOTE_HOST="35.222.111.222"  # Replace with actual GCP instance IP
REMOTE_DIR="/home/x/data/"
SSH_KEY="/root/.ssh/id_rsa"
LOG_FILE="/root/rsync_logs/rsync_from_gcp_$(date +%Y%m%d_%H%M%S).log"
EXCLUDE_FILE="/root/rsync_scripts/exclude.txt"

# Create log directory if it doesn't exist
mkdir -p /root/rsync_logs

# Create rsync exclude file
cat > "$EXCLUDE_FILE" << EOF
.Trash*
lost+found
*.tmp
*.temp
*.lock
EOF

# Ensure the destination directory exists and is mounted
if [ ! -d "$DESTINATION_DIR" ]; then
    echo "Error: Destination directory $DESTINATION_DIR does not exist or is not mounted" | tee -a "$LOG_FILE"
    exit 1
fi

# Display start message
echo "Starting rsync from GCP to IBM Cloud at $(date)" | tee -a "$LOG_FILE"
echo "Source: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR" | tee -a "$LOG_FILE"
echo "Destination: $DESTINATION_DIR" | tee -a "$LOG_FILE"

# Run rsync with progress, compression, and logging
rsync -avz --progress --stats \
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

exit $RSYNC_EXIT_CODE