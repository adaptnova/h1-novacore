#!/bin/bash
# Script to download Linux ISOs from multiple mirrors to test connectivity and load balancing
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="linux_iso_download.log"

# Linux ISO mirrors to test
MIRRORS=(
  "https://mirrors.edge.kernel.org/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-2009.iso|Kernel.org CentOS"
  "https://mirror.arizona.edu/ubuntu-releases/22.04/ubuntu-22.04.3-live-server-amd64.iso|Arizona Ubuntu"
  "https://mirrors.mit.edu/debian-cd/current/amd64/iso-cd/debian-12.4.0-amd64-netinst.iso|MIT Debian"
  "https://download.fedoraproject.org/pub/fedora/linux/releases/39/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-39-1.5.iso|Fedora Official"
  "https://mirrors.ocf.berkeley.edu/archlinux/iso/2023.12.01/archlinux-2023.12.01-x86_64.iso|Berkeley Arch"
)

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Initialize log file
> "$LOG_FILE"

log "Starting Linux ISO download test"

# Get list of all interfaces
log "Getting list of all network interfaces..."
INTERFACES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -br addr show | grep -v lo | awk '{print \$1}'")

if [ -z "$INTERFACES" ]; then
  log "No interfaces found"
  exit 1
fi

log "Found interfaces: $INTERFACES"

# Create results directory on the server
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "mkdir -p /tmp/iso_downloads"

# Create results file
echo "Interface,Source,Speed (MB/s)" > iso_download_results.csv

# Test each interface with each mirror
for iface in $INTERFACES; do
  log "Testing interface $iface..."
  
  # Get IP address for this interface
  IP=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -4 addr show dev $iface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}' | head -1")
  
  if [ -z "$IP" ]; then
    log "No IP address found for $iface, skipping"
    continue
  fi
  
  log "Using IP address $IP for $iface"
  
  # Test each mirror
  for mirror_info in "${MIRRORS[@]}"; do
    IFS='|' read -r url name <<< "$mirror_info"
    
    log "Testing download from $name on $iface ($IP)..."
    
    # Run the test - download for 10 seconds then abort
    RESULT=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cd /tmp/iso_downloads && curl --interface $IP -o ${name// /_}.iso --max-time 10 -w '%{speed_download}' $url 2>/dev/null")
    
    if [ -z "$RESULT" ]; then
      log "Test failed for $name on $iface"
      SPEED="0"
    else
      # Convert to MB/s
      SPEED=$(echo "scale=2; $RESULT / 1048576" | bc)
      log "Download speed from $name on $iface: $SPEED MB/s"
    fi
    
    # Save result
    echo "$iface,$name,$SPEED" >> iso_download_results.csv
  done
  
  # Add a blank line for readability
  log ""
done

# Generate summary
log "Generating summary report..."

# Calculate average speed by interface
log "Average download speed by interface:"
for iface in $INTERFACES; do
  AVG=$(awk -F, -v iface="$iface" '$1==iface {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' iso_download_results.csv)
  log "$iface: $AVG MB/s"
done

# Calculate average speed by source
log "Average download speed by source:"
for mirror_info in "${MIRRORS[@]}"; do
  IFS='|' read -r url name <<< "$mirror_info"
  AVG=$(awk -F, -v name="$name" '$2==name {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' iso_download_results.csv)
  log "$name: $AVG MB/s"
done

# Find best interface
BEST_IFACE=$(awk -F, 'NR>1 {sum[$1]+=$3; count[$1]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxif=i}} print maxif}' iso_download_results.csv)
BEST_SPEED=$(awk -F, -v iface="$BEST_IFACE" '$1==iface {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' iso_download_results.csv)
log "Best performing interface: $BEST_IFACE with average speed of $BEST_SPEED MB/s"

# Find best source
BEST_SOURCE=$(awk -F, 'NR>1 {sum[$2]+=$3; count[$2]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxsrc=i}} print maxsrc}' iso_download_results.csv)
BEST_SOURCE_SPEED=$(awk -F, -v source="$BEST_SOURCE" '$2==source {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' iso_download_results.csv)
log "Best performing source: $BEST_SOURCE with average speed of $BEST_SOURCE_SPEED MB/s"

# Clean up
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "rm -rf /tmp/iso_downloads"

log "Linux ISO download test completed. Results saved to iso_download_results.csv"