#!/bin/bash

# Check if an instance ID was provided
INSTANCE_ID=${1:-1}
NUM_INSTANCES=${2:-20}

# Configuration
GCP_USER="x"
GCP_HOST="35.243.206.117"
RSYNC_SSH="ssh -T -o Compression=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
RSYNC_OPTS="-az --compress-level=0 --info=flist2,name,progress2,stats2 --progress --no-motd --partial-dir=.rsync-partial --delete"

# Source directories to process
SOURCE_DIRS=("/data-nova/00" "/data-nova/ax")

# Function to sync subdirectories that match this instance's allocation
sync_subdirs() {
    local src_dir=$1
    local dest_suffix=$(basename "$src_dir")
    
    echo -e "\n📂 Instance $INSTANCE_ID/$NUM_INSTANCES scanning: $src_dir"
    
    # Get all first-level subdirectories
    local subdirs=()
    while IFS= read -r line; do
        subdirs+=("$line")
    done < <(find "$src_dir" -mindepth 1 -maxdepth 1 -type d | sort)
    
    # Calculate which subdirectories this instance should handle
    local total_subdirs=${#subdirs[@]}
    local i=0
    
    for subdir in "${subdirs[@]}"; do
        # Simple round-robin distribution: subdirectory i goes to instance (i % NUM_INSTANCES) + 1
        local target_instance=$(( (i % NUM_INSTANCES) + 1 ))
        
        if [ "$target_instance" -eq "$INSTANCE_ID" ]; then
            local subdir_name=$(basename "$subdir")
            echo -e "\n🚀 Instance $INSTANCE_ID syncing: $subdir → /c/${dest_suffix}-fix/$subdir_name"
            
            # Create remote directory if it doesn't exist
            ssh $GCP_USER@$GCP_HOST "mkdir -p /c/${dest_suffix}-fix/$subdir_name" 2>/dev/null
            
            # Run the rsync command
            rsync $RSYNC_OPTS -e "$RSYNC_SSH" "$subdir/" "$GCP_USER@$GCP_HOST:/c/${dest_suffix}-fix/$subdir_name/"
            
            echo -e "✅ Completed: $subdir"
        fi
        
        i=$((i+1))
    done
}

# Process each source directory
for src_dir in "${SOURCE_DIRS[@]}"; do
    sync_subdirs "$src_dir"
done

echo -e "\n🏁 Instance $INSTANCE_ID completed all assigned directories."
