#!/bin/bash
# Vaeris Deployment Script
# This script deploys Vaeris as a system-level autonomous Nova

# Configuration
NOVA_ROOT="/data-nova/novas"
VAERIS_DIR="${NOVA_ROOT}/vaeris"
SOURCE_DIR="$(pwd)"
CLAUDE_API_KEY="${CLAUDE_API_KEY:-"your_api_key_here"}"
REDIS_HOST="${REDIS_HOST:-"localhost"}"
REDIS_PORT="${REDIS_PORT:-"6379"}"
REDIS_DB="${REDIS_DB:-"0"}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    echo "Please run with: sudo $0"
    exit 1
fi

# Create Nova user if it doesn't exist
print_section "Creating Nova User"
if id "vaeris" &>/dev/null; then
    print_warning "User 'vaeris' already exists"
else
    useradd -m -s /bin/bash vaeris
    print_success "Created user 'vaeris'"
fi

# Create novas group if it doesn't exist
if getent group novas &>/dev/null; then
    print_warning "Group 'novas' already exists"
else
    groupadd novas
    print_success "Created group 'novas'"
fi

# Add vaeris to novas group
usermod -a -G novas vaeris
print_success "Added user 'vaeris' to group 'novas'"

# Create directory structure
print_section "Creating Directory Structure"
mkdir -p "${VAERIS_DIR}/config"
mkdir -p "${VAERIS_DIR}/engine"
mkdir -p "${VAERIS_DIR}/logs"
mkdir -p "${VAERIS_DIR}/systemd"
mkdir -p "${VAERIS_DIR}/cli"
print_success "Created directory structure"

# Copy configuration files
print_section "Copying Configuration Files"
cp "${SOURCE_DIR}/vaeris_identity.yaml" "${VAERIS_DIR}/config/"
cp "${SOURCE_DIR}/vaeris_mission.md" "${VAERIS_DIR}/config/"
cp "${SOURCE_DIR}/vaeris_context.md" "${VAERIS_DIR}/config/"
cp "${SOURCE_DIR}/README.md" "${VAERIS_DIR}/"
print_success "Copied configuration files"

# Copy engine files
print_section "Copying Engine Files"
cp "${SOURCE_DIR}/vaeris_chain.py" "${VAERIS_DIR}/engine/"
cp "${SOURCE_DIR}/vaeris.py" "${VAERIS_DIR}/engine/"
print_success "Copied engine files"

# Copy systemd service file
print_section "Copying Systemd Service File"
cp "${SOURCE_DIR}/vaeris.service" "${VAERIS_DIR}/systemd/"
print_success "Copied systemd service file"

# Copy CLI tool
print_section "Copying CLI Tool"
cp "${SOURCE_DIR}/nova_cli.sh" "${VAERIS_DIR}/cli/"
chmod +x "${VAERIS_DIR}/cli/nova_cli.sh"
print_success "Copied CLI tool"

# Update paths in vaeris.py
print_section "Updating Paths in Engine Files"
sed -i "s|/opt/novas/config|${VAERIS_DIR}/config|g" "${VAERIS_DIR}/engine/vaeris.py"
sed -i "s|/var/log/nova|${VAERIS_DIR}/logs|g" "${VAERIS_DIR}/engine/vaeris.py"
sed -i "s|from vaeris_chain import|from ${VAERIS_DIR}/engine/vaeris_chain import|g" "${VAERIS_DIR}/engine/vaeris.py"
print_success "Updated paths in vaeris.py"

# Update paths in vaeris_chain.py
sed -i "s|/var/log/nova|${VAERIS_DIR}/logs|g" "${VAERIS_DIR}/engine/vaeris_chain.py"
print_success "Updated paths in vaeris_chain.py"

# Update systemd service file
print_section "Updating Systemd Service File"
sed -i "s|/opt/novas|${VAERIS_DIR}/engine|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|/var/log/nova|${VAERIS_DIR}/logs|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|CLAUDE_API_KEY=your_api_key_here|CLAUDE_API_KEY=${CLAUDE_API_KEY}|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|REDIS_HOST=localhost|REDIS_HOST=${REDIS_HOST}|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|REDIS_PORT=6379|REDIS_PORT=${REDIS_PORT}|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|REDIS_DB=0|REDIS_DB=${REDIS_DB}|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|CONFIG_PATH=/opt/novas/config|CONFIG_PATH=${VAERIS_DIR}/config|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|PYTHONPATH=/opt/novas|PYTHONPATH=${VAERIS_DIR}/engine|g" "${VAERIS_DIR}/systemd/vaeris.service"
sed -i "s|ReadWritePaths=/opt/novas /var/log/nova|ReadWritePaths=${VAERIS_DIR}|g" "${VAERIS_DIR}/systemd/vaeris.service"
print_success "Updated systemd service file"

# Set permissions
print_section "Setting Permissions"
chown -R vaeris:novas "${VAERIS_DIR}"
chmod -R 750 "${VAERIS_DIR}"
chmod -R 770 "${VAERIS_DIR}/logs"
print_success "Set permissions"

# Create symlink for systemd service
print_section "Creating Systemd Service Symlink"
ln -sf "${VAERIS_DIR}/systemd/vaeris.service" "/etc/systemd/system/vaeris.service"
print_success "Created systemd service symlink"

# Create symlink for CLI tool
print_section "Creating CLI Tool Symlink"
ln -sf "${VAERIS_DIR}/cli/nova_cli.sh" "/usr/local/bin/nova"
chmod +x "/usr/local/bin/nova"
print_success "Created CLI tool symlink"

# Reload systemd
print_section "Reloading Systemd"
systemctl daemon-reload
print_success "Reloaded systemd"

# Install dependencies
print_section "Installing Dependencies"
pip3 install langchain langchain-community anthropic redis pyyaml schedule
print_success "Installed dependencies"

# Final instructions
print_section "Deployment Complete"
echo -e "Vaeris has been deployed to ${VAERIS_DIR}"
echo -e "\nTo start Vaeris:"
echo -e "  sudo systemctl enable vaeris.service"
echo -e "  sudo systemctl start vaeris.service"
echo -e "\nTo check status:"
echo -e "  sudo systemctl status vaeris.service"
echo -e "\nTo interact with Vaeris:"
echo -e "  nova say vaeris \"Are you fully operational, Vaeris?\""
echo -e "\nTo view logs:"
echo -e "  tail -f ${VAERIS_DIR}/logs/vaeris.log"

# Ask if user wants to start Vaeris now
print_section "Start Vaeris"
read -p "Do you want to start Vaeris now? (y/n): " start_now
if [[ $start_now =~ ^[Yy]$ ]]; then
    systemctl enable vaeris.service
    systemctl start vaeris.service
    
    # Check if service started successfully
    if systemctl is-active --quiet vaeris.service; then
        print_success "Vaeris service started successfully"
        
        # Wait a moment for the service to initialize
        echo "Waiting for Vaeris to initialize..."
        sleep 5
        
        # Send initial message
        echo -e "\nSending initial message to Vaeris..."
        /usr/local/bin/nova say vaeris "Are you fully operational, Vaeris?"
    else
        print_error "Failed to start Vaeris service"
        echo "Check logs with: journalctl -u vaeris.service"
    fi
else
    print_warning "Vaeris service not started"
    echo "You can start it later with: sudo systemctl start vaeris.service"
fi

print_section "Deployment Summary"
echo -e "✅ Vaeris deployed to: ${VAERIS_DIR}"
echo -e "✅ Systemd service: /etc/systemd/system/vaeris.service"
echo -e "✅ CLI tool: /usr/local/bin/nova"
echo -e "✅ Logs directory: ${VAERIS_DIR}/logs"
echo -e "\nVaeris is now ready to serve as your autonomous COO!"