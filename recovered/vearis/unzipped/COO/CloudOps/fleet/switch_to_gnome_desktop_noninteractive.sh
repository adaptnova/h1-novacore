#!/bin/bash
# Script to switch Chrome Remote Desktop from Xfce to GNOME desktop (non-interactive version)
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

print_section "Switching Chrome Remote Desktop to GNOME Desktop"

# Check if GNOME is installed
if ! dpkg -l | grep -q "gnome-shell"; then
    print_info "GNOME is not installed. Installing GNOME..."
    apt-get update
    apt-get install -y gnome-shell gnome-session gnome-terminal
    if [ $? -eq 0 ]; then
        print_success "GNOME installed successfully."
    else
        print_error "Failed to install GNOME."
        exit 1
    fi
else
    print_info "GNOME is already installed."
fi

# Backup the current Chrome Remote Desktop session file
print_info "Backing up the current Chrome Remote Desktop session file..."
if [ -f /home/x/.chrome-remote-desktop-session ]; then
    cp /home/x/.chrome-remote-desktop-session /home/x/.chrome-remote-desktop-session.bak
    print_success "Backup created at /home/x/.chrome-remote-desktop-session.bak"
else
    print_info "No existing Chrome Remote Desktop session file found."
fi

# Create a new Chrome Remote Desktop session file for GNOME
print_info "Creating new Chrome Remote Desktop session file for GNOME..."
cat > /home/x/.chrome-remote-desktop-session << EOF
#!/bin/bash
export GNOME_SHELL_SESSION_MODE=ubuntu
export XDG_CURRENT_DESKTOP=ubuntu:GNOME
export XDG_CONFIG_DIRS=/etc/xdg/xdg-ubuntu:/etc/xdg
exec /usr/bin/gnome-session
EOF
chmod +x /home/x/.chrome-remote-desktop-session
chown x:x /home/x/.chrome-remote-desktop-session
print_success "Chrome Remote Desktop session file updated to use GNOME."

# Remove Xfce desktop
print_info "Removing Xfce desktop..."
apt-get remove --purge -y xfce4 xfce4-goodies
apt-get autoremove -y
print_success "Xfce desktop removed."

# Restart Chrome Remote Desktop service
print_info "Restarting Chrome Remote Desktop service..."
systemctl restart chrome-remote-desktop@x.service
if [ $? -eq 0 ]; then
    print_success "Chrome Remote Desktop service restarted successfully."
else
    print_error "Failed to restart Chrome Remote Desktop service."
    print_info "You may need to reboot the server for changes to take effect."
fi

print_section "Summary"
print_success "Chrome Remote Desktop has been configured to use GNOME desktop."
print_info "Next time you connect to Chrome Remote Desktop, you should see the GNOME desktop."
print_info "If you still see Xfce desktop, try rebooting the server with:"
print_info "  sudo reboot"