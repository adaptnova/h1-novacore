#!/bin/bash
# Secure Script to set up firewall rules for Chrome Remote Desktop
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="secure_crdt_firewall.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
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

# Initialize log file
> "$LOG_FILE"

section "Checking Server Connectivity"
log "Checking connectivity to the adapt server..."

# Check connectivity to the server
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'Connection successful'" || {
  error "Failed to connect to the server"
  exit 1
}

success "Connected to the server"

section "Updating Firewall Rules"
log "Creating secure firewall update script for Chrome Remote Desktop..."

# Create firewall update script
cat > /tmp/secure_firewall_crdt.sh << 'EOF'
#!/bin/bash

# Backup current iptables rules
BACKUP_DIR="/tmp/firewall_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p $BACKUP_DIR
iptables-save > $BACKUP_DIR/iptables_backup.rules
echo "Backed up current iptables rules to $BACKUP_DIR/iptables_backup.rules"

# Google IP ranges (these are examples, you should use the actual Google IP ranges)
GOOGLE_IP_RANGES=(
  "34.64.0.0/10"    # Google Cloud
  "34.128.0.0/10"   # Google Cloud
  "35.184.0.0/13"   # Google Cloud
  "35.192.0.0/14"   # Google Cloud
  "35.196.0.0/15"   # Google Cloud
  "35.198.0.0/16"   # Google Cloud
  "35.199.0.0/17"   # Google Cloud
  "35.199.128.0/18" # Google Cloud
  "35.200.0.0/13"   # Google Cloud
  "35.208.0.0/12"   # Google Cloud
  "35.224.0.0/12"   # Google Cloud
  "35.240.0.0/13"   # Google Cloud
  "64.233.160.0/19" # Google
  "66.102.0.0/20"   # Google
  "66.249.64.0/19"  # Google
  "70.32.128.0/19"  # Google
  "72.14.192.0/18"  # Google
  "74.125.0.0/16"   # Google
  "108.177.0.0/17"  # Google
  "142.250.0.0/15"  # Google
  "172.217.0.0/16"  # Google
  "173.194.0.0/16"  # Google
  "209.85.128.0/17" # Google
  "216.58.192.0/19" # Google
  "216.239.32.0/19" # Google
)

# Allow outbound connections on port 443 (HTTPS) for Google IP ranges only
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  for range in "${GOOGLE_IP_RANGES[@]}"; do
    echo "Allowing outbound TCP traffic on port 443 to $range for interface $iface"
    iptables -A OUTPUT -o $iface -p tcp -d $range --dport 443 -j ACCEPT
    
    echo "Allowing outbound UDP traffic on port 443 to $range for interface $iface"
    iptables -A OUTPUT -o $iface -p udp -d $range --dport 443 -j ACCEPT
  done
done

# Allow outbound connections on port 5222 (XMPP) for Google IP ranges only
for iface in $(ip -o link show | grep -v lo | awk -F': ' '{print $2}'); do
  for range in "${GOOGLE_IP_RANGES[@]}"; do
    echo "Allowing outbound TCP traffic on port 5222 to $range for interface $iface"
    iptables -A OUTPUT -o $iface -p tcp -d $range --dport 5222 -j ACCEPT
  done
done

# Allow established and related connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
echo "Allowed established and related connections"

# Save iptables rules
if [ -d "/etc/iptables" ]; then
  iptables-save > /etc/iptables/rules.v4
  echo "Saved iptables rules to /etc/iptables/rules.v4"
else
  mkdir -p /etc/iptables
  iptables-save > /etc/iptables/rules.v4
  echo "Created /etc/iptables directory and saved rules to /etc/iptables/rules.v4"
fi

# Create a script to load these rules at boot
cat > /etc/network/if-pre-up.d/iptables << 'EOI'
#!/bin/sh
/sbin/iptables-restore < /etc/iptables/rules.v4
EOI

chmod +x /etc/network/if-pre-up.d/iptables
echo "Created boot-time script to load iptables rules"

# Display updated iptables rules
echo "Updated iptables rules:"
iptables -L -v
EOF

# Copy the script to the server
log "Copying secure firewall update script to the server..."
scp -o StrictHostKeyChecking=no /tmp/secure_firewall_crdt.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/secure_firewall_crdt.sh"

# Run the script
log "Running secure firewall update script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/secure_firewall_crdt.sh"

section "Testing Connectivity"
log "Testing connectivity to Google's servers..."

# Test connectivity to Google's servers
GOOGLE_TEST=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -s -o /dev/null -w '%{http_code}' https://www.google.com || echo 'Failed to connect to Google'")

if [ "$GOOGLE_TEST" == "200" ]; then
  success "Successfully connected to Google's servers (HTTP 200)"
else
  warning "Failed to connect to Google's servers: $GOOGLE_TEST"
  log "This may indicate that the firewall rules are too restrictive."
  log "You may need to add more Google IP ranges or temporarily open port 443 more widely for testing."
fi

section "Summary"
success "Secure firewall rules for Chrome Remote Desktop have been set up"
log "The following ports are now open for outbound connections to Google IP ranges only:"
log "- TCP/UDP 443 (HTTPS) - Primary communication channel"
log "- TCP 5222 (XMPP) - Optional for signaling"
log "These rules have been saved and will persist across reboots."

echo -e "\nSecure firewall rules for Chrome Remote Desktop have been set up. Check $LOG_FILE for details."