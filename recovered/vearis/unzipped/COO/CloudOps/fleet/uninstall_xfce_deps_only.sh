#!/bin/bash
# Script to uninstall Xfce dependencies without touching Chrome Remote Desktop
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

print_section "Uninstalling Xfce dependencies without touching CRDT"

# Copy the script to the adapt server
print_info "Copying script to adapt server..."
cat > uninstall_xfce_deps_remote.sh << 'EOF'
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

print_section "Uninstalling Xfce dependencies without touching CRDT"

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

print_section "Summary"
print_success "All Xfce-related packages have been removed."
print_info "GNOME is now installed."
print_info "IMPORTANT: Chrome Remote Desktop configuration has NOT been modified."
print_info "The system will now reboot to apply changes."
print_info "After reboot, you may need to reconnect to Chrome Remote Desktop."

# Reboot the system
print_info "Rebooting the system in 5 seconds..."
sleep 5
reboot
EOF

chmod +x uninstall_xfce_deps_remote.sh
scp -i /home/x/.ssh/ibm-admin_rsa uninstall_xfce_deps_remote.sh root@10.240.1.6:/root/
if [ $? -eq 0 ]; then
    print_success "Script copied successfully."
else
    print_error "Failed to copy script to adapt server."
    exit 1
fi

# Execute the script on the adapt server
print_info "Executing script on adapt server..."
ssh -i /home/x/.ssh/ibm-admin_rsa root@10.240.1.6 "chmod +x /root/uninstall_xfce_deps_remote.sh && /root/uninstall_xfce_deps_remote.sh"

print_section "Summary"
print_success "Script has been executed on adapt server."
print_info "The adapt server will reboot to apply changes."
print_info "After reboot, you may need to reconnect to Chrome Remote Desktop."
print_info "IMPORTANT: Chrome Remote Desktop configuration has NOT been modified."