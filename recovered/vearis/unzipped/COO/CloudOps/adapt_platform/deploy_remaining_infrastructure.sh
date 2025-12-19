#!/bin/bash
# deploy_remaining_infrastructure.sh - Script to deploy the remaining infrastructure after ethos GPU server
# Created by Synaptic - March 21, 2025

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}Remaining Infrastructure Deployment Script${RESET}"
echo "=================================================="
echo "This script will deploy the remaining infrastructure after the ethos GPU server."
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

# Check if ethos GPU server is running
echo -e "${YELLOW}Checking if ethos GPU server is running...${RESET}"
ETHOS_STATUS=$(ibmcloud is instance ethos --output json 2>/dev/null | jq -r '.status' 2>/dev/null || echo "not_found")

if [ "$ETHOS_STATUS" != "running" ]; then
    echo -e "${RED}Error: ethos GPU server is not running (status: ${ETHOS_STATUS}).${RESET}"
    echo "Please deploy the ethos GPU server first using deploy_ethos_gpu.sh"
    exit 1
fi

echo -e "${GREEN}ethos GPU server is running. Proceeding with remaining infrastructure deployment.${RESET}"

# Set variables
RESOURCE_GROUP="adapt"
REGION="us-south"
ZONE="us-south-2"
VPC_NAME="dataops-vpc"
SUBNET_NAME="dataops-subnet"
DB_SECURITY_GROUP_NAME="nova-db-sg"
LOGS_SECURITY_GROUP_NAME="nova-logs-sg"
ADAPT_SECURITY_GROUP_NAME="adapt-sg"
SSH_KEY_NAME="nova-ssh-key"
IMAGE="ibm-ubuntu-22-04-minimal-amd64-1"

# Database servers
DB_SERVERS=(
    "nova-db-primary:bx2-8x32:50:3000:50:3000:10:1000"
    "nova-db-graph:bx2-8x32:50:3000:40:3000:10:1000"
    "nova-db-timeseries:bx2-8x32:50:2000:30:2000:10:1000"
)

# Logging server
LOGS_SERVER="nova-logs:bx2-4x16:50:2000:100:5000"

# User data for initial setup
USER_DATA_FILE="server_user_data.sh"

# Step 1: Create security groups
echo -e "${YELLOW}Step 1: Creating security groups...${RESET}"

# Create database security group
echo "Creating ${DB_SECURITY_GROUP_NAME}..."
DB_SG_ID=$(ibmcloud is security-group-create ${DB_SECURITY_GROUP_NAME} ${VPC_NAME} --output json | jq -r '.id')
echo -e "${GREEN}Security group created with ID: ${DB_SG_ID}${RESET}"

# Create logs security group
echo "Creating ${LOGS_SECURITY_GROUP_NAME}..."
LOGS_SG_ID=$(ibmcloud is security-group-create ${LOGS_SECURITY_GROUP_NAME} ${VPC_NAME} --output json | jq -r '.id')
echo -e "${GREEN}Security group created with ID: ${LOGS_SG_ID}${RESET}"

# Create adapt security group
echo "Creating ${ADAPT_SECURITY_GROUP_NAME}..."
ADAPT_SG_ID=$(ibmcloud is security-group-create ${ADAPT_SECURITY_GROUP_NAME} ${VPC_NAME} --output json | jq -r '.id')
echo -e "${GREEN}Security group created with ID: ${ADAPT_SG_ID}${RESET}"

# Step 2: Add security group rules
echo -e "${YELLOW}Step 2: Adding security group rules...${RESET}"

# Database security group rules
echo "Adding rules to ${DB_SECURITY_GROUP_NAME}..."
ibmcloud is security-group-rule-add ${DB_SG_ID} inbound tcp --port-min 22 --port-max 22
ibmcloud is security-group-rule-add ${DB_SG_ID} inbound all
ibmcloud is security-group-rule-add ${DB_SG_ID} outbound all

# Logs security group rules
echo "Adding rules to ${LOGS_SECURITY_GROUP_NAME}..."
ibmcloud is security-group-rule-add ${LOGS_SG_ID} inbound tcp --port-min 22 --port-max 22
ibmcloud is security-group-rule-add ${LOGS_SG_ID} inbound tcp --port-min 5601 --port-max 5601
ibmcloud is security-group-rule-add ${LOGS_SG_ID} inbound tcp --port-min 9200 --port-max 9200
ibmcloud is security-group-rule-add ${LOGS_SG_ID} inbound tcp --port-min 5044 --port-max 5044
ibmcloud is security-group-rule-add ${LOGS_SG_ID} inbound all
ibmcloud is security-group-rule-add ${LOGS_SG_ID} outbound all

# Adapt security group rules
echo "Adding rules to ${ADAPT_SECURITY_GROUP_NAME}..."
ibmcloud is security-group-rule-add ${ADAPT_SG_ID} inbound tcp --port-min 22 --port-max 22
ibmcloud is security-group-rule-add ${ADAPT_SG_ID} inbound all
ibmcloud is security-group-rule-add ${ADAPT_SG_ID} outbound all

echo -e "${GREEN}Security group rules added.${RESET}"

# Step 3: Create user data script for database servers
echo -e "${YELLOW}Step 3: Creating user data script for database servers...${RESET}"
cat > db_user_data.sh << 'EOF'
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

# Format and mount log volume
mkfs.xfs /dev/vde
mkdir -p /var/log.new
echo "/dev/vde /var/log xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
rsync -av /var/log/ /var/log.new/
mount /var/log.new /var/log -o bind
umount /var/log.new
mount /dev/vde /var/log
chmod 755 /var/log

# Install Filebeat for log forwarding
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
apt-get install -y filebeat

# Configure system optimizations
cat > /etc/sysctl.d/99-db-optimizations.conf << 'EOC'
# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr

# Memory optimizations
vm.swappiness=10
EOC

sysctl -p /etc/sysctl.d/99-db-optimizations.conf

# Set CPU governor to performance
apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils

# Create deployment success marker
echo "Database server deployed successfully on $(date)" > /data/deployment_complete.txt

# Get hostname to determine which database to install
HOSTNAME=$(hostname)

if [[ "$HOSTNAME" == *"primary"* ]]; then
    # Install MongoDB and PostgreSQL
    apt-get install -y mongodb postgresql
    echo "Installed MongoDB and PostgreSQL on primary database server" >> /data/deployment_complete.txt
elif [[ "$HOSTNAME" == *"graph"* ]]; then
    # Install Neo4j
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list
    apt-get update
    apt-get install -y neo4j
    echo "Installed Neo4j on graph database server" >> /data/deployment_complete.txt
elif [[ "$HOSTNAME" == *"timeseries"* ]]; then
    # Install Redis
    apt-get install -y redis-server
    echo "Installed Redis on timeseries database server" >> /data/deployment_complete.txt
fi
EOF

chmod +x db_user_data.sh
echo -e "${GREEN}Database user data script created.${RESET}"

# Step 4: Create user data script for logging server
echo -e "${YELLOW}Step 4: Creating user data script for logging server...${RESET}"
cat > logs_user_data.sh << 'EOF'
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

# Format and mount log volume
mkfs.xfs /dev/vdd
mkdir -p /var/log.new
echo "/dev/vdd /var/log xfs defaults,noatime,nodiratime 0 0" >> /etc/fstab
rsync -av /var/log/ /var/log.new/
mount /var/log.new /var/log -o bind
umount /var/log.new
mount /dev/vdd /var/log
chmod 755 /var/log

# Install ELK stack
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
apt-get install -y elasticsearch kibana logstash

# Install Prometheus, Grafana, and Alertmanager
apt-get install -y apt-transport-https software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | tee /etc/apt/sources.list.d/grafana.list
apt-get update
apt-get install -y prometheus prometheus-alertmanager grafana

# Configure system optimizations
cat > /etc/sysctl.d/99-logs-optimizations.conf << 'EOC'
# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr

# Memory optimizations
vm.swappiness=10
EOC

sysctl -p /etc/sysctl.d/99-logs-optimizations.conf

# Set CPU governor to performance
apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils

# Start services
systemctl enable elasticsearch kibana logstash prometheus grafana-server
systemctl start elasticsearch kibana logstash prometheus grafana-server

# Create deployment success marker
echo "Logging server deployed successfully on $(date)" > /var/log/deployment_complete.txt
EOF

chmod +x logs_user_data.sh
echo -e "${GREEN}Logging user data script created.${RESET}"

# Step 5: Deploy database servers
echo -e "${YELLOW}Step 5: Deploying database servers...${RESET}"
SUBNET_ID=$(ibmcloud is subnets | grep ${SUBNET_NAME} | awk '{print $1}')
SSH_KEY_ID=$(ibmcloud is keys | grep ${SSH_KEY_NAME} | awk '{print $1}')

for DB_SERVER in "${DB_SERVERS[@]}"; do
    # Parse server details
    IFS=':' read -r SERVER_NAME PROFILE BOOT_SIZE BOOT_IOPS DATA_SIZE DATA_IOPS LOG_SIZE LOG_IOPS <<< "${DB_SERVER}"
    
    echo "Deploying ${SERVER_NAME}..."
    
    # Create boot volume
    echo "Creating boot volume..."
    BOOT_VOLUME_NAME="${SERVER_NAME}-boot"
    BOOT_VOLUME_ID=$(ibmcloud is volume-create ${BOOT_VOLUME_NAME} general-purpose ${BOOT_SIZE} --iops ${BOOT_IOPS} --zone ${ZONE} --output json | jq -r '.id')
    
    # Create data volume
    echo "Creating data volume..."
    DATA_VOLUME_NAME="${SERVER_NAME}-data"
    DATA_VOLUME_ID=$(ibmcloud is volume-create ${DATA_VOLUME_NAME} general-purpose ${DATA_SIZE} --iops ${DATA_IOPS} --zone ${ZONE} --output json | jq -r '.id')
    
    # Create log volume
    echo "Creating log volume..."
    LOG_VOLUME_NAME="${SERVER_NAME}-log"
    LOG_VOLUME_ID=$(ibmcloud is volume-create ${LOG_VOLUME_NAME} general-purpose ${LOG_SIZE} --iops ${LOG_IOPS} --zone ${ZONE} --output json | jq -r '.id')
    
    # Deploy server
    ibmcloud is instance-create ${SERVER_NAME} ${VPC_NAME} ${ZONE} ${PROFILE} ${SUBNET_ID} \
      --image ${IMAGE} \
      --keys ${SSH_KEY_ID} \
      --security-groups ${DB_SG_ID} \
      --user-data @db_user_data.sh \
      --volume-attach name=data,volume=${DATA_VOLUME_ID} \
      --volume-attach name=logs,volume=${LOG_VOLUME_ID}
    
    echo -e "${GREEN}${SERVER_NAME} deployment initiated.${RESET}"
done

# Step 6: Deploy logging server
echo -e "${YELLOW}Step 6: Deploying logging server...${RESET}"
IFS=':' read -r SERVER_NAME PROFILE BOOT_SIZE BOOT_IOPS LOG_SIZE LOG_IOPS <<< "${LOGS_SERVER}"

# Create boot volume
echo "Creating boot volume..."
BOOT_VOLUME_NAME="${SERVER_NAME}-boot"
BOOT_VOLUME_ID=$(ibmcloud is volume-create ${BOOT_VOLUME_NAME} general-purpose ${BOOT_SIZE} --iops ${BOOT_IOPS} --zone ${ZONE} --output json | jq -r '.id')

# Create log volume
echo "Creating log volume..."
LOG_VOLUME_NAME="${SERVER_NAME}-log"
LOG_VOLUME_ID=$(ibmcloud is volume-create ${LOG_VOLUME_NAME} general-purpose ${LOG_SIZE} --iops ${LOG_IOPS} --zone ${ZONE} --output json | jq -r '.id')

# Deploy server
ibmcloud is instance-create ${SERVER_NAME} ${VPC_NAME} ${ZONE} ${PROFILE} ${SUBNET_ID} \
  --image ${IMAGE} \
  --keys ${SSH_KEY_ID} \
  --security-groups ${LOGS_SG_ID} \
  --user-data @logs_user_data.sh \
  --volume-attach name=logs,volume=${LOG_VOLUME_ID}

echo -e "${GREEN}${SERVER_NAME} deployment initiated.${RESET}"

# Step 7: Rename adapt3 to adapt
echo -e "${YELLOW}Step 7: Renaming adapt3 to adapt...${RESET}"
echo "Note: This step requires manual coordination with the operations team."
echo "Please follow these steps:"
echo "1. Coordinate with operations team for the rename process"
echo "2. Update DNS and other references"
echo "3. Apply the adapt-sg security group to the server"
echo ""
echo "Command to apply security group (after rename):"
echo "ibmcloud is instance-network-interface-update adapt <network_interface_id> --security-groups ${ADAPT_SG_ID}"

# Step 8: Monitor deployment
echo -e "${YELLOW}Step 8: Monitoring deployment status...${RESET}"
echo "Checking server status every 30 seconds..."

# Array of servers to monitor
SERVERS=("nova-db-primary" "nova-db-graph" "nova-db-timeseries" "nova-logs")
DEPLOYED=()

while [ ${#DEPLOYED[@]} -lt ${#SERVERS[@]} ]; do
    for SERVER in "${SERVERS[@]}"; do
        # Skip if already deployed
        if [[ " ${DEPLOYED[@]} " =~ " ${SERVER} " ]]; then
            continue
        fi
        
        STATUS=$(ibmcloud is instance ${SERVER} --output json 2>/dev/null | jq -r '.status' 2>/dev/null || echo "not_found")
        echo "${SERVER} status: ${STATUS}"
        
        if [ "${STATUS}" == "running" ]; then
            echo -e "${GREEN}${SERVER} is now running!${RESET}"
            DEPLOYED+=("${SERVER}")
        elif [ "${STATUS}" == "failed" ]; then
            echo -e "${RED}${SERVER} deployment failed. Please check the IBM Cloud console for details.${RESET}"
        fi
    done
    
    # Break if all servers are deployed
    if [ ${#DEPLOYED[@]} -eq ${#SERVERS[@]} ]; then
        break
    fi
    
    sleep 30
done

echo -e "${GREEN}All servers deployed successfully!${RESET}"
echo "=================================================="
echo "Server Details:"

for SERVER in "${SERVERS[@]}"; do
    SERVER_DETAILS=$(ibmcloud is instance ${SERVER} --output json)
    PRIVATE_IP=$(echo ${SERVER_DETAILS} | jq -r '.primary_network_interface.primary_ipv4_address')
    
    echo "${SERVER}: ${PRIVATE_IP}"
done

echo ""
echo "Next steps:"
echo "1. Verify server functionality by SSH to each server"
echo "2. Check deployment logs: /data/deployment_complete.txt or /var/log/deployment_complete.txt"
echo "3. Configure monitoring and alerts"
echo "4. Complete documentation"
echo ""
echo "For detailed information, refer to adapt_platform/implementation_plan.md"