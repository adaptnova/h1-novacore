#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "NOVA COMMS GUI Integration Testing"
echo "================================="
echo "Start Time: $(date)"
echo "Testing Window: 14:00-15:00 MST"

# Function to print status
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        echo -e "${YELLOW}Details: $3${NC}"
    fi
}

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local headers=$4

    echo -e "\nTesting $name..."
    if [ -n "$headers" ]; then
        response=$(curl -X $method -H "$headers" -s -w "\n%{http_code}" $url)
    else
        response=$(curl -X $method -s -w "\n%{http_code}" $url)
    fi
    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')

    if [ "$status_code" -eq 200 ]; then
        print_status "$name" 0
        echo "Response: $response_body"
    else
        print_status "$name" 1 "Status code: $status_code"
    fi
}

# Function to test RabbitMQ message
test_rabbitmq_message() {
    local queue=$1
    local message=$2

    echo -e "\nTesting RabbitMQ message to $queue..."
    rabbitmqadmin publish exchange=nova.comms routing_key="$queue" payload="$message"
    status=$?
    print_status "Message Publishing" $status

    # Wait for message processing
    sleep 2

    # Check queue status
    response=$(rabbitmqadmin get queue="$queue" count=1)
    if [[ $response == *"message_count"* ]]; then
        print_status "Message Processing" 0
    else
        print_status "Message Processing" 1 "Message not processed"
    fi
}

echo -e "\n1. Testing Backend API"
echo "====================="
test_endpoint "Health Check" "https://nova-backend:8000/health"
test_endpoint "Metrics" "https://nova-backend:8000/api/v1/metrics"
test_endpoint "Field Status" "https://nova-backend:8000/api/v1/nova-field/status"

echo -e "\n2. Testing RASA Integration"
echo "========================="
test_endpoint "RASA Health" "http://localhost:5005/health"
test_endpoint "RASA WebSocket" "ws://localhost:5005/socket.io"

echo -e "\n3. Testing Kafka Integration"
echo "==========================="
test_endpoint "Kafka Metrics" "http://localhost:9090/metrics/kafka"
test_endpoint "Kafka Broker Status" "http://localhost:9090/metrics/kafka/brokers"
test_endpoint "Kafka Consumer Groups" "http://localhost:9090/metrics/kafka/consumer-groups"

echo -e "\n4. Testing RabbitMQ Integration"
echo "=============================="
test_endpoint "RabbitMQ Health" "http://localhost:15672/api/health/checks"
test_endpoint "RabbitMQ RASA Exchange" "http://localhost:15672/api/exchanges/%2F/rasa_exchange"
test_endpoint "RabbitMQ Chase Queue" "http://localhost:15672/api/queues/%2F/nova.comms.chase"

echo -e "\n5. Testing Chase Comms Channel"
echo "=============================="
test_rabbitmq_message "chase.comms" '{
    "type": "chase.comms.status",
    "target": "system",
    "status": "checking",
    "timestamp": '$(date +%s)'
}'

echo -e "\n6. Testing Database Connections"
echo "=============================="
test_endpoint "PostgreSQL Health" "http://timescaledb:5432/health"
test_endpoint "Redis Health" "http://redis:6379/health"

echo -e "\n7. Testing Message Queue"
echo "======================="
test_endpoint "RabbitMQ Health" "http://localhost:15672/api/health/checks"
test_endpoint "RabbitMQ Queues" "http://localhost:15672/api/queues/%2Fnova"

echo -e "\n8. Testing Monitoring Stack"
echo "========================="
test_endpoint "Prometheus Metrics" "http://localhost:9090/metrics"
test_endpoint "Alert Manager" "http://localhost:9093/api/v1/alerts"
test_endpoint "Loki Logs" "http://localhost:3100/loki/api/v1/labels"

echo -e "\n9. Testing Atlassian Integration"
echo "=============================="
test_endpoint "Jira API" "https://levelup2x.atlassian.net/rest/api/2/myself" \
    "GET" "Authorization: Bearer $REACT_APP_ATLASSIAN_TOKEN"
test_endpoint "Service Desk" "https://levelup2x.atlassian.net/rest/servicedeskapi/servicedesk" \
    "GET" "Authorization: Bearer $REACT_APP_ATLASSIAN_TOKEN"

echo -e "\n10. Testing WebSocket Connections"
echo "==============================="
wscat -c wss://nova-backend:8000/ws/system --timeout 5 > /dev/null 2>&1
print_status "System WebSocket" $?

wscat -c ws://localhost:5005/socket.io --timeout 5 > /dev/null 2>&1
print_status "RASA WebSocket" $?

echo -e "\n11. Verifying Service Status"
echo "==========================="
systemctl is-active --quiet nova-comms-gui
print_status "Service Status" $? "$(systemctl status nova-comms-gui)"

echo -e "\n12. Checking Resource Usage"
echo "=========================="
MEMORY_USAGE=$(free -m | awk '/^Mem:/ {print $3/$2 * 100}')
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
print_status "Memory Usage: ${MEMORY_USAGE}%" 0
print_status "CPU Usage: ${CPU_USAGE}%" 0

# Create test report
REPORT_FILE="../memos/$(date +%Y-%m-%d_%H-%M-%S)_MST_INTEGRATION_TEST_REPORT.md"
cat << EOF > $REPORT_FILE
# NovaComms GUI Integration Test Report
Time: $(date)
Status: ${GREEN}Complete${NC}

## Test Results
1. Backend API: ${status_backend:-Unknown}
2. RASA Integration: ${status_rasa:-Unknown}
3. Kafka Integration: ${status_kafka:-Unknown}
4. RabbitMQ Integration: ${status_rabbitmq:-Unknown}
5. Chase Comms Channel: ${status_chase:-Unknown}
6. Database Connections: ${status_db:-Unknown}
7. Message Queue: ${status_mq:-Unknown}
8. Monitoring Stack: ${status_monitoring:-Unknown}
9. Atlassian Integration: ${status_atlassian:-Unknown}
10. WebSocket Connections: ${status_ws:-Unknown}
11. Service Status: ${status_service:-Unknown}
12. Resource Usage: ${status_resources:-Unknown}

## Next Steps
1. Review test results
2. Address any failed tests
3. Update launch checklist
4. Notify relevant teams of status

## Notes
- Test window: 14:00-15:00 MST
- Launch window: 16:15 MST
- Emergency channel: #nova-911
EOF

echo -e "\nTest report saved to: $REPORT_FILE"
echo -e "Please review and update the launch checklist accordingly."