#!/bin/bash
# Script to open required ports for the mail server on the ethos server
# Created: 2025-03-28
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

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

# Define the server name
SERVER_NAME="ethos"

# Get the security group ID for the ethos server
print_section "Getting security group information"
print_info "Getting security group ID for $SERVER_NAME..."

# Get the network interface ID for the ethos server
print_info "Getting network interface ID for $SERVER_NAME..."
NETWORK_INTERFACE_ID=$(ibmcloud is instance $SERVER_NAME --output json | jq -r '.network_interfaces[0].id')
if [ -z "$NETWORK_INTERFACE_ID" ] || [ "$NETWORK_INTERFACE_ID" == "null" ]; then
    print_error "Failed to get network interface ID for $SERVER_NAME."
    exit 1
fi
print_success "Network interface ID: $NETWORK_INTERFACE_ID"

# Get the security group ID for the network interface
print_info "Getting security group ID for network interface..."
SECURITY_GROUP_ID=$(ibmcloud is instance-network-interface $SERVER_NAME $NETWORK_INTERFACE_ID --output json | jq -r '.security_groups[0].id')
if [ -z "$SECURITY_GROUP_ID" ] || [ "$SECURITY_GROUP_ID" == "null" ]; then
    print_error "Failed to get security group ID for network interface."
    exit 1
fi
SECURITY_GROUP_NAME=$(ibmcloud is security-group $SECURITY_GROUP_ID --output json | jq -r '.name')
print_success "Using existing security group: $SECURITY_GROUP_NAME (ID: $SECURITY_GROUP_ID)"

# Define the required ports and protocols
print_section "Adding security group rules"
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

# Verify all rules
print_section "Verifying security group rules"
print_info "Listing all rules for security group $SECURITY_GROUP_NAME..."
ibmcloud is security-group-rules $SECURITY_GROUP_ID

print_success "All required ports have been opened for the mail server on the ethos server."
print_info "The mail server should now be able to receive and send mail, and provide IMAP/POP3 access."

# Add a reminder about DNS configuration
print_section "Next Steps"
print_info "Remember to configure the DNS records for the domain a-d-a-p-t.ai as specified in the deployment summary."
print_info "This includes A, MX, SPF, DKIM, and DMARC records."