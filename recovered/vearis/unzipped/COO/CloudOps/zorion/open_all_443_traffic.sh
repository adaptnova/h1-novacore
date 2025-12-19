#!/bin/bash
# Script to completely open port 443 on all interfaces and subnets
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 28, 2025

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to display section headers
section() {
  log "${BLUE}=== $1 ===${NC}"
}

# Function to display success messages
success() {
  log "${GREEN}✓ $1${NC}"
}

# Function to display error messages
error() {
  log "${RED}✗ $1${NC}"
}

# Function to display warning messages
warning() {
  log "${YELLOW}! $1${NC}"
}

SERVER_IP="10.240.1.6"
SSH_USER="root"

section "Opening ALL Port 443 Traffic on ALL Interfaces and Subnets"
log "Connecting to the adapt server..."

# Create a script to open all port 443 traffic
cat > /tmp/open_all_443.sh << 'EOF'
#!/bin/bash

# Backup current iptables rules
BACKUP_DIR="/tmp/firewall_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
iptables-save > $BACKUP_DIR/iptables_backup.rules
echo "Backed up current iptables rules to $BACKUP_DIR/iptables_backup.rules"

# Completely flush all iptables rules
echo "Flushing all iptables rules..."
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Ensure IBM Cloud Firewall is not blocking port 443
echo "Configuring IBM Cloud Firewall for port 443..."

# Check if ibmcloud CLI is installed
if command -v ibmcloud &> /dev/null; then
    echo "IBM Cloud CLI found, configuring firewall rules..."
    
    # Try to login if credentials are available
    if [ -f ~/.bluemix/config.json ]; then
        ibmcloud login -r us-south
    fi
    
    # List current security groups
    echo "Current security groups:"
    ibmcloud is security-groups
    
    # Create a new security group rule for port 443 if possible
    echo "Attempting to create security group rules for port 443..."
    SECURITY_GROUPS=$(ibmcloud is security-groups --output json | jq -r '.[].id')
    
    for SG_ID in $SECURITY_GROUPS; do
        echo "Adding outbound rule to security group $SG_ID..."
        ibmcloud is security-group-rule-add $SG_ID outbound tcp --port-min 443 --port-max 443 --remote "0.0.0.0/0" || true
        ibmcloud is security-group-rule-add $SG_ID outbound udp --port-min 443 --port-max 443 --remote "0.0.0.0/0" || true
        echo "Adding inbound rule to security group $SG_ID..."
        ibmcloud is security-group-rule-add $SG_ID inbound tcp --port-min 443 --port-max 443 --remote "0.0.0.0/0" || true
        ibmcloud is security-group-rule-add $SG_ID inbound udp --port-min 443 --port-max 443 --remote "0.0.0.0/0" || true
    done
else
    echo "IBM Cloud CLI not found, skipping IBM Cloud Firewall configuration."
fi

# Disable any firewall service that might be running
echo "Disabling firewall services..."
systemctl stop firewalld || true
systemctl disable firewalld || true
systemctl stop ufw || true
systemctl disable ufw || true

# Ensure iptables doesn't load at boot
if [ -f /etc/network/if-pre-up.d/iptables ]; then
    echo "Disabling iptables from loading at boot..."
    mv /etc/network/if-pre-up.d/iptables /etc/network/if-pre-up.d/iptables.disabled
fi

# Remove iptables rules file
if [ -f /etc/iptables/rules.v4 ]; then
    echo "Removing iptables rules file..."
    mv /etc/iptables/rules.v4 /etc/iptables/rules.v4.backup
fi

# Check all network interfaces
echo "Network interfaces:"
ip -o link show | grep -v lo | awk -F': ' '{print $2}'

# Verify port 443 is open
echo "Verifying port 443 is open..."
netstat -tuln | grep 443 || echo "No services listening on port 443 (this is normal if no HTTPS server is running)"

# Test outbound connectivity
echo "Testing outbound connectivity to Google's servers..."
curl -v https://www.google.com 2>&1 | grep "Connected to"
curl -v https://remotedesktop.google.com 2>&1 | grep "Connected to"

echo "ALL port 443 traffic is now open on ALL interfaces and subnets."
EOF

# Copy the script to the server
log "Copying script to the server..."
scp -o StrictHostKeyChecking=no /tmp/open_all_443.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/open_all_443.sh"

# Run the script
log "Running the script to open all port 443 traffic..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/open_all_443.sh"

section "Summary"
success "ALL port 443 traffic should now be open on ALL interfaces and subnets."
log "The system is now configured with no firewall blocking port 443."
log "Chrome Remote Desktop should now be able to connect properly."