#!/bin/bash

# Memory System Launch Script
# Created by Forge on March 14, 2025
# Version: 1.0.0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base configuration
WORKSPACE_DIR="/data-nova/ax/DevOps/personal/vaeris_synergy"
AGENT_COMM_DIR="$WORKSPACE_DIR/agent_communication"
LOG_DIR="/data-nova/ax/DevOps/DevOps-Codium/NovaIDE/logs/memory_system"
REDIS_URL="redis://localhost:6379/0"
MEMORY_PIDFILE="$WORKSPACE_DIR/memory_system.pid"

echo -e "${BLUE}=== Memory System Launch Script ===${NC}"

# Check if Redis is running
echo -n "Checking Redis connection... "
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED${NC}"
        echo "Error: Redis server is not running"
        echo "Please start Redis first: ./launch_redis.sh"
        exit 1
    fi
else
    echo -e "${YELLOW}WARNING${NC}"
    echo "redis-cli not found. Cannot verify Redis connection."
    echo "Please ensure Redis is running: ./launch_redis.sh"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for memory_manager.py and memory_integration.py
echo -n "Checking for memory system files... "
if [ -f "$AGENT_COMM_DIR/memory_manager.py" ] && [ -f "$AGENT_COMM_DIR/memory_integration.py" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Error: Memory system files not found at $AGENT_COMM_DIR"
    echo "Please ensure memory_manager.py and memory_integration.py exist"
    exit 1
fi

# Check python3 and redis module
echo -n "Checking Python environment... "
if command -v python3 &> /dev/null; then
    if python3 -c "import redis" &> /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}MISSING REDIS MODULE${NC}"
        echo "Redis Python module not found. Installing..."
        sudo apt-get update && sudo apt-get install -y python3-redis
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install Redis Python module.${NC}"
            echo "Please install it manually: sudo apt-get install python3-redis"
            exit 1
        fi
        echo -e "${GREEN}Redis Python module installed successfully.${NC}"
    fi
else
    echo -e "${RED}FAILED${NC}"
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 and the Redis module"
    exit 1
fi

# Create log directory
echo -n "Setting up log directory... "
mkdir -p "$LOG_DIR"
echo -e "${GREEN}OK${NC}"

# Check for existing process
echo -n "Checking for existing memory system process... "
if [ -f "$MEMORY_PIDFILE" ]; then
    MEMORY_PID=$(cat "$MEMORY_PIDFILE")
    if ps -p $MEMORY_PID > /dev/null; then
        echo -e "${YELLOW}FOUND${NC}"
        echo "Memory system is already running with PID $MEMORY_PID"
        echo "Please stop it first: kill $MEMORY_PID"
        exit 1
    else
        echo -e "${YELLOW}STALE PIDFILE${NC}"
        rm -f "$MEMORY_PIDFILE"
    fi
else
    echo -e "${GREEN}NONE${NC}"
fi

echo
echo -e "${MAGENTA}===== Launching Memory System =====${NC}"

# Set up the Vaeris-Synergy team memory
echo -e "${CYAN}Setting up Vaeris-Synergy team memory...${NC}"
python3 "$AGENT_COMM_DIR/memory_integration.py" \
    --redis-url "$REDIS_URL" \
    --stream-prefix "nova_agents" \
    --memory-channel "memory" \
    --setup-team \
    --log-level "INFO" > "$LOG_DIR/memory_setup.log" 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Setup failed. See logs at $LOG_DIR/memory_setup.log${NC}"
    exit 1
fi

# Start the memory integration service
echo -e "${CYAN}Starting memory integration service...${NC}"
python3 "$AGENT_COMM_DIR/memory_integration.py" \
    --redis-url "$REDIS_URL" \
    --stream-prefix "nova_agents" \
    --memory-channel "memory" \
    --log-level "INFO" > "$LOG_DIR/memory_integration.log" 2>&1 &

MEMORY_PID=$!
echo $MEMORY_PID > "$MEMORY_PIDFILE"
echo -e "${GREEN}Memory integration service started with PID $MEMORY_PID${NC}"

# Wait a moment to ensure the service is running
sleep 2
if ! ps -p $MEMORY_PID > /dev/null; then
    echo -e "${RED}Memory integration service failed to start. See logs at $LOG_DIR/memory_integration.log${NC}"
    rm -f "$MEMORY_PIDFILE"
    exit 1
fi

echo
echo -e "${GREEN}Memory system is now running!${NC}"
echo "The three-tiered memory architecture is active:"
echo "- Personal memories for individual agents"
echo "- Team memory for Vaeris-Synergy collaboration"
echo "- System-wide memory for global knowledge"
echo
echo -e "${YELLOW}To stop the memory system:${NC}"
echo "  kill $(cat $MEMORY_PIDFILE)"
echo
echo "Or use the convenience script: ./stop_memory_system.sh"

# Create stop script
cat > "$WORKSPACE_DIR/stop_memory_system.sh" << EOF
#!/bin/bash
# Stop script for memory system
# Auto-generated on $(date)

echo "Stopping memory system..."

if [ -f "$MEMORY_PIDFILE" ]; then
    MEMORY_PID=\$(cat "$MEMORY_PIDFILE")
    if ps -p \$MEMORY_PID > /dev/null; then
        echo "Stopping memory integration service (PID \$MEMORY_PID)..."
        kill \$MEMORY_PID
    fi
    rm -f "$MEMORY_PIDFILE"
fi

echo "Memory system stopped."
EOF

chmod +x "$WORKSPACE_DIR/stop_memory_system.sh"

# Run a quick test to verify the memory system is working
echo -e "${CYAN}Running a quick test of the memory system...${NC}"

# Run the test script
python3 "$AGENT_COMM_DIR/test_memory_manager.py" >> "$LOG_DIR/memory_test.log" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Memory system test successful!${NC}"
    echo "See test output at $LOG_DIR/memory_test.log"
else
    echo -e "${YELLOW}Memory system test had issues.${NC}"
    echo "Please check the logs at $LOG_DIR/memory_test.log"
fi

echo
echo -e "${MAGENTA}===== Next Steps =====${NC}"
echo "1. Launch Vaeris agent: ./launch_separate_agents.sh"
echo "2. Try storing and retrieving memories"
echo "3. Experiment with the different memory tiers"
echo
echo -e "${GREEN}Memory system setup complete!${NC}"