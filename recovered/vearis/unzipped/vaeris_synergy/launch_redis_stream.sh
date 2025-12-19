#!/bin/bash

# Redis Stream Launch Script for Nova Agent Communication
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
LOG_DIR="/logs/nova_stream"
REDIS_URL="redis://localhost:6379/0"
PAIR_PROGRAMMING=true
LOG_LEVEL="INFO"
PIDFILE="$WORKSPACE_DIR/novastream.pid"

echo -e "${BLUE}=== Nova Stream Launch Script ===${NC}"
echo "Starting Redis-based communication for Nova agents..."

# Ensure log directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo -n "Creating log directory... "
    mkdir -p "$LOG_DIR"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED${NC}"
        echo "Error: Could not create log directory"
        exit 1
    fi
fi

# Check if Redis is running
echo -n "Checking Redis connection... "
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED${NC}"
        echo "Error: Redis server is not running"
        echo "Please start Redis: sudo systemctl start redis"
        exit 1
    fi
else
    echo -e "${YELLOW}WARNING${NC}"
    echo "redis-cli not found. Cannot verify Redis connection."
    echo "Proceeding with caution..."
fi

# Check for python dependencies
echo -n "Checking Python dependencies... "
if command -v python3 &> /dev/null; then
    # Check for redis module
    if python3 -c "import redis" &> /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}INSTALLING${NC}"
        pip3 install redis &> /dev/null
        if [ $? -eq 0 ]; then
            echo "Installed redis module"
        else
            echo -e "${RED}FAILED${NC}"
            echo "Error: Could not install required Python modules"
            echo "Please install manually: pip3 install redis"
            exit 1
        fi
    fi
else
    echo -e "${RED}FAILED${NC}"
    echo "Error: Python 3 not found"
    exit 1
fi

# Check for existing processes
echo -n "Checking for existing processes... "
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p $PID > /dev/null; then
        echo -e "${YELLOW}FOUND${NC}"
        echo -n "Stopping existing process (PID: $PID)... "
        kill $PID
        sleep 2
        if ps -p $PID > /dev/null; then
            echo -e "${YELLOW}FORCE KILL${NC}"
            kill -9 $PID
            sleep 1
        fi
        if ps -p $PID > /dev/null; then
            echo -e "${RED}FAILED${NC}"
            echo "Error: Could not stop existing process"
            exit 1
        else
            echo -e "${GREEN}STOPPED${NC}"
        fi
    else
        echo -e "${YELLOW}STALE PIDFILE${NC}"
        echo "Removing stale PID file"
    fi
    rm -f "$PIDFILE"
else
    echo -e "${GREEN}NONE${NC}"
fi

echo
echo -e "${MAGENTA}===== Launching Nova Stream for Agent Communication =====${NC}"
echo

# Launch in pair programming mode
if [ "$PAIR_PROGRAMMING" = true ]; then
    echo -e "${CYAN}Starting Pair Programming integration for Vaeris and Synergy...${NC}"
    
    # Start the server in background
    python3 "$WORKSPACE_DIR/agent_communication/nova_stream.py" \
        --redis-url "$REDIS_URL" \
        --log-level "$LOG_LEVEL" \
        --health-check-interval 30 > "$LOG_DIR/nova_stream.log" 2>&1 &
    STREAM_PID=$!
    
    # Give it a moment to start
    sleep 1
    
    # Check if it started
    if ps -p $STREAM_PID > /dev/null; then
        echo -e "${GREEN}Nova Stream server started (PID: $STREAM_PID)${NC}"
        echo $STREAM_PID > "$PIDFILE"
        
        # Start the cursor integration
        echo -e "${CYAN}Starting Cursor integration...${NC}"
        python3 "$WORKSPACE_DIR/agent_communication/cursor_integration.py" \
            --pair-programming \
            --redis-url "$REDIS_URL" \
            --workspace "$WORKSPACE_DIR" \
            --log-level "$LOG_LEVEL" > "$LOG_DIR/cursor_integration.log" 2>&1 &
        INTEGRATION_PID=$!
        
        # Give it a moment to start
        sleep 1
        
        # Check if it started
        if ps -p $INTEGRATION_PID > /dev/null; then
            echo -e "${GREEN}Cursor integration started (PID: $INTEGRATION_PID)${NC}"
            echo $INTEGRATION_PID >> "$PIDFILE"
            
            echo
            echo -e "${GREEN}Nova Stream communication system started successfully!${NC}"
            echo "Vaeris and Synergy can now communicate through Redis Streams."
            echo "Log files:"
            echo "  - Nova Stream server: $LOG_DIR/nova_stream.log"
            echo "  - Cursor integration: $LOG_DIR/cursor_integration.log"
            echo
            echo -e "${YELLOW}To stop all processes:${NC} ./stop_redis_stream.sh"
            echo
        else
            echo -e "${RED}Failed to start Cursor integration${NC}"
            kill $STREAM_PID
            exit 1
        fi
    else
        echo -e "${RED}Failed to start Nova Stream server${NC}"
        exit 1
    fi
else
    # Individual agent mode
    echo "Usage instructions for individual agent mode will be added later"
    exit 0
fi

# Create stop script for convenience
cat > "$WORKSPACE_DIR/stop_redis_stream.sh" << EOF
#!/bin/bash
# Stop script for Nova Stream
# Auto-generated on $(date)

if [ -f "$PIDFILE" ]; then
    echo "Stopping Nova Stream processes..."
    while read PID; do
        if ps -p \$PID > /dev/null; then
            echo "Stopping process \$PID..."
            kill \$PID
            sleep 1
        fi
    done < "$PIDFILE"
    
    # Check if processes are still running
    STILL_RUNNING=false
    while read PID; do
        if ps -p \$PID > /dev/null; then
            echo "Process \$PID still running, force killing..."
            kill -9 \$PID
            STILL_RUNNING=true
        fi
    done < "$PIDFILE"
    
    rm -f "$PIDFILE"
    echo "Nova Stream stopped"
else
    echo "No PID file found at $PIDFILE"
    echo "Nova Stream may not be running"
fi
EOF

chmod +x "$WORKSPACE_DIR/stop_redis_stream.sh"

echo -e "${BLUE}The stop_redis_stream.sh script has been created for convenient shutdown${NC}"
echo -e "${GREEN}You can now start the Vaeris-Synergy pair programming environment:${NC}"
echo -e "./launch_vaeris_synergy_pair.sh"