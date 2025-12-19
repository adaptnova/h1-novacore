#!/bin/bash
# IBM Cloud Volume Snapshot Schedule Script
# Created by: Synaptic
# Date: March 21, 2025
#
# This script creates snapshots for boot and data volumes on IBM Cloud
# Schedule: Hourly snapshots, keeping all for 2 days, then 1 per day for days 3-14, then delete

# Set variables
BOOT_VOLUME_ID="r006-d8bf7a41-eb4b-4724-a36a-d571fed941e7"
DATA_VOLUME_ID="r006-9d0c6f44-d456-4722-8226-66192087347f"
RESOURCE_GROUP="adapt"
TIMESTAMP=$(date +"%Y%m%d-%H%M")
CURRENT_DATE=$(date +"%Y%m%d")
CURRENT_HOUR=$(date +"%H")

# Function to create a snapshot
create_snapshot() {
    local volume_id=$1
    local volume_type=$2
    local snapshot_name="${volume_type}-${TIMESTAMP}"
    
    echo "Creating snapshot: $snapshot_name for volume: $volume_id"
    ibmcloud is snapshot-create --name "$snapshot_name" --volume "$volume_id" --resource-group-name "$RESOURCE_GROUP" --tags "type:${volume_type},created:${CURRENT_DATE},hour:${CURRENT_HOUR},retention:hourly"
}

# Function to clean up old snapshots based on retention policy
cleanup_snapshots() {
    local volume_type=$1
    
    echo "Cleaning up old snapshots for $volume_type volumes..."
    
    # Get all snapshots
    SNAPSHOTS=$(ibmcloud is snapshots --output json)
    
    # Filter snapshots by name prefix
    FILTERED_SNAPSHOTS=$(echo "$SNAPSHOTS" | jq -r --arg prefix "${volume_type}-" '.[] | select(.name | startswith($prefix))')
    
    # Calculate dates for retention policy
    TWO_DAYS_AGO=$(date -d "2 days ago" +"%Y%m%d")
    FOURTEEN_DAYS_AGO=$(date -d "14 days ago" +"%Y%m%d")
    
    # Process each snapshot
    echo "$FILTERED_SNAPSHOTS" | while read -r snapshot_line; do
        # Parse the snapshot line to extract ID and name
        SNAPSHOT_ID=$(echo "$snapshot_line" | jq -r '.id')
        SNAPSHOT_NAME=$(echo "$snapshot_line" | jq -r '.name')
        
        # Skip if ID or name is empty
        if [[ -z "$SNAPSHOT_ID" || -z "$SNAPSHOT_NAME" || "$SNAPSHOT_ID" == "null" || "$SNAPSHOT_NAME" == "null" ]]; then
            continue
        }
        
        # Extract date and hour from snapshot name
        # Format: volume_type-YYYYMMDD-HHMM
        SNAPSHOT_DATE=$(echo "$SNAPSHOT_NAME" | grep -oP '\d{8}' || echo "")
        SNAPSHOT_HOUR=$(echo "$SNAPSHOT_NAME" | grep -oP '\d{8}-\K\d{2}' || echo "")
        
        if [[ -z "$SNAPSHOT_DATE" ]]; then
            echo "Skipping snapshot with invalid name format: $SNAPSHOT_NAME"
            continue
        fi
        
        # Apply retention policy
        if [[ "$SNAPSHOT_DATE" < "$FOURTEEN_DAYS_AGO" ]]; then
            # Delete snapshots older than 14 days
            echo "Deleting snapshot older than 14 days: $SNAPSHOT_NAME (ID: $SNAPSHOT_ID)"
            ibmcloud is snapshot-delete "$SNAPSHOT_ID" --force
        elif [[ "$SNAPSHOT_DATE" < "$TWO_DAYS_AGO" ]]; then
            # For snapshots between 3-14 days old, keep only one per day (the latest one at hour 23)
            if [[ "$SNAPSHOT_HOUR" != "23" ]]; then
                echo "Deleting non-23:00 snapshot for day $SNAPSHOT_DATE: $SNAPSHOT_NAME (ID: $SNAPSHOT_ID)"
                ibmcloud is snapshot-delete "$SNAPSHOT_ID" --force
            fi
        fi
        # Snapshots less than 2 days old are kept (all hourly snapshots)
    done
}

# Main execution
echo "Starting snapshot process at $(date)"

# Create snapshots for both volumes
create_snapshot "$BOOT_VOLUME_ID" "boot"
create_snapshot "$DATA_VOLUME_ID" "data"

# Clean up old snapshots based on retention policy
cleanup_snapshots "boot"
cleanup_snapshots "data"

echo "Snapshot process completed at $(date)"