#!/bin/bash
# Script to completely remove all Xfce-related packages
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

print_section "Removing all Xfce-related packages"

# Copy the script to the adapt server
print_info "Copying script to adapt server..."
cat > remove_all_xfce_remote.sh << 'EOF'
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

print_section "Removing all Xfce-related packages"

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
    apt-get clean
    print_success "All Xfce-related packages removed."
else
    print_info "No Xfce-related packages found."
fi

# Make sure GNOME is installed
print_info "Making sure GNOME is installed..."
apt-get install -y gnome-shell gnome-session gnome-terminal
print_success "GNOME installation verified."

# Update Chrome Remote Desktop session file
print_info "Updating Chrome Remote Desktop session file..."
cat > /home/x/.chrome-remote-desktop-session << 'EOL'
#!/bin/bash
export GNOME_SHELL_SESSION_MODE=ubuntu
export XDG_CURRENT_DESKTOP=ubuntu:GNOME
export XDG_CONFIG_DIRS=/etc/xdg/xdg-ubuntu:/etc/xdg
exec /usr/bin/gnome-session
EOL
chmod +x /home/x/.chrome-remote-desktop-session
chown x:x /home/x/.chrome-remote-desktop-session
print_success "Chrome Remote Desktop session file updated."

# Restart Chrome Remote Desktop service
print_info "Restarting Chrome Remote Desktop service..."
systemctl restart chrome-remote-desktop@x.service
print_success "Chrome Remote Desktop service restarted."

print_section "Summary"
print_success "All Xfce-related packages have been removed."
print_info "GNOME is now the only desktop environment installed."
print_info "Chrome Remote Desktop has been configured to use GNOME."
print_info "You may need to reboot the server for all changes to take effect:"
print_info "  sudo reboot"
EOF

chmod +x remove_all_xfce_remote.sh
scp -i /home/x/.ssh/ibm-admin_rsa remove_all_xfce_remote.sh root@10.240.1.6:/root/
if [ $? -eq 0 ]; then
    print_success "Script copied successfully."
else
    print_error "Failed to copy script to adapt server."
    exit 1
fi

# Execute the script on the adapt server
print_info "Executing script on adapt server..."
ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.1.6 "chmod +x /root/remove_all_xfce_remote.sh && /root/remove_all_xfce_remote.sh"
if [ $? -eq 0 ]; then
    print_success "Script executed successfully."
else
    print_error "Failed to execute script on adapt server."
    exit 1
fi

print_section "Summary"
print_success "All Xfce-related packages have been removed from adapt server."
print_info "GNOME is now the only desktop environment installed."
print_info "Chrome Remote Desktop has been configured to use GNOME."
print_info "You may need to reboot the server for all changes to take effect:"
print_info "  ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.1.6 \"reboot\""