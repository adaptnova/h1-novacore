#!/bin/bash
# Script to set up Chrome Remote Desktop on the adapt server
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

print_section "Setting up Chrome Remote Desktop on adapt server"

# Check if Chrome Remote Desktop is installed
if ! dpkg -l | grep -q chrome-remote-desktop; then
    print_info "Chrome Remote Desktop is not installed. Installing..."
    apt-get update
    apt-get install -y chrome-remote-desktop
    if [ $? -eq 0 ]; then
        print_success "Chrome Remote Desktop installed successfully."
    else
        print_error "Failed to install Chrome Remote Desktop."
        exit 1
    fi
else
    print_info "Chrome Remote Desktop is already installed."
fi

# Check if Google Chrome is installed
if ! dpkg -l | grep -q google-chrome-stable; then
    print_info "Google Chrome is not installed. Installing..."
    apt-get update
    apt-get install -y google-chrome-stable
    if [ $? -eq 0 ]; then
        print_success "Google Chrome installed successfully."
    else
        print_error "Failed to install Google Chrome."
        exit 1
    fi
else
    print_info "Google Chrome is already installed."
fi

# Check if a desktop environment is installed
if ! dpkg -l | grep -q "gnome\|kde\|xfce\|lxde\|mate\|cinnamon"; then
    print_info "No desktop environment found. Installing GNOME..."
    apt-get update
    apt-get install -y gnome-shell gnome-session gnome-terminal
    if [ $? -eq 0 ]; then
        print_success "GNOME installed successfully."
    else
        print_error "Failed to install GNOME."
        exit 1
    fi
else
    print_info "Desktop environment is already installed."
fi

# Create Chrome Remote Desktop session file for user x
print_info "Creating Chrome Remote Desktop session file for user x..."
cat > /home/x/.chrome-remote-desktop-session << EOF
#!/bin/bash
exec /usr/bin/xfce4-session
EOF
chmod +x /home/x/.chrome-remote-desktop-session
chown x:x /home/x/.chrome-remote-desktop-session
print_success "Chrome Remote Desktop session file created."

# Create Chrome Remote Desktop config directory for user x
print_info "Creating Chrome Remote Desktop config directory for user x..."
mkdir -p /home/x/.config/chrome-remote-desktop
chown -R x:x /home/x/.config/chrome-remote-desktop
print_success "Chrome Remote Desktop config directory created."

# Create Chrome Remote Desktop config file for user x
print_info "Creating Chrome Remote Desktop config file for user x..."
cat > /home/x/.config/chrome-remote-desktop/config << EOF
CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
CHROME_REMOTE_DESKTOP_HOST_EXTRA_PARAMS=
EOF
chown x:x /home/x/.config/chrome-remote-desktop/config
print_success "Chrome Remote Desktop config file created."

# Unmask Chrome Remote Desktop service
print_info "Unmasking Chrome Remote Desktop service..."
systemctl unmask chrome-remote-desktop.service
print_success "Chrome Remote Desktop service unmasked."

print_section "Next Steps"
print_info "To complete the setup, the user needs to:"
print_info "1. Log in to the adapt server as user 'x'"
print_info "2. Open Google Chrome and log in to their Google account"
print_info "3. Visit https://remotedesktop.google.com/access"
print_info "4. Click on 'Set up remote access'"
print_info "5. Follow the instructions to set up Chrome Remote Desktop"
print_info "6. After setup is complete, the Chrome Remote Desktop service will start automatically"

print_section "Troubleshooting"
print_info "If you encounter any issues, check the following:"
print_info "1. Make sure the user has logged in to their Google account in Chrome"
print_info "2. Check if the host configuration file exists:"
print_info "   ls -la /home/x/.config/chrome-remote-desktop/host#*.json"
print_info "3. Check the Chrome Remote Desktop service status:"
print_info "   systemctl status chrome-remote-desktop@x.service"
print_info "4. Check the Chrome Remote Desktop logs:"
print_info "   journalctl -u chrome-remote-desktop@x.service"

print_section "Summary"
print_success "Chrome Remote Desktop setup script completed."
print_info "Follow the 'Next Steps' section to complete the setup."