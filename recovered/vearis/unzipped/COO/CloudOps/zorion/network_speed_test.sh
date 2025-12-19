#!/bin/bash

# Network Speed Test Script for IBM Cloud Servers
# This script performs comprehensive download speed tests across all network interfaces
# Created by: Zorion (IBM Cloud Infrastructure Engineer)
# Date: March 26, 2025

# Configuration - Edit these variables as needed
SERVER_NAME="adapt"
SERVER_IP="10.240.1.6"
SSH_USER="root"
TEST_DURATION=10  # Duration of each test in seconds
REPEAT_TESTS=3    # Number of times to repeat each test
OUTPUT_DIR="./speed_test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/${SERVER_NAME}_speed_test_report_${TIMESTAMP}.md"

# Test files from different sources (varying sizes and locations)
# Format: "Name|URL|Description"
TEST_FILES=(
  "IBM|https://s3.us-south.cloud-object-storage.appdomain.cloud/speedtest-cos-bucket/100MB.bin|IBM Cloud Object Storage 100MB"
  "AWS|https://speedtest-nyc3.digitalocean.com/100mb.test|DigitalOcean NYC 100MB"
  "Azure|https://azspeedtest.azurewebsites.net/100MB.bin|Azure US East 100MB"
  "Cloudflare|https://speed.cloudflare.com/__down?bytes=104857600|Cloudflare CDN 100MB"
  "Google|https://storage.googleapis.com/speedtest-public/100MB.test|Google Cloud Storage 100MB"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display section headers
section() {
  echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to display success messages
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to display error messages
error() {
  echo -e "${RED}✗ $1${NC}"
}

# Function to display warning messages
warning() {
  echo -e "${YELLOW}! $1${NC}"
}

# Function to display info messages
info() {
  echo -e "  $1"
}

# Function to check if required tools are installed on the server
check_prerequisites() {
  section "Checking Prerequisites"
  
  # Create output directory if it doesn't exist
  mkdir -p "$OUTPUT_DIR"
  success "Created output directory: $OUTPUT_DIR"
  
  # Check SSH connectivity
  info "Checking SSH connectivity to $SERVER_IP..."
  ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP exit 2>/dev/null
  
  if [ $? -eq 0 ]; then
    success "SSH connection successful"
  else
    error "SSH connection failed"
    exit 1
  fi
  
  # Check if required tools are installed on the server
  info "Checking required tools on the server..."
  
  # Create a temporary script to check prerequisites
  cat > /tmp/check_prereqs.sh << 'EOF'
#!/bin/bash

MISSING_TOOLS=()

# Check for curl
if ! command -v curl &> /dev/null; then
    MISSING_TOOLS+=("curl")
fi

# Check for wget
if ! command -v wget &> /dev/null; then
    MISSING_TOOLS+=("wget")
fi

# Check for iperf3
if ! command -v iperf3 &> /dev/null; then
    MISSING_TOOLS+=("iperf3")
fi

# Check for speedtest-cli
if ! command -v speedtest-cli &> /dev/null; then
    MISSING_TOOLS+=("speedtest-cli")
fi

# Report missing tools
if [ ${#MISSING_TOOLS[@]} -eq 0 ]; then
    echo "All required tools are installed"
    exit 0
else
    echo "Missing tools: ${MISSING_TOOLS[*]}"
    exit 1
fi
EOF

  # Make the script executable
  chmod +x /tmp/check_prereqs.sh
  
  # Copy and execute the script on the remote server
  scp -o StrictHostKeyChecking=no /tmp/check_prereqs.sh $SSH_USER@$SERVER_IP:/tmp/
  PREREQ_CHECK=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/check_prereqs.sh")
  PREREQ_STATUS=$?
  
  # Clean up
  rm /tmp/check_prereqs.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "rm /tmp/check_prereqs.sh"
  
  if [ $PREREQ_STATUS -eq 0 ]; then
    success "All required tools are installed"
  else
    warning "$PREREQ_CHECK"
    info "Installing missing tools..."
    
    # Install missing tools
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "apt-get update && apt-get install -y curl wget iperf3 speedtest-cli"
    
    if [ $? -eq 0 ]; then
      success "Successfully installed missing tools"
    else
      error "Failed to install missing tools"
      exit 1
    fi
  fi
}

# Function to get network interface information
get_network_info() {
  section "Getting Network Interface Information"
  
  info "Retrieving network interfaces on $SERVER_NAME..."
  
  # Get network interface information
  NETWORK_INFO=$(ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "ip -br addr show && echo '---' && ip route && echo '---' && cat /proc/net/dev | grep -v 'lo:' | grep ':' | awk '{print \$1, \$2, \$10}' | sed 's/:/ /g'")
  
  # Save network information to file
  echo "$NETWORK_INFO" > "${OUTPUT_DIR}/${SERVER_NAME}_network_info_${TIMESTAMP}.txt"
  
  # Extract interface names
  INTERFACES=$(echo "$NETWORK_INFO" | grep -v "lo " | awk '{print $1}' | grep -v "---" | grep -v "^$" | sort | uniq)
  
  # Count interfaces
  INTERFACE_COUNT=$(echo "$INTERFACES" | wc -l)
  
  success "Found $INTERFACE_COUNT network interfaces"
  info "Interfaces: $INTERFACES"
  
  # Save interface list for later use
  echo "$INTERFACES" > "${OUTPUT_DIR}/${SERVER_NAME}_interfaces_${TIMESTAMP}.txt"
}

# Function to perform download speed tests
perform_speed_tests() {
  section "Performing Download Speed Tests"
  
  # Get interface list
  INTERFACES=$(cat "${OUTPUT_DIR}/${SERVER_NAME}_interfaces_${TIMESTAMP}.txt")
  
  # Create results directory on the server
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "mkdir -p /tmp/speed_tests"
  
  # Create a temporary script to run the tests
  cat > /tmp/run_speed_tests.sh << 'EOF'
#!/bin/bash

# Configuration
TEST_DURATION=$1
REPEAT_TESTS=$2
RESULTS_FILE=$3

# Initialize results file
echo "Interface,Source,Test,Run,Speed (MB/s),Time (s)" > $RESULTS_FILE

# Function to run a single test
run_test() {
    local interface=$1
    local source_name=$2
    local url=$3
    local description=$4
    local run=$5
    
    echo "Testing $description on $interface (Run $run)..."
    
    # Set up routing for the specific interface if it's not the primary
    if [[ "$interface" != "eth0" ]]; then
        # Get the IP address of the interface
        ip_addr=$(ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}')
        
        if [[ -n "$ip_addr" ]]; then
            # Use the specific interface for the test
            start_time=$(date +%s.%N)
            result=$(curl -s --interface $ip_addr -o /dev/null -w "%{speed_download}" -m $TEST_DURATION $url)
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            
            # Convert to MB/s (curl returns bytes/sec)
            speed_mbps=$(echo "scale=2; $result / 1048576" | bc)
            
            echo "$interface,$source_name,Download,$run,$speed_mbps,$duration" >> $RESULTS_FILE
        else
            echo "$interface,$source_name,Download,$run,0,0" >> $RESULTS_FILE
            echo "No IP address found for $interface, skipping test"
        fi
    else
        # For primary interface, no special routing needed
        start_time=$(date +%s.%N)
        result=$(curl -s -o /dev/null -w "%{speed_download}" -m $TEST_DURATION $url)
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        # Convert to MB/s (curl returns bytes/sec)
        speed_mbps=$(echo "scale=2; $result / 1048576" | bc)
        
        echo "$interface,$source_name,Download,$run,$speed_mbps,$duration" >> $RESULTS_FILE
    fi
}

# Function to run speedtest-cli
run_speedtest() {
    local interface=$1
    local run=$2
    
    echo "Running speedtest-cli on $interface (Run $run)..."
    
    # Set up routing for the specific interface if it's not the primary
    if [[ "$interface" != "eth0" ]]; then
        # Get the IP address of the interface
        ip_addr=$(ip -4 addr show dev $interface | grep -oP '(?<=inet\s)[0-9]+(\.[0-9]+){3}')
        
        if [[ -n "$ip_addr" ]]; then
            # Use the specific interface for the test
            start_time=$(date +%s.%N)
            result=$(speedtest-cli --source $ip_addr --simple | grep "Download" | awk '{print $2}')
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            
            echo "$interface,Speedtest.net,Speedtest,$run,$result,$duration" >> $RESULTS_FILE
        else
            echo "$interface,Speedtest.net,Speedtest,$run,0,0" >> $RESULTS_FILE
            echo "No IP address found for $interface, skipping test"
        fi
    else
        # For primary interface, no special routing needed
        start_time=$(date +%s.%N)
        result=$(speedtest-cli --simple | grep "Download" | awk '{print $2}')
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        echo "$interface,Speedtest.net,Speedtest,$run,$result,$duration" >> $RESULTS_FILE
    fi
}

# Main execution
# Read test files from stdin
while IFS="|" read -r source_name url description; do
    # Read interfaces from arguments
    for interface in "${@:4}"; do
        for run in $(seq 1 $REPEAT_TESTS); do
            run_test "$interface" "$source_name" "$url" "$description" "$run"
        done
    done
done

# Run speedtest-cli tests
for interface in "${@:4}"; do
    for run in $(seq 1 $REPEAT_TESTS); do
        run_speedtest "$interface" "$run"
    done
done

echo "All tests completed. Results saved to $RESULTS_FILE"
EOF

  # Make the script executable
  chmod +x /tmp/run_speed_tests.sh
  
  # Copy the script to the server
  scp -o StrictHostKeyChecking=no /tmp/run_speed_tests.sh $SSH_USER@$SERVER_IP:/tmp/
  
  # Prepare test files input
  TEST_FILES_INPUT=""
  for test_file in "${TEST_FILES[@]}"; do
    TEST_FILES_INPUT+="$test_file"$'\n'
  done
  
  # Run the tests
  info "Starting speed tests across all interfaces..."
  info "This may take some time depending on the number of interfaces and tests..."
  
  echo "$TEST_FILES_INPUT" | ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "bash /tmp/run_speed_tests.sh $TEST_DURATION $REPEAT_TESTS /tmp/speed_tests/results.csv $INTERFACES"
  
  # Copy results back
  scp -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP:/tmp/speed_tests/results.csv "${OUTPUT_DIR}/${SERVER_NAME}_speed_test_results_${TIMESTAMP}.csv"
  
  # Clean up
  rm /tmp/run_speed_tests.sh
  ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "rm /tmp/run_speed_tests.sh && rm -rf /tmp/speed_tests"
  
  success "Speed tests completed"
  success "Results saved to ${OUTPUT_DIR}/${SERVER_NAME}_speed_test_results_${TIMESTAMP}.csv"
}

# Function to generate a report
generate_report() {
  section "Generating Report"
  
  info "Analyzing results and generating report..."
  
  # Create report file
  cat > "$REPORT_FILE" << EOF
# Network Speed Test Report for $SERVER_NAME

## Test Information
- **Server**: $SERVER_NAME ($SERVER_IP)
- **Date**: $(date)
- **Test Duration**: $TEST_DURATION seconds per test
- **Repeat Tests**: $REPEAT_TESTS times per source/interface

## Network Interfaces
\`\`\`
$(cat "${OUTPUT_DIR}/${SERVER_NAME}_network_info_${TIMESTAMP}.txt")
\`\`\`

## Speed Test Results

### Summary by Interface
| Interface | Average Download Speed (MB/s) | Max Download Speed (MB/s) |
|-----------|-------------------------------|---------------------------|
EOF

  # Process results
  RESULTS_FILE="${OUTPUT_DIR}/${SERVER_NAME}_speed_test_results_${TIMESTAMP}.csv"
  INTERFACES=$(cat "${OUTPUT_DIR}/${SERVER_NAME}_interfaces_${TIMESTAMP}.txt")
  
  # Calculate averages and maximums by interface
  for interface in $INTERFACES; do
    # Skip header line
    AVG_SPEED=$(awk -F, -v interface="$interface" 'NR>1 && $1==interface {sum+=$5; count++} END {if(count>0) print sum/count; else print 0}' "$RESULTS_FILE")
    MAX_SPEED=$(awk -F, -v interface="$interface" 'NR>1 && $1==interface {if($5>max) max=$5} END {print max}' "$RESULTS_FILE")
    
    # Format to 2 decimal places
    AVG_SPEED=$(printf "%.2f" $AVG_SPEED)
    MAX_SPEED=$(printf "%.2f" $MAX_SPEED)
    
    # Add to report
    echo "| $interface | $AVG_SPEED | $MAX_SPEED |" >> "$REPORT_FILE"
  done
  
  # Add detailed results by source
  cat >> "$REPORT_FILE" << EOF

### Results by Source
| Source | Interface | Average Download Speed (MB/s) | Max Download Speed (MB/s) |
|--------|-----------|-------------------------------|---------------------------|
EOF

  # Calculate averages and maximums by source and interface
  for source in "IBM" "AWS" "Azure" "Cloudflare" "Google" "Speedtest.net"; do
    for interface in $INTERFACES; do
      # Skip header line
      AVG_SPEED=$(awk -F, -v interface="$interface" -v source="$source" 'NR>1 && $1==interface && $2==source {sum+=$5; count++} END {if(count>0) print sum/count; else print 0}' "$RESULTS_FILE")
      MAX_SPEED=$(awk -F, -v interface="$interface" -v source="$source" 'NR>1 && $1==interface && $2==source {if($5>max) max=$5} END {print max}' "$RESULTS_FILE")
      
      # Format to 2 decimal places
      AVG_SPEED=$(printf "%.2f" $AVG_SPEED)
      MAX_SPEED=$(printf "%.2f" $MAX_SPEED)
      
      # Add to report if there are results
      if [ "$MAX_SPEED" != "0.00" ]; then
        echo "| $source | $interface | $AVG_SPEED | $MAX_SPEED |" >> "$REPORT_FILE"
      fi
    done
  done
  
  # Add detailed results for each test
  cat >> "$REPORT_FILE" << EOF

### Detailed Test Results
| Interface | Source | Test Type | Run | Speed (MB/s) | Time (s) |
|-----------|--------|-----------|-----|-------------|----------|
EOF

  # Add all results (skip header)
  awk -F, 'NR>1 {printf "| %s | %s | %s | %s | %s | %s |\n", $1, $2, $3, $4, $5, $6}' "$RESULTS_FILE" >> "$REPORT_FILE"
  
  # Add conclusion
  cat >> "$REPORT_FILE" << EOF

## Conclusion

This report provides a comprehensive analysis of network download speeds across all interfaces on the $SERVER_NAME server. The tests were conducted using multiple sources to ensure a thorough evaluation of network performance.

### Key Findings

- The fastest interface is $(awk -F, 'NR>1 {sum[$1]+=$5; count[$1]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxif=i}} print maxif}' "$RESULTS_FILE") with an average download speed of $(awk -F, -v interface="$(awk -F, 'NR>1 {sum[$1]+=$5; count[$1]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxif=i}} print maxif}' "$RESULTS_FILE")" 'NR>1 && $1==interface {sum+=$5; count++} END {printf "%.2f", sum/count}' "$RESULTS_FILE") MB/s.
- The fastest source is $(awk -F, 'NR>1 {sum[$2]+=$5; count[$2]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxsrc=i}} print maxsrc}' "$RESULTS_FILE") with an average download speed of $(awk -F, -v source="$(awk -F, 'NR>1 {sum[$2]+=$5; count[$2]++} END {max=0; for(i in sum) {avg=sum[i]/count[i]; if(avg>max) {max=avg; maxsrc=i}} print maxsrc}' "$RESULTS_FILE")" 'NR>1 && $2==source {sum+=$5; count++} END {printf "%.2f", sum/count}' "$RESULTS_FILE") MB/s.
- The overall average download speed across all interfaces and sources is $(awk -F, 'NR>1 {sum+=$5; count++} END {printf "%.2f", sum/count}' "$RESULTS_FILE") MB/s.

### Recommendations

Based on these results, the following recommendations can be made:

1. Optimize routing for the fastest interfaces to maximize throughput.
2. Consider load balancing across multiple interfaces for improved performance.
3. Monitor network performance regularly to ensure optimal operation.

## Report Generated
- **Date**: $(date)
- **Engineer**: Zorion (IBM Cloud Infrastructure Engineer)
EOF

  success "Report generated: $REPORT_FILE"
  info "You can view the report using: cat $REPORT_FILE"
}

# Main execution
echo "Network Speed Test for $SERVER_NAME"
echo "Date: $(date)"
echo "----------------------------------------------"

# Check prerequisites
check_prerequisites

# Get network interface information
get_network_info

# Perform speed tests
perform_speed_tests

# Generate report
generate_report

section "Summary"
echo "Server: $SERVER_NAME ($SERVER_IP)"
echo "Tests completed: $(grep -c "^|" "$REPORT_FILE" | awk '{print $1-4}')"
echo "Interfaces tested: $(cat "${OUTPUT_DIR}/${SERVER_NAME}_interfaces_${TIMESTAMP}.txt" | wc -l)"
echo "Report: $REPORT_FILE"

echo -e "\nSpeed test completed."
echo "You can view the detailed report using: cat $REPORT_FILE"

exit 0