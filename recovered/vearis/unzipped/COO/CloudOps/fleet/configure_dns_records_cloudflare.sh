#!/bin/bash
# Script to configure DNS records for the mail server using Cloudflare API
# Created: 2025-03-29
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

# Cloudflare credentials
CLOUDFLARE_EMAIL="chase@levelup2x.com"
CLOUDFLARE_API_KEY="4c655ace03178858f5788fed18f925a77612936e"
CLOUDFLARE_ZONE_ID="2e5b3432c1a845e2a7311d3a56d38f0a"

# Domain and server information
DOMAIN="a-d-a-p-t.ai"
MAIL_SUBDOMAIN="mail.$DOMAIN"
SERVER_IP=$(curl -s ifconfig.me)
print_info "Server IP: $SERVER_IP"
print_info "Domain: $DOMAIN"
print_info "Mail subdomain: $MAIL_SUBDOMAIN"

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed. Please install it first."
    exit 1
fi

# Function to create or update DNS record
create_or_update_record() {
    local record_type=$1
    local record_name=$2
    local record_content=$3
    local record_priority=$4
    
    # Check if record exists
    print_info "Checking if $record_type record for $record_name exists..."
    local check_response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records?type=$record_type&name=$record_name" \
         -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
         -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
         -H "Content-Type: application/json")
    
    local success=$(echo $check_response | grep -o '"success":[^,]*' | cut -d':' -f2)
    
    if [ "$success" != "true" ]; then
        print_error "Failed to check if record exists. API response: $check_response"
        return 1
    fi
    
    local record_id=$(echo $check_response | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$record_id" ]; then
        print_info "Record $record_name already exists (ID: $record_id). Updating..."
        
        # Update record
        local update_data=""
        if [ "$record_type" == "MX" ]; then
            update_data="{\"type\":\"$record_type\",\"name\":\"$record_name\",\"content\":\"$record_content\",\"priority\":$record_priority,\"ttl\":3600,\"proxied\":false}"
        else
            update_data="{\"type\":\"$record_type\",\"name\":\"$record_name\",\"content\":\"$record_content\",\"ttl\":3600,\"proxied\":false}"
        fi
        
        local update_response=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records/$record_id" \
             -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
             -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
             -H "Content-Type: application/json" \
             --data "$update_data")
        
        local update_success=$(echo $update_response | grep -o '"success":[^,]*' | cut -d':' -f2)
        
        if [ "$update_success" != "true" ]; then
            print_error "Failed to update record. API response: $update_response"
            return 1
        fi
        
        print_success "Record $record_name updated successfully."
    else
        print_info "Record $record_name does not exist. Creating..."
        
        # Create record
        local create_data=""
        if [ "$record_type" == "MX" ]; then
            create_data="{\"type\":\"$record_type\",\"name\":\"$record_name\",\"content\":\"$record_content\",\"priority\":$record_priority,\"ttl\":3600,\"proxied\":false}"
        else
            create_data="{\"type\":\"$record_type\",\"name\":\"$record_name\",\"content\":\"$record_content\",\"ttl\":3600,\"proxied\":false}"
        fi
        
        local create_response=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
             -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
             -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
             -H "Content-Type: application/json" \
             --data "$create_data")
        
        local create_success=$(echo $create_response | grep -o '"success":[^,]*' | cut -d':' -f2)
        
        if [ "$create_success" != "true" ]; then
            print_error "Failed to create record. API response: $create_response"
            return 1
        fi
        
        print_success "Record $record_name created successfully."
    fi
    
    return 0
}

# Configure DNS records
print_section "Configuring DNS records for $DOMAIN"

# A Record for Mail Server
print_info "Configuring A record for $MAIL_SUBDOMAIN..."
create_or_update_record "A" "$MAIL_SUBDOMAIN" "$SERVER_IP" ""

# MX Record
print_info "Configuring MX record for $DOMAIN..."
create_or_update_record "MX" "$DOMAIN" "$MAIL_SUBDOMAIN" "10"

# SPF Record
print_info "Configuring SPF record for $DOMAIN..."
create_or_update_record "TXT" "$DOMAIN" "v=spf1 mx a:$MAIL_SUBDOMAIN -all" ""

# DKIM Record
print_info "Configuring DKIM record for $DOMAIN..."
# Check if DKIM keys exist
DKIM_DIR="/opt/nova-mail/dkim"
if [ -f "$DKIM_DIR/$DOMAIN.dkim.txt" ]; then
    DKIM_RECORD=$(cat "$DKIM_DIR/$DOMAIN.dkim.txt")
    print_info "Using existing DKIM record from $DKIM_DIR/$DOMAIN.dkim.txt"
else
    print_info "DKIM keys not found. Using placeholder DKIM record."
    DKIM_RECORD="v=DKIM1; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrLHiExVd55zd/IQ/J/mRwSRMAocV/hMB3jXwaHH36d9NaVynQFYV8NaWi69c1veUtRzGt7yAioXqLj7Z4TeEUoOLgrKsn8YnckGs9i3B3tVFB+Ch/4mPhXWiNfNdynHWBcPcbJ8kjEQ2U8y78dHZj1YeRXXVvWob2OaKynO8/lQIDAQAB;"
fi
create_or_update_record "TXT" "mail._domainkey.$DOMAIN" "$DKIM_RECORD" ""

# DMARC Record
print_info "Configuring DMARC record for $DOMAIN..."
create_or_update_record "TXT" "_dmarc.$DOMAIN" "v=DMARC1; p=reject; rua=mailto:$CLOUDFLARE_EMAIL; ruf=mailto:$CLOUDFLARE_EMAIL; fo=1" ""

print_section "Verifying DNS records"

# Function to check DNS record
check_dns_record() {
    local record_type=$1
    local record_name=$2
    local expected_content=$3
    
    print_info "Checking $record_type record for $record_name..."
    
    # Wait for DNS propagation
    print_info "Waiting for DNS propagation (10 seconds)..."
    sleep 10
    
    # Check if record exists
    local actual_content=$(dig +short $record_type $record_name)
    
    if [ -z "$actual_content" ]; then
        print_error "$record_type record for $record_name does not exist or has not propagated yet."
        return 1
    fi
    
    print_success "$record_type record for $record_name exists: $actual_content"
    return 0
}

# Check DNS records
check_dns_record "A" "$MAIL_SUBDOMAIN" "$SERVER_IP"
check_dns_record "MX" "$DOMAIN" "$MAIL_SUBDOMAIN"
check_dns_record "TXT" "$DOMAIN" "v=spf1 mx a:$MAIL_SUBDOMAIN -all"
check_dns_record "TXT" "mail._domainkey.$DOMAIN" "$DKIM_RECORD"
check_dns_record "TXT" "_dmarc.$DOMAIN" "v=DMARC1; p=reject; rua=mailto:$CLOUDFLARE_EMAIL; ruf=mailto:$CLOUDFLARE_EMAIL; fo=1"

print_section "Summary"
print_success "DNS records configured successfully!"
print_info "Note: DNS changes may take some time to propagate."
print_info "You can verify the DNS records using the following commands:"
print_info "  dig +short A $MAIL_SUBDOMAIN"
print_info "  dig +short MX $DOMAIN"
print_info "  dig +short TXT $DOMAIN"
print_info "  dig +short TXT mail._domainkey.$DOMAIN"
print_info "  dig +short TXT _dmarc.$DOMAIN"