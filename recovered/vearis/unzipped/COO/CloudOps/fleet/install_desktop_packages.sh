#!/bin/bash
# Script to install VS Code, GNOME desktop, Chrome, Chrome Remote Desktop, and Slack
# Created: 2025-03-23
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Update package lists
print_section "Updating package lists"
apt-get update
if [ $? -eq 0 ]; then
    print_success "Package lists updated successfully."
else
    print_error "Failed to update package lists."
    exit 1
fi

# Install necessary dependencies
print_section "Installing dependencies"
apt-get install -y apt-transport-https curl wget gnupg software-properties-common
if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully."
else
    print_error "Failed to install dependencies."
    exit 1
fi

# Install GNOME desktop
print_section "Installing GNOME desktop"
apt-get install -y task-gnome-desktop
if [ $? -eq 0 ]; then
    print_success "GNOME desktop installed successfully."
else
    print_error "Failed to install GNOME desktop."
    exit 1
fi

# Install VS Code
print_section "Installing VS Code"
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg
apt-get update
apt-get install -y code
if [ $? -eq 0 ]; then
    print_success "VS Code installed successfully."
else
    print_error "Failed to install VS Code."
    exit 1
fi

# Install Google Chrome
print_section "Installing Google Chrome"
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update
apt-get install -y google-chrome-stable
if [ $? -eq 0 ]; then
    print_success "Google Chrome installed successfully."
else
    print_error "Failed to install Google Chrome."
    exit 1
fi

# Install Chrome Remote Desktop
print_section "Installing Chrome Remote Desktop"
curl -L -o chrome-remote-desktop_current_amd64.deb https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
apt-get install -y ./chrome-remote-desktop_current_amd64.deb
rm chrome-remote-desktop_current_amd64.deb
if [ $? -eq 0 ]; then
    print_success "Chrome Remote Desktop installed successfully."
else
    print_error "Failed to install Chrome Remote Desktop."
    exit 1
fi

# Install Slack
print_section "Installing Slack"
wget -q -O - https://packagecloud.io/slacktechnologies/slack/gpgkey | apt-key add -
sh -c 'echo "deb https://packagecloud.io/slacktechnologies/slack/debian/ jessie main" > /etc/apt/sources.list.d/slack.list'
apt-get update
apt-get install -y slack-desktop
if [ $? -eq 0 ]; then
    print_success "Slack installed successfully."
else
    print_error "Failed to install Slack."
    exit 1
fi

print_success "All packages installed successfully!"