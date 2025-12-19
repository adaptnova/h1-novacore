#!/bin/bash

# GDRIVE BACKUP - Google Drive Setup Script
# Version: 1.0.0

echo "Setting up Google Drive with rclone..."

# Create rclone config
rclone config create gdrive drive \
    user tonkateltec@gmai.com \
    scope "drive" \
    root_folder_id "" \
    service_account_file "" \
    config_is_local "true" \
    config_refresh_token "true"

echo "Google Drive setup initiated. Please run:"
echo "rclone authorize \"drive\""
echo "And follow the browser authentication process"
echo "After authentication, the configuration will be automatically saved"