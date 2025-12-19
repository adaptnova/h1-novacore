#!/bin/bash
# Script to configure DNS records for the mail server on a-d-a-p-t.ai domain
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

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    print_error "jq is not installed. Installing..."
    apt-get update && apt-get install -y jq
    if [ $? -eq 0 ]; then
        print_success "jq installed successfully."
    else
        print_error "Failed to install jq. Please install it manually and run this script again."
        exit 1
    fi
fi

# Check if dig is installed
if ! command -v dig &> /dev/null; then
    print_error "dig is not installed. Installing..."
    apt-get update && apt-get install -y dnsutils
    if [ $? -eq 0 ]; then
        print_success "dig installed successfully."
    else
        print_error "Failed to install dig. Please install it manually and run this script again."
        exit 1
    fi
fi

# Load environment variables
if [ -f .env ]; then
    print_info "Loading environment variables from .env file..."
    source .env
else
    print_error ".env file not found. Please create it with the required Cloudflare credentials."
    exit 1
fi

# Check if Cloudflare credentials are set
if [ -z "$CLOUDFLARE_EMAIL" ] || [ -z "$CLOUDFLARE_API_KEY" ] || [ -z "$CLOUDFLARE_ZONE_ID" ]; then
    print_error "Cloudflare credentials not found in .env file."
    print_info "Please add the following to your .env file:"
    echo "CLOUDFLARE_EMAIL=your_cloudflare_email"
    echo "CLOUDFLARE_API_KEY=your_cloudflare_api_key"
    echo "CLOUDFLARE_ZONE_ID=your_cloudflare_zone_id"
    
    # Try to extract email from existing variables
    if grep -q "ATLASSIAN_EMAIL" .env; then
        EMAIL=$(grep "ATLASSIAN_EMAIL" .env | cut -d'=' -f2)
        print_info "Found email: $EMAIL. You can use this for CLOUDFLARE_EMAIL."
    fi
    
    exit 1
fi

# Domain and server information
DOMAIN="a-d-a-p-t.ai"
MAIL_SUBDOMAIN="mail.$DOMAIN"
SERVER_IP=$(curl -s ifconfig.me)
print_info "Server IP: $SERVER_IP"

# Generate DKIM keys if they don't exist
print_section "Generating DKIM keys"
if [ ! -f /etc/opendkim/keys/$DOMAIN/mail.private ]; then
    print_info "Generating DKIM keys for $DOMAIN..."
    mkdir -p /etc/opendkim/keys/$DOMAIN
    opendkim-genkey -d $DOMAIN -s mail -D /etc/opendkim/keys/$DOMAIN
    if [ $? -eq 0 ]; then
        print_success "DKIM keys generated successfully."
    else
        print_error "Failed to generate DKIM keys."
        exit 1
    fi
else
    print_info "DKIM keys already exist."
fi

# Get DKIM public key
DKIM_PUBLIC_KEY=$(cat /etc/opendkim/keys/$DOMAIN/mail.txt | grep -o '".*"' | tr -d '"' | tr -d '\n')
if [ -z "$DKIM_PUBLIC_KEY" ]; then
    print_error "Failed to get DKIM public key."
    exit 1
fi
print_info "DKIM public key: $DKIM_PUBLIC_KEY"

# Configure DNS records using Cloudflare API
print_section "Configuring DNS records"

# Function to create or update DNS record
create_or_update_record() {
    local type=$1
    local name=$2
    local content=$3
    local ttl=${4:-3600}
    local priority=${5:-10}
    
    print_info "Checking if $type record for $name exists..."
    
    # Check if record exists
    RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records?type=$type&name=$name" \
        -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
        -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
        -H "Content-Type: application/json" | jq -r '.result[0].id')
    
    if [ "$RECORD_ID" != "null" ] && [ -n "$RECORD_ID" ]; then
        print_info "$type record for $name exists. Updating..."
        
        # Update existing record
        RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records/$RECORD_ID" \
            -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
            -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"ttl\":$ttl,\"priority\":$priority}")
        
        SUCCESS=$(echo $RESPONSE | jq -r '.success')
        if [ "$SUCCESS" = "true" ]; then
            print_success "$type record for $name updated successfully."
        else
            print_error "Failed to update $type record for $name."
            echo $RESPONSE | jq '.'
        fi
    else
        print_info "$type record for $name does not exist. Creating..."
        
        # Create new record
        RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
            -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
            -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"ttl\":$ttl,\"priority\":$priority}")
        
        SUCCESS=$(echo $RESPONSE | jq -r '.success')
        if [ "$SUCCESS" = "true" ]; then
            print_success "$type record for $name created successfully."
        else
            print_error "Failed to create $type record for $name."
            echo $RESPONSE | jq '.'
        fi
    fi
}

# Create A record for mail subdomain
print_info "Creating A record for $MAIL_SUBDOMAIN..."
create_or_update_record "A" "$MAIL_SUBDOMAIN" "$SERVER_IP"

# Create MX record
print_info "Creating MX record for $DOMAIN..."
create_or_update_record "MX" "$DOMAIN" "$MAIL_SUBDOMAIN"

# Create SPF record
print_info "Creating SPF record for $DOMAIN..."
create_or_update_record "TXT" "$DOMAIN" "v=spf1 mx a:$MAIL_SUBDOMAIN -all"

# Create DKIM record
print_info "Creating DKIM record for mail._domainkey.$DOMAIN..."
create_or_update_record "TXT" "mail._domainkey.$DOMAIN" "v=DKIM1; k=rsa; p=$DKIM_PUBLIC_KEY"

# Create DMARC record
print_info "Creating DMARC record for _dmarc.$DOMAIN..."
create_or_update_record "TXT" "_dmarc.$DOMAIN" "v=DMARC1; p=reject; rua=mailto:chase@levelup2x.com; ruf=mailto:chase@levelup2x.com; fo=1"

# Verify DNS records
print_section "Verifying DNS records"

# Function to verify DNS record
verify_dns_record() {
    local type=$1
    local name=$2
    local expected=$3
    
    print_info "Verifying $type record for $name..."
    
    # Wait for DNS propagation
    print_info "Waiting for DNS propagation (10 seconds)..."
    sleep 10
    
    # Check DNS record
    if [ "$type" = "MX" ]; then
        RECORD=$(dig +short MX $name | grep -o "$expected")
    else
        RECORD=$(dig +short $type $name | tr -d '"' | grep -o "$expected")
    fi
    
    if [ -n "$RECORD" ]; then
        print_success "$type record for $name is configured correctly."
    else
        print_error "$type record for $name is not configured correctly."
        print_info "Expected: $expected"
        print_info "Actual: $(dig +short $type $name)"
    fi
}

# Verify A record
verify_dns_record "A" "$MAIL_SUBDOMAIN" "$SERVER_IP"

# Verify MX record
verify_dns_record "MX" "$DOMAIN" "$MAIL_SUBDOMAIN"

# Verify SPF record
verify_dns_record "TXT" "$DOMAIN" "v=spf1 mx a:$MAIL_SUBDOMAIN -all"

# Verify DKIM record
verify_dns_record "TXT" "mail._domainkey.$DOMAIN" "v=DKIM1; k=rsa; p=$DKIM_PUBLIC_KEY"

# Verify DMARC record
verify_dns_record "TXT" "_dmarc.$DOMAIN" "v=DMARC1; p=reject"

print_section "Summary"
print_success "DNS records for the mail server have been configured."
print_info "The following DNS records have been created or updated:"
print_info "- A record for $MAIL_SUBDOMAIN pointing to $SERVER_IP"
print_info "- MX record for $DOMAIN pointing to $MAIL_SUBDOMAIN"
print_info "- SPF record for $DOMAIN"
print_info "- DKIM record for mail._domainkey.$DOMAIN"
print_info "- DMARC record for _dmarc.$DOMAIN"
print_info "It may take some time for the DNS records to propagate."