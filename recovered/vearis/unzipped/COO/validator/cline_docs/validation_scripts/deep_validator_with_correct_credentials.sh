#!/bin/bash
# deep_validator_with_correct_credentials.sh - Deep Verification with Correct Connection Details
# Version: 1.0
# Date: April 17, 2025
# Author: Catalyst (Nova #95)
# Usage: ./deep_validator_with_correct_credentials.sh

echo "============================================================="
echo "   DATAOPS INFRASTRUCTURE DEEP COMPONENT VALIDATION"
echo "   Version: 1.0  -  Date: $(date +%Y-%m-%d)"
echo "   USING CORRECT CREDENTIALS FROM MASTER_CONNECTION_REFERENCE"
echo "============================================================="
echo ""

# Set up color codes and icons
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"

# Global variables
LOG_FILE="./dataops_deep_validation_correct_creds_$(date +%Y%m%d%H%M%S).log"
REPORT_FILE="./dataops_validation_report_correct_creds_$(date +%Y%m%d%H%M%S).md"
TEMP_OUTPUT="/tmp/deep_validation_output.tmp"
SERVERS=("10.240.8.5" "10.240.1.7" "10.240.1.9" "10.240.1.11")
SERVER_NAMES=("Primary" "Vector" "TimeSeries" "GPU")

# Correct credentials from master connection reference
PG_PASSWORD="ADAPT*nova*06032000"  # Correct PostgreSQL password
REDIS_PORTS=("7000" "7001" "7002")  # Redis cluster ports
REDIS_PASSWORD="d5d7817937232ca5"  # Redis password
ES_PASSWORD="nova_secure_password"  # Elasticsearch password
ES_USERNAME="elastic"              # Elasticsearch username

# Initialize log and report
initialize_logs() {
  echo "# DataOps Deep Component Validation Report (Correct Credentials)" > $REPORT_FILE
  echo "**Date:** $(date)" >> $REPORT_FILE
  echo "**Validator:** Catalyst (Nova #95)" >> $REPORT_FILE
  echo "**Note:** Using credentials from master_connection_reference.md" >> $REPORT_FILE
  echo "" >> $REPORT_FILE
  
  echo "DataOps Deep Component Validation Log - $(date)" > $LOG_FILE
  echo "=============================================================" >> $LOG_FILE
  echo "Using credentials from master_connection_reference.md" >> $LOG_FILE
  echo "" >> $LOG_FILE
}

# Logging function
log() {
  local level=$1
  local message=$2
  local color=$NC
  local icon=""
  
  case $level in
    "INFO") color=$BLUE; icon=$INFO ;;
    "SUCCESS") color=$GREEN; icon=$CHECK ;;
    "WARNING") color=$YELLOW; icon=$WARNING ;;
    "ERROR") color=$RED; icon=$CROSS ;;
    "PHASE") color=$CYAN; icon="" ;;
  esac
  
  echo -e "[$(date +%Y-%m-%d\ %H:%M:%S)] ${color}[${level}]${NC} ${icon} ${message}"
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] [${level}] ${message}" >> $LOG_FILE
}

# Add section to report
add_report_section() {
  local title=$1
  local level=$2
  
  echo "" >> $REPORT_FILE
  if [[ $level -eq 1 ]]; then
    echo "## $title" >> $REPORT_FILE
  elif [[ $level -eq 2 ]]; then
    echo "### $title" >> $REPORT_FILE
  elif [[ $level -eq 3 ]]; then
    echo "#### $title" >> $REPORT_FILE
  fi
  echo "" >> $REPORT_FILE
}

# Add result to report
add_report_result() {
  local title=$1
  local status=$2
  local details=$3
  
  if [[ "$status" == "PASS" ]]; then
    echo "- **$title**: $CHECK PASS - $details" >> $REPORT_FILE
  elif [[ "$status" == "WARNING" ]]; then
    echo "- **$title**: $WARNING WARNING - $details" >> $REPORT_FILE
  else
    echo "- **$title**: $CROSS FAIL - $details" >> $REPORT_FILE
  fi
}

# Add raw command output to report
add_raw_output() {
  local title=$1
  local output=$2
  
  echo "" >> $REPORT_FILE
  echo "**Raw Output - $title:**" >> $REPORT_FILE
  echo '```' >> $REPORT_FILE
  echo "$output" >> $REPORT_FILE
  echo '```' >> $REPORT_FILE
  echo "" >> $REPORT_FILE
}

# Function to execute a command on a remote server
remote_exec() {
  local server=$1
  local command=$2
  local output
  
  output=$(ssh -o ConnectTimeout=5 x@$server "$command" 2>&1)
  echo "$output"
}

# Function to check server connectivity with detailed info
check_server_detailed() {
  local server=$1
  local server_name=$2
  local output
  
  log "PHASE" "Deep validation of $server_name Server ($server)"
  add_report_section "$server_name Server ($server)" 1
  
  # Ping test with statistics
  log "INFO" "Testing network connectivity to $server with detailed statistics..."
  output=$(ping -c 5 $server 2>&1)
  
  if echo "$output" | grep -q "5 received"; then
    local avg_ping=$(echo "$output" | grep "avg" | sed 's/.*= [0-9\.]*\/\([0-9\.]*\)\/.*/\1/')
    log "SUCCESS" "Network connectivity to $server successful (avg ping: ${avg_ping}ms)"
    add_report_result "Network Connectivity" "PASS" "Average ping: ${avg_ping}ms"
  else
    local received=$(echo "$output" | grep "received" | sed 's/.* \([0-9]*\) received.*/\1/')
    log "ERROR" "Network connectivity to $server partial or failed ($received/5 packets)"
    add_report_result "Network Connectivity" "FAIL" "Only $received/5 packets received"
    add_raw_output "Ping Test" "$output"
    return 1
  fi
  
  # SSH connection test
  log "INFO" "Testing SSH connectivity to $server..."
  output=$(ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no x@$server 'echo "SSH Connection Successful"; uname -a; uptime' 2>&1)
  
  if echo "$output" | grep -q "SSH Connection Successful"; then
    local kernel_info=$(echo "$output" | grep "Linux" | head -1)
    local uptime_info=$(echo "$output" | grep "load average" | sed 's/.*load average: \(.*\)/\1/')
    log "SUCCESS" "SSH connection to $server successful"
    add_report_result "SSH Connectivity" "PASS" "Connection established successfully"
    echo "- Kernel: $kernel_info" >> $REPORT_FILE
    echo "- Load Average: $uptime_info" >> $REPORT_FILE
    
    # Get more system information
    local cpu_info=$(remote_exec $server "cat /proc/cpuinfo | grep 'model name' | head -1 | sed 's/model name.*: //'")
    local mem_info=$(remote_exec $server "free -h | grep Mem | awk '{print \"Total: \"\$2\" Used: \"\$3\" Free: \"\$4}'")
    local disk_info=$(remote_exec $server "df -h / | grep / | awk '{print \"Total: \"\$2\" Used: \"\$3\" Free: \"\$4\" Usage: \"\$5}'")
    
    add_report_section "System Information" 2
    echo "- CPU: $cpu_info" >> $REPORT_FILE
    echo "- Memory: $mem_info" >> $REPORT_FILE
    echo "- Disk: $disk_info" >> $REPORT_FILE
    
    return 0
  else
    log "ERROR" "SSH connection to $server failed"
    add_report_result "SSH Connectivity" "FAIL" "Connection failed"
    add_raw_output "SSH Error" "$output"
    return 1
  fi
}

# Function for deep PostgreSQL validation with peer authentication
validate_postgresql_with_correct_creds() {
  local server=$1
  
  add_report_section "PostgreSQL Database" 2
  
  # 1. Check if service is running
  log "INFO" "Checking PostgreSQL service on $server..."
  local output=$(remote_exec $server "systemctl status postgresql.service")
  
  if echo "$output" | grep -q "Active: active (running)"; then
    log "SUCCESS" "PostgreSQL service is running on $server"
    add_report_result "PostgreSQL Service" "PASS" "Service is running normally"
    
    # Get more service details
    local uptime=$(echo "$output" | grep "Active:" | sed 's/.*; \(.*\)/\1/')
    local process_count=$(remote_exec $server "ps aux | grep postgresql | grep -v grep | wc -l")
    local memory_usage=$(remote_exec $server "ps aux | grep postgresql | grep -v grep | awk '{sum += \$6} END {print sum}'")
    
    echo "- Uptime: $uptime" >> $REPORT_FILE
    echo "- Process Count: $process_count" >> $REPORT_FILE
    echo "- Memory Usage: ${memory_usage}KB" >> $REPORT_FILE
  else
    log "ERROR" "PostgreSQL service is NOT running on $server"
    add_report_result "PostgreSQL Service" "FAIL" "Service is not running"
    add_raw_output "PostgreSQL Service Status" "$output"
    return 1
  fi
  
  # 2. Test basic PostgreSQL connectivity with PEER authentication
  log "INFO" "Testing PostgreSQL basic connectivity using peer authentication..."
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"SELECT version();\"")
  
  if echo "$output" | grep -q "PostgreSQL"; then
    local version=$(echo "$output" | grep "PostgreSQL" | sed 's/^\s*//')
    log "SUCCESS" "PostgreSQL connection successful using peer authentication"
    add_report_result "Basic Connectivity" "PASS" "Connected to $version using peer authentication"
    
    # Add authentication method information
    local auth_methods=$(remote_exec $server "sudo grep -v \"^#\" /etc/postgresql/15/main/pg_hba.conf | grep -v \"^$\" | cat")
    add_report_section "PostgreSQL Authentication Configuration" 3
    add_raw_output "pg_hba.conf Settings" "$auth_methods"
  else
    log "ERROR" "PostgreSQL connection failed even with peer authentication"
    add_report_result "Basic Connectivity" "FAIL" "Could not connect to PostgreSQL"
    add_raw_output "PostgreSQL Connection" "$output"
    return 1
  fi
  
  # 3. Test database operations with peer authentication
  log "INFO" "Testing PostgreSQL database operations..."
  local test_table="dataops_validation_$(date +%s)"
  
  # Create table
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"CREATE TABLE ${test_table}(id SERIAL PRIMARY KEY, test_value TEXT);\"")
  if echo "$output" | grep -q "CREATE TABLE"; then
    log "SUCCESS" "PostgreSQL CREATE TABLE operation successful"
    add_report_result "CREATE TABLE" "PASS" "Successfully created test table"
  else
    log "ERROR" "PostgreSQL CREATE TABLE operation failed"
    add_report_result "CREATE TABLE" "FAIL" "Could not create test table"
    add_raw_output "PostgreSQL CREATE TABLE" "$output"
    return 1
  fi
  
  # Insert data
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"INSERT INTO ${test_table}(test_value) VALUES ('test_data_$(date +%s)') RETURNING id;\"")
  if echo "$output" | grep -q "[0-9]\+"; then
    log "SUCCESS" "PostgreSQL INSERT operation successful"
    add_report_result "INSERT Operation" "PASS" "Successfully inserted test data"
  else
    log "ERROR" "PostgreSQL INSERT operation failed"
    add_report_result "INSERT Operation" "FAIL" "Could not insert test data"
    add_raw_output "PostgreSQL INSERT" "$output"
    return 1
  fi
  
  # Query data
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"SELECT * FROM ${test_table};\"")
  if echo "$output" | grep -q "test_data"; then
    log "SUCCESS" "PostgreSQL SELECT operation successful"
    add_report_result "SELECT Operation" "PASS" "Successfully retrieved test data"
  else
    log "ERROR" "PostgreSQL SELECT operation failed"
    add_report_result "SELECT Operation" "FAIL" "Could not retrieve test data"
    add_raw_output "PostgreSQL SELECT" "$output"
    return 1
  fi
  
  # Drop table
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"DROP TABLE ${test_table};\"")
  if echo "$output" | grep -q "DROP TABLE"; then
    log "SUCCESS" "PostgreSQL DROP TABLE operation successful"
    add_report_result "DROP TABLE" "PASS" "Successfully dropped test table"
  else
    log "ERROR" "PostgreSQL DROP TABLE operation failed"
    add_report_result "DROP TABLE" "FAIL" "Could not drop test table"
    add_raw_output "PostgreSQL DROP TABLE" "$output"
    return 1
  fi
  
  # 4. Check PostgreSQL server status
  log "INFO" "Checking PostgreSQL server status and configuration..."
  
  # Database size
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"SELECT pg_size_pretty(pg_database_size('postgres'));\"")
  local db_size=$(echo "$output" | grep -v "pg_size_pretty" | grep -v "row" | grep -v "\-\-\-" | grep -v "^$" | sed 's/^\s*//' | tr -d '\r')
  
  # Active connections
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"SELECT count(*) FROM pg_stat_activity;\"")
  local connections=$(echo "$output" | grep -v "count" | grep -v "row" | grep -v "\-\-\-" | grep -v "^$" | sed 's/^\s*//' | tr -d '\r')
  
  # Authentication method check
  output=$(remote_exec $server "sudo -u postgres psql -p 5432 -c \"SELECT rolname, rolpassword FROM pg_authid WHERE rolname = 'postgres';\"")
  
  add_report_section "PostgreSQL Status" 3
  echo "- Database Size: $db_size" >> $REPORT_FILE
  echo "- Active Connections: $connections" >> $REPORT_FILE
  echo "- Authentication Note: Using peer authentication is required until pg_hba.conf is updated" >> $REPORT_FILE
  
  log "SUCCESS" "PostgreSQL deep validation completed successfully"
  return 0
}

# Function for deep Redis validation with correct cluster configuration
validate_redis_cluster() {
  local server=$1
  
  add_report_section "Redis Cluster" 2
  log "INFO" "Testing Redis cluster configuration on ports 7000-7002..."
  
  # Check cluster info for each port
  local success=0
  local total=0
  
  for redis_port in "${REDIS_PORTS[@]}"; do
    ((total++))
    log "INFO" "Testing Redis cluster node on port $redis_port..."
    
    # Check if the Redis service is running on this port
    local output=$(remote_exec $server "redis-cli -h 127.0.0.1 -p $redis_port -a $REDIS_PASSWORD ping")
    
    if echo "$output" | grep -q "PONG"; then
      log "SUCCESS" "Redis cluster node on port $redis_port is responding"
      add_report_result "Redis Node Port $redis_port" "PASS" "Node is responding to PING"
      ((success++))
      
      # Get cluster info
      output=$(remote_exec $server "redis-cli -h 127.0.0.1 -p $redis_port -a $REDIS_PASSWORD cluster info")
      local cluster_state=$(echo "$output" | grep "cluster_state" | cut -d':' -f2 | tr -d '\r')
      local cluster_size=$(echo "$output" | grep "cluster_size" | cut -d':' -f2 | tr -d '\r')
      local cluster_slots_assigned=$(echo "$output" | grep "cluster_slots_assigned" | cut -d':' -f2 | tr -d '\r')
      
      # Get node info
      local node_info=$(remote_exec $server "redis-cli -h 127.0.0.1 -p $redis_port -a $REDIS_PASSWORD info")
      local role=$(echo "$node_info" | grep "role:" | cut -d':' -f2 | tr -d '\r')
      local connected_clients=$(echo "$node_info" | grep "connected_clients:" | cut -d':' -f2 | tr -d '\r')
      local used_memory_human=$(echo "$node_info" | grep "used_memory_human:" | cut -d':' -f2 | tr -d '\r')
      
      add_report_section "Redis Cluster Node $redis_port" 3
      echo "- Role: $role" >> $REPORT_FILE
      echo "- Cluster State: $cluster_state" >> $REPORT_FILE
      echo "- Cluster Size: $cluster_size" >> $REPORT_FILE
      echo "- Slots Assigned: $cluster_slots_assigned" >> $REPORT_FILE
      echo "- Connected Clients: $connected_clients" >> $REPORT_FILE
      echo "- Memory Usage: $used_memory_human" >> $REPORT_FILE
      
      # Test data operations on this node
      log "INFO" "Testing Redis data operations on port $redis_port..."
      local test_key="dataops_validation_$redis_port"
      local test_value="test_value_$(date +%s)"
      
      # SET operation
      local set_output=$(remote_exec $server "redis-cli -h 127.0.0.1 -p $redis_port -a $REDIS_PASSWORD set $test_key $test_value")
      # GET operation
      local get_output=$(remote_exec $server "redis-cli -h 127.0.0.1 -p $redis_port -a $REDIS_PASSWORD get $test_key")
      # DEL operation
      local del_output=$(remote_exec $server "redis-cli -h 127.0.0.1 -p $redis_port -a $REDIS_PASSWORD del $test_key")
      
      # Check data operation results
      if [[ "$set_output" == "OK" && "$get_output" == "$test_value" && "$del_output" == "1" ]]; then
        log "SUCCESS" "Redis data operations successful on port $redis_port"
        add_report_result "Data Operations (Port $redis_port)" "PASS" "SET/GET/DEL operations working correctly"
      else
        log "ERROR" "Redis data operations failed on port $redis_port"
        add_report_result "Data Operations (Port $redis_port)" "FAIL" "Could not perform data operations"
      fi
    else
      log "ERROR" "Redis cluster node on port $redis_port is not responding"
      add_report_result "Redis Node Port $redis_port" "FAIL" "Node is not responding"
      add_raw_output "Redis Port $redis_port Connection" "$output"
    fi
  done
  
  # Summary for all ports
  if [[ $success -eq $total ]]; then
    log "SUCCESS" "All Redis cluster nodes are operational"
    add_report_result "Redis Cluster" "PASS" "All $total cluster nodes are operational"
    return 0
  elif [[ $success -gt 0 ]]; then
    log "WARNING" "Some Redis cluster nodes are operational ($success/$total)"
    add_report_result "Redis Cluster" "WARNING" "Only $success out of $total cluster nodes are operational"
    return 1
  else
    log "ERROR" "No Redis cluster nodes are operational"
    add_report_result "Redis Cluster" "FAIL" "None of the $total cluster nodes are operational"
    return 2
  fi
}

# Function for deep Elasticsearch validation
validate_elasticsearch_with_correct_creds() {
  local server=$1
  
  add_report_section "Elasticsearch Database" 2
  
  # 1. Check if service is running
  log "INFO" "Checking Elasticsearch service on $server..."
  local output=$(remote_exec $server "systemctl status elasticsearch.service || echo 'Service not found'")
  
  if echo "$output" | grep -q "Active: active (running)"; then
    log "SUCCESS" "Elasticsearch service is running on $server"
    add_report_result "Elasticsearch Service" "PASS" "Service is running normally"
    
    # Get more service details
    local uptime=$(echo "$output" | grep "Active:" | sed 's/.*; \(.*\)/\1/')
    local process_count=$(remote_exec $server "ps aux | grep elasticsearch | grep -v grep | wc -l")
    local memory_usage=$(remote_exec $server "ps aux | grep elasticsearch | grep -v grep | awk '{sum += \$6} END {print sum}'")
    
    echo "- Uptime: $uptime" >> $REPORT_FILE
    echo "- Process Count: $process_count" >> $REPORT_FILE
    echo "- Memory Usage: ${memory_usage}KB" >> $REPORT_FILE
  else
    if echo "$output" | grep -q "Service not found"; then
      log "ERROR" "Elasticsearch service is NOT installed on $server"
      add_report_result "Elasticsearch Service" "FAIL" "Service is not installed"
    else
      log "ERROR" "Elasticsearch service is NOT running on $server"
      add_report_result "Elasticsearch Service" "FAIL" "Service is not running"
    fi
    add_raw_output "Elasticsearch Service Status" "$output"
    
    # Check if the installer package exists on the system
    output=$(remote_exec $server "dpkg -l | grep elasticsearch || apt list --installed | grep elasticsearch || yum list installed | grep elasticsearch || echo 'No Elasticsearch package found'")
    add_raw_output "Elasticsearch Package Check" "$output"
    
    log "INFO" "Elasticsearch not found, validation cannot continue"
    add_report_result "Installation Recommendation" "WARNING" "Elasticsearch needs to be installed per master_connection_reference.md"
    return 1
  fi
  
  # 2. Test basic Elasticsearch connectivity
  log "INFO" "Testing Elasticsearch basic connectivity..."
  
  # Try with correct credentials
  if echo "$output" | grep -q "X-Pack"; then
    # Using authentication for X-Pack secured Elasticsearch
    output=$(remote_exec $server "curl -s -u '$ES_USERNAME:$ES_PASSWORD' http://localhost:9200/")
  else
    # Standard connection for non-secured Elasticsearch
    output=$(remote_exec $server "curl -s http://localhost:9200/")
  fi
  
  if echo "$output" | grep -q "You Know, for Search"; then
    local version=$(echo "$output" | grep '"version"' | sed 's/.*"number":"\([^"]*\)".*/\1/')
    log "SUCCESS" "Elasticsearch connection successful"
    add_report_result "Basic Connectivity" "PASS" "Connected to Elasticsearch $version"
  else
    log "ERROR" "Elasticsearch connection failed"
    add_report_result "Basic Connectivity" "FAIL" "Could not connect to Elasticsearch"
    add_raw_output "Elasticsearch Connection" "$output"
    return 1
  fi
  
  # 3. Test cluster health with correct credentials
  log "INFO" "Checking Elasticsearch cluster health..."
  
  if echo "$output" | grep -q "X-Pack"; then
    # Using authentication for X-Pack secured Elasticsearch
    output=$(remote_exec $server "curl -s -u '$ES_USERNAME:$ES_PASSWORD' http://localhost:9200/_cluster/health")
  else
    # Standard connection for non-secured Elasticsearch
    output=$(remote_exec $server "curl -s http://localhost:9200/_cluster/health")
  fi
  
  if echo "$output" | grep -q "status"; then
    local cluster_name=$(echo "$output" | grep '"cluster_name"' | sed 's/.*"cluster_name":"\([^"]*\)".*/\1/')
    local status=$(echo "$output" | grep '"status"' | sed 's/.*"status":"\([^"]*\)".*/\1/')
    local node_count=$(echo "$output" | grep '"number_of_nodes"' | sed 's/.*"number_of_nodes":\([^,]*\).*/\1/')
    
    add_report_section "Elasticsearch Cluster Status" 3
    echo "- Cluster Name: $cluster_name" >> $REPORT_FILE
    echo "- Status: $status" >> $REPORT_FILE
    echo "- Nodes: $node_count" >> $REPORT_FILE
    
    if [[ "$status" == "green" ]]; then
      log "SUCCESS" "Elasticsearch cluster health is green"
      add_report_result "Cluster Health" "PASS" "Cluster health status is green"
    elif [[ "$status" == "yellow" ]]; then
      log "WARNING" "Elasticsearch cluster health is yellow"
      add_report_result "Cluster Health" "WARNING" "Cluster health status is yellow"
    else
      log "ERROR" "Elasticsearch cluster health is red"
      add_report_result "Cluster Health" "FAIL" "Cluster health status is red"
      add_raw_output "Elasticsearch Health" "$output"
      return 1
    fi
  else
    log "ERROR" "Could not get Elasticsearch cluster health"
    add_report_result "Cluster Health" "FAIL" "Could not get cluster health"
    add_raw_output "Elasticsearch Health" "$output"
    return 1
  fi
  
  log "SUCCESS" "Elasticsearch validation completed successfully"
  return 0
}

# Main function with correct credentials
main() {
  # Initialize logs
  initialize_logs
  
  log "INFO" "Starting DataOps deep component validation with CORRECT CREDENTIALS..."
  
  # Check server connectivity first
  for i in "${!SERVERS[@]}"; do
    check_server_detailed "${SERVERS[$i]}" "${SERVER_NAMES[$i]}"
    local server_status=$?
    
    # Only proceed with component validation if server is accessible
    if [[ $server_status -eq 0 ]]; then
      if [[ ${SERVER_NAMES[$i]} == "Primary" ]]; then
        log "INFO" "Validating database components on ${SERVER_NAMES[$i]} Server..."
        validate_postgresql_with_correct_creds "${SERVERS[$i]}"
        validate_redis_cluster "${SERVERS[$i]}"
      elif [[ ${SERVER_NAMES[$i]} == "TimeSeries" ]]; then
        log "INFO" "Validating database components on ${SERVER_NAMES[$i]} Server..."
        validate_elasticsearch_with_correct_creds "${SERVERS[$i]}"
      fi
    else
      log "WARNING" "Skipping component validation for ${SERVER_NAMES[$i]} Server due to connectivity issues"
    fi
  done
  
  log "INFO" "Deep component validation with correct credentials completed."
  echo ""
  echo "Detailed validation report saved to $REPORT_FILE"
  echo "Validation log saved to $LOG_FILE"
}

# Execute main function
main "$@"
