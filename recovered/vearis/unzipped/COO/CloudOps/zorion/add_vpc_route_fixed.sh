#!/bin/bash
# Script to manually add a route to the VPC routing table
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
LOG_FILE="add_vpc_route_fixed.log"

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

section "Getting Subnet Information"
log "Getting subnet information..."
SUBNET_ID=$(ibmcloud is subnets --output json | jq -r '.[] | select(.name=="nic8-subnet") | .id')

if [ -z "$SUBNET_ID" ]; then
  error "Failed to get subnet ID for nic8-subnet"
  exit 1
fi

success "Found subnet ID: $SUBNET_ID"

section "Getting Zone Information"
log "Getting zone information..."
ZONE=$(ibmcloud is subnet $SUBNET_ID --output json | jq -r '.zone.name')

if [ -z "$ZONE" ] || [ "$ZONE" == "null" ]; then
  error "Failed to get zone for subnet"
  exit 1
fi

success "Found zone: $ZONE"

section "Adding Internet Route to Routing Table"
log "Adding internet route (0.0.0.0/0) to routing table..."
log "Using hardcoded gateway IP: 10.240.8.1"
log "Using zone: $ZONE"

# Create a direct route to the internet via the gateway
ibmcloud is vpc-routing-table-route-create $VPC_ID $ROUTING_TABLE_ID --zone $ZONE --destination 0.0.0.0/0 --action deliver --next-hop 10.240.8.1 --name internet-route

if [ $? -ne 0 ]; then
  error "Failed to add internet route to routing table"
  exit 1
fi

success "Added internet route to routing table"

section "Verifying Routing Table Routes"
log "Verifying routing table routes..."
ROUTES=$(ibmcloud is vpc-routing-table-routes $VPC_ID $ROUTING_TABLE_ID --output json | jq -r '.[] | .name')

if [ -z "$ROUTES" ]; then
  error "No routes found in routing table"
  exit 1
fi

success "Verified routes in routing table: $ROUTES"

section "Testing Connectivity"
log "Testing connectivity to external destinations..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "ping -c 4 8.8.8.8 && ping -c 4 cloud.ibm.com"

section "Testing Load Balancing"
log "Testing load balancing..."
ssh -o StrictHostKeyChecking=no root@10.240.1.6 "for i in {1..5}; do for dest in 8.8.8.8 1.1.1.1 72.247.204.160 169.62.82.68 169.63.118.82; do iface=\$(ip route get \$dest | grep -oP \"dev \\K\\S+\"); echo \"Connection to \$dest uses interface \$iface\"; done; echo; done"

section "Summary"
success "Added internet route to routing table"
log "Gateway IP: 10.240.8.1"
log "Zone: $ZONE"
log "VPC ID: $VPC_ID"
log "Routing Table ID: $ROUTING_TABLE_ID"

echo -e "\nRoute addition completed. Check $LOG_FILE for details."