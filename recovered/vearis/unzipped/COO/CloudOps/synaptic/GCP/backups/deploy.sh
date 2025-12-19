#!/bin/bash

# GDRIVE BACKUP - Deployment Script
# Version: 1.0.0

# Log file
LOG_FILE="/var/log/backup_deploy.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Create log file
sudo touch "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"

log_message "Starting deployment process..."

# Install required packages
log_message "Installing required packages..."
sudo apt update && sudo apt install -y rclone inotify-tools rsync

# Create mount point
log_message "Creating mount point..."
sudo mkdir -p /mnt/gdrive
sudo chmod 755 /mnt/gdrive

# Move service files to appropriate locations
log_message "Installing service files..."
sudo cp backup_service.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup_service.sh
sudo cp gdrive-backup.service /etc/systemd/system/

# Create required log directories
log_message "Setting up log files..."
sudo touch /var/log/backup_service.log /var/log/backup_service.error.log
sudo chmod 644 /var/log/backup_service.log /var/log/backup_service.error.log

# Reload systemd
log_message "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start the service
log_message "Enabling and starting backup service..."
sudo systemctl enable gdrive-backup
sudo systemctl start gdrive-backup

log_message "Deployment completed successfully"
log_message "You can check service status with: sudo systemctl status gdrive-backup"
log_message "View logs with: tail -f /var/log/backup_service.log"