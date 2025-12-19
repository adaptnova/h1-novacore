#!/bin/bash
# Script to complete Chrome Remote Desktop setup
# Version: 1.0.0
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 27, 2025

# Configuration
SERVER_IP="10.240.1.6"
SSH_USER="root"
LOG_FILE="chrome_remote_desktop_setup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log and display messages
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to display section headers
section() {
  log "${BLUE}=== $1 ===${NC}"
}

# Function to display success messages
success() {
  log "${GREEN}✓ $1${NC}"
}

# Function to display error messages
error() {
  log "${RED}✗ $1${NC}"
}

# Function to display warning messages
warning() {
  log "${YELLOW}! $1${NC}"
}

# Initialize log file
> "$LOG_FILE"

section "Checking Chrome Remote Desktop Setup"
log "Checking if Chrome Remote Desktop is already installed..."

# Check if Chrome Remote Desktop is installed
CRD_INSTALLED=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "dpkg -l | grep chrome-remote-desktop || echo 'Not installed'")

if [[ "$CRD_INSTALLED" == *"Not installed"* ]]; then
  warning "Chrome Remote Desktop is not installed yet"
  
  section "Installing Chrome Remote Desktop"
  log "Downloading Chrome Remote Desktop package..."
  
  # Try to download Chrome Remote Desktop package
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "apt-get update && apt-get install -y wget curl"
  
  # Try different methods to download the package
  log "Trying wget..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "wget -O /tmp/chrome-remote-desktop_current_amd64.deb https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb || echo 'wget failed'"
  
  log "Trying curl..."
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "curl -L -o /tmp/chrome-remote-desktop_current_amd64.deb https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb || echo 'curl failed'"
  
  # Check if the package was downloaded
  PACKAGE_EXISTS=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ls -la /tmp/chrome-remote-desktop_current_amd64.deb 2>/dev/null || echo 'File not found'")
  
  if [[ "$PACKAGE_EXISTS" == *"File not found"* ]]; then
    error "Failed to download Chrome Remote Desktop package"
    warning "You will need to manually download and install the package on the server"
    warning "Use the following command on the server:"
    warning "wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb && apt-get install -y ./chrome-remote-desktop_current_amd64.deb"
  else
    log "Installing Chrome Remote Desktop package..."
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "apt-get install -y /tmp/chrome-remote-desktop_current_amd64.deb"
    success "Chrome Remote Desktop package installed"
  fi
else
  success "Chrome Remote Desktop is already installed"
fi

section "Checking Chrome Remote Desktop Configuration"
log "Checking if Chrome Remote Desktop configuration is set up..."

# Check if Chrome Remote Desktop configuration is set up
CRD_CONFIG=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ls -la /etc/chrome-remote-desktop/config 2>/dev/null || echo 'File not found'")

if [[ "$CRD_CONFIG" == *"File not found"* ]]; then
  warning "Chrome Remote Desktop configuration is not set up"
  
  section "Setting up Chrome Remote Desktop Configuration"
  log "Creating Chrome Remote Desktop configuration..."
  
  # Create Chrome Remote Desktop configuration
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "mkdir -p /etc/chrome-remote-desktop"
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat > /etc/chrome-remote-desktop/config << 'EOC'
# Chrome Remote Desktop configuration
CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
CHROME_REMOTE_DESKTOP_HOST_EXTRA_PARAMS=\"--enable-webrtc-remote-desktop\"
EOC"
  
  success "Chrome Remote Desktop configuration created"
else
  success "Chrome Remote Desktop configuration is already set up"
fi

section "Checking XFCE4 Session Script"
log "Checking if XFCE4 session script is set up..."

# Check if XFCE4 session script is set up
XFCE_SESSION=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ls -la /opt/google/chrome-remote-desktop/xfce-session 2>/dev/null || echo 'File not found'")

if [[ "$XFCE_SESSION" == *"File not found"* ]]; then
  warning "XFCE4 session script is not set up"
  
  section "Setting up XFCE4 Session Script"
  log "Creating XFCE4 session script..."
  
  # Create XFCE4 session script
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "mkdir -p /opt/google/chrome-remote-desktop"
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat > /opt/google/chrome-remote-desktop/xfce-session << 'EOX'
#!/bin/bash
export CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
export DISPLAY=:20
export LANG=en_US.UTF-8
startxfce4 &
EOX"
  
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chmod +x /opt/google/chrome-remote-desktop/xfce-session"
  
  success "XFCE4 session script created"
else
  success "XFCE4 session script is already set up"
fi

section "Checking crduser"
log "Checking if crduser is set up..."

# Check if crduser is set up
CRDUSER=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "id crduser 2>/dev/null || echo 'User not found'")

if [[ "$CRDUSER" == *"User not found"* ]]; then
  warning "crduser is not set up"
  
  section "Setting up crduser"
  log "Creating crduser..."
  
  # Create crduser
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "useradd -m -s /bin/bash crduser"
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'crduser:crdpassword' | chpasswd"
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "usermod -aG sudo crduser"
  
  success "crduser created"
else
  success "crduser is already set up"
fi

section "Checking crduser Chrome Remote Desktop Configuration"
log "Checking if crduser Chrome Remote Desktop configuration is set up..."

# Check if crduser Chrome Remote Desktop configuration is set up
CRDUSER_CONFIG=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ls -la /home/crduser/.config/chrome-remote-desktop/config 2>/dev/null || echo 'File not found'")

if [[ "$CRDUSER_CONFIG" == *"File not found"* ]]; then
  warning "crduser Chrome Remote Desktop configuration is not set up"
  
  section "Setting up crduser Chrome Remote Desktop Configuration"
  log "Creating crduser Chrome Remote Desktop configuration..."
  
  # Create crduser Chrome Remote Desktop configuration
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "su - crduser -c 'mkdir -p ~/.config/chrome-remote-desktop'"
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "su - crduser -c 'cat > ~/.config/chrome-remote-desktop/config << EOC
export CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES=1920x1080
export DISPLAY=:20
export LANG=en_US.UTF-8
startxfce4 &
EOC'"
  
  success "crduser Chrome Remote Desktop configuration created"
else
  success "crduser Chrome Remote Desktop configuration is already set up"
fi

section "Checking Setup Instructions"
log "Checking if setup instructions are set up..."

# Check if setup instructions are set up
SETUP_INSTRUCTIONS=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ls -la /home/crduser/chrome_remote_desktop_setup_instructions.txt 2>/dev/null || echo 'File not found'")

if [[ "$SETUP_INSTRUCTIONS" == *"File not found"* ]]; then
  warning "Setup instructions are not set up"
  
  section "Setting up Setup Instructions"
  log "Creating setup instructions..."
  
  # Create setup instructions
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat > /home/crduser/chrome_remote_desktop_setup_instructions.txt << 'EOI'
Chrome Remote Desktop Installation Instructions

To complete the setup, follow these steps:

1. Visit https://remotedesktop.google.com/headless
2. Click on \"Set up another computer\"
3. Click on \"Begin\"
4. Click on \"Next\"
5. Click on \"Authorize\"
6. Copy the command that looks like:
   DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/XXXX\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=\$(hostname)

7. Run the command as the crduser:
   su - crduser
   [paste the command here]

8. Set a PIN when prompted

9. Go back to https://remotedesktop.google.com/access
   You should see your computer listed there.

10. Click on it and enter your PIN to connect.

Note: The crduser password is \"crdpassword\"
EOI"
  
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "chown crduser:crduser /home/crduser/chrome_remote_desktop_setup_instructions.txt"
  
  success "Setup instructions created"
else
  success "Setup instructions are already set up"
fi

section "Displaying Setup Instructions"
log "Displaying Chrome Remote Desktop setup instructions..."
ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "cat /home/crduser/chrome_remote_desktop_setup_instructions.txt"

section "Summary"
success "Chrome Remote Desktop setup completed"
log "User: crduser"
log "Password: crdpassword"
log "Follow the instructions above to complete the setup"

echo -e "\nChrome Remote Desktop setup completed. Check $LOG_FILE for details."