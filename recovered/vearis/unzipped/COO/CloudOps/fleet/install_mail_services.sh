#!/bin/bash
# Script to install and start mail services on the ethos server
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

# Check if running as root
if [ "$(id -u)" != "0" ]; then
    print_error "This script must be run as root."
    exit 1
fi

# Update package lists
print_section "Updating package lists"
apt-get update
if [ $? -eq 0 ]; then
    print_success "Package lists updated successfully."
else
    print_error "Failed to update package lists."
    exit 1
fi

# Install Nginx for ports 80 and 443
print_section "Installing and configuring Nginx"
apt-get install -y nginx
if [ $? -eq 0 ]; then
    print_success "Nginx installed successfully."
else
    print_error "Failed to install Nginx."
    exit 1
fi

# Start and enable Nginx
systemctl start nginx
systemctl enable nginx
if systemctl is-active --quiet nginx; then
    print_success "Nginx started and enabled successfully."
else
    print_error "Failed to start Nginx."
    exit 1
fi

# Install Dovecot for ports 143, 993, 110, 995, and 4190
print_section "Installing and configuring Dovecot"
apt-get install -y dovecot-core dovecot-imapd dovecot-pop3d dovecot-lmtpd dovecot-sieve
if [ $? -eq 0 ]; then
    print_success "Dovecot installed successfully."
else
    print_error "Failed to install Dovecot."
    exit 1
fi

# Configure Dovecot to listen on all interfaces
print_info "Configuring Dovecot to listen on all interfaces..."
sed -i 's/#listen = \*, ::/listen = \*, ::/' /etc/dovecot/dovecot.conf

# Start and enable Dovecot
systemctl start dovecot
systemctl enable dovecot
if systemctl is-active --quiet dovecot; then
    print_success "Dovecot started and enabled successfully."
else
    print_error "Failed to start Dovecot."
    exit 1
fi

# Install Postfix for ports 465 and 587
print_section "Installing and configuring Postfix"
DEBIAN_FRONTEND=noninteractive apt-get install -y postfix
if [ $? -eq 0 ]; then
    print_success "Postfix installed successfully."
else
    print_error "Failed to install Postfix."
    exit 1
fi

# Configure Postfix to listen on all interfaces
print_info "Configuring Postfix to listen on all interfaces..."
sed -i 's/inet_interfaces = loopback-only/inet_interfaces = all/' /etc/postfix/main.cf

# Start and enable Postfix
systemctl start postfix
systemctl enable postfix
if systemctl is-active --quiet postfix; then
    print_success "Postfix started and enabled successfully."
else
    print_error "Failed to start Postfix."
    exit 1
fi

# Check if all services are running
print_section "Checking service status"
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running."
else
    print_error "Nginx is not running."
fi

if systemctl is-active --quiet dovecot; then
    print_success "Dovecot is running."
else
    print_error "Dovecot is not running."
fi

if systemctl is-active --quiet postfix; then
    print_success "Postfix is running."
else
    print_error "Postfix is not running."
fi

# Check if ports are open
print_section "Checking mail server ports"
print_info "Running check_mail_ports.sh script..."
./check_mail_ports.sh

print_section "Summary"
print_info "Mail services have been installed and started."
print_info "The following services are now running:"
print_info "- Nginx (ports 80 and 443)"
print_info "- Dovecot (ports 143, 993, 110, 995, and 4190)"
print_info "- Postfix (ports 25, 465, and 587)"
print_info "- Exim4 (port 25)"
print_info "Note: Exim4 and Postfix both listen on port 25, which may cause conflicts."
print_info "You may want to disable one of them if you experience issues."