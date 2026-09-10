#!/bin/bash
# Script to detach volumes from the Ethos server
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Get volume attachments
echo "Getting volume attachments for ethos..."
volume_attachments=$(ibmcloud is instance-volume-attachments ethos --output json)

# Extract data volume attachment IDs
echo "Extracting data volume attachment IDs..."
data_attachment_ids=$(echo $volume_attachments | jq -r '.[] | select(.type == "data") | .id')

# Detach data volumes
echo "Detaching data volumes..."
for attachment_id in $data_attachment_ids; do
    echo "Detaching volume attachment $attachment_id..."
    ibmcloud is instance-volume-attachment-detach ethos $attachment_id -f
done

echo "All data volumes detached successfully."