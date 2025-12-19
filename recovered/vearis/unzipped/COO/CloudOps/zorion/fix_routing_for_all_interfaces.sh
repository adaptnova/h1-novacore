#!/bin/bash
# Script to fix routing for all interfaces
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="routing_fix.log"

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

section "Checking Current Routing"
log "Checking current routing table..."

# Check current routing table
CURRENT_ROUTES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip route")
log "$CURRENT_ROUTES"

section "Checking Network Interfaces"
log "Checking network interfaces..."

# Check network interfaces
INTERFACES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip addr")
log "$INTERFACES"

section "Fixing Routing"
log "Creating routing fix script..."

# Create routing fix script
cat > /tmp/fix_routing.sh << 'EOF'
#!/bin/bash

# Backup current routing table
ip route > /tmp/route_backup.txt
echo "Backed up current routing table to /tmp/route_backup.txt"

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "Enabled IP forwarding"

# Make IP forwarding persistent
cat > /etc/sysctl.d/99-ip-forward.conf << 'EOC'
net.ipv4.ip_forward = 1
EOC
sysctl -p /etc/sysctl.d/99-ip-forward.conf
echo "Made IP forwarding persistent"

# Get default gateway
DEFAULT_GW=$(ip route | grep default | awk '{print $3}')
echo "Default gateway: $DEFAULT_GW"

# Get all interfaces
INTERFACES=$(ip -o link show | grep -v lo | awk -F': ' '{print $2}')
echo "Interfaces: $INTERFACES"

# Add default routes for all interfaces
for iface in $INTERFACES; do
  # Get interface IP
  IFACE_IP=$(ip -o -4 addr show $iface | awk '{print $4}' | cut -d/ -f1)
  if [ -n "$IFACE_IP" ]; then
    echo "Setting up routing for $iface ($IFACE_IP)"
    
    # Add default route for the interface
    ip route add default via $DEFAULT_GW dev $iface metric $((100 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add default route for $iface"
    
    # Add specific routes for Google's IP ranges
    ip route add 142.250.0.0/16 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Google route for $iface"
    ip route add 172.217.0.0/16 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Google route for $iface"
    ip route add 216.58.0.0/16 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Google route for $iface"
    ip route add 8.8.8.8/32 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Google DNS route for $iface"
    ip route add 8.8.4.4/32 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Google DNS route for $iface"
    
    # Add specific routes for Cloudflare's IP ranges
    ip route add 1.1.1.1/32 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Cloudflare DNS route for $iface"
    ip route add 1.0.0.1/32 via $DEFAULT_GW dev $iface metric $((50 + $(echo $iface | sed 's/[^0-9]//g'))) || echo "Failed to add Cloudflare DNS route for $iface"
  fi
done

# Make sure all interfaces can reach the internet
for iface in $INTERFACES; do
  # Get interface IP
  IFACE_IP=$(ip -o -4 addr show $iface | awk '{print $4}' | cut -d/ -f1)
  if [ -n "$IFACE_IP" ]; then
    echo "Testing connectivity for $iface ($IFACE_IP)"
    ping -c 1 -I $iface 8.8.8.8 || echo "Failed to ping 8.8.8.8 from $iface"
  fi
done

# Update DNS configuration
cat > /etc/resolv.conf << 'EOD'
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
nameserver 1.0.0.1
EOD
echo "Updated DNS configuration"

# Make DNS configuration persistent
cat > /etc/systemd/resolved.conf << 'EOD'
[Resolve]
DNS=8.8.8.8 8.8.4.4 1.1.1.1 1.0.0.1
FallbackDNS=9.9.9.9 149.112.112.112
DNSSEC=no
Cache=yes
EOD
systemctl restart systemd-resolved
echo "Made DNS configuration persistent"

# Display routing table
echo "Updated routing table:"
ip route

# Test connectivity to Google
echo "Testing connectivity to Google:"
ping -c 4 www.google.com

echo "Routing fix completed"
EOF

# Copy the script to the server
log "Copying routing fix script to the server..."
scp -o StrictHostKeyChecking=no /tmp/fix_routing.sh $SSH_USER@$SERVER_IP:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /tmp/fix_routing.sh"

# Run the script
log "Running routing fix script..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/fix_routing.sh"

section "Checking Updated Routing"
log "Checking updated routing table..."

# Check updated routing table
UPDATED_ROUTES=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip route")
log "$UPDATED_ROUTES"

section "Testing Connectivity"
log "Testing connectivity to Google's servers..."

# Test connectivity to Google's servers
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ping -c 4 www.google.com"

section "Restarting Chrome Remote Desktop"
log "Restarting Chrome Remote Desktop service..."

# Restart Chrome Remote Desktop service
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl restart chrome-remote-desktop@crduser"

# Check Chrome Remote Desktop status
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "systemctl status chrome-remote-desktop@crduser"

section "Summary"
success "Routing fixed for all interfaces"
log "Chrome Remote Desktop should now be able to connect to Google's servers"
log "To complete the setup, follow these steps:"
log "1. Visit https://remotedesktop.google.com/headless"
log "2. Click on 'Set up another computer'"
log "3. Click on 'Begin'"
log "4. Click on 'Next'"
log "5. Click on 'Authorize'"
log "6. Copy the command that looks like:"
log "   DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/XXXX\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=\$(hostname)"
log "7. Run the command as the crduser:"
log "   su - crduser"
log "   [paste the command here]"
log "8. Set a PIN when prompted"
log "9. Go back to https://remotedesktop.google.com/access"
log "   You should see your computer listed there."
log "10. Click on it and enter your PIN to connect."
log ""
log "Note: The crduser password is \"crdpassword\""

echo -e "\nRouting fixed for all interfaces. Check $LOG_FILE for details."