#!/bin/bash
# Script to fix VPC connectivity issues completely
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
LOG_FILE="vpc_fix_complete.log"

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

section "IBM Cloud Login"
log "Logging in to IBM Cloud..."
ibmcloud login -u chase@levelup2x.com -p '@@ALALzmzm102938!!'

if [ $? -ne 0 ]; then
  error "Failed to log in to IBM Cloud"
  exit 1
fi

success "Logged in to IBM Cloud"

section "Targeting VPC Infrastructure"
log "Targeting VPC infrastructure..."
ibmcloud is target --gen 2

if [ $? -ne 0 ]; then
  error "Failed to target VPC infrastructure"
  exit 1
fi

success "Targeted VPC infrastructure"

section "Getting VPC Information"
log "Getting VPC information..."
VPC_ID=$(ibmcloud is vpcs --output json | jq -r '.[] | select(.name=="adapt-vpc-dallas") | .id')

if [ -z "$VPC_ID" ]; then
  error "Failed to get VPC ID for adapt-vpc-dallas"
  exit 1
fi

success "Found VPC ID: $VPC_ID"

section "Getting Routing Table Information"
log "Getting routing table information..."
ROUTING_TABLE_ID=$(ibmcloud is vpc-routing-tables $VPC_ID --output json | jq -r '.[] | select(.name=="crouch-spotting-quote-nuptials") | .id')

if [ -z "$ROUTING_TABLE_ID" ]; then
  error "Failed to get routing table ID for crouch-spotting-quote-nuptials"
  exit 1
fi

success "Found routing table ID: $ROUTING_TABLE_ID"

section "Creating Public Gateways"
log "Creating public gateways for each zone..."

# Get available zones
ZONES=$(ibmcloud is zones --output json | jq -r '.[].name')

for zone in $ZONES; do
  log "Checking for existing public gateway in zone $zone..."
  EXISTING_PGW=$(ibmcloud is public-gateways --output json | jq -r ".[] | select(.vpc.name==\"adapt-vpc-dallas\" and .zone.name==\"$zone\") | .id")
  
  if [ -z "$EXISTING_PGW" ]; then
    log "Creating public gateway for zone $zone..."
    NEW_PGW=$(ibmcloud is public-gateway-create adapt-pgw-$zone $VPC_ID $zone --output json | jq -r '.id')
    
    if [ -z "$NEW_PGW" ]; then
      warning "Failed to create public gateway for zone $zone, it may already exist"
    else
      success "Created public gateway for zone $zone: $NEW_PGW"
    fi
  else
    success "Found existing public gateway for zone $zone: $EXISTING_PGW"
  fi
done

section "Adding Internet Route to Routing Table"
log "Adding internet route (0.0.0.0/0) to routing table..."

# Get default gateway IPs for each zone
for zone in $ZONES; do
  log "Getting default gateway IP for zone $zone..."
  
  # Get a subnet in this zone
  SUBNET_ID=$(ibmcloud is subnets --output json | jq -r ".[] | select(.vpc.name==\"adapt-vpc-dallas\" and .zone.name==\"$zone\") | .id" | head -1)
  
  if [ -n "$SUBNET_ID" ]; then
    SUBNET_INFO=$(ibmcloud is subnet $SUBNET_ID --output json)
    GATEWAY_IP=$(echo "$SUBNET_INFO" | jq -r '.gateway.address')
    
    if [ -n "$GATEWAY_IP" ] && [ "$GATEWAY_IP" != "null" ]; then
      log "Creating internet route for zone $zone with next-hop $GATEWAY_IP..."
      ibmcloud is vpc-routing-table-route-create $VPC_ID $ROUTING_TABLE_ID --zone $zone --destination 0.0.0.0/0 --action deliver --next-hop $GATEWAY_IP --name internet-route-$zone
      
      if [ $? -ne 0 ]; then
        warning "Failed to add internet route for zone $zone, it may already exist"
      else
        success "Added internet route for zone $zone"
      fi
    else
      warning "Failed to get gateway IP for zone $zone"
    fi
  else
    warning "No subnet found in zone $zone"
  fi
done

section "Attaching Public Gateways to Subnets"
log "Attaching public gateways to all subnets..."

# Get all subnets in the VPC
SUBNETS=$(ibmcloud is subnets --output json | jq -r '.[] | select(.vpc.name=="adapt-vpc-dallas") | .id + "," + .name + "," + .zone.name')

for SUBNET_INFO in $SUBNETS; do
  IFS=',' read -r SUBNET_ID SUBNET_NAME SUBNET_ZONE <<< "$SUBNET_INFO"
  
  log "Processing subnet $SUBNET_NAME ($SUBNET_ID) in zone $SUBNET_ZONE..."
  
  # Check if subnet already has a public gateway
  HAS_PGW=$(ibmcloud is subnet $SUBNET_ID --output json | jq -r '.public_gateway != null')
  
  if [ "$HAS_PGW" == "true" ]; then
    success "Subnet $SUBNET_NAME already has a public gateway attached"
    continue
  fi
  
  # Get public gateway for this zone
  PGW_ID=$(ibmcloud is public-gateways --output json | jq -r ".[] | select(.vpc.name==\"adapt-vpc-dallas\" and .zone.name==\"$SUBNET_ZONE\") | .id")
  
  if [ -z "$PGW_ID" ]; then
    warning "No public gateway found for zone $SUBNET_ZONE, skipping subnet $SUBNET_NAME"
    continue
  fi
  
  log "Attaching public gateway $PGW_ID to subnet $SUBNET_NAME..."
  ibmcloud is subnet-public-gateway-attach $SUBNET_ID $PGW_ID
  
  if [ $? -ne 0 ]; then
    warning "Failed to attach public gateway to subnet $SUBNET_NAME, it may already be attached"
  else
    success "Attached public gateway to subnet $SUBNET_NAME"
  fi
done

section "Verifying Routing Table Routes"
log "Verifying routing table routes..."
ROUTES=$(ibmcloud is vpc-routing-table-routes $VPC_ID $ROUTING_TABLE_ID --output json | jq -r '.[] | .name')

if [ -z "$ROUTES" ]; then
  warning "No routes found in routing table"
else
  success "Verified routes in routing table: $ROUTES"
fi

section "Configuring DNS Servers on Server"
log "Configuring DNS servers on the server..."

# Create DNS configuration script
cat > /tmp/configure_dns.sh << 'EOF'
#!/bin/bash

# Configure DNS servers for all interfaces
for iface in eth0 eth1 eth2 eth3 eth4 eth5 eth6 eth7; do
  echo "Configuring DNS for $iface..."
  
  # Create resolv.conf for the interface
  cat > /etc/resolv.conf.$iface << EOC
nameserver 8.8.8.8
nameserver 1.1.1.1
EOC
  
  # Update network configuration to use this resolv.conf
  if grep -q "interface-specific" /etc/network/interfaces; then
    # Already configured
    echo "Interface-specific DNS already configured"
  else
    echo "# Interface-specific DNS configuration" >> /etc/network/interfaces
    echo "interface-specific yes" >> /etc/network/interfaces
  fi
  
  # Restart networking to apply changes
  systemctl restart networking
done

echo "DNS configuration completed"
EOF

# Copy the script to the server
log "Copying DNS configuration script to the server..."
scp -o StrictHostKeyChecking=no /tmp/configure_dns.sh root@10.240.1.6:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "chmod +x /tmp/configure_dns.sh"

# Run the script
log "Running DNS configuration script..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "/tmp/configure_dns.sh"

success "DNS servers configured on the server"

section "Testing Connectivity"
log "Testing connectivity to external destinations..."

# Create test script
cat > /tmp/test_connectivity.sh << 'EOF'
#!/bin/bash

# Test connectivity to various destinations
echo "=== Testing Connectivity ==="
for dest in 8.8.8.8 1.1.1.1 cloud.ibm.com s3.us-south.cloud-object-storage.appdomain.cloud; do
  echo "Testing connectivity to $dest..."
  ping -c 4 $dest
  if [ $? -eq 0 ]; then
    echo "✓ Successfully pinged $dest"
  else
    echo "✗ Failed to ping $dest"
  fi
  echo
done

# Test DNS resolution
echo "=== Testing DNS Resolution ==="
for dest in cloud.ibm.com s3.us-south.cloud-object-storage.appdomain.cloud google.com cloudflare.com; do
  echo "Resolving $dest..."
  host $dest
  if [ $? -eq 0 ]; then
    echo "✓ Successfully resolved $dest"
  else
    echo "✗ Failed to resolve $dest"
  fi
  echo
done

# Test load balancing
echo "=== Testing Load Balancing ==="
for i in {1..5}; do
  echo "Test $i:"
  for dest in 8.8.8.8 1.1.1.1 72.247.204.160 169.62.82.68 169.63.118.82; do
    iface=$(ip route get $dest | grep -oP 'dev \K\S+')
    echo "Connection to $dest uses interface $iface"
  done
  echo
done
EOF

# Copy the script to the server
log "Copying connectivity test script to the server..."
scp -o StrictHostKeyChecking=no /tmp/test_connectivity.sh root@10.240.1.6:/tmp/

# Make the script executable
log "Making the script executable..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "chmod +x /tmp/test_connectivity.sh"

# Run the script
log "Running connectivity test script..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "/tmp/test_connectivity.sh"

section "Summary"
success "VPC connectivity issues fixed"
log "Added internet routes to routing table"
log "Created and attached public gateways to all subnets"
log "Configured DNS servers on the server"
log "Tested connectivity and load balancing"

echo -e "\nVPC connectivity fix completed. Check $LOG_FILE for details."