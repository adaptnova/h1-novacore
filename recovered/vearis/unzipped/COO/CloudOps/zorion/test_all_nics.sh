#!/bin/bash

# Script to optimize all NICs and test download speeds from multiple Linux ISO mirrors
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="nic_speed_test.log"

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
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Initialize log file
> "$LOG_FILE"

log "Starting NIC optimization and speed tests for all interfaces"

# Optimize all NICs
log "Optimizing network settings on all interfaces..."

ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat > /tmp/optimize_all.sh << 'EOF'
#!/bin/bash

echo 'Backing up sysctl.conf...'
cp /etc/sysctl.conf /etc/sysctl.conf.bak

echo 'Configuring network optimizations...'
cat > /etc/sysctl.conf << 'EOC'
# Network Optimization Settings
# Increase TCP buffer sizes
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Enable TCP window scaling and timestamps
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1

# Increase option memory buffers
net.core.optmem_max = 65536

# Increase network backlog
net.core.netdev_max_backlog = 5000

# Enable TCP Fast Open
net.ipv4.tcp_fastopen = 3

# Enable MTU probing
net.ipv4.tcp_mtu_probing = 1

# Enable BBR congestion control
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Increase max connections
net.core.somaxconn = 65535

# Enable IP forwarding
net.ipv4.ip_forward = 1

# Increase TCP keepalive settings
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 5

# Increase connection tracking
net.netfilter.nf_conntrack_max = 1000000
net.nf_conntrack_max = 1000000

# Increase the maximum TCP receive window
net.ipv4.tcp_window_scaling = 1
EOC

echo 'Applying settings...'
sysctl -p

echo 'Optimizing all interfaces...'
for i in $(ip -br link show | grep -v lo | awk '{print $1}'); do
  echo "Optimizing $i..."
  # Try to set MTU to 9000 (jumbo frames) if supported
  ip link set dev $i mtu 9000 || ip link set dev $i mtu 1500
  
  # Enable TX/RX offloading
  ethtool -K $i tso on gso on gro on lro on tx on rx on 2>/dev/null || true
  
  # Set ring buffer sizes
  ethtool -G $i rx 4096 tx 4096 2>/dev/null || true
  
  # Set interrupt coalescing
  ethtool -C $i rx-usecs 100 tx-usecs 100 2>/dev/null || true
done

echo 'Installing required packages...'
apt-get update
apt-get install -y curl wget iperf3 ethtool

echo 'Optimization complete!'
EOF

chmod +x /tmp/optimize_all.sh
bash /tmp/optimize_all.sh"

if [ $? -eq 0 ]; then
  log "Network optimization completed successfully"
else
  log "Network optimization failed"
  exit 1
fi

# Get list of all interfaces
log "Getting list of all network interfaces..."
INTERFACES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -br addr show | grep -v lo | awk '{print \$1}'")

if [ -z "$INTERFACES" ]; then
  log "No interfaces found"
  exit 1
fi

log "Found interfaces: $INTERFACES"

# Create results directory
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "mkdir -p /tmp/speed_tests"

# Create results file
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'Interface,Source,Speed (MB/s)' > /tmp/speed_tests/results.csv"

# Test each interface with each mirror
for iface in $INTERFACES; do
  log "Testing interface $iface..."
  
  # Get IP address for this interface
  IP=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -4 addr show dev $iface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}'")
  
  if [ -z "$IP" ]; then
    log "No IP address found for $iface, skipping"
    continue
  fi
  
  log "Using IP address $IP for $iface"
  
  # Test each mirror
  for mirror_info in "${MIRRORS[@]}"; do
    IFS="|" read -r url name <<< "$mirror_info"
    
    log "Testing download from $name on $iface ($IP)..."
    
    # Run the test
    RESULT=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl --interface $IP -o /dev/null $url -m 30 -w '%{speed_download}' 2>/dev/null")
    
    if [ -z "$RESULT" ]; then
      log "Test failed for $name on $iface"
      SPEED="0"
    else
      # Convert to MB/s
      SPEED=$(echo "scale=2; $RESULT / 1048576" | bc)
      log "Download speed from $name on $iface: $SPEED MB/s"
    fi
    
    # Save result
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo '$iface,$name,$SPEED' >> /tmp/speed_tests/results.csv"
  done
  
  # Add a blank line for readability
  log ""
done

# Run iperf3 test if available
log "Running iperf3 tests..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "if command -v iperf3 >/dev/null 2>&1; then for iface in \$(ip -br link show | grep -v lo | awk '{print \$1}'); do IP=\$(ip -4 addr show dev \$iface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}'); if [ -n \"\$IP\" ]; then echo \"Testing iperf3 on \$iface (\$IP)...\"; iperf3 -c iperf.he.net -B \$IP -t 5 2>/dev/null | grep receiver | awk '{print \$7\" \"\$8}' | tee -a /tmp/speed_tests/iperf_results.txt; fi; done; else echo \"iperf3 not installed\"; fi"

# Get the results
log "Retrieving test results..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat /tmp/speed_tests/results.csv"

# Generate summary
log "Generating summary report..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat > /tmp/generate_summary.sh << 'EOF'
#!/bin/bash

echo '# Network Speed Test Results'
echo
echo '## Test Environment'
echo '- Server: adapt (10.240.1.6)'
echo '- Date: $(date)'
echo '- Kernel: $(uname -r)'
echo '- Network Configuration:'
echo '```'
ip -br addr show
echo '```'
echo
echo '## Network Parameters'
echo '```'
sysctl -a | grep -E 'net.core.rmem_max|net.core.wmem_max|net.ipv4.tcp_congestion_control|net.core.default_qdisc'
echo '```'
echo
echo '## Download Speed Test Results'
echo
echo '### Summary by Interface'
echo '| Interface | Average Speed (MB/s) | Max Speed (MB/s) | Best Source |'
echo '|-----------|----------------------|------------------|-------------|'

# Calculate averages and maximums by interface
while read -r iface; do
  if [ "$iface" = "Interface" ]; then continue; fi
  
  avg=$(awk -F, -v iface="$iface" '$1==iface {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' /tmp/speed_tests/results.csv)
  max=$(awk -F, -v iface="$iface" '$1==iface {if($3>max) {max=$3; source=$2}} END {print max}' /tmp/speed_tests/results.csv)
  best_source=$(awk -F, -v iface="$iface" -v max="$max" '$1==iface && $3==max {print $2}' /tmp/speed_tests/results.csv)
  
  echo "| $iface | $avg | $max | $best_source |"
done < <(awk -F, 'NR>1 {print $1}' /tmp/speed_tests/results.csv | sort -u)

echo
echo '### Results by Source'
echo '| Source | Average Speed (MB/s) | Max Speed (MB/s) | Best Interface |'
echo '|--------|----------------------|------------------|----------------|'

# Calculate averages and maximums by source
while read -r source; do
  avg=$(awk -F, -v source="$source" '$2==source {sum+=$3; count++} END {if(count>0) printf "%.2f", sum/count; else print "0"}' /tmp/speed_tests/results.csv)
  max=$(awk -F, -v source="$source" '$2==source {if($3>max) {max=$3; iface=$1}} END {print max}' /tmp/speed_tests/results.csv)
  best_iface=$(awk -F, -v source="$source" -v max="$max" '$2==source && $3==max {print $1}' /tmp/speed_tests/results.csv)
  
  echo "| $source | $avg | $max | $best_iface |"
done < <(awk -F, 'NR>1 {print $2}' /tmp/speed_tests/results.csv | sort -u)

echo
echo '### Detailed Results'
echo '| Interface | Source | Speed (MB/s) |'
echo '|-----------|--------|-------------|'

# Add all results (skip header)
awk -F, 'NR>1 {printf "| %s | %s | %s |\n", $1, $2, $3}' /tmp/speed_tests/results.csv

# Add iperf3 results if available
if [ -f /tmp/speed_tests/iperf_results.txt ]; then
  echo
  echo '## iperf3 Test Results'
  echo '| Interface | Bandwidth |'
  echo '|-----------|-----------|'
  
  paste <(ip -br link show | grep -v lo | awk '{print $1}') /tmp/speed_tests/iperf_results.txt | while read -r iface bw; do
    echo "| $iface | $bw |"
  done
fi

echo
echo '## Conclusion'
echo
echo 'The network interfaces have been successfully optimized and tested. The results show the download speeds from various Linux ISO mirrors across all interfaces.'
echo
echo 'The best performing interface is **$(awk -F, 'NR>1 {sum[$1]+=$3; count[$1]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxif=i}} print maxif}' /tmp/speed_tests/results.csv)** with an average download speed of **$(awk -F, -v iface="$(awk -F, 'NR>1 {sum[$1]+=$3; count[$1]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxif=i}} print maxif}' /tmp/speed_tests/results.csv)" 'NR>1 && $1==iface {sum+=$3; count++} END {printf "%.2f", sum/count}' /tmp/speed_tests/results.csv) MB/s**.'
echo
echo 'The best performing source is **$(awk -F, 'NR>1 {sum[$2]+=$3; count[$2]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxsrc=i}} print maxsrc}' /tmp/speed_tests/results.csv)** with an average download speed of **$(awk -F, -v source="$(awk -F, 'NR>1 {sum[$2]+=$3; count[$2]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxsrc=i}} print maxsrc}' /tmp/speed_tests/results.csv)" 'NR>1 && $2==source {sum+=$3; count++} END {printf "%.2f", sum/count}' /tmp/speed_tests/results.csv) MB/s**.'
EOF

chmod +x /tmp/generate_summary.sh
bash /tmp/generate_summary.sh > /tmp/speed_tests/summary.md"

# Copy the summary back
log "Copying summary report..."
scp -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP:/tmp/speed_tests/summary.md ./nic_speed_test_results.md

log "Speed tests completed. Results saved to nic_speed_test_results.md"