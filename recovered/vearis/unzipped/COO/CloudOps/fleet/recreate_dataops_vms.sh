#!/bin/bash
# Script to recreate DataOps VMs with the ibm-admin key
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Subnet ID
SUBNET_ID="0717-57b4b629-9704-4ba2-9fdb-63386cdba641"
# SSH Key ID
SSH_KEY_ID="r006-3183fd0f-80b8-49ce-9e49-080fdf64b115"
# Image ID
IMAGE_ID="r006-ae2c7bd1-25b3-4a42-8f01-59ee2cb0a6b5"
# VPC ID
VPC_ID="r006-273e9e7d-9da9-4df2-8f93-c935d34b6a00"
# Profile
PROFILE="bx2-8x32"

# Function to recreate a VM
recreate_vm() {
    local vm_name=$1
    local vm_id=$2
    
    echo "Processing $vm_name..."
    
    # Get volume attachments
    echo "Getting volume attachments for $vm_name..."
    volume_attachments=$(ibmcloud is instance-volume-attachments $vm_name --output json)
    
    # Extract volume IDs and names
    echo "Extracting volume information..."
    volume_info=$(echo $volume_attachments | jq -r '.[] | select(.type != "boot") | {id: .volume.id, name: .name}')
    
    # Stop the VM
    echo "Stopping $vm_name..."
    ibmcloud is instance-stop $vm_name
    
    # Wait for the VM to stop
    echo "Waiting for $vm_name to stop..."
    while [[ $(ibmcloud is instance $vm_name --output json | jq -r '.status') != "stopped" ]]; do
        echo "Waiting for $vm_name to stop..."
        sleep 10
    done
    
    # Detach volumes
    echo "Detaching volumes from $vm_name..."
    for attachment in $(echo $volume_attachments | jq -r '.[] | select(.type != "boot") | .id'); do
        echo "Detaching volume attachment $attachment..."
        ibmcloud is instance-volume-attachment-detach $vm_name $attachment
    done
    
    # Wait for volumes to be detached
    echo "Waiting for volumes to be detached..."
    sleep 30
    
    # Delete the VM
    echo "Deleting $vm_name..."
    ibmcloud is instance-delete $vm_name
    
    # Wait for the VM to be deleted
    echo "Waiting for $vm_name to be deleted..."
    sleep 30
    
    # Create a new VM with the same name
    echo "Creating new $vm_name with ibm-admin key..."
    ibmcloud is instance-create $vm_name $VPC_ID us-south-1 $PROFILE $SUBNET_ID --image $IMAGE_ID --keys $SSH_KEY_ID
    
    # Wait for the VM to be running
    echo "Waiting for $vm_name to be running..."
    while [[ $(ibmcloud is instance $vm_name --output json | jq -r '.status') != "running" ]]; do
        echo "Waiting for $vm_name to be running..."
        sleep 10
    done
    
    # Attach volumes
    echo "Attaching volumes to $vm_name..."
    for volume in $(echo $volume_info | jq -c '.'); do
        volume_id=$(echo $volume | jq -r '.id')
        volume_name=$(echo $volume | jq -r '.name')
        echo "Attaching volume $volume_id as $volume_name..."
        ibmcloud is instance-volume-attachment-add $volume_name $vm_name $volume_id
    done
    
    echo "$vm_name recreated successfully."
}

# Recreate dataops-primary
recreate_vm "dataops-primary" "0717_43d1b974-388d-41bd-809b-1b8938651a5a"

# Recreate dataops-timeseries
recreate_vm "dataops-timeseries" "0717_2f6509b5-7ea3-4989-921f-e976e044818e"

# Recreate dataops-vector
recreate_vm "dataops-vector" "0717_d4d79516-0459-4e07-9135-12e15c690375"

echo "All DataOps VMs recreated successfully."