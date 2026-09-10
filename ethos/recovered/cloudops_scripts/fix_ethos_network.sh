#!/bin/bash
# Script to fix ethos server network bandwidth issue
# Current issue: Server has 72 Gbps network bandwidth capacity but only 32 Gbps is configured

# Log file
LOG_FILE="/var/log/ethos_network_fix.log"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting ethos network bandwidth fix script"
log "Current configuration: 1 NIC with 32 Gbps bandwidth (out of 72 Gbps capacity)"

# Option 1: Configure network bonding to increase bandwidth
# This requires multiple network interfaces to be bonded together

log "Checking if bonding module is loaded"
if ! lsmod | grep -q bonding; then
    log "Loading bonding module"
    modprobe bonding
    echo "bonding" >> /etc/modules
fi

# Create bonding configuration
log "Creating bonding configuration"
cat > /etc/network/interfaces.d/bond0.conf << EOF
# Bond interface
auto bond0
iface bond0 inet static
    address 10.240.0.5
    netmask 255.255.255.0
    gateway 10.240.0.1
    bond-mode 802.3ad
    bond-miimon 100
    bond-lacp-rate 1
    bond-slaves eth0
EOF

# Restart networking
log "Restarting networking service"
systemctl restart networking

# Option 2: Optimize network settings for high performance
log "Optimizing network settings for high performance"

# Increase network buffer sizes
cat >> /etc/sysctl.conf << EOF
# Increase network buffer sizes
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.rmem_default = 16777216
net.core.wmem_default = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.core.netdev_max_backlog = 30000
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_congestion_control = bbr
EOF

# Apply sysctl changes
log "Applying sysctl changes"
sysctl -p

# Option 3: Configure ethtool settings for optimal performance
log "Configuring ethtool settings for optimal performance"
ethtool -G eth0 rx 4096 tx 4096

# Create a persistent ethtool configuration
cat > /etc/networkd-dispatcher/routable.d/50-ethtool << EOF
#!/bin/bash
ethtool -G eth0 rx 4096 tx 4096
EOF

chmod +x /etc/networkd-dispatcher/routable.d/50-ethtool

# Option 4: Contact IBM Cloud support
log "For full 72 Gbps bandwidth utilization, contact IBM Cloud support with the following information:"
log "  - Instance ID: 0717_03ed7300-9111-4cd8-82c9-f6d5f5d10224"
log "  - Current network interface speed: 32 Gbps"
log "  - Desired network interface speed: 72 Gbps"
log "  - Profile network bandwidth capacity: 72 Gbps"

log "Network optimization completed. Please monitor network performance and contact IBM Cloud support if needed."

# Instructions for IBM Cloud support ticket
cat > ibm_cloud_support_request.txt << EOF
Subject: Request to increase network interface speed for ethos server

Details:
- Instance ID: 0717_03ed7300-9111-4cd8-82c9-f6d5f5d10224
- Instance Name: ethos
- Current network interface speed: 32 Gbps
- Desired network interface speed: 72 Gbps
- Profile network bandwidth capacity: 72 Gbps

Our ethos server (gx3-48x240x2l40s profile) has a network bandwidth capacity of 72 Gbps, but the current network interface is only configured for 32 Gbps. We would like to utilize the full network bandwidth capacity of the server.

We have attempted to add additional network interfaces but were unsuccessful. Please advise on how to increase the network interface speed to utilize the full 72 Gbps capacity.

Thank you.
EOF

log "Created IBM Cloud support request template: ibm_cloud_support_request.txt"