#!/bin/bash
# deep_component_validator.sh - Deep Verification of Critical DataOps Components
# Version: 1.0
# Date: April 17, 2025
# Author: Catalyst (Nova #95)
# Usage: ./deep_component_validator.sh

echo "============================================================="
echo "   DATAOPS INFRASTRUCTURE DEEP COMPONENT VALIDATION"
echo "   Version: 1.0  -  Date: $(date +%Y-%m-%d)"
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
LOG_FILE="./dataops_deep_validation_$(date +%Y%m%d%H%M%S).log"
REPORT_FILE="./dataops_validation_report_$(date +%Y%m%d%H%M%S).md"
TEMP_OUTPUT="/tmp/deep_validation_output.tmp"
SERVERS=("10.240.8.5" "10.240.1.7" "10.240.1.9" "10.240.1.11")
SERVER_NAMES=("Primary" "Vector" "TimeSeries" "GPU")

# Initialize log and report
initialize_logs() {
  echo "# DataOps Deep Component Validation Report" > $REPORT_FILE
  echo "**Date:** $(date)" >> $REPORT_FILE
  echo "**Validator:** Catalyst (Nova #95)" >> $REPORT_FILE
  echo "" >> $REPORT_FILE
  
  echo "DataOps Deep Component Validation Log - $(date)" > $LOG_FILE
  echo "=============================================================" >> $LOG_FILE
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

# Add table to report
add_report_table() {
  local headers=$1
  
  echo "$headers" >> $REPORT_FILE
  local header_count=$(echo "$headers" | awk -F'|' '{print NF-1}')
  local separator="|"
  for ((i=0; i<$header_count; i++)); do
    separator="${separator}---|"
  done
  echo "$separator" >> $REPORT_FILE
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

# Function to check if a service is running properly
check_service() {
  local server=$1
  local service=$2
  local description=$3
  local output
  
  log "INFO" "Checking $description service on $server..."
  output=$(remote_exec $server "systemctl status $service")
  
  if echo "$output" | grep -q "Active: active (running)"; then
    log "SUCCESS" "$description service is running on $server"
    add_report_result "$description Service" "PASS" "Service is running normally"
    
    # Get more service details
    local uptime=$(echo "$output" | grep "Active:" | sed 's/.*; \(.*\)/\1/')
    local process_count=$(remote_exec $server "ps aux | grep $service | grep -v grep | wc -l")
    local memory_usage=$(remote_exec $server "ps aux | grep $service | grep -v grep | awk '{sum += \$6} END {print sum}'")
    
    echo "- Uptime: $uptime" >> $REPORT_FILE
    echo "- Process Count: $process_count" >> $REPORT_FILE
    echo "- Memory Usage: ${memory_usage}KB" >> $REPORT_FILE
    
    return 0
  else
    log "ERROR" "$description service is NOT running on $server"
    add_report_result "$description Service" "FAIL" "Service is not running"
    add_raw_output "$description Service Status" "$output"
    return 1
  fi
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

# Function for deep Redis validation
validate_redis() {
  local server=$1
  
  add_report_section "Redis Database" 2
  
  # 1. Check if service is running
  check_service $server "redis-server" "Redis"
  
  # 2. Test basic Redis functionality
  log "INFO" "Testing Redis basic functionality..."
  local output=$(remote_exec $server "redis-cli ping")
  
  if echo "$output" | grep -q "PONG"; then
    log "SUCCESS" "Redis responds to PING command"
    add_report_result "Basic Connectivity" "PASS" "Redis responds to PING command"
  else
    log "ERROR" "Redis does not respond to PING command"
    add_report_result "Basic Connectivity" "FAIL" "No response to PING command"
    add_raw_output "Redis Ping" "$output"
    return 1
  fi
  
  # 3. Test data operations
  log "INFO" "Testing Redis data operations..."
  local test_key="dataops_validation_$(date +%s)"
  local test_value="test_value_$(date +%s)"
  
  # SET operation
  output=$(remote_exec $server "redis-cli set $test_key $test_value")
  if echo "$output" | grep -q "OK"; then
    log "SUCCESS" "Redis SET operation successful"
    add_report_result "SET Operation" "PASS" "Successfully stored test data"
  else
    log "ERROR" "Redis SET operation failed"
    add_report_result "SET Operation" "FAIL" "Could not store test data"
    add_raw_output "Redis SET" "$output"
    return 1
  fi
  
  # GET operation
  output=$(remote_exec $server "redis-cli get $test_key")
  if echo "$output" | grep -q "$test_value"; then
    log "SUCCESS" "Redis GET operation successful"
    add_report_result "GET Operation" "PASS" "Successfully retrieved test data"
  else
    log "ERROR" "Redis GET operation failed"
    add_report_result "GET Operation" "FAIL" "Could not retrieve test data"
    add_raw_output "Redis GET" "$output"
    return 1
  fi
  
  # DEL operation
  output=$(remote_exec $server "redis-cli del $test_key")
  if echo "$output" | grep -q "1"; then
    log "SUCCESS" "Redis DEL operation successful"
    add_report_result "DEL Operation" "PASS" "Successfully deleted test data"
  else
    log "ERROR" "Redis DEL operation failed"
    add_report_result "DEL Operation" "FAIL" "Could not delete test data"
    add_raw_output "Redis DEL" "$output"
    return 1
  fi
  
  # 4. Check Redis configuration
  log "INFO" "Checking Redis configuration..."
  
  # Memory configuration
  output=$(remote_exec $server "redis-cli CONFIG GET maxmemory")
  local maxmemory=$(echo "$output" | grep -v "maxmemory" | tr -d '\r')
  
  # Memory policy
  output=$(remote_exec $server "redis-cli CONFIG GET maxmemory-policy")
  local memory_policy=$(echo "$output" | grep -v "maxmemory-policy" | tr -d '\r')
  
  # Persistence configuration
  output=$(remote_exec $server "redis-cli CONFIG GET save")
  local persistence=$(echo "$output" | grep -v "save" | tr -d '\r')
  
  add_report_section "Redis Configuration" 3
  echo "- Max Memory: ${maxmemory:-Not Set}" >> $REPORT_FILE
  echo "- Memory Policy: $memory_policy" >> $REPORT_FILE
  echo "- Persistence: ${persistence:-Not Set}" >> $REPORT_FILE
  
  # 5. Check Redis info for performance metrics
  log "INFO" "Collecting Redis performance metrics..."
  
  output=$(remote_exec $server "redis-cli info")
  
  local connected_clients=$(echo "$output" | grep "connected_clients" | cut -d':' -f2 | tr -d '\r')
  local used_memory_human=$(echo "$output" | grep "used_memory_human" | cut -d':' -f2 | tr -d '\r')
  local total_commands_processed=$(echo "$output" | grep "total_commands_processed" | cut -d':' -f2 | tr -d '\r')
  local rejected_connections=$(echo "$output" | grep "rejected_connections" | cut -d':' -f2 | tr -d '\r')
  
  add_report_section "Redis Performance Metrics" 3
  echo "- Connected Clients: $connected_clients" >> $REPORT_FILE
  echo "- Memory Usage: $used_memory_human" >> $REPORT_FILE
  echo "- Commands Processed: $total_commands_processed" >> $REPORT_FILE
  echo "- Rejected Connections: $rejected_connections" >> $REPORT_FILE
  
  # Check for high rejection rate
  if [[ $rejected_connections -gt 0 ]]; then
    log "WARNING" "Redis has rejected $rejected_connections connections"
    add_report_result "Connection Rejection" "WARNING" "Redis has rejected $rejected_connections connections"
  fi
  
  log "SUCCESS" "Redis deep validation completed successfully"
  return 0
}

# Function for deep PostgreSQL validation
validate_postgresql() {
  local server=$1
  
  add_report_section "PostgreSQL Database" 2
  
  # 1. Check if service is running
  check_service $server "postgresql" "PostgreSQL"
  
  # 2. Test basic PostgreSQL connectivity
  log "INFO" "Testing PostgreSQL basic connectivity..."
  local output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT version();\"")
  
  if echo "$output" | grep -q "PostgreSQL"; then
    local version=$(echo "$output" | grep "PostgreSQL" | sed 's/^\s*//')
    log "SUCCESS" "PostgreSQL connection successful"
    add_report_result "Basic Connectivity" "PASS" "Connected to $version"
  else
    log "ERROR" "PostgreSQL connection failed"
    add_report_result "Basic Connectivity" "FAIL" "Could not connect to PostgreSQL"
    add_raw_output "PostgreSQL Connection" "$output"
    return 1
  fi
  
  # 3. Test database operations
  log "INFO" "Testing PostgreSQL database operations..."
  local test_table="dataops_validation_$(date +%s)"
  
  # Create table
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"CREATE TABLE ${test_table}(id SERIAL PRIMARY KEY, test_value TEXT);\"")
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
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"INSERT INTO ${test_table}(test_value) VALUES ('test_data_$(date +%s)') RETURNING id;\"")
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
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT * FROM ${test_table};\"")
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
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"DROP TABLE ${test_table};\"")
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
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT pg_size_pretty(pg_database_size('postgres'));\"")
  local db_size=$(echo "$output" | grep -v "pg_size_pretty" | grep -v "row" | grep -v "\-\-\-" | grep -v "^$" | sed 's/^\s*//' | tr -d '\r')
  
  # Active connections
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT count(*) FROM pg_stat_activity;\"")
  local connections=$(echo "$output" | grep -v "count" | grep -v "row" | grep -v "\-\-\-" | grep -v "^$" | sed 's/^\s*//' | tr -d '\r')
  
  # Connection limit
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SHOW max_connections;\"")
  local max_connections=$(echo "$output" | grep -v "max_connections" | grep -v "row" | grep -v "\-\-\-" | grep -v "^$" | sed 's/^\s*//' | tr -d '\r')
  
  add_report_section "PostgreSQL Status" 3
  echo "- Database Size: $db_size" >> $REPORT_FILE
  echo "- Active Connections: $connections" >> $REPORT_FILE
  echo "- Max Connections: $max_connections" >> $REPORT_FILE
  
  # 5. Check for PostgreSQL performance issues
  log "INFO" "Checking PostgreSQL performance metrics..."
  
  # Long-running queries
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND (now() - query_start) > interval '5 minutes';\"")
  local long_queries=$(echo "$output" | grep -v "count" | grep -v "row" | grep -v "\-\-\-" | grep -v "^$" | sed 's/^\s*//' | tr -d '\r')
  
  # Cache hit ratio
  output=$(remote_exec $server "PGPASSWORD=nova_secure_password psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c \"SELECT sum(heap_blks_read) as heap_read, sum(heap_blks_hit) as heap_hit, sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio FROM pg_statio_user_tables;\"")
  local cache_hit_ratio=$(echo "$output" | grep "[0-9]" | awk '{print $3}' | tr -d '\r')
  
  add_report_section "PostgreSQL Performance" 3
  echo "- Long-Running Queries (>5min): $long_queries" >> $REPORT_FILE
  echo "- Cache Hit Ratio: ${cache_hit_ratio:-N/A}" >> $REPORT_FILE
  
  if [[ $long_queries -gt 0 ]]; then
    log "WARNING" "PostgreSQL has $long_queries long-running queries"
    add_report_result "Long-Running Queries" "WARNING" "Found $long_queries queries running for over 5 minutes"
  fi
  
  log "SUCCESS" "PostgreSQL deep validation completed successfully"
  return 0
}

# Function for deep Elasticsearch validation
validate_elasticsearch() {
  local server=$1
  
  add_report_section "Elasticsearch Database" 2
  
  # 1. Check if service is running
  check_service $server "elasticsearch" "Elasticsearch"
  
  # 2. Test basic Elasticsearch connectivity
  log "INFO" "Testing Elasticsearch basic connectivity..."
  local output=$(remote_exec $server "curl -s http://localhost:9200/")
  
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
  
  # 3. Test cluster health
  log "INFO" "Checking Elasticsearch cluster health..."
  output=$(remote_exec $server "curl -s http://localhost:9200/_cluster/health")
  
  local cluster_name=$(echo "$output" | grep '"cluster_name"' | sed 's/.*"cluster_name":"\([^"]*\)".*/\1/')
  local status=$(echo "$output" | grep '"status"' | sed 's/.*"status":"\([^"]*\)".*/\1/')
  local node_count=$(echo "$output" | grep '"number_of_nodes"' | sed 's/.*"number_of_nodes":\([^,]*\).*/\1/')
  local data_node_count=$(echo "$output" | grep '"number_of_data_nodes"' | sed 's/.*"number_of_data_nodes":\([^,]*\).*/\1/')
  
  add_report_section "Elasticsearch Cluster Status" 3
  echo "- Cluster Name: $cluster_name" >> $REPORT_FILE
  echo "- Status: $status" >> $REPORT_FILE
  echo "- Nodes: $node_count" >> $REPORT_FILE
  echo "- Data Nodes: $data_node_count" >> $REPORT_FILE
  
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
  
  # 4. Test data operations
  log "INFO" "Testing Elasticsearch data operations..."
  local index_name="dataops_validation_$(date +%s)"
  
  # Create index
  output=$(remote_exec $server "curl -s -X PUT http://localhost:9200/${index_name}")
  if echo "$output" | grep -q '"acknowledged":true'; then
    log "SUCCESS" "Elasticsearch CREATE INDEX operation successful"
    add_report_result "CREATE INDEX" "PASS" "Successfully created test index"
  else
    log "ERROR" "Elasticsearch CREATE INDEX operation failed"
    add_report_result "CREATE INDEX" "FAIL" "Could not create test index"
    add_raw_output "Elasticsearch CREATE INDEX" "$output"
    return 1
  fi
  
  # Index document
  output=$(remote_exec $server "curl -s -X POST http://localhost:9200/${index_name}/_doc -H 'Content-Type: application/json' -d '{\"test_field\": \"test_value\", \"timestamp\": \"$(date -Iseconds)\"}'")
  if echo "$output" | grep -q '"result":"created"'; then
    log "SUCCESS" "Elasticsearch INDEX operation successful"
    add_report_result "INDEX Document" "PASS" "Successfully indexed test document"
  else
    log "ERROR" "Elasticsearch INDEX operation failed"
    add_report_result "INDEX Document" "FAIL" "Could not index test document"
    add_raw_output "Elasticsearch INDEX" "$output"
    
    # Try to clean up the index even if indexing failed
    remote_exec $server "curl -s -X DELETE http://localhost:9200/${index_name} > /dev/null 2>&1"
    return 1
  fi
  
  # Search
  output=$(remote_exec $server "curl -s -X GET http://localhost:9200/${index_name}/_search -H 'Content-Type: application/json' -d '{\"query\": {\"match\": {\"test_field\": \"test_value\"}}}'")
  if echo "$output" | grep -q '"hits":{"total":'; then
    local hits=$(echo "$output" | grep '"total"' | sed 's/.*"value":\([^,}]*\).*/\1/')
    log "SUCCESS" "Elasticsearch SEARCH operation successful"
    add_report_result "SEARCH Operation" "PASS" "Successfully found $hits matching documents"
  else
    log "ERROR" "Elasticsearch SEARCH operation failed"
    add_report_result "SEARCH Operation" "FAIL" "Could not search documents"
    add_raw_output "Elasticsearch SEARCH" "$output"
    
    # Try to clean up the index even if search failed
    remote_exec $server "curl -s -X DELETE http://localhost:9200/${index_name} > /dev/null 2>&1"
    return 1
  fi
  
  # Delete index
  output=$(remote_exec $server "curl -s -X DELETE http://localhost:9200/${index_name}")
  if echo "$output" | grep -q '"acknowledged":true'; then
    log "SUCCESS" "Elasticsearch DELETE INDEX operation successful"
    add_report_result "DELETE INDEX" "PASS" "Successfully deleted test index"
  else
    log "ERROR" "Elasticsearch DELETE INDEX operation failed"
    add_report_result "DELETE INDEX" "FAIL" "Could not delete test index"
    add_raw_output "Elasticsearch DELETE INDEX" "$output"
    return 1
  fi
  
  # 5. Check Elasticsearch node stats
  log "INFO" "Collecting Elasticsearch node statistics..."
  
  output=$(remote_exec $server "curl -s http://localhost:9200/_nodes/stats")
  
  # JVM heap stats
  local heap_used_percent=$(echo "$output" | grep -o '"heap_used_percent":[0-9]*' | head -1 | cut -d':' -f2)
  local heap_max=$(echo "$output" | grep -o '"heap_max_in_bytes":[0-9]*' | head -1 | cut -d':' -f2)
  local heap_max_mb=$((heap_max / 1024 / 1024))
  
  # Document count
  local doc_count=$(echo "$output" | grep -o '"docs":{"count":[0-9]*' | head -1 | sed 's/.*"count":\([0-9]*\).*/\1/')
  
  # CPU usage
  local cpu_percent=$(echo "$output" | grep -o '"percent":[0-9]*' | head -1 | cut -d':' -f2)
  
  add_report_section "Elasticsearch Node Statistics" 3
  echo "- JVM Heap Usage: ${heap_used_percent}% of ${heap_max_mb}MB" >> $REPORT_FILE
  echo "- Document Count: ${doc_count:-N/A}" >> $REPORT_FILE
  echo "- CPU Usage: ${cpu_percent:-N/A}%" >> $REPORT_FILE
  
  # Warning for high heap usage
  if [[ $heap_used_percent -gt 85 ]]; then
    log "WARNING" "Elasticsearch has high heap usage: $heap_used_percent%"
    add_report_result "JVM Heap Usage" "WARNING" "High heap usage at $heap_used_percent%"
  fi
  
  log "SUCCESS" "Elasticsearch deep validation completed successfully"
  return 0
}

# Main function
main() {
  # Initialize logs
  initialize_logs
  
  log "INFO" "Starting DataOps deep component validation..."
  
  # Check server connectivity first
  for i in "${!SERVERS[@]}"; do
    check_server_detailed "${SERVERS[$i]}" "${SERVER_NAMES[$i]}"
    local server_status=$?
    
    # Only proceed with component validation if server is accessible
    if [[ $server_status -eq 0 ]]; then
      if [[ ${SERVER_NAMES[$i]} == "Primary" ]]; then
        log "INFO" "Validating database components on ${SERVER_NAMES[$i]} Server..."
        validate_postgresql "${SERVERS[$i]}"
        validate_redis "${SERVERS[$i]}"
      elif [[ ${SERVER_NAMES[$i]} == "TimeSeries" ]]; then
        log "INFO" "Validating database components on ${SERVER_NAMES[$i]} Server..."
        validate_elasticsearch "${SERVERS[$i]}"
      fi
    else
      log "WARNING" "Skipping component validation for ${SERVER_NAMES[$i]} Server due to connectivity issues"
    fi
  done
  
  log "INFO" "Deep component validation completed."
  echo ""
  echo "Detailed validation report saved to $REPORT_FILE"
  echo "Validation log saved to $LOG_FILE"
}

# Execute main function
main "$@"
