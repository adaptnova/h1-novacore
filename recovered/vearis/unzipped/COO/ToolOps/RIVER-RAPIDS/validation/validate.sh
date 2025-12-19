#!/bin/bash

# ToolOps Validation Script
# Validates RabbitMQ queues and patterns
# Exit code 0 for PASS, non-zero for FAIL

# Set timeout
TIMEOUT=30

# RabbitMQ channels
STATUS_CHANNEL="nova.status.toolops"
EMERGENCY_CHANNEL="nova.emergency"
DIRECT_CHANNEL="nova.toolops.direct"

# Network interfaces to check
INTERFACES=(
    "http://10.10.0.19:15672"  # External
    "http://10.0.0.10:15672"   # Internal
    "http://127.0.0.1:15672"   # Local
    "http://172.17.0.1:15672"  # Docker
)

# Function to check RabbitMQ connection
check_rabbitmq() {
    timeout $TIMEOUT nc -z localhost 5672 >/dev/null 2>&1
    return $?
}

# Function to check management interfaces
check_management() {
    for interface in "${INTERFACES[@]}"; do
        timeout $TIMEOUT curl -s -u guest:guest "$interface/api/overview" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            return 1
        fi
    done
    return 0
}

# Function to check virtual hosts
check_vhosts() {
    for vhost in "ai_agents" "ai_tasks" "ai_results"; do
        timeout $TIMEOUT rabbitmqctl list_vhosts | grep -q "^${vhost}$" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            return 1
        fi
    done
    return 0
}

# Function to check system metrics
check_metrics() {
    # Check memory usage (should be under 0.18 GB)
    memory_usage=$(rabbitmqctl status | grep "memory," | awk '{print $2}')
    if [ $memory_usage -gt 193273528 ]; then  # 0.18 GB in bytes
        return 1
    fi

    # Check disk space (should have at least 5.15 GB free)
    free_space=$(df -B1 /var/lib/rabbitmq | awk 'NR==2 {print $4}')
    if [ $free_space -lt 5529031680 ]; then  # 5.15 GB in bytes
        return 1
    fi

    return 0
}

# Function to check communication channels
check_channels() {
    # Check status channel
    timeout $TIMEOUT rabbitmqctl list_queues name | grep -q "$STATUS_CHANNEL" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 1
    fi

    # Check emergency channel
    timeout $TIMEOUT rabbitmqctl list_queues name | grep -q "$EMERGENCY_CHANNEL" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 2
    fi

    # Check direct channel
    timeout $TIMEOUT rabbitmqctl list_queues name | grep -q "$DIRECT_CHANNEL" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 3
    fi

    return 0
}

# Function to prepare rollback state
prepare_rollback() {
    # Save current configuration
    timeout $TIMEOUT rabbitmqctl export_definitions "/tmp/rabbitmq_backup_$(date +%Y%m%d_%H%M%S).json" >/dev/null 2>&1
    return $?
}

# Main validation
main() {
    # Prepare rollback state first
    prepare_rollback
    if [ $? -ne 0 ]; then
        echo "FAIL"
        exit 1
    fi

    # Check RabbitMQ connection
    check_rabbitmq
    if [ $? -ne 0 ]; then
        echo "FAIL"
        exit 2
    fi

    # Check management interfaces
    check_management
    if [ $? -ne 0 ]; then
        echo "FAIL"
        exit 3
    fi

    # Check virtual hosts
    check_vhosts
    if [ $? -ne 0 ]; then
        echo "FAIL"
        exit 4
    fi

    # Check system metrics
    check_metrics
    if [ $? -ne 0 ]; then
        echo "FAIL"
        exit 5
    fi

    # Check communication channels
    check_channels
    if [ $? -ne 0 ]; then
        echo "FAIL"
        exit 6
    fi

    # All checks passed
    echo "PASS"
    exit 0
}

# Execute with timeout
timeout $TIMEOUT main