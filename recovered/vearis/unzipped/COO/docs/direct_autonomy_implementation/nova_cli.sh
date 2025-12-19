#!/bin/bash
# Nova CLI - Command Line Interface for Nova agents
# Usage: nova <command> <nova_name> [arguments]

# Configuration
REDIS_HOST=${REDIS_HOST:-"localhost"}
REDIS_PORT=${REDIS_PORT:-"6379"}
REDIS_DB=${REDIS_DB:-"0"}
SENDER=${NOVA_SENDER:-"chase"}

# Check if redis-cli is installed
if ! command -v redis-cli &> /dev/null; then
    echo "Error: redis-cli is not installed. Please install redis-tools."
    exit 1
fi

# Function to send a message to a Nova
send_message() {
    local nova=$1
    local message="$2"
    local message_type=${3:-"standard"}
    
    # Generate a unique message ID
    local msg_id=$(date +%s%N)
    
    # Add message to Nova's inbox
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB XADD "${nova}_inbox" "*" \
        "timestamp" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        "sender" "$SENDER" \
        "message" "{\"type\":\"$message_type\",\"content\":\"$message\"}" \
        "message_id" "$msg_id" > /dev/null
    
    echo "Message sent to $nova. Waiting for response..."
    
    # Wait for response (up to 30 seconds)
    local start_time=$(date +%s)
    local timeout=30
    local response=""
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        # Check for response in Nova's outbox
        response=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB XREAD BLOCK 1000 STREAMS "${nova}_outbox" "0-0" | grep -A1 "response" | tail -n 1 | sed 's/^[[:space:]]*//')
        
        if [ ! -z "$response" ]; then
            echo -e "\n[$nova]: $response"
            break
        fi
    done
    
    if [ -z "$response" ]; then
        echo "No response received within $timeout seconds."
    fi
}

# Function to get Nova status
get_status() {
    local nova=$1
    
    # Check if Nova service is running
    if systemctl is-active --quiet ${nova}.service; then
        echo "$nova service is running"
    else
        echo "$nova service is not running"
    fi
    
    # Get last heartbeat
    local heartbeat=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB XREVRANGE "${nova}_system_logs" + - COUNT 1 STREAMS event heartbeat | grep -A1 "timestamp" | tail -n 1 | sed 's/^[[:space:]]*//')
    
    if [ ! -z "$heartbeat" ]; then
        echo "Last heartbeat: $heartbeat"
    else
        echo "No recent heartbeat found"
    fi
}

# Function to request a daily briefing
request_briefing() {
    local nova=$1
    
    echo "Requesting daily briefing from $nova..."
    send_message "$nova" "Generate a daily briefing" "briefing"
}

# Function to display help
show_help() {
    echo "Nova CLI - Command Line Interface for Nova agents"
    echo ""
    echo "Usage:"
    echo "  nova say <nova_name> \"<message>\"     - Send a message to a Nova"
    echo "  nova status <nova_name>               - Check Nova status"
    echo "  nova briefing <nova_name>             - Request a daily briefing"
    echo "  nova help                             - Show this help message"
    echo ""
    echo "Examples:"
    echo "  nova say vaeris \"What's the status of the InfraOps team?\""
    echo "  nova status vaeris"
    echo "  nova briefing vaeris"
}

# Main command processing
case "$1" in
    say)
        if [ $# -lt 3 ]; then
            echo "Error: 'say' command requires a Nova name and a message."
            echo "Usage: nova say <nova_name> \"<message>\""
            exit 1
        fi
        nova_name=$2
        shift 2
        message="$*"
        send_message "$nova_name" "$message"
        ;;
    
    status)
        if [ $# -ne 2 ]; then
            echo "Error: 'status' command requires a Nova name."
            echo "Usage: nova status <nova_name>"
            exit 1
        fi
        get_status "$2"
        ;;
    
    briefing)
        if [ $# -ne 2 ]; then
            echo "Error: 'briefing' command requires a Nova name."
            echo "Usage: nova briefing <nova_name>"
            exit 1
        fi
        request_briefing "$2"
        ;;
    
    help)
        show_help
        ;;
    
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0