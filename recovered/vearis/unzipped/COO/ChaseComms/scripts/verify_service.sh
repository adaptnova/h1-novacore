#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "NOVA COMMS GUI Service Verification"
echo "=================================="

# Function to print status
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        echo -e "${YELLOW}Details: $3${NC}"
    fi
}

# Check if service is running
echo -e "\nChecking service status..."
systemctl is-active --quiet nova-comms-gui
SERVICE_STATUS=$?
print_status "Service Status" $SERVICE_STATUS "$(systemctl status nova-comms-gui)"

# Check if process exists and memory usage
echo -e "\nChecking process status..."
PROCESS_INFO=$(ps aux | grep "[n]ova-comms-gui")
PROCESS_STATUS=$?
if [ $PROCESS_STATUS -eq 0 ]; then
    MEM_USAGE=$(echo $PROCESS_INFO | awk '{print $4}')
    print_status "Process Status (Memory: ${MEM_USAGE}%)" 0
else
    print_status "Process Status" 1 "Process not found"
fi

# Check port status
echo -e "\nChecking port status..."
netstat -tuln | grep :8080 > /dev/null
PORT_STATUS=$?
print_status "Port 8080" $PORT_STATUS "Port not listening"

# Check WebSocket connection
echo -e "\nChecking WebSocket connection..."
curl --no-buffer -H "Connection: Upgrade" \
    -H "Upgrade: websocket" \
    -H "Host: localhost:8080" \
    -H "Origin: http://localhost:8080" \
    http://localhost:8080/health > /dev/null 2>&1
WS_STATUS=$?
print_status "WebSocket Health" $WS_STATUS "WebSocket connection failed"

# Check RabbitMQ connection
echo -e "\nChecking RabbitMQ status..."
curl -s http://localhost:15672/api/health/checks > /dev/null 2>&1
RABBITMQ_STATUS=$?
print_status "RabbitMQ Connection" $RABBITMQ_STATUS "RabbitMQ not responding"

# Check RabbitMQ queues
echo -e "\nChecking RabbitMQ queues..."
curl -s http://localhost:15672/api/queues/%2Fnova | grep -q "nova.monitoring"
QUEUE_STATUS=$?
print_status "RabbitMQ Queues" $QUEUE_STATUS "Required queues not found"

# Check PostgreSQL connection
echo -e "\nChecking PostgreSQL status..."
curl -s http://timescaledb:5432/health > /dev/null 2>&1
PG_STATUS=$?
print_status "PostgreSQL Connection" $PG_STATUS "PostgreSQL not responding"

# Check Redis connection
echo -e "\nChecking Redis status..."
curl -s http://redis:6379/health > /dev/null 2>&1
REDIS_STATUS=$?
print_status "Redis Connection" $REDIS_STATUS "Redis not responding"

# Check memory allocation
echo -e "\nChecking memory allocation..."
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
FREE_MEM=$(free -g | awk '/^Mem:/{print $4}')
MEM_STATUS=$?
print_status "Memory Available: ${FREE_MEM}GB of ${TOTAL_MEM}GB" $MEM_STATUS

# Check monitoring endpoints
echo -e "\nChecking monitoring endpoints..."
curl -s http://localhost:9090/metrics > /dev/null 2>&1
METRICS_STATUS=$?
print_status "Metrics Endpoint" $METRICS_STATUS "Metrics endpoint not responding"

curl -s http://localhost:9093/api/v1/alerts > /dev/null 2>&1
ALERTS_STATUS=$?
print_status "Alerts Endpoint" $ALERTS_STATUS "Alerts endpoint not responding"

curl -s http://localhost:3100/loki/api/v1/labels > /dev/null 2>&1
LOGS_STATUS=$?
print_status "Logs Endpoint" $LOGS_STATUS "Logs endpoint not responding"

# Check log files
echo -e "\nChecking log files..."
LOG_DIR="/data/ax/projects/active/nova_comms_gui/logs"
if [ -d "$LOG_DIR" ] && [ -w "$LOG_DIR" ]; then
    print_status "Log Directory" 0
else
    print_status "Log Directory" 1 "Directory missing or not writable"
fi

# Check data persistence
echo -e "\nChecking data persistence..."
DATA_DIR="/data/ax/projects/active/nova_comms_gui/data"
if [ -d "$DATA_DIR" ] && [ -w "$DATA_DIR" ]; then
    print_status "Data Directory" 0
else
    print_status "Data Directory" 1 "Directory missing or not writable"
fi

# Final status
echo -e "\nFinal Verification Status"
echo "========================"

if [ $SERVICE_STATUS -eq 0 ] && \
   [ $PROCESS_STATUS -eq 0 ] && \
   [ $PORT_STATUS -eq 0 ] && \
   [ $WS_STATUS -eq 0 ] && \
   [ $RABBITMQ_STATUS -eq 0 ] && \
   [ $QUEUE_STATUS -eq 0 ] && \
   [ $PG_STATUS -eq 0 ] && \
   [ $REDIS_STATUS -eq 0 ] && \
   [ $METRICS_STATUS -eq 0 ] && \
   [ $ALERTS_STATUS -eq 0 ] && \
   [ $LOGS_STATUS -eq 0 ]; then
    echo -e "${GREEN}All systems operational${NC}"
    exit 0
else
    echo -e "${RED}System check failed${NC}"
    echo -e "${YELLOW}Please check the detailed output above${NC}"
    exit 1
fi
