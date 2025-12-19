#!/bin/bash
# Setup Cron Job for IBM Cloud Volume Snapshot Schedule
# Created by: Synaptic
# Date: March 21, 2025

# Set variables
SCRIPT_PATH="/home/x/ibm_guy/snapshot_schedule.sh"
LOG_PATH="/home/x/ibm_guy/snapshot_logs"
CRON_JOB="0 * * * * $SCRIPT_PATH >> $LOG_PATH/snapshot_\$(date +\%Y\%m\%d).log 2>&1"

# Create log directory if it doesn't exist
mkdir -p "$LOG_PATH"
echo "Created log directory: $LOG_PATH"

# Check if script exists and is executable
if [[ ! -x "$SCRIPT_PATH" ]]; then
    echo "Error: $SCRIPT_PATH does not exist or is not executable"
    exit 1
fi

# Add cron job
(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH" ; echo "$CRON_JOB") | crontab -
echo "Added hourly cron job for snapshot schedule"

# Display current crontab
echo "Current crontab:"
crontab -l

echo "Snapshot schedule has been set up to run every hour"
echo "Logs will be stored in: $LOG_PATH"
echo ""
echo "Retention policy:"
echo "- All hourly snapshots kept for 2 days"
echo "- One snapshot per day (23:00) kept for days 3-14"
echo "- All snapshots deleted after 14 days"