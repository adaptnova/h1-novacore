#!/bin/bash
# Script to install Chrome Remote Desktop on adapt server
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="chrome_remote_desktop_install.log"

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Initialize log file
> "$LOG_FILE"

log "Starting Chrome Remote Desktop installation on adapt server"

# Create installation script
cat > /tmp/install_crd.sh << 'EOF'
#!/bin/bash

# Update package lists
echo "Updating package lists..."
apt-get update

# Install necessary dependencies
echo "Installing dependencies..."
apt-get install -y wget gnupg2 xvfb xbase-clients xfonts-base xfonts-100dpi xfonts-75dpi xfonts-scalable x11-xserver-utils

# Install desktop environment (XFCE4)
echo "Installing XFCE4 desktop environment..."
apt-get install -y xfce4 xfce4-terminal

# Download Chrome Remote Desktop
echo "Downloading Chrome Remote Desktop..."
wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb

# Install Chrome Remote Desktop
echo "Installing Chrome Remote Desktop..."
apt-get install -y ./chrome-remote-desktop_current_amd64.deb

# Install Chrome browser
echo "Downloading Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install Chrome browser
echo "Installing Google Chrome..."
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Configure Chrome Remote Desktop
echo "Configuring Chrome Remote Desktop..."

# Create Chrome Remote Desktop service configuration
mkdir -p /etc/chrome-remote-desktop
cat > /etc/chrome-remote-desktop/config << 'EOC'
# Chrome Remote Desktop configuration
CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
CHROME_REMOTE_DESKTOP_HOST_EXTRA_PARAMS="--enable-webrtc-remote-desktop"
EOC

# Create XFCE4 session script
mkdir -p /opt/google/chrome-remote-desktop
cat > /opt/google/chrome-remote-desktop/xfce-session << 'EOX'
#!/bin/bash
export CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
export DISPLAY=:20
export LANG=en_US.UTF-8
startxfce4 &
EOX
chmod +x /opt/google/chrome-remote-desktop/xfce-session

# Create a user for Chrome Remote Desktop
echo "Creating user for Chrome Remote Desktop..."
if ! id -u crduser > /dev/null 2>&1; then
  useradd -m -s /bin/bash crduser
  echo "crduser:crdpassword" | chpasswd
  usermod -aG sudo crduser
fi

# Set up Chrome Remote Desktop for the user
echo "Setting up Chrome Remote Desktop for crduser..."
su - crduser -c "mkdir -p ~/.config/chrome-remote-desktop"
su - crduser -c "echo 'export CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080' > ~/.config/chrome-remote-desktop/config"
su - crduser -c "echo 'export DISPLAY=:20' >> ~/.config/chrome-remote-desktop/config"
su - crduser -c "echo 'export LANG=en_US.UTF-8' >> ~/.config/chrome-remote-desktop/config"
su - crduser -c "echo 'startxfce4 &' >> ~/.config/chrome-remote-desktop/config"

# Create instructions for completing setup
cat > /home/crduser/chrome_remote_desktop_setup_instructions.txt << 'EOI'
Chrome Remote Desktop Installation Instructions

To complete the setup, follow these steps:

1. Visit https://remotedesktop.google.com/headless
2. Click on "Set up another computer"
3. Click on "Begin"
4. Click on "Next"
5. Click on "Authorize"
6. Copy the command that looks like:
   DISPLAY= /opt/google/chrome-remote-desktop/start-host --code="4/XXXX" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name=$(hostname)

7. Run the command as the crduser:
   su - crduser
   [paste the command here]

8. Set a PIN when prompted

9. Go back to https://remotedesktop.google.com/access
   You should see your computer listed there.

10. Click on it and enter your PIN to connect.

Note: The crduser password is "crdpassword"
EOI

# Set permissions
chown crduser:crduser /home/crduser/chrome_remote_desktop_setup_instructions.txt

echo "Chrome Remote Desktop installation completed!"
echo "Please follow the instructions in /home/crduser/chrome_remote_desktop_setup_instructions.txt to complete the setup."
EOF

# Make the script executable
chmod +x /tmp/install_crd.sh

# Copy the script to the server
log "Copying installation script to the server..."
scp -o StrictHostKeyChecking=no /tmp/install_crd.sh $SSH_USER@$SERVER_IP:/tmp/

# Execute the script on the server
log "Executing installation script on the server..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/install_crd.sh"

log "Chrome Remote Desktop installation completed on adapt server"
log "Please follow the instructions in /home/crduser/chrome_remote_desktop_setup_instructions.txt on the server to complete the setup."