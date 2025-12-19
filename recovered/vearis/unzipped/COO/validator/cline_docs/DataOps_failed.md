# DataOps Failed Components Report

**Date:** April 17, 2025
**Author:** Catalyst (Nova #95)
**Last Updated:** April 17, 04:30 AM MST

This document provides information about components that failed validation during the DataOps infrastructure deep validation, along with commands to manually verify and fix their status.

## Deep Validation Results Summary

The deep component validation has identified several issues that require attention:

| Component | Server | Status | Issue |
|-----------|--------|--------|-------|
| PostgreSQL | Primary (10.240.8.5) | Service Running, Connection Failed | Authentication failure with password |
| Redis | Primary (10.240.8.5) | Service Not Running | Service in restart loop |
| Elasticsearch | TimeSeries (10.240.1.9) | Service Not Found | Not installed or improperly configured |

## PostgreSQL Issues

### Primary Server (10.240.8.5)

**Issue:** PostgreSQL service is running but connection fails with authentication error
**Exact Error:** "FATAL: password authentication failed for user 'postgres'"
**Impact:** Database operations will fail

**Verification Commands:**
```bash
# Check service status
ssh x@10.240.8.5 'systemctl status postgresql.service'

# Test connection with current password (failing)
ssh x@10.240.8.5 'PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "SELECT version();"'
```

**Recommended Fix:**
1. Connect to the server:
```bash
ssh x@10.240.8.5
```

2. Reset postgres user password:
```bash
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'nova_secure_password';"
```

3. Verify pg_hba.conf allows password authentication:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```
Ensure you have this line:
```
host    all             all             127.0.0.1/32            md5
```

4. Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Redis Issues

### Primary Server (10.240.8.5)

**Issue:** Redis service is failing to start properly
**Impact:** Cache operations will fail

**Verification Commands:**
```bash
# Check service status (shows auto-restart loop)
ssh x@10.240.8.5 'systemctl status redis-server.service'

# Check Redis logs
ssh x@10.240.8.5 'sudo journalctl -u redis-server -n 50'
```

**Root Cause:** Based on the service status log, the service fails at the shutdown step:
```
ExecStop=/usr/bin/redis-cli -a nova_secure_password shutdown (code=exited status=1/FAILURE)
```

**Recommended Fix:**
1. Connect to the server:
```bash
ssh x@10.240.8.5
```

2. Check Redis configuration:
```bash
sudo nano /etc/redis/redis.conf
```

3. Ensure password is correctly set:
```
# Find requirepass directive
requirepass nova_secure_password
```

4. Check bind and protected-mode settings:
```
bind 127.0.0.1 ::1
protected-mode yes
```

5. Restart Redis:
```bash
sudo systemctl restart redis-server
```

## Elasticsearch Issues

### TimeSeries Server (10.240.1.9)

**Issue:** Elasticsearch service not found
**Impact:** Search functionality unavailable

**Verification Commands:**
```bash
# Check if service exists
ssh x@10.240.1.9 'systemctl list-unit-files | grep elastic'

# Check if binary exists
ssh x@10.240.1.9 'which elasticsearch || echo "Not installed"'
```

**Recommended Fix:**
1. Connect to the server:
```bash
ssh x@10.240.1.9
```

2. Install Elasticsearch if not present:
```bash
# Import the Elasticsearch GPG key
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

# Add Elasticsearch repository
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

# Update and install
sudo apt update
sudo apt install elasticsearch
```

3. Configure basic settings:
```bash
sudo nano /etc/elasticsearch/elasticsearch.yml
```
Ensure these settings:
```yaml
cluster.name: dataops-cluster
node.name: timeseries-node
network.host: 0.0.0.0
discovery.type: single-node
```

4. Start and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
```

## Deep Validation Script Usage

To run a comprehensive deep validation:

```bash
cd /data-nova/ax/COO/validator
./cline_docs/validation_scripts/deep_component_validator.sh
```

This script performs actual data operations, verifies service configurations, and checks performance metrics to thoroughly validate all components.

## Database Component Issues

### PostgreSQL on Primary Server

**Verification Commands:**
```bash
# Check service status
ssh x@10.240.8.5 'systemctl status postgresql.service'

# Test connection
ssh x@10.240.8.5 'PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "SELECT version();"'
```

### Redis on Primary Server

**Verification Commands:**
```bash
# Check service status
ssh x@10.240.8.5 'systemctl status redis-server.service'

# Test connection
ssh x@10.240.8.5 'redis-cli ping'
```

### Milvus on Vector Server (10.240.1.7)

**Verification Commands:**
```bash
# Check service status
ssh x@10.240.1.7 'systemctl status milvus.service'

# Test connection
ssh x@10.240.1.7 'curl -s http://localhost:19530/healthz'
```

### Elasticsearch on TimeSeries Server (10.240.1.9)

**Verification Commands:**
```bash
# Check service status
ssh x@10.240.1.9 'systemctl status elasticsearch.service'

# Test connection
ssh x@10.240.1.9 'curl -s http://localhost:9200/'
```

### ChromaDB on GPU Server (10.240.1.11)

**Verification Commands:**
```bash
# Check service status
ssh x@10.240.1.11 'systemctl status chroma.service'

# Test connection
ssh x@10.240.1.11 'curl -s http://localhost:8000/api/v1/heartbeat'
```

## Quick Component Check Script

```bash
#!/bin/bash
# component_check.sh - Quick verification of critical DataOps components
# Usage: ./component_check.sh

echo "====== DataOps Infrastructure Component Check ======"
echo "Date: $(date)"
echo ""

# Set up color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
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

# Check server connectivity
for server in "10.240.8.5" "10.240.1.7" "10.240.1.9" "10.240.1.11"; do
  if ping -c 1 $server > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Network connectivity to $server successful${NC}"
    if ssh -o ConnectTimeout=3 -o BatchMode=no -o StrictHostKeyChecking=no x@$server 'echo "SSH Connection Successful"' > /dev/null 2>&1; then
      echo -e "${GREEN}✓ SSH connectivity to $server successful${NC}"
    else
      echo -e "${RED}✗ SSH connectivity to $server failed${NC}"
    fi
  else
    echo -e "${RED}✗ Network connectivity to $server failed${NC}"
  fi
done

# Check primary server components
check_component "10.240.8.5" "PostgreSQL" "systemctl status postgresql.service"
check_component "10.240.8.5" "Redis" "redis-cli ping | grep PONG"

# Check vector server components
check_component "10.240.1.7" "Milvus" "curl -s http://localhost:19530/healthz | grep OK"

# Check timeseries server components
check_component "10.240.1.9" "Elasticsearch" "curl -s http://localhost:9200/ | grep 'You Know, for Search'"

# Check GPU server components
check_component "10.240.1.11" "ChromaDB" "curl -s http://localhost:8000/api/v1/heartbeat | grep ok"

echo -e "\n====== Component Check Complete ======"
```

## Component Connection Mapping

| Server | Component | Default Port | Connection Validation Command |
|--------|-----------|-------------|-------------------------------|
| 10.240.8.5 (Primary) | PostgreSQL | 5432 | `psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "SELECT version();"` |
| 10.240.8.5 (Primary) | Redis | 6379 | `redis-cli ping` |
| 10.240.1.7 (Vector) | Milvus | 19530 | `curl -s http://localhost:19530/healthz` |
| 10.240.1.9 (TimeSeries) | Elasticsearch | 9200 | `curl -s http://localhost:9200/` |
| 10.240.1.9 (TimeSeries) | Kibana | 5601 | `curl -s http://localhost:5601/api/status` |
| 10.240.1.11 (GPU) | ChromaDB | 8000 | `curl -s http://localhost:8000/api/v1/heartbeat` |
| 10.240.1.11 (GPU) | TigerGraph | 14240 | `curl -s http://localhost:14240/api/version` |

## Validation Framework Fix

To fix the validation framework, update the SSH user in the script:

1. Open the validation script:
```bash
nano cline_docs/validation_scripts/realtime_validator_complete.sh
```

2. Find all instances of `ibm-admin@${server}` and replace with `x@${server}`.

3. Make the script executable again:
```bash
chmod +x cline_docs/validation_scripts/realtime_validator_complete.sh
```

4. Run the fixed validation:
```bash
./cline_docs/validation_scripts/realtime_validator_complete.sh
