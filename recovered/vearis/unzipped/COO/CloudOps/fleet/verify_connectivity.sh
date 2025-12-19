#!/bin/bash
# Script to verify connectivity to CloudOps Fleet servers
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to test SSH connectivity
test_ssh() {
    local host=$1
    local user=$2
    local ip=$3
    
    echo -e "${YELLOW}Testing SSH connectivity to $host ($ip) as $user...${NC}"
    
    # Try to connect using the SSH config alias
    if ssh -o BatchMode=yes -o ConnectTimeout=5 $host "hostname && whoami && sudo -n whoami"; then
        echo -e "${GREEN}✓ Successfully connected to $host as $user with sudo privileges${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to connect to $host as $user${NC}"
        
        # Try direct connection to IP
        echo -e "${YELLOW}Trying direct connection to $ip as $user...${NC}"
        if ssh -o BatchMode=yes -o ConnectTimeout=5 $user@$ip "hostname && whoami && sudo -n whoami"; then
            echo -e "${GREEN}✓ Successfully connected to $ip as $user with sudo privileges${NC}"
            return 0
        else
            echo -e "${RED}✗ Failed to connect to $ip as $user${NC}"
            return 1
        fi
    fi
}

# Main script
echo "=== CloudOps Fleet Connectivity Verification ==="
echo "This script will verify SSH connectivity to all servers"
echo "and check if sudo privileges are working correctly."
echo "=================================================="

# Test connectivity to Ethos server
test_ssh "ethos" "ethos" "10.240.0.5"
ethos_status=$?

# Test connectivity to DataOps servers
test_ssh "dataops-primary" "vertex" "10.240.0.6"
primary_status=$?

test_ssh "dataops-timeseries" "vertex" "10.240.0.8"
timeseries_status=$?

test_ssh "dataops-vector" "vertex" "10.240.0.7"
vector_status=$?

# Summary
echo "=================================================="
echo "Connectivity Verification Summary:"
echo "=================================================="

if [ $ethos_status -eq 0 ]; then
    echo -e "${GREEN}✓ Ethos server: Connected successfully${NC}"
else
    echo -e "${RED}✗ Ethos server: Connection failed${NC}"
fi

if [ $primary_status -eq 0 ]; then
    echo -e "${GREEN}✓ DataOps Primary server: Connected successfully${NC}"
else
    echo -e "${RED}✗ DataOps Primary server: Connection failed${NC}"
fi

if [ $timeseries_status -eq 0 ]; then
    echo -e "${GREEN}✓ DataOps Timeseries server: Connected successfully${NC}"
else
    echo -e "${RED}✗ DataOps Timeseries server: Connection failed${NC}"
fi

if [ $vector_status -eq 0 ]; then
    echo -e "${GREEN}✓ DataOps Vector server: Connected successfully${NC}"
else
    echo -e "${RED}✗ DataOps Vector server: Connection failed${NC}"
fi

# Overall status
if [ $ethos_status -eq 0 ] && [ $primary_status -eq 0 ] && [ $timeseries_status -eq 0 ] && [ $vector_status -eq 0 ]; then
    echo -e "\n${GREEN}All connections successful! User setup and SSH configuration are working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}Some connections failed. Please check the user setup and SSH configuration.${NC}"
    exit 1
fi