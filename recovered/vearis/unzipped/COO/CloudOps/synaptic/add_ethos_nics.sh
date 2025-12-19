#!/bin/bash
# Script to add multiple network interfaces to ethos server to utilize full 72 Gbps bandwidth

# Set variables
INSTANCE_ID="0717_03ed7300-9111-4cd8-82c9-f6d5f5d10224"
SUBNET_ID="0717-57b4b629-9704-4ba2-9fdb-63386cdba641"
SECURITY_GROUP="exchange-evacuate-subgroup-gravel"

# Log file
LOG_FILE="ethos_nics_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting script to add NICs to ethos server"
log "Instance ID: $INSTANCE_ID"
log "Subnet ID: $SUBNET_ID"
log "Security Group: $SECURITY_GROUP"

# Check current network interfaces
log "Checking current network interfaces"
ibmcloud is instance-network-interfaces $INSTANCE_ID | tee -a $LOG_FILE

# Add 9 more network interfaces to reach the maximum of 10
for i in {1..9}; do
    NIC_NAME="ethos-nic-$i"
    log "Adding network interface $NIC_NAME"
    
    # Create the network interface
    ibmcloud is instance-network-interface-create $NIC_NAME $INSTANCE_ID $SUBNET_ID --sg $SECURITY_GROUP --allow-ip-spoofing true
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        log "Successfully added network interface $NIC_NAME"
    else
        log "Failed to add network interface $NIC_NAME"
    fi
    
    # Wait a few seconds before adding the next interface
    sleep 5
done

# Check network interfaces after adding
log "Checking network interfaces after adding"
ibmcloud is instance-network-interfaces $INSTANCE_ID | tee -a $LOG_FILE

# Create script to configure network bonding on the ethos server
cat > configure_bonding.sh << 'EOF'
#!/bin/bash

# Install required packages
apt-get update
apt-get install -y ifenslave

# Load bonding module
modprobe bonding
echo "bonding" >> /etc/modules

# Create bonding configuration
cat > /etc/network/interfaces.d/bond0.conf << 'BONDCONF'
# Bond interface
auto bond0
iface bond0 inet static
    address 10.240.0.5
    netmask 255.255.255.0
    gateway 10.240.0.1
    dns-nameservers 8.8.8.8 8.8.4.4
    bond-mode 802.3ad
    bond-miimon 100
    bond-lacp-rate 1
    bond-slaves eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7 eth8 eth9
BONDCONF

# Restart networking
systemctl restart networking

# Check bonding status
cat /proc/net/bonding/bond0

# Check network speed
ethtool bond0 | grep Speed
EOF

log "Created configure_bonding.sh script to be run on the ethos server"

# Instructions for SSH to ethos and running the bonding script
log "Instructions:"
log "1. Copy configure_bonding.sh to ethos server:"
log "   scp configure_bonding.sh ethos@10.240.0.5:~/"
log "2. SSH to ethos server:"
log "   ssh ethos@10.240.0.5"
log "3. Run the bonding script:"
log "   sudo bash configure_bonding.sh"

log "Script completed. Check $LOG_FILE for details."