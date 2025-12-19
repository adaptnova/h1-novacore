#!/bin/bash

# rsync_monitor.sh - Script to monitor rsync progress and performance
# Created by Synaptic on March 19, 2025

# Configuration
LOG_DIR="/root/rsync_logs"
STATS_FILE="$LOG_DIR/rsync_stats.csv"
INTERVAL=10  # Seconds between checks
DURATION=0   # 0 for indefinite monitoring, or specify in seconds
NOTIFY_EMAIL=""  # Optional email for notifications

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Initialize stats file with headers if it doesn't exist
if [ ! -f "$STATS_FILE" ]; then
    echo "Timestamp,CPU_Usage,Memory_Usage,Disk_Read,Disk_Write,Network_In,Network_Out,Rsync_Processes,Transfer_Speed" > "$STATS_FILE"
fi

# Function to get current timestamp
get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Function to collect system stats
collect_stats() {
    TIMESTAMP=$(get_timestamp)
    
    # CPU usage (percentage)
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    
    # Memory usage (percentage)
    MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    
    # Disk I/O (KB/s)
    DISK_STATS=$(iostat -d -k 1 2 | tail -n 4 | head -n 1)
    DISK_READ=$(echo "$DISK_STATS" | awk '{print $3}')
    DISK_WRITE=$(echo "$DISK_STATS" | awk '{print $4}')
    
    # Network I/O (KB/s)
    NETWORK_STATS=$(sar -n DEV 1 1 | grep -A 1 "IFACE" | tail -n 1)
    NETWORK_IN=$(echo "$NETWORK_STATS" | awk '{print $5}')
    NETWORK_OUT=$(echo "$NETWORK_STATS" | awk '{print $6}')
    
    # Count rsync processes
    RSYNC_PROCESSES=$(pgrep -c rsync || echo "0")
    
    # Estimate transfer speed from rsync processes (if any)
    if [ "$RSYNC_PROCESSES" -gt 0 ]; then
        # Extract transfer speed from rsync progress output
        TRANSFER_SPEED=$(ps aux | grep rsync | grep -v grep | grep -o "[0-9.]\+ [KMG]B/s" | head -n 1 || echo "0 KB/s")
    else
        TRANSFER_SPEED="0 KB/s"
    fi
    
    # Write stats to CSV
    echo "$TIMESTAMP,$CPU_USAGE,$MEM_USAGE,$DISK_READ,$DISK_WRITE,$NETWORK_IN,$NETWORK_OUT,$RSYNC_PROCESSES,$TRANSFER_SPEED" >> "$STATS_FILE"
    
    # Display current stats
    echo "===== Rsync Monitor Stats at $TIMESTAMP ====="
    echo "CPU Usage: $CPU_USAGE%"
    echo "Memory Usage: $MEM_USAGE%"
    echo "Disk Read: $DISK_READ KB/s"
    echo "Disk Write: $DISK_WRITE KB/s"
    echo "Network In: $NETWORK_IN KB/s"
    echo "Network Out: $NETWORK_OUT KB/s"
    echo "Rsync Processes: $RSYNC_PROCESSES"
    echo "Transfer Speed: $TRANSFER_SPEED"
    echo "=============================================="
}

# Function to check if rsync is running
is_rsync_running() {
    pgrep rsync > /dev/null
    return $?
}

# Function to send notification
send_notification() {
    if [ -n "$NOTIFY_EMAIL" ]; then
        echo "$1" | mail -s "Rsync Monitor Notification" "$NOTIFY_EMAIL"
    fi
    echo "$1"
}

# Install required tools if not present
for pkg in sysstat iostat bc; do
    if ! command -v $pkg &> /dev/null; then
        echo "Installing required package: $pkg"
        apt-get update && apt-get install -y sysstat
        break  # sysstat includes both sysstat and iostat
    fi
done

# Main monitoring loop
echo "Starting rsync monitoring at $(get_timestamp)"
echo "Stats will be collected every $INTERVAL seconds"
echo "Stats file: $STATS_FILE"

START_TIME=$(date +%s)
RSYNC_RUNNING_PREV=false

if is_rsync_running; then
    RSYNC_RUNNING_PREV=true
    send_notification "Rsync monitoring started. Rsync is already running."
else
    send_notification "Rsync monitoring started. Waiting for rsync to start."
fi

while true; do
    # Check if we should exit based on duration
    if [ $DURATION -gt 0 ]; then
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
        if [ $ELAPSED_TIME -ge $DURATION ]; then
            send_notification "Rsync monitoring completed after $DURATION seconds."
            break
        fi
    fi
    
    # Check if rsync is running
    if is_rsync_running; then
        if [ "$RSYNC_RUNNING_PREV" = false ]; then
            send_notification "Rsync process started at $(get_timestamp)"
            RSYNC_RUNNING_PREV=true
        fi
        collect_stats
    else
        if [ "$RSYNC_RUNNING_PREV" = true ]; then
            send_notification "Rsync process ended at $(get_timestamp)"
            RSYNC_RUNNING_PREV=false
        fi
        echo "No rsync process running at $(get_timestamp). Waiting..."
    fi
    
    sleep $INTERVAL
done

echo "Monitoring complete. Stats saved to $STATS_FILE"