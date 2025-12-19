#!/bin/bash

# rsync_daemon_setup.sh - Script to set up rsync daemon for efficient transfers
# Created by Synaptic on March 19, 2025

# Configuration
RSYNCD_CONF="/etc/rsyncd.conf"
RSYNCD_SECRETS="/etc/rsyncd.secrets"
MODULE_NAME="data_transfer"
DATA_PATH="/mnt/data"
AUTH_USER="transfer"
AUTH_PASS="$(openssl rand -base64 12)"  # Generate random password
LOG_FILE="/var/log/rsyncd.log"
PORT="873"  # Default rsync port

# Install rsync if not already installed
if ! command -v rsync &> /dev/null; then
    echo "Installing rsync..."
    apt-get update
    apt-get install -y rsync
fi

# Create rsync daemon configuration
cat > "$RSYNCD_CONF" << EOF
# rsyncd.conf - rsync daemon configuration
# Created by Synaptic on $(date)

# Global settings
uid = root
gid = root
use chroot = yes
max connections = 10
pid file = /var/run/rsyncd.pid
lock file = /var/run/rsync.lock
log file = $LOG_FILE
port = $PORT

# Module definitions
[$MODULE_NAME]
    path = $DATA_PATH
    comment = Data Transfer Module
    read only = no
    list = yes
    auth users = $AUTH_USER
    secrets file = $RSYNCD_SECRETS
    hosts allow = *
EOF

# Create secrets file with secure permissions
echo "$AUTH_USER:$AUTH_PASS" > "$RSYNCD_SECRETS"
chmod 600 "$RSYNCD_SECRETS"

# Create log file if it doesn't exist
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

# Start rsync daemon
systemctl stop rsync || true
rsync --daemon --config="$RSYNCD_CONF"

# Create a systemd service file for rsync daemon
cat > /etc/systemd/system/rsync.service << EOF
[Unit]
Description=Rsync Daemon
After=network.target

[Service]
ExecStart=/usr/bin/rsync --daemon --no-detach --config=$RSYNCD_CONF
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable rsync
systemctl restart rsync

# Display connection information
echo "Rsync daemon setup complete!"
echo "Connection information:"
echo "  Module name: $MODULE_NAME"
echo "  Username: $AUTH_USER"
echo "  Password: $AUTH_PASS"
echo "  Port: $PORT"
echo ""
echo "To connect from another machine, use:"
echo "  rsync -avz --port=$PORT rsync://$AUTH_USER@<server-ip>/$MODULE_NAME/ /path/to/destination/"
echo ""
echo "Or with password file (create a file with just the password in it):"
echo "  rsync -avz --port=$PORT --password-file=/path/to/password.txt rsync://$AUTH_USER@<server-ip>/$MODULE_NAME/ /path/to/destination/"

# Save connection info to a file for reference
CONNECTION_INFO="/root/rsync_scripts/connection_info.txt"
mkdir -p "$(dirname "$CONNECTION_INFO")"
cat > "$CONNECTION_INFO" << EOF
Rsync Daemon Connection Information
==================================
Module name: $MODULE_NAME
Username: $AUTH_USER
Password: $AUTH_PASS
Port: $PORT

Connection command:
rsync -avz --port=$PORT rsync://$AUTH_USER@<server-ip>/$MODULE_NAME/ /path/to/destination/

With password file:
rsync -avz --port=$PORT --password-file=/path/to/password.txt rsync://$AUTH_USER@<server-ip>/$MODULE_NAME/ /path/to/destination/
EOF

echo "Connection information saved to $CONNECTION_INFO"