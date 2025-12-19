#!/bin/bash

# Get the current directory
CURRENT_DIR="$(pwd)"
RSYNC_SCRIPT="$CURRENT_DIR/nova_rsync_parallel.sh"
TOTAL_INSTANCES=20

# Verify the script exists
if [ ! -f "$RSYNC_SCRIPT" ]; then
    echo "Error: $RSYNC_SCRIPT not found!"
    exit 1
fi

# Make sure the script is executable
chmod +x "$RSYNC_SCRIPT"

# Command to launch gnome-terminal with a tab running the rsync script
LAUNCH_CMD="gnome-terminal"

# Create tabs with unique instance IDs
for i in $(seq 1 $TOTAL_INSTANCES); do
    # Each tab gets a unique instance ID and knows the total number of instances
    LAUNCH_CMD+=" --tab --title='RSYNC-$i' --working-directory='$CURRENT_DIR' -- bash -c '$RSYNC_SCRIPT $i $TOTAL_INSTANCES; exec bash'"
done

# Execute the launch command
echo "Launching $TOTAL_INSTANCES distributed instances of $RSYNC_SCRIPT in gnome-terminal tabs..."
eval $LAUNCH_CMD

echo "All terminals launched! Each instance will process its own set of directories."
