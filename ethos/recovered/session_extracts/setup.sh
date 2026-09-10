#!/bin/bash

# Setup script for GPU deployment tools
# Author: Ethos

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo -e "${GREEN}Starting setup for GPU deployment tools...${NC}"

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Python 3 is required but not found${NC}"
    exit 1
fi

# Check for virtual environment
if [ -d "aiml_env" ]; then
    echo -e "${YELLOW}Virtual environment exists. Removing...${NC}"
    rm -rf aiml_env
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python3 -m venv aiml_env
source aiml_env/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Check for gcloud CLI
echo -e "\n${YELLOW}Checking for gcloud CLI...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}gcloud CLI not found${NC}"
    echo "Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check for kubectl
echo -e "\n${YELLOW}Checking for kubectl...${NC}"
if ! command -v kubectl &> /dev/null; then
    echo -e "${YELLOW}Installing kubectl...${NC}"
    gcloud components install kubectl
fi

# Setup git hooks
echo -e "\n${YELLOW}Setting up git hooks...${NC}"
if [ -d ".git" ]; then
    pre-commit install
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p configs
mkdir -p data

# Make scripts executable
echo -e "\n${YELLOW}Making scripts executable...${NC}"
chmod +x deploy_gke_gpu.py
chmod +x apply_k8s_manifests.py
chmod +x track_quotas.py

# Create config file if it doesn't exist
if [ ! -f "configs/gpu_config.yaml" ]; then
    echo -e "\n${YELLOW}Creating default config file...${NC}"
    cat > configs/gpu_config.yaml << EOL
project_id: "a-d-a-p-t"
region: "us-central1"
zones:
  - "us-central1-a"
  - "us-central1-b"
  - "us-central1-c"
cluster_name: "ml-cluster-1"
network_name: "ml-network"
subnet_name: "ml-subnet"
EOL
fi

# Setup environment variables
echo -e "\n${YELLOW}Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << EOL
# GCP Configuration
export PROJECT_ID="a-d-a-p-t"
export REGION="us-central1"
export ZONE="us-central1-a"

# Kubernetes Configuration
export CLUSTER_NAME="ml-cluster-1"
export NETWORK_NAME="ml-network"
export SUBNET_NAME="ml-subnet"

# GPU Configuration
export GPU_DRIVER_VERSION="525.85.12"
export CUDA_VERSION="12.0"

# Monitoring Configuration
export ENABLE_MONITORING="true"
export ENABLE_LOGGING="true"

# Development Configuration
export PYTHONPATH="${PYTHONPATH}:${PWD}"
export KUBECONFIG="${PWD}/configs/kubeconfig"
EOL
fi

# Source environment variables
echo -e "\n${YELLOW}Sourcing environment variables...${NC}"
source .env

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 -c "import kubernetes; import google.cloud.container; import yaml; print('Dependencies verified')"

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "\nNext steps:"
echo -e "1. Update configs/gpu_config.yaml with your settings"
echo -e "2. Update .env with your environment variables"
echo -e "3. Run 'source aiml_env/bin/activate' to activate the virtual environment"
echo -e "4. Use deploy_gke_gpu.py to create your cluster"
echo -e "5. Use apply_k8s_manifests.py to deploy workloads"

# Print current configuration
echo -e "\n${YELLOW}Current configuration:${NC}"
echo -e "Project ID: ${PROJECT_ID}"
echo -e "Region: ${REGION}"
echo -e "Cluster Name: ${CLUSTER_NAME}"
echo -e "Python Environment: $(which python3)"
echo -e "Kubernetes Version: $(kubectl version --client --short 2>/dev/null || echo 'Not installed')"
echo -e "gcloud Version: $(gcloud --version | head -n 1)"
