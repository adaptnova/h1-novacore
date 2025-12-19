#!/bin/bash

# rsync_to_gcp.sh - Script to rsync data from IBM Cloud to Google Cloud Platform
# Created by Synaptic on March 19, 2025

# Configuration
SOURCE_DIR="/mnt/data/"
REMOTE_USER="x"
REMOTE_HOST="35.222.111.222"  # Replace with actual GCP instance IP
REMOTE_DIR="/home/x/data/"
SSH_KEY="/root/.ssh/id_rsa"
LOG_FILE="/root/rsync_logs/rsync_to_gcp_$(date +%Y%m%d_%H%M%S).log"
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

# Ensure the source directory exists and is mounted
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR does not exist or is not mounted" | tee -a "$LOG_FILE"
    exit 1
fi

# Display start message
echo "Starting rsync from IBM Cloud to GCP at $(date)" | tee -a "$LOG_FILE"
echo "Source: $SOURCE_DIR" | tee -a "$LOG_FILE"
echo "Destination: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR" | tee -a "$LOG_FILE"

# Run rsync with progress, compression, and logging
rsync -avz --progress --stats \
    --exclude-from="$EXCLUDE_FILE" \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    "$SOURCE_DIR" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR" 2>&1 | tee -a "$LOG_FILE"

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