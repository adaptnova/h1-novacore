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

print_section "Uninstalling Xfce, Chrome, and Chrome Remote Desktop"

# Uninstall Xfce
print_info "Uninstalling Xfce..."
apt-get remove --purge -y xfce4 xfce4-goodies
apt-get autoremove -y

# Get a list of all Xfce-related packages
print_info "Getting a list of all Xfce-related packages..."
XFCE_PACKAGES=$(dpkg -l | grep -i xfce | awk '{print $2}')
THUNAR_PACKAGES=$(dpkg -l | grep -i thunar | awk '{print $2}')
EXOPACKAGES=$(dpkg -l | grep -i exo | awk '{print $2}')
GARCON_PACKAGES=$(dpkg -l | grep -i garcon | awk '{print $2}')

# Combine all packages
ALL_PACKAGES="$XFCE_PACKAGES $THUNAR_PACKAGES $EXOPACKAGES $GARCON_PACKAGES"

# Remove all Xfce-related packages
if [ -n "$ALL_PACKAGES" ]; then
    print_info "Removing the following packages:"
    echo "$ALL_PACKAGES"
    apt-get remove --purge -y $ALL_PACKAGES
    apt-get autoremove -y
    print_success "All Xfce-related packages removed."
else
    print_info "No Xfce-related packages found."
fi

# Uninstall Chrome Remote Desktop
print_info "Uninstalling Chrome Remote Desktop..."
apt-get remove --purge -y chrome-remote-desktop
rm -rf /opt/google/chrome-remote-desktop
rm -rf /home/x/.config/chrome-remote-desktop
rm -f /home/x/.chrome-remote-desktop-session
print_success "Chrome Remote Desktop uninstalled."

# Uninstall Google Chrome
print_info "Uninstalling Google Chrome..."
apt-get remove --purge -y google-chrome-stable
rm -rf /opt/google/chrome
rm -rf /home/x/.config/google-chrome
print_success "Google Chrome uninstalled."

# Clean up
print_info "Cleaning up..."
apt-get autoremove -y
apt-get clean
print_success "Cleanup completed."

print_section "Installing GNOME"

# Install GNOME
print_info "Installing GNOME..."
apt-get update
apt-get install -y gnome-shell gnome-session gnome-terminal
print_success "GNOME installed."

print_section "Installing Google Chrome"

# Install Google Chrome
print_info "Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable
print_success "Google Chrome installed."

print_section "Installing Chrome Remote Desktop"

# Install Chrome Remote Desktop
print_info "Installing Chrome Remote Desktop..."
curl -L -o /tmp/chrome-remote-desktop.deb https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
apt-get install -y /tmp/chrome-remote-desktop.deb
rm -f /tmp/chrome-remote-desktop.deb
print_success "Chrome Remote Desktop installed."

print_section "Setting up default desktop environment"

# Set GNOME as the default desktop environment
print_info "Setting GNOME as the default desktop environment..."
update-alternatives --set x-session-manager /usr/bin/gnome-session
print_success "GNOME set as the default desktop environment."

print_section "Summary"
print_success "Xfce, Chrome, and Chrome Remote Desktop have been uninstalled and reinstalled."
print_info "GNOME has been installed and set as the default desktop environment."
print_info "To complete the setup, Chase needs to:"
print_info "1. Log in to the adapt server as user 'x'"
print_info "2. Open Google Chrome and log in to their Google account"
print_info "3. Visit https://remotedesktop.google.com/access"
print_info "4. Click on 'Set up remote access'"
print_info "5. Follow the instructions to set up Chrome Remote Desktop"
print_info "The system will now reboot to apply changes."

# Reboot the system
print_info "Rebooting the system in 5 seconds..."
sleep 5
reboot
