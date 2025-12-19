#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "NOVA COMMS GUI Memory Verification"
echo "================================="

# Function to convert to GB
to_gb() {
    echo "scale=2; $1 / 1024 / 1024" | bc
}

# Function to print status
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        echo -e "${YELLOW}Details: $3${NC}"
    fi
}

# Check total system memory
echo -e "\nChecking system memory..."
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
TOTAL_MEM_GB=$(to_gb $TOTAL_MEM)
if [ $(echo "$TOTAL_MEM_GB >= 1400" | bc) -eq 1 ]; then
    print_status "Total Memory: ${TOTAL_MEM_GB}GB" 0
else
    print_status "Total Memory: ${TOTAL_MEM_GB}GB" 1 "Expected at least 1,408GB"
fi

# Check Node.js memory limits
echo -e "\nChecking Node.js memory limits..."
NODE_HEAP=$(node -e "console.log(require('v8').getHeapStatistics().heap_size_limit)" 2>/dev/null)
NODE_HEAP_GB=$(to_gb $NODE_HEAP)
if [ $(echo "$NODE_HEAP_GB >= 30" | bc) -eq 1 ]; then
    print_status "Node.js Heap: ${NODE_HEAP_GB}GB" 0
else
    print_status "Node.js Heap: ${NODE_HEAP_GB}GB" 1 "Expected at least 32GB"
fi

# Check RabbitMQ memory
echo -e "\nChecking RabbitMQ memory..."
RABBITMQ_MEM=$(rabbitmqctl status 2>/dev/null | grep -A 5 "Memory" | grep "total" | awk '{print $2}')
RABBITMQ_MEM_GB=$(to_gb $RABBITMQ_MEM)
if [ $(echo "$RABBITMQ_MEM_GB >= 60" | bc) -eq 1 ]; then
    print_status "RabbitMQ Memory: ${RABBITMQ_MEM_GB}GB" 0
else
    print_status "RabbitMQ Memory: ${RABBITMQ_MEM_GB}GB" 1 "Expected at least 64GB"
fi

# Check available memory
echo -e "\nChecking available memory..."
AVAIL_MEM=$(free -m | awk '/^Mem:/{print $7}')
AVAIL_MEM_GB=$(to_gb $AVAIL_MEM)
if [ $(echo "$AVAIL_MEM_GB >= 15" | bc) -eq 1 ]; then
    print_status "Available Memory: ${AVAIL_MEM_GB}GB" 0
else
    print_status "Available Memory: ${AVAIL_MEM_GB}GB" 1 "Expected at least 16GB available"
fi

# Check systemd memory limits
echo -e "\nChecking systemd memory limits..."
SYSTEMD_MEM_HIGH=$(systemctl show nova-comms-gui | grep MemoryHigh | cut -d= -f2)
SYSTEMD_MEM_MAX=$(systemctl show nova-comms-gui | grep MemoryMax | cut -d= -f2)
SYSTEMD_MEM_HIGH_GB=$(to_gb $SYSTEMD_MEM_HIGH)
SYSTEMD_MEM_MAX_GB=$(to_gb $SYSTEMD_MEM_MAX)

if [ $(echo "$SYSTEMD_MEM_HIGH_GB >= 30" | bc) -eq 1 ]; then
    print_status "Systemd MemoryHigh: ${SYSTEMD_MEM_HIGH_GB}GB" 0
else
    print_status "Systemd MemoryHigh: ${SYSTEMD_MEM_HIGH_GB}GB" 1 "Expected at least 32GB"
fi

if [ $(echo "$SYSTEMD_MEM_MAX_GB >= 60" | bc) -eq 1 ]; then
    print_status "Systemd MemoryMax: ${SYSTEMD_MEM_MAX_GB}GB" 0
else
    print_status "Systemd MemoryMax: ${SYSTEMD_MEM_MAX_GB}GB" 1 "Expected at least 64GB"
fi

# Check process memory usage
echo -e "\nChecking process memory usage..."
PROCESS_MEM=$(ps -o rss= -p $(pgrep -f "nova-comms-gui") | awk '{sum += $1} END {print sum}')
PROCESS_MEM_GB=$(to_gb $PROCESS_MEM)
print_status "Process Memory Usage: ${PROCESS_MEM_GB}GB" 0

# Final status
echo -e "\nMemory Verification Status"
echo "========================="

if [ $(echo "$TOTAL_MEM_GB >= 1400" | bc) -eq 1 ] && \
   [ $(echo "$NODE_HEAP_GB >= 30" | bc) -eq 1 ] && \
   [ $(echo "$RABBITMQ_MEM_GB >= 60" | bc) -eq 1 ] && \
   [ $(echo "$AVAIL_MEM_GB >= 15" | bc) -eq 1 ]; then
    echo -e "${GREEN}Memory configuration verified${NC}"
    exit 0
else
    echo -e "${RED}Memory verification failed${NC}"
    echo -e "${YELLOW}Please check the detailed output above${NC}"
    exit 1
fi
