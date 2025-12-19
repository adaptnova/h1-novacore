#!/bin/bash

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

print_section "Installing Google Chrome"

# Install Google Chrome
print_info "Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable
if [ $? -eq 0 ]; then
    print_success "Google Chrome installed successfully."
else
    print_error "Failed to install Google Chrome."
    exit 1
fi

print_section "Installing Chrome Remote Desktop"

# Install Chrome Remote Desktop
print_info "Installing Chrome Remote Desktop..."
curl -L -o /tmp/chrome-remote-desktop.deb https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
apt-get install -y /tmp/chrome-remote-desktop.deb
if [ $? -eq 0 ]; then
    print_success "Chrome Remote Desktop installed successfully."
else
    print_error "Failed to install Chrome Remote Desktop."
    exit 1
fi
rm -f /tmp/chrome-remote-desktop.deb

print_section "Setting up default desktop environment"

# Set GNOME as the default desktop environment
print_info "Setting GNOME as the default desktop environment..."
update-alternatives --set x-session-manager /usr/bin/gnome-session
print_success "GNOME set as the default desktop environment."

print_section "Summary"
print_success "Google Chrome and Chrome Remote Desktop have been installed."
print_info "GNOME has been set as the default desktop environment."
print_info "To complete the setup, Chase needs to:"
print_info "1. Log in to the adapt server as user 'x'"
print_info "2. Open Google Chrome and log in to their Google account"
print_info "3. Visit https://remotedesktop.google.com/access"
print_info "4. Click on 'Set up remote access'"
print_info "5. Follow the instructions to set up Chrome Remote Desktop"
