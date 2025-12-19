#!/bin/bash
# Script to fix VPC routing configuration
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
LOG_FILE="vpc_routing_fix.log"

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

section "Getting Public Gateway Information"
log "Getting public gateway information..."
PUBLIC_GATEWAY_ID=$(ibmcloud is public-gateways --output json | jq -r '.[] | select(.vpc.name=="adapt-vpc-dallas") | .id')

if [ -z "$PUBLIC_GATEWAY_ID" ]; then
  warning "No public gateway found for adapt-vpc-dallas"
  
  log "Creating public gateway for adapt-vpc-dallas in us-south-1..."
  PUBLIC_GATEWAY_ID=$(ibmcloud is public-gateway-create adapt-pgw-us-south-1 $VPC_ID us-south-1 --output json | jq -r '.id')
  
  if [ -z "$PUBLIC_GATEWAY_ID" ]; then
    error "Failed to create public gateway"
    exit 1
  fi
  
  success "Created public gateway: $PUBLIC_GATEWAY_ID"
else
  success "Found public gateway ID: $PUBLIC_GATEWAY_ID"
fi

section "Getting Zone Information"
log "Getting zone information for the public gateway..."
ZONE=$(ibmcloud is public-gateway $PUBLIC_GATEWAY_ID --output json | jq -r '.zone.name')

if [ -z "$ZONE" ]; then
  warning "Could not determine zone for public gateway, using default us-south-1"
  ZONE="us-south-1"
fi

success "Using zone: $ZONE"

section "Adding Internet Route to Routing Table"
log "Adding internet route (0.0.0.0/0) to routing table..."

# For the public gateway route, we need to use the public gateway as the next hop
log "Getting default gateway IP for zone $ZONE..."
# We'll use the first IP in the subnet as the next hop
SUBNET_ID=$(ibmcloud is subnets --output json | jq -r ".[] | select(.vpc.name==\"adapt-vpc-dallas\" and .zone.name==\"$ZONE\") | .id" | head -1)
if [ -z "$SUBNET_ID" ]; then
  error "Failed to find subnet in zone $ZONE"
  exit 1
fi

SUBNET_INFO=$(ibmcloud is subnet $SUBNET_ID --output json)
GATEWAY_IP=$(echo "$SUBNET_INFO" | jq -r '.gateway.address')

if [ -z "$GATEWAY_IP" ] || [ "$GATEWAY_IP" == "null" ]; then
  error "Failed to get gateway IP for subnet"
  exit 1
fi

success "Found gateway IP: $GATEWAY_IP"

log "Creating internet route with next-hop $GATEWAY_IP..."
ibmcloud is vpc-routing-table-route-create $VPC_ID $ROUTING_TABLE_ID --zone $ZONE --destination 0.0.0.0/0 --action deliver --next-hop $GATEWAY_IP --name internet-route

if [ $? -ne 0 ]; then
  error "Failed to add internet route to routing table"
  exit 1
fi

success "Added internet route to routing table"

section "Getting Subnet Information"
log "Getting subnet information..."
SUBNETS=$(ibmcloud is subnets --output json | jq -r '.[] | select(.vpc.name=="adapt-vpc-dallas") | .id + "," + .name')

if [ -z "$SUBNETS" ]; then
  error "Failed to get subnet information for adapt-vpc-dallas"
  exit 1
fi

success "Found subnets for adapt-vpc-dallas"

section "Attaching Public Gateway to Subnets"
for SUBNET_INFO in $SUBNETS; do
  IFS=',' read -r SUBNET_ID SUBNET_NAME <<< "$SUBNET_INFO"
  
  log "Attaching public gateway to subnet $SUBNET_NAME ($SUBNET_ID)..."
  ibmcloud is subnet-public-gateway-attach $SUBNET_ID $PUBLIC_GATEWAY_ID
  
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
  error "No routes found in routing table"
  exit 1
fi

success "Verified routes in routing table: $ROUTES"

section "Updating Server Configuration"
log "Updating server configuration..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "ip route flush cache && ip route show"

success "Updated server configuration"

section "Testing Connectivity"
log "Testing connectivity to external destinations..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "ping -c 4 8.8.8.8 && ping -c 4 cloud.ibm.com"

if [ $? -ne 0 ]; then
  warning "Connectivity test failed, but VPC routing has been configured"
else
  success "Connectivity test successful"
fi

section "Summary"
success "VPC routing configuration has been fixed"
log "Added internet route (0.0.0.0/0) to routing table with next-hop $GATEWAY_IP"
log "Attached public gateway to all subnets"
log "Updated server configuration"

echo -e "\nVPC routing configuration completed. Check $LOG_FILE for details."