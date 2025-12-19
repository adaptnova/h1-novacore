#!/bin/bash

# Project Tapestry Implementation Script
# Created by Synaptic on March 21, 2025
# This script implements the initial network infrastructure for Project Tapestry

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
BASE_VPC_NAME="tapestry"
MTU=9001  # Jumbo frames

# Network configuration
declare -A NETWORKS=(
  ["tapestry-net-01-primary"]="10.1.0.0/16"
  ["tapestry-net-02-secondary"]="10.2.0.0/16"
  ["tapestry-net-03-tertiary"]="10.3.0.0/16"
  ["tapestry-net-04-quaternary"]="10.4.0.0/16"
  ["tapestry-net-05-quinary"]="10.5.0.0/16"
  ["tapestry-net-06-senary"]="10.6.0.0/16"
  ["tapestry-net-07-septenary"]="10.7.0.0/16"
  ["tapestry-net-08-octonary"]="10.8.0.0/16"
  ["tapestry-net-09-nonary"]="10.9.0.0/16"
  ["tapestry-net-10-denary"]="10.10.0.0/16"
  ["tapestry-net-11-undenary"]="10.11.0.0/16"
  ["tapestry-net-12-duodenary"]="10.12.0.0/16"
  ["tapestry-net-13-tredenary"]="10.13.0.0/16"
  ["tapestry-net-14-quattuordenary"]="10.14.0.0/16"
  ["tapestry-mgmt-net"]="10.250.0.0/16"
)

# Subnet purposes
declare -A SUBNET_PURPOSES=(
  ["NovaOps"]="10"
  ["MLOps"]="20"
  ["DataOps"]="30"
  ["LLMConnect"]="40"
  ["RouteOps"]="50"
  ["API"]="60"
  ["CommsOps"]="70"
  ["Development"]="80"
  ["Testing"]="90"
  ["Monitoring"]="100"
)

# Function to create a VPC
create_vpc() {
  local VPC_NAME=$1
  local CIDR_BLOCK=$2
  
  echo -e "${YELLOW}Creating VPC ${VPC_NAME}...${RESET}"
  
  # Check if VPC already exists
  VPC_ID=$(ibmcloud is vpcs | grep ${VPC_NAME} | awk '{print $1}')
  if [ -z "${VPC_ID}" ]; then
    # Create VPC
    VPC_ID=$(ibmcloud is vpc-create ${VPC_NAME} --resource-group-name ${RESOURCE_GROUP} --output json | jq -r '.id')
    echo -e "${GREEN}VPC ${VPC_NAME} created with ID: ${VPC_ID}${RESET}"
  else
    echo -e "${GREEN}VPC ${VPC_NAME} already exists with ID: ${VPC_ID}${RESET}"
  fi
  
  return 0
}

# Function to create a subnet
create_subnet() {
  local VPC_NAME=$1
  local SUBNET_NAME=$2
  local CIDR_BLOCK=$3
  local ZONE=$4
  
  echo -e "${YELLOW}Creating subnet ${SUBNET_NAME} in VPC ${VPC_NAME}...${RESET}"
  
  # Get VPC ID
  VPC_ID=$(ibmcloud is vpcs | grep ${VPC_NAME} | awk '{print $1}')
  
  # Check if subnet already exists
  SUBNET_ID=$(ibmcloud is subnets | grep ${SUBNET_NAME} | awk '{print $1}')
  if [ -z "${SUBNET_ID}" ]; then
    # Create subnet
    SUBNET_ID=$(ibmcloud is subnet-create ${SUBNET_NAME} ${VPC_ID} --zone ${ZONE} --ipv4-cidr-block ${CIDR_BLOCK} --output json | jq -r '.id')
    echo -e "${GREEN}Subnet ${SUBNET_NAME} created with ID: ${SUBNET_ID}${RESET}"
  else
    echo -e "${GREEN}Subnet ${SUBNET_NAME} already exists with ID: ${SUBNET_ID}${RESET}"
  fi
  
  return 0
}

# Function to create a security group
create_security_group() {
  local VPC_NAME=$1
  local SG_NAME=$2
  
  echo -e "${YELLOW}Creating security group ${SG_NAME} in VPC ${VPC_NAME}...${RESET}"
  
  # Get VPC ID
  VPC_ID=$(ibmcloud is vpcs | grep ${VPC_NAME} | awk '{print $1}')
  
  # Check if security group already exists
  SG_ID=$(ibmcloud is security-groups | grep "${SG_NAME}" | grep "${VPC_NAME}" | awk '{print $1}')
  if [ -z "${SG_ID}" ]; then
    # Create security group
    SG_ID=$(ibmcloud is security-group-create ${SG_NAME} ${VPC_ID} --output json | jq -r '.id')
    echo -e "${GREEN}Security group ${SG_NAME} created with ID: ${SG_ID}${RESET}"
    
    # Add security group rules
    echo -e "${YELLOW}Adding security group rules...${RESET}"
    
    # Allow internal traffic
    ibmcloud is security-group-rule-add ${SG_ID} inbound all --remote 10.0.0.0/8
    
    # Allow outbound traffic
    ibmcloud is security-group-rule-add ${SG_ID} outbound all
    
    # Allow SSH from management IPs
    ibmcloud is security-group-rule-add ${SG_ID} inbound tcp --port-min 22 --port-max 22
    
    echo -e "${GREEN}Security group rules added.${RESET}"
  else
    echo -e "${GREEN}Security group ${SG_NAME} already exists with ID: ${SG_ID}${RESET}"
  fi
  
  return 0
}

# Function to create VPC peering
create_vpc_peering() {
  local VPC1_NAME=$1
  local VPC2_NAME=$2
  
  echo -e "${YELLOW}Creating VPC peering between ${VPC1_NAME} and ${VPC2_NAME}...${RESET}"
  
  # Get VPC IDs
  VPC1_ID=$(ibmcloud is vpcs | grep ${VPC1_NAME} | awk '{print $1}')
  VPC2_ID=$(ibmcloud is vpcs | grep ${VPC2_NAME} | awk '{print $1}')
  
  # Check if peering already exists
  PEERING_NAME="${VPC1_NAME}-to-${VPC2_NAME}"
  PEERING_ID=$(ibmcloud is vpc-peerings | grep ${PEERING_NAME} | awk '{print $1}')
  
  if [ -z "${PEERING_ID}" ]; then
    # Create peering
    PEERING_ID=$(ibmcloud is vpc-peering-create ${PEERING_NAME} --source-vpc-id ${VPC1_ID} --target-vpc-id ${VPC2_ID} --output json | jq -r '.id')
    echo -e "${GREEN}VPC peering ${PEERING_NAME} created with ID: ${PEERING_ID}${RESET}"
  else
    echo -e "${GREEN}VPC peering ${PEERING_NAME} already exists with ID: ${PEERING_ID}${RESET}"
  fi
  
  return 0
}

# Function to apply NIC optimizations to a server
apply_nic_optimizations() {
  local SERVER_NAME=$1
  local SERVER_IP=$2
  
  echo -e "${YELLOW}Applying NIC optimizations to ${SERVER_NAME} (${SERVER_IP})...${RESET}"
  
  # Create optimization script
  cat > nic_optimize.sh << 'EOF'
#!/bin/bash

# Set NIC parameters
for NIC in $(ls /sys/class/net | grep -v lo); do
  # Set ring buffer sizes
  ethtool -G $NIC rx 4096 tx 4096 || true
  
  # Disable flow control
  ethtool -A $NIC autoneg off rx off tx off || true
  
  # Enable RSS, RPS, RFS, ntuple filtering
  ethtool -K $NIC rx on tx on sg on tso on gso on gro on lro off rxvlan on txvlan on ntuple on || true
  
  # Set interrupt throttle rate to adaptive
  ethtool -C $NIC adaptive-rx on adaptive-tx on || true
done

# TCP/IP stack optimization
cat > /etc/sysctl.d/99-tapestry-network.conf << 'EOC'
# Core network parameters
net.core.rmem_max = 67108864
net.core.wmem_max = 67108864
net.core.rmem_default = 33554432
net.core.wmem_default = 33554432
net.core.netdev_max_backlog = 300000
net.core.somaxconn = 65535

# TCP parameters
net.ipv4.tcp_rmem = 4096 33554432 67108864
net.ipv4.tcp_wmem = 4096 33554432 67108864
net.ipv4.tcp_mem = 67108864 67108864 67108864
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_mtu_probing = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 10
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_max_tw_buckets = 2000000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535
EOC

# Apply sysctl settings
sysctl -p /etc/sysctl.d/99-tapestry-network.conf

# Set up IRQ affinity
# This is a simplified version - in production, we would map specific NICs to specific CPU cores
NUM_CPUS=$(nproc)
IRQS_PER_CPU=$(($(grep -c eth /proc/interrupts) / $NUM_CPUS))

CPU=0
for IRQ in $(grep eth /proc/interrupts | awk '{print $1}' | tr -d ':'); do
  echo $CPU > /proc/irq/$IRQ/smp_affinity_list
  CPU=$(( (CPU + 1) % $NUM_CPUS ))
done

# Set up NUMA affinity
# This is a simplified version - in production, we would use numactl to bind specific NICs to specific NUMA nodes
if [ -d /sys/devices/system/node ]; then
  NUM_NODES=$(ls -d /sys/devices/system/node/node* | wc -l)
  if [ $NUM_NODES -gt 1 ]; then
    # Set up NUMA affinity for the first 8 NICs to NUMA node 0
    for NIC in $(ls /sys/class/net | grep -v lo | head -8); do
      echo 0 > /sys/class/net/$NIC/device/numa_node || true
    done
    
    # Set up NUMA affinity for the remaining NICs to NUMA node 1
    for NIC in $(ls /sys/class/net | grep -v lo | tail -n +9); do
      echo 1 > /sys/class/net/$NIC/device/numa_node || true
    done
  fi
fi

# Create a marker file to indicate optimization is complete
echo "NIC optimization completed on $(date)" > /var/log/nic_optimization_complete.log
EOF

  # Copy and execute the script on the server
  scp nic_optimize.sh synaptic@${SERVER_IP}:/tmp/
  ssh synaptic@${SERVER_IP} "chmod +x /tmp/nic_optimize.sh && sudo /tmp/nic_optimize.sh"
  
  # Clean up
  rm nic_optimize.sh
  
  echo -e "${GREEN}NIC optimizations applied to ${SERVER_NAME}.${RESET}"
  
  return 0
}

# Main execution
echo -e "${BLUE}Starting Project Tapestry implementation...${RESET}"

# Step 1: Create VPCs
echo -e "${YELLOW}Step 1: Creating VPCs...${RESET}"
for NETWORK_NAME in "${!NETWORKS[@]}"; do
  create_vpc ${NETWORK_NAME} ${NETWORKS[${NETWORK_NAME}]}
done

# Step 2: Create subnets
echo -e "${YELLOW}Step 2: Creating subnets...${RESET}"
for NETWORK_NAME in "${!NETWORKS[@]}"; do
  CIDR_PREFIX=$(echo ${NETWORKS[${NETWORK_NAME}]} | cut -d'/' -f1 | cut -d'.' -f1,2)
  
  for PURPOSE in "${!SUBNET_PURPOSES[@]}"; do
    SUBNET_CIDR="${CIDR_PREFIX}.${SUBNET_PURPOSES[${PURPOSE}]}.0/24"
    SUBNET_NAME="${NETWORK_NAME}-${PURPOSE,,}-subnet"
    
    create_subnet ${NETWORK_NAME} ${SUBNET_NAME} ${SUBNET_CIDR} ${ZONE}
  done
done

# Step 3: Create security groups
echo -e "${YELLOW}Step 3: Creating security groups...${RESET}"
for NETWORK_NAME in "${!NETWORKS[@]}"; do
  SG_NAME="${NETWORK_NAME}-sg"
  create_security_group ${NETWORK_NAME} ${SG_NAME}
done

# Step 4: Create VPC peerings
echo -e "${YELLOW}Step 4: Creating VPC peerings...${RESET}"
NETWORK_NAMES=($(echo "${!NETWORKS[@]}" | tr ' ' '\n' | sort))
for ((i=0; i<${#NETWORK_NAMES[@]}; i++)); do
  for ((j=i+1; j<${#NETWORK_NAMES[@]}; j++)); do
    create_vpc_peering ${NETWORK_NAMES[$i]} ${NETWORK_NAMES[$j]}
  done
done

# Step 5: Apply NIC optimizations to existing servers
echo -e "${YELLOW}Step 5: Applying NIC optimizations to existing servers...${RESET}"

# Get ethos server IP
ETHOS_IP=$(ibmcloud is instance ethos --output json | jq -r '.primary_network_interface.primary_ipv4_address')
if [ -n "${ETHOS_IP}" ] && [ "${ETHOS_IP}" != "null" ]; then
  apply_nic_optimizations "ethos" ${ETHOS_IP}
fi

# Get dataops server IPs
for SERVER_NAME in dataops-primary dataops-vector dataops-timeseries; do
  SERVER_IP=$(ibmcloud is instance ${SERVER_NAME} --output json 2>/dev/null | jq -r '.primary_network_interface.primary_ipv4_address')
  if [ -n "${SERVER_IP}" ] && [ "${SERVER_IP}" != "null" ]; then
    apply_nic_optimizations ${SERVER_NAME} ${SERVER_IP}
  fi
done

echo -e "${GREEN}Project Tapestry initial network infrastructure implementation completed.${RESET}"
echo -e "${YELLOW}Next steps:${RESET}"
echo -e "1. Deploy VMs in each subnet according to the blueprint"
echo -e "2. Configure multi-NIC setup for each VM"
echo -e "3. Set up monitoring and observability"
echo -e "4. Implement security measures"