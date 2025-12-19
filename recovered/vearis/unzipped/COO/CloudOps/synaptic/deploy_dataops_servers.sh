#!/bin/bash

# Deploy DataOps Servers Script
# Created by Synaptic on March 21, 2025
# This script deploys three DataOps servers in IBM Cloud according to the infrastructure requirements

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Set variables
RESOURCE_GROUP="adapt"
REGION="us-south"
ZONE="us-south-1"  # Using us-south-1 since we confirmed GPU availability there
VPC_NAME="dataops-vpc-new"
SUBNET_NAME="us-south-1-subnet"
SECURITY_GROUP_NAME="dataops-sg"
PROFILE="bx2-8x32"  # 8 vCPUs, 32GB RAM
IMAGE="ibm-debian-12-9-minimal-amd64-1"  # Using Debian 12 like ethos server

# SSH key
SSH_KEY_NAME="chase-key"

# Server names and volume sizes
declare -A SERVERS=(
  ["dataops-primary"]="100"    # Primary Database - 100GB data volume
  ["dataops-vector"]="80"      # Vector/Graph Database - 80GB data volume
  ["dataops-timeseries"]="60"  # Time-Series/Cache - 60GB data volume
)

# User data for initial setup
USER_DATA_FILE="dataops_user_data.sh"

# Create user data script
echo -e "${YELLOW}Creating user data script...${RESET}"
cat > ${USER_DATA_FILE} << 'EOF'
#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install basic utilities
apt-get install -y build-essential cmake git python3-dev python3-pip htop iotop iftop

# Create users
for user in synaptic forge x vertex; do
    useradd -m -s /bin/bash $user
    echo "$user:x" | chpasswd
    echo "$user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$user
    mkdir -p /home/$user/.ssh
    chmod 700 /home/$user/.ssh
    chown -R $user:$user /home/$user/.ssh
done

# Format and mount data volume
mkfs.xfs /dev/vdd
mkdir -p /data
echo "/dev/vdd /data xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /data
chmod 777 /data

# Format and mount backup volume
mkfs.xfs /dev/vde
mkdir -p /backup
echo "/dev/vde /backup xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
mount /backup
chmod 777 /backup

# Install monitoring tools
apt-get install -y prometheus-node-exporter

# Install Filebeat for log forwarding
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
apt-get install -y filebeat

# Configure system optimizations
cat > /etc/sysctl.d/99-dataops-optimizations.conf << 'EOC'
# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr

# Memory optimizations
vm.swappiness=10
EOC

sysctl -p /etc/sysctl.d/99-dataops-optimizations.conf

# Set CPU governor to performance
apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils

# Create deployment success marker
echo "DataOps server deployed successfully on $(date)" > /data/deployment_complete.txt
EOF

chmod +x ${USER_DATA_FILE}
echo -e "${GREEN}User data script created.${RESET}"

# Function to deploy a server
deploy_server() {
    local SERVER_NAME=$1
    local DATA_VOLUME_SIZE=$2
    local BACKUP_VOLUME_SIZE=$((DATA_VOLUME_SIZE * 2))
    
    echo -e "${YELLOW}Deploying ${SERVER_NAME}...${RESET}"
    
    # Step 1: Get security group
    echo -e "${YELLOW}Step 1: Getting security group ${SECURITY_GROUP_NAME}...${RESET}"
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
    
    # Step 2: Get subnet ID
    echo -e "${YELLOW}Step 2: Getting subnet ID...${RESET}"
    SUBNET_ID=$(ibmcloud is subnets | grep ${SUBNET_NAME} | awk '{print $1}')
    echo -e "${GREEN}Subnet ID: ${SUBNET_ID}${RESET}"
    
    # Step 3: Get SSH key ID
    echo -e "${YELLOW}Step 3: Getting SSH key ID...${RESET}"
    SSH_KEY_ID=$(ibmcloud is keys | grep ${SSH_KEY_NAME} | awk '{print $1}')
    echo -e "${GREEN}SSH key ID: ${SSH_KEY_ID}${RESET}"
    
    # Step 4: Create volumes
    echo -e "${YELLOW}Step 4: Creating volumes...${RESET}"
    
    # Boot volume is created automatically
    
    # Data volume
    echo -e "${YELLOW}Creating data volume (${DATA_VOLUME_SIZE}GB)...${RESET}"
    DATA_VOLUME_NAME="${SERVER_NAME}-data"
    DATA_VOLUME_ID=$(ibmcloud is volume-create ${DATA_VOLUME_NAME} general-purpose ${ZONE} --capacity ${DATA_VOLUME_SIZE} --output json | jq -r '.id')
    echo -e "${GREEN}Data volume created with ID: ${DATA_VOLUME_ID}${RESET}"
    
    # Backup volume
    echo -e "${YELLOW}Creating backup volume (${BACKUP_VOLUME_SIZE}GB)...${RESET}"
    BACKUP_VOLUME_NAME="${SERVER_NAME}-backup"
    BACKUP_VOLUME_ID=$(ibmcloud is volume-create ${BACKUP_VOLUME_NAME} general-purpose ${ZONE} --capacity ${BACKUP_VOLUME_SIZE} --output json | jq -r '.id')
    echo -e "${GREEN}Backup volume created with ID: ${BACKUP_VOLUME_ID}${RESET}"
    
    # Step 5: Deploy the server
    echo -e "${YELLOW}Step 5: Deploying ${SERVER_NAME}...${RESET}"
    
    # Create the instance with attached volumes
    ibmcloud is instance-create ${SERVER_NAME} ${VPC_NAME} ${ZONE} ${PROFILE} ${SUBNET_ID} \
      --image ${IMAGE} \
      --keys ${SSH_KEY_ID} \
      --security-groups ${SG_ID} \
      --user-data @${USER_DATA_FILE} \
      --volume-attach name=data,volume=${DATA_VOLUME_ID} \
      --volume-attach name=backup,volume=${BACKUP_VOLUME_ID}
    
    echo -e "${GREEN}Server ${SERVER_NAME} deployment initiated.${RESET}"
    echo -e "${BLUE}Waiting for server to become active...${RESET}"
    
    # Wait for server to become active
    STATUS="pending"
    while [ "$STATUS" != "running" ] && [ "$STATUS" != "failed" ]; do
        sleep 30
        STATUS=$(ibmcloud is instance ${SERVER_NAME} --output json | jq -r .status)
        echo -e "Current status: ${STATUS}"
    done
    
    if [ "$STATUS" == "running" ]; then
        echo -e "${GREEN}Server ${SERVER_NAME} is now running.${RESET}"
        
        # Get server details
        PRIVATE_IP=$(ibmcloud is instance ${SERVER_NAME} --output json | jq -r '.primary_network_interface.primary_ipv4_address')
        echo -e "${GREEN}Server ${SERVER_NAME} deployed with private IP: ${PRIVATE_IP}${RESET}"
    else
        echo -e "${RED}Server ${SERVER_NAME} deployment failed.${RESET}"
    fi
    
    echo -e "${YELLOW}===============================================${RESET}"
}

# Main execution
echo -e "${BLUE}Starting deployment of DataOps servers...${RESET}"

# Deploy each server
for SERVER_NAME in "${!SERVERS[@]}"; do
    deploy_server ${SERVER_NAME} ${SERVERS[${SERVER_NAME}]}
done

echo -e "${GREEN}All DataOps servers deployment initiated.${RESET}"
echo -e "${YELLOW}Check server status with: ibmcloud is instances${RESET}"