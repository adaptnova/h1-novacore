#!/bin/bash
# component_check.sh - Quick verification of critical DataOps components
# Version: 1.0
# Date: April 17, 2025
# Author: Catalyst (Nova #95)
# Usage: ./component_check.sh

echo "====== DataOps Infrastructure Component Check ======"
echo "Date: $(date)"
echo ""

# Set up color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check a component
check_component() {
  local server=$1
  local name=$2
  local command=$3
  
  echo -e "\n==== Checking $name on $server ===="
  if ssh -o ConnectTimeout=5 x@$server "$command" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ $name is operational${NC}"
    return 0
  else
    echo -e "${RED}✗ $name failed check${NC}"
    echo "Command used: ssh x@$server '$command'"
    return 1
  fi
}

# Function to check server connectivity
check_server() {
  local server=$1
  local server_name=$2
  
  echo -e "\n==== Checking $server_name Server ($server) ===="
  
  if ping -c 1 $server > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Network connectivity to $server successful${NC}"
    if ssh -o ConnectTimeout=3 -o BatchMode=no -o StrictHostKeyChecking=no x@$server 'echo "SSH Connection Successful"' > /dev/null 2>&1; then
      echo -e "${GREEN}✓ SSH connectivity to $server successful${NC}"
      return 0
    else
      echo -e "${RED}✗ SSH connectivity to $server failed${NC}"
      return 1
    fi
  else
    echo -e "${RED}✗ Network connectivity to $server failed${NC}"
    return 2
  fi
}

echo -e "${BLUE}[INFO]${NC} Checking server connectivity..."
# Check servers
check_server "10.240.8.5" "Primary"
check_server "10.240.1.7" "Vector"
check_server "10.240.1.9" "TimeSeries"
check_server "10.240.1.11" "GPU"

echo -e "\n${BLUE}[INFO]${NC} Checking database components..."

# Check primary server components
echo -e "\n${YELLOW}Primary Server Components:${NC}"
check_component "10.240.8.5" "PostgreSQL" "systemctl status postgresql.service"
check_component "10.240.8.5" "PostgreSQL Connection" "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT 'Connection successful';\""
check_component "10.240.8.5" "Redis" "systemctl status redis-server.service"
check_component "10.240.8.5" "Redis Connection" "redis-cli ping | grep PONG"
check_component "10.240.8.5" "MongoDB" "systemctl status mongod.service"

# Check vector server components
echo -e "\n${YELLOW}Vector Server Components:${NC}"
check_component "10.240.1.7" "Milvus" "systemctl status milvus.service"
check_component "10.240.1.7" "Milvus Connection" "curl -s http://localhost:19530/healthz | grep OK"
check_component "10.240.1.7" "Weaviate" "systemctl status weaviate.service"

# Check timeseries server components
echo -e "\n${YELLOW}TimeSeries Server Components:${NC}"
check_component "10.240.1.9" "Elasticsearch" "systemctl status elasticsearch.service"
check_component "10.240.1.9" "Elasticsearch Connection" "curl -s http://localhost:9200/ | grep 'You Know, for Search'"
check_component "10.240.1.9" "Kibana" "systemctl status kibana.service"
check_component "10.240.1.9" "InfluxDB" "systemctl status influxdb.service"

# Check GPU server components
echo -e "\n${YELLOW}GPU Server Components:${NC}"
check_component "10.240.1.11" "ChromaDB" "systemctl status chroma.service"
check_component "10.240.1.11" "ChromaDB Connection" "curl -s http://localhost:8000/api/v1/heartbeat | grep ok"
check_component "10.240.1.11" "TigerGraph" "systemctl status tigergraph.service"
check_component "10.240.1.11" "FAISS Server" "systemctl status faiss-server.service"

echo -e "\n${GREEN}====== Component Check Complete ======${NC}"
echo "Check the output above for any failed components."
echo "For detailed information about failed components and how to fix them,"
echo "refer to the DataOps_failed.md document."
