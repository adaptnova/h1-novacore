#!/bin/bash
# deploy_ethos_gpu.sh - Script to deploy the ethos GPU server in IBM Cloud
# Created by Synaptic - March 21, 2025

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}Ethos GPU Server Deployment Script${RESET}"
echo "=================================================="
echo "This script will deploy the ethos GPU server in IBM Cloud."
echo "Make sure you have the IBM Cloud CLI installed and are logged in."
echo ""

# Check if ibmcloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo -e "${RED}Error: IBM Cloud CLI is not installed.${RESET}"
    echo "Please install it first: https://cloud.ibm.com/docs/cli"
    exit 1
fi

# Check if logged in
echo -e "${YELLOW}Checking IBM Cloud CLI login status...${RESET}"
ibmcloud target &> /dev/null || {
    echo -e "${RED}Error: Not logged in to IBM Cloud.${RESET}"
    echo "Please login first: ibmcloud login"
    exit 1
}

# Set variables
RESOURCE_GROUP="adapt"
REGION="us-south"
ZONE="us-south-2"
VPC_NAME="dataops-vpc-new"
SUBNET_NAME="dataops-subnet"
SECURITY_GROUP_NAME="ethos-sg"
SERVER_NAME="ethos"
PROFILE="gx3-48x240x2l40s"
IMAGE="ibm-debian-12-9-minimal-amd64-1"

# Boot volume
BOOT_VOLUME_NAME="${SERVER_NAME}-boot"
BOOT_VOLUME_SIZE="50"
BOOT_VOLUME_IOPS="5000"

# Data volume
DATA_VOLUME_NAME="${SERVER_NAME}-data"
DATA_VOLUME_SIZE="50"
DATA_VOLUME_IOPS="5000"

# Log volume
LOG_VOLUME_NAME="${SERVER_NAME}-logs"
LOG_VOLUME_SIZE="50"
LOG_VOLUME_IOPS="5000"

# LLMs volume
LLMS_VOLUME_NAME="${SERVER_NAME}-llms"
LLMS_VOLUME_SIZE="1"
LLMS_VOLUME_IOPS="3000"

# SSH key
SSH_KEY_NAME="chase-key"

# User data for initial setup
USER_DATA_FILE="ethos_user_data_updated.sh"

# Step 1: Verify GPU availability
echo -e "${YELLOW}Step 1: Verifying GPU availability in ${ZONE}...${RESET}"
ibmcloud is instance-profiles | grep "${PROFILE}" &> /dev/null || {
    echo -e "${RED}Error: GPU profile ${PROFILE} not found in this region.${RESET}"
    echo "Please check available profiles and update the script."
    exit 1
}

echo -e "${GREEN}GPU profile ${PROFILE} is available.${RESET}"

# Step 2: Get existing security group
echo -e "${YELLOW}Step 2: Getting existing security group ${SECURITY_GROUP_NAME}...${RESET}"
SG_ID=$(ibmcloud is security-groups | grep "${SECURITY_GROUP_NAME}" | grep "${VPC_NAME}" | awk '{print $1}')
if [ -z "${SG_ID}" ]; then
    echo -e "${YELLOW}Security group ${SECURITY_GROUP_NAME} not found. Creating it...${RESET}"
    SG_ID=$(ibmcloud is security-group-create ${SECURITY_GROUP_NAME} ${VPC_NAME} --output json | jq -r '.id')
    echo -e "${GREEN}Security group created with ID: ${SG_ID}${RESET}"
    
    echo -e "${YELLOW}Adding security group rules...${RESET}"
    # Allow SSH from management IPs
    ibmcloud is security-group-rule-add ${SG_ID} inbound tcp --port-min 22 --port-max 22
    
    # Allow internal VPC traffic
    ibmcloud is security-group-rule-add ${SG_ID} inbound all
    
    # Allow outbound traffic
    ibmcloud is security-group-rule-add ${SG_ID} outbound all
    
    echo -e "${GREEN}Security group rules added.${RESET}"
else
    echo -e "${GREEN}Using existing security group with ID: ${SG_ID}${RESET}"
fi

# Step 3: Verify security group rules
echo -e "${YELLOW}Step 3: Verifying security group rules...${RESET}"
ibmcloud is security-group-rules ${SG_ID}

# Step 4: Create volumes
echo -e "${YELLOW}Step 4: Creating volumes...${RESET}"

# Create boot volume
echo "Creating boot volume..."
BOOT_VOLUME_ID=$(ibmcloud is volume-create ${BOOT_VOLUME_NAME} general-purpose ${BOOT_VOLUME_SIZE} --iops ${BOOT_VOLUME_IOPS} --zone ${ZONE} --output json | jq -r '.id')
echo -e "${GREEN}Boot volume created with ID: ${BOOT_VOLUME_ID}${RESET}"

# Create data volume
echo "Creating data volume..."
DATA_VOLUME_ID=$(ibmcloud is volume-create ${DATA_VOLUME_NAME} general-purpose ${DATA_VOLUME_SIZE} --iops ${DATA_VOLUME_IOPS} --zone ${ZONE} --output json | jq -r '.id')
echo -e "${GREEN}Data volume created with ID: ${DATA_VOLUME_ID}${RESET}"

# Create log volume
echo "Creating log volume..."
LOG_VOLUME_ID=$(ibmcloud is volume-create ${LOG_VOLUME_NAME} general-purpose ${LOG_VOLUME_SIZE} --iops ${LOG_VOLUME_IOPS} --zone ${ZONE} --output json | jq -r '.id')
echo -e "${GREEN}Log volume created with ID: ${LOG_VOLUME_ID}${RESET}"

# Create LLMs volume
echo "Creating LLMs volume..."
LLMS_VOLUME_ID=$(ibmcloud is volume-create ${LLMS_VOLUME_NAME} general-purpose ${LLMS_VOLUME_SIZE} --iops ${LLMS_VOLUME_IOPS} --zone ${ZONE} --output json | jq -r '.id')
echo -e "${GREEN}LLMs volume created with ID: ${LLMS_VOLUME_ID}${RESET}"

# Step 5: Verify user data script exists
echo -e "${YELLOW}Step 5: Verifying user data script...${RESET}"
if [ ! -f "${USER_DATA_FILE}" ]; then
    echo -e "${RED}Error: User data script ${USER_DATA_FILE} not found.${RESET}"
    echo "Please create the user data script first."
    exit 1
fi
echo -e "${GREEN}User data script ${USER_DATA_FILE} found.${RESET}"

# Step 6: Deploy the server
echo -e "${YELLOW}Step 6: Deploying ethos GPU server...${RESET}"
SUBNET_ID=$(ibmcloud is subnets | grep ${SUBNET_NAME} | awk '{print $1}')
SSH_KEY_ID=$(ibmcloud is keys | grep ${SSH_KEY_NAME} | awk '{print $1}')

ibmcloud is instance-create ${SERVER_NAME} ${VPC_NAME} ${ZONE} ${PROFILE} ${SUBNET_ID} \
  --image ${IMAGE} \
  --keys ${SSH_KEY_ID} \
  --security-groups ${SG_ID} \
  --user-data @${USER_DATA_FILE} \
  --volume-attach name=data,volume=${DATA_VOLUME_ID} \
  --volume-attach name=logs,volume=${LOG_VOLUME_ID} \
  --volume-attach name=llms,volume=${LLMS_VOLUME_ID}

echo -e "${GREEN}Ethos GPU server deployment initiated.${RESET}"
echo "It may take 10-15 minutes for the server to be fully provisioned and configured."

# Step 7: Monitor deployment
echo -e "${YELLOW}Step 7: Monitoring deployment status...${RESET}"
echo "Checking server status every 30 seconds..."

while true; do
    STATUS=$(ibmcloud is instance ${SERVER_NAME} --output json | jq -r '.status')
    echo "Current status: ${STATUS}"
    
    if [ "${STATUS}" == "running" ]; then
        echo -e "${GREEN}Server is now running!${RESET}"
        break
    elif [ "${STATUS}" == "failed" ]; then
        echo -e "${RED}Server deployment failed. Please check the IBM Cloud console for details.${RESET}"
        exit 1
    fi
    
    sleep 30
done

# Get server details
SERVER_DETAILS=$(ibmcloud is instance ${SERVER_NAME} --output json)
PRIVATE_IP=$(echo ${SERVER_DETAILS} | jq -r '.primary_network_interface.primary_ipv4_address')
FLOATING_IP=$(echo ${SERVER_DETAILS} | jq -r '.floating_ips[0].address // "None"')

echo -e "${GREEN}Ethos GPU server deployed successfully!${RESET}"
echo "=================================================="
echo "Server Details:"
echo "Name: ${SERVER_NAME}"
echo "Profile: ${PROFILE}"
echo "Private IP: ${PRIVATE_IP}"
echo "Floating IP: ${FLOATING_IP}"
echo ""
echo "To connect to the server:"
if [ "${FLOATING_IP}" != "None" ]; then
    echo "ssh synaptic@${FLOATING_IP}"
else
    echo "No floating IP assigned. Connect through a bastion host or assign a floating IP."
fi
echo ""
echo "Next steps:"
echo "1. Verify GPU functionality: ssh to the server and run 'nvidia-smi'"
echo "2. Check deployment log: /data/deployment_complete.txt"
echo "3. Proceed with deploying the rest of the infrastructure"
echo ""
echo "For detailed information, refer to adapt_platform/ethos_gpu_server.md"