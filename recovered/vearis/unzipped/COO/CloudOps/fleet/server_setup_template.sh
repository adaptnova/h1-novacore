#!/bin/bash
# IBM Cloud Server Setup Template
# Version: 1.0.0
# Created: 2025-03-28
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)
#
# This template can be used to set up any IBM Cloud server with:
# - Network interfaces (up to 8)
# - Security group rules for mail server
# - Optimized network configuration
# - Route setup
#
# Usage: ./server_setup_template.sh <server_name> <subnet_id> <security_group_id>

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}===== $1 =====${NC}\n"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info message
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if all required parameters are provided
if [ $# -lt 3 ]; then
    print_error "Usage: $0 <server_name> <subnet_id> <security_group_id>"
    exit 1
fi

SERVER_NAME="$1"
SUBNET_ID="$2"
SECURITY_GROUP_ID="$3"

# Check if IBM Cloud CLI is installed and logged in
print_section "Checking IBM Cloud CLI"
if ! command -v ibmcloud &> /dev/null; then
    print_error "IBM Cloud CLI is not installed. Please install it first."
    exit 1
fi

# Login to IBM Cloud
print_info "Logging in to IBM Cloud..."
ibmcloud login -u chase@levelup2x.com -p '@@ALALzmzm102938!!'

# Set target to VPC infrastructure
print_info "Setting target to VPC infrastructure..."
ibmcloud is target --gen 2

# Part 1: Add Network Interfaces (up to 8)
print_section "Adding Network Interfaces"

# Get the existing network interface ID
print_info "Getting existing network interface ID..."
EXISTING_NIC_ID=$(ibmcloud is instance $SERVER_NAME --output json | jq -r '.network_interfaces[0].id')
print_info "Existing network interface ID: $EXISTING_NIC_ID"

# Count existing network interfaces
print_info "Counting existing network interfaces..."
EXISTING_NIC_COUNT=$(ibmcloud is instance-network-interfaces $SERVER_NAME --output json | jq '. | length')
print_info "Existing network interface count: $EXISTING_NIC_COUNT"

# Calculate how many interfaces to add
INTERFACES_TO_ADD=$((8 - EXISTING_NIC_COUNT))
if [ $INTERFACES_TO_ADD -le 0 ]; then
    print_success "Server already has 8 or more network interfaces. No need to add more."
else
    print_info "Adding $INTERFACES_TO_ADD network interfaces..."
    
    # Add network interfaces
    for i in $(seq 1 $INTERFACES_TO_ADD); do
        INTERFACE_NAME="eth$((EXISTING_NIC_COUNT + i - 1))"
        print_info "Adding $INTERFACE_NAME interface..."
        NIC_RESULT=$(ibmcloud is instance-network-interface-create $INTERFACE_NAME $SERVER_NAME $SUBNET_ID --output json || echo '{"id": ""}')
        NIC_ID=$(echo $NIC_RESULT | jq -r '.id')
        
        if [ -n "$NIC_ID" ] && [ "$NIC_ID" != "null" ]; then
            print_success "Created $INTERFACE_NAME with ID: $NIC_ID"
        else
            print_error "Failed to create $INTERFACE_NAME interface."
        fi
    done
    
    # Wait for interfaces to be attached
    print_info "Waiting for interfaces to be attached..."
    sleep 30
    
    # Verify all interfaces
    print_info "Verifying all network interfaces..."
    ibmcloud is instance-network-interfaces $SERVER_NAME
fi

# Part 2: Configure Security Group Rules for Mail Server
print_section "Configuring Security Group Rules"

# Define the required ports and protocols for mail server
print_info "Adding rules for required mail server ports..."

# Array of port definitions: port,protocol,description
PORTS=(
    "25,tcp,SMTP - Receiving mail from other mail servers"
    "465,tcp,SMTPS - Secure SMTP (legacy)"
    "587,tcp,Submission - Sending mail (with authentication)"
    "143,tcp,IMAP - Mail access (unencrypted)"
    "993,tcp,IMAPS - Secure IMAP mail access"
    "110,tcp,POP3 - Mail access (unencrypted)"
    "995,tcp,POP3S - Secure POP3 mail access"
    "4190,tcp,Sieve - Mail filtering"
    "80,tcp,HTTP - Web access and Let's Encrypt verification"
    "443,tcp,HTTPS - Secure web access"
)

# Add rules for each port
for PORT_INFO in "${PORTS[@]}"; do
    IFS=',' read -r PORT PROTOCOL DESCRIPTION <<< "$PORT_INFO"
    
    print_info "Adding rule for port $PORT ($DESCRIPTION)..."
    
    # Check if rule already exists
    EXISTING_RULE=$(ibmcloud is security-group-rules $SECURITY_GROUP_ID --output json | jq -r '.[] | select(.direction=="inbound" and .port_min=='$PORT' and .port_max=='$PORT' and .protocol=="'$PROTOCOL'") | .id')
    
    if [ -n "$EXISTING_RULE" ] && [ "$EXISTING_RULE" != "null" ]; then
        print_info "Rule for port $PORT already exists (ID: $EXISTING_RULE). Skipping..."
    else
        # Add rule for the port
        RULE_RESULT=$(ibmcloud is security-group-rule-add $SECURITY_GROUP_ID inbound $PROTOCOL --port-min $PORT --port-max $PORT --output json)
        RULE_ID=$(echo $RULE_RESULT | jq -r '.id')
        
        if [ -n "$RULE_ID" ] && [ "$RULE_ID" != "null" ]; then
            print_success "Added rule for port $PORT (ID: $RULE_ID)"
        else
            print_error "Failed to add rule for port $PORT."
        fi
    fi
done

# Part 3: SSH to the server and optimize network configuration
print_section "Optimizing Network Configuration"

# Get the floating IP of the server
print_info "Getting floating IP of the server..."
FLOATING_IP=$(ibmcloud is instance $SERVER_NAME --output json | jq -r '.network_interfaces[0].floating_ips[0].address // empty')

if [ -z "$FLOATING_IP" ]; then
    print_error "No floating IP found for the server. Cannot SSH to optimize network configuration."
    exit 1
fi

print_info "Server floating IP: $FLOATING_IP"

# SSH to the server and optimize network configuration
print_info "SSH to the server and optimize network configuration..."
ssh -o StrictHostKeyChecking=no -i id_rsa root@$FLOATING_IP << 'EOF'
# Set MTU to 1500 on all interfaces
echo "Setting MTU to 1500 on all interfaces..."
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
    echo "Setting MTU 1500 on $iface..."
    ip link set $iface mtu 1500
done

# Optimize TCP settings
echo "Optimizing TCP settings..."
cat > /etc/sysctl.d/99-network-tuning.conf << 'EOT'
# TCP tuning
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_congestion_control = cubic
net.ipv4.tcp_mtu_probing = 1
net.ipv4.tcp_fastopen = 3
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_sack = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_window_scaling = 1
EOT

# Apply sysctl settings
echo "Applying sysctl settings..."
sysctl -p /etc/sysctl.d/99-network-tuning.conf

# Configure network interfaces
echo "Configuring network interfaces..."
for i in $(seq 0 7); do
    if [ -e "/sys/class/net/eth$i" ]; then
        echo "Configuring eth$i..."
        
        # Create network configuration file
        cat > "/etc/network/interfaces.d/eth$i.conf" << EOC
auto eth$i
iface eth$i inet dhcp
    mtu 1500
EOC
    fi
done

# Restart networking
echo "Restarting networking..."
systemctl restart networking

# Set up routes
echo "Setting up routes..."
# Add default route via eth0
ip route add default via $(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | cut -d'/' -f1 | sed 's/\.[0-9]*$/.1/') dev eth0

# Add additional routes for each interface
for i in $(seq 1 7); do
    if [ -e "/sys/class/net/eth$i" ]; then
        # Get the IP address of the interface
        IP=$(ip -4 addr show eth$i | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | cut -d'/' -f1)
        if [ -n "$IP" ]; then
            # Extract network prefix
            NETWORK=$(echo $IP | cut -d'.' -f1-3)
            # Add route for this network
            ip route add $NETWORK.0/24 dev eth$i
        fi
    fi
done

# Make routes persistent
echo "Making routes persistent..."
cat > /etc/network/if-up.d/routes << 'EOR'
#!/bin/bash
# Default route via eth0
ip route add default via $(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | cut -d'/' -f1 | sed 's/\.[0-9]*$/.1/') dev eth0

# Additional routes for each interface
for i in $(seq 1 7); do
    if [ -e "/sys/class/net/eth$i" ]; then
        # Get the IP address of the interface
        IP=$(ip -4 addr show eth$i | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | cut -d'/' -f1)
        if [ -n "$IP" ]; then
            # Extract network prefix
            NETWORK=$(echo $IP | cut -d'.' -f1-3)
            # Add route for this network
            ip route add $NETWORK.0/24 dev eth$i
        fi
    fi
done
EOR
chmod +x /etc/network/if-up.d/routes

# Verify network configuration
echo "Verifying network configuration..."
ip addr show
ip route show
EOF

print_section "Summary"
print_success "Server setup completed successfully."
print_info "The server has been configured with:"
print_info "- Network interfaces (up to 8)"
print_info "- Security group rules for mail server"
print_info "- Optimized network configuration"
print_info "- Route setup"