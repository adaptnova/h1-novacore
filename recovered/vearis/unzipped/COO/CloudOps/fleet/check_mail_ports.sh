#!/bin/bash
# Script to check if mail server ports are open
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

# Check if nc (netcat) is installed
if ! command -v nc &> /dev/null; then
    print_error "nc (netcat) is not installed. Installing..."
    apt-get update && apt-get install -y netcat-openbsd
    if [ $? -eq 0 ]; then
        print_success "nc installed successfully."
    else
        print_error "Failed to install nc. Please install it manually and run this script again."
        exit 1
    fi
fi

# Server to check
SERVER_IP=$(curl -s ifconfig.me)
print_info "Server IP: $SERVER_IP"

# Ports to check
PORTS=(
    "25:SMTP - Receiving mail from other mail servers"
    "465:SMTPS - Secure SMTP (legacy)"
    "587:Submission - Sending mail (with authentication)"
    "143:IMAP - Mail access (unencrypted)"
    "993:IMAPS - Secure IMAP mail access"
    "110:POP3 - Mail access (unencrypted)"
    "995:POP3S - Secure POP3 mail access"
    "4190:Sieve - Mail filtering"
    "80:HTTP - Web access and Let's Encrypt verification"
    "443:HTTPS - Secure web access"
)

print_section "Checking mail server ports"

# Check if ports are open
for PORT_INFO in "${PORTS[@]}"; do
    PORT=$(echo $PORT_INFO | cut -d':' -f1)
    DESCRIPTION=$(echo $PORT_INFO | cut -d':' -f2-)
    
    print_info "Checking port $PORT ($DESCRIPTION)..."
    
    # Check if port is open
    nc -z -v -w 5 $SERVER_IP $PORT 2>&1 | grep -q "succeeded"
    if [ $? -eq 0 ]; then
        print_success "Port $PORT is open."
    else
        print_error "Port $PORT is closed."
        
        # Check if the port is open locally
        nc -z -v -w 5 localhost $PORT 2>&1 | grep -q "succeeded"
        if [ $? -eq 0 ]; then
            print_info "Port $PORT is open locally but not externally. This may be due to a firewall."
        else
            print_info "Port $PORT is closed locally. No service is listening on this port."
        fi
    fi
done

print_section "Summary"

# Count open and closed ports
OPEN_PORTS=0
CLOSED_PORTS=0

for PORT_INFO in "${PORTS[@]}"; do
    PORT=$(echo $PORT_INFO | cut -d':' -f1)
    
    nc -z -v -w 5 $SERVER_IP $PORT 2>&1 | grep -q "succeeded"
    if [ $? -eq 0 ]; then
        OPEN_PORTS=$((OPEN_PORTS + 1))
    else
        CLOSED_PORTS=$((CLOSED_PORTS + 1))
    fi
done

print_info "Open ports: $OPEN_PORTS"
print_info "Closed ports: $CLOSED_PORTS"

if [ $CLOSED_PORTS -eq 0 ]; then
    print_success "All mail server ports are open."
else
    print_error "Some mail server ports are closed. Please check the security group rules."
    print_info "You can run the open_mail_server_ports_ethos.sh script to open the required ports."
fi

# Check if any mail server is running
print_section "Checking mail server status"

# Check if Postfix is running
if systemctl is-active --quiet postfix; then
    print_success "Postfix mail server is running."
else
    print_info "Postfix mail server is not running."
fi

# Check if Dovecot is running
if systemctl is-active --quiet dovecot; then
    print_success "Dovecot IMAP/POP3 server is running."
else
    print_info "Dovecot IMAP/POP3 server is not running."
fi

# Check if Nginx is running
if systemctl is-active --quiet nginx; then
    print_success "Nginx web server is running."
else
    print_info "Nginx web server is not running."
fi

print_section "Next Steps"

if [ $CLOSED_PORTS -gt 0 ]; then
    print_info "1. Run the open_mail_server_ports_ethos.sh script to open the required ports."
fi

if ! systemctl is-active --quiet postfix || ! systemctl is-active --quiet dovecot || ! systemctl is-active --quiet nginx; then
    print_info "2. Install and configure the mail server software (Postfix, Dovecot, Nginx)."
fi

print_info "3. Configure DNS records for the mail server using the configure_dns_records.sh script."
print_info "4. Test the mail server functionality."