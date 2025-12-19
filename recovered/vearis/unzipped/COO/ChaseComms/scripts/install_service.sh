#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "NOVA COMMS GUI Service Installation"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Create nova user and group if they don't exist
echo -e "\nSetting up user and group..."
id -u nova &>/dev/null || useradd -r -s /bin/false nova
id -g nova &>/dev/null || groupadd nova

# Create required directories
echo -e "\nCreating required directories..."
mkdir -p /etc/nova
mkdir -p /data/ax/projects/active/nova_comms_gui/logs
mkdir -p /data/ax/projects/active/nova_comms_gui/data

# Set proper permissions
echo -e "\nSetting permissions..."
chown -R nova:nova /data/ax/projects/active/nova_comms_gui
chmod 755 /data/ax/projects/active/nova_comms_gui
chmod 755 /data/ax/projects/active/nova_comms_gui/scripts/verify_service.sh

# Create environment file
echo -e "\nCreating environment file..."
cat > /etc/nova/nova-comms-gui.env << EOL
# Node environment
NODE_ENV=production
PORT=3001

# Memory settings for high-memory instance
NODE_OPTIONS="--max-old-space-size=32768"

# RabbitMQ settings
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_VHOST=nova

# Application settings
REACT_APP_WS_URL=ws://localhost:3001
REACT_APP_API_BASE=http://localhost:3001/api
REACT_APP_ATLASSIAN_URL=https://nova-adapt.atlassian.net
EOL

# Set environment file permissions
chmod 600 /etc/nova/nova-comms-gui.env
chown nova:nova /etc/nova/nova-comms-gui.env

# Install systemd service
echo -e "\nInstalling systemd service..."
cp /data/ax/projects/active/nova_comms_gui/nova-comms-gui.service /etc/systemd/system/
chmod 644 /etc/systemd/system/nova-comms-gui.service

# Reload systemd
echo -e "\nReloading systemd..."
systemctl daemon-reload

# Enable and start service
echo -e "\nEnabling and starting service..."
systemctl enable nova-comms-gui
systemctl start nova-comms-gui

# Wait for service to start
echo -e "\nWaiting for service to start..."
sleep 5

# Run verification script
echo -e "\nRunning verification script..."
/data/ax/projects/active/nova_comms_gui/scripts/verify_service.sh
VERIFY_STATUS=$?

if [ $VERIFY_STATUS -eq 0 ]; then
    echo -e "\n${GREEN}Installation completed successfully${NC}"
    echo -e "\nService status:"
    systemctl status nova-comms-gui
    echo -e "\nUseful commands:"
    echo "  systemctl status nova-comms-gui  # Check service status"
    echo "  journalctl -u nova-comms-gui -f  # View logs"
    echo "  systemctl restart nova-comms-gui # Restart service"
else
    echo -e "\n${RED}Installation completed with verification errors${NC}"
    echo -e "${YELLOW}Please check the verification output above${NC}"
    exit 1
fi
