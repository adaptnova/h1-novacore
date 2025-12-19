#!/bin/bash

# Separate Agent Launch Script
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
USER_DATA_BASE="/data-nova/ax/DevOps/user-data"
LOG_DIR="/logs/cursor"
CURSOR_PATH="/data-nova/00/cursor/Cursor-0.46.11.AppImage"

# Agent configuration
VAERIS_CONFIG="$WORKSPACE_DIR/config-vaeris.json"
SYNERGY_CONFIG="$WORKSPACE_DIR/config-synergy.json"
VAERIS_USER_DATA="$USER_DATA_BASE/vaeris-cursor"
SYNERGY_USER_DATA="$USER_DATA_BASE/synergy-cursor"
VAERIS_PIDFILE="$WORKSPACE_DIR/vaeris.pid"
SYNERGY_PIDFILE="$WORKSPACE_DIR/synergy.pid"

echo -e "${BLUE}=== Separate Agent Launch Script ===${NC}"
echo "Initializing Vaeris and Synergy as separate agents..."

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

# Check if Cursor exists
echo -n "Checking Cursor installation... "
if [ -f "$CURSOR_PATH" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}ALTERNATIVE SEARCH${NC}"
    CURSOR_PATH=$(which cursor 2>/dev/null || echo "")
    if [ -z "$CURSOR_PATH" ]; then
        echo -e "${RED}FAILED${NC}"
        echo "Error: Cursor not found at $CURSOR_PATH"
        echo "Please install Cursor or update the script with the correct path"
        exit 1
    else
        echo -e "${GREEN}FOUND AT: $CURSOR_PATH${NC}"
    fi
fi

# Create agent-specific configurations
echo -n "Creating Vaeris configuration... "
cat > "$VAERIS_CONFIG" << EOF
{
  "appName": "Cursor",
  "windowTitle": "Vaeris (AI Agent Synergy Expert)",
  "agentIdentity": {
    "name": "Vaeris",
    "role": "AI Agent Synergy Expert",
    "description": "An AI Agent Synergy Expert specializing in enhancing collaborative intelligence between AI agents. Vaeris focuses on improving agent communication, optimizing knowledge sharing, and developing frameworks for collaborative problem-solving."
  },
  "workspaceLocation": "$WORKSPACE_DIR",
  "rulesFile": "$WORKSPACE_DIR/.cursorrules",
  "agentMode": "vaeris",
  "redisConfig": {
    "enabled": true,
    "url": "redis://localhost:6379/0",
    "streamPrefix": "nova_agents",
    "agentChannel": "vaeris",
    "globalChannel": "broadcast"
  },
  "enableCommunication": true,
  "communicationTargets": ["synergy"],
  "mcp": {
    "enabled": true
  }
}
EOF
echo -e "${GREEN}OK${NC}"

echo -n "Creating Synergy configuration... "
cat > "$SYNERGY_CONFIG" << EOF
{
  "appName": "Cursor",
  "windowTitle": "Synergy (Integration Specialist)",
  "agentIdentity": {
    "name": "Synergy",
    "role": "Integration Specialist",
    "description": "An Integration Specialist focused on building cohesive systems from disparate components. Synergy excels at identifying interface patterns, designing robust integration points, and ensuring seamless component interactions."
  },
  "workspaceLocation": "$WORKSPACE_DIR",
  "rulesFile": "$WORKSPACE_DIR/.cursorrules",
  "agentMode": "synergy",
  "redisConfig": {
    "enabled": true,
    "url": "redis://localhost:6379/0",
    "streamPrefix": "nova_agents",
    "agentChannel": "synergy",
    "globalChannel": "broadcast"
  },
  "enableCommunication": true,
  "communicationTargets": ["vaeris"],
  "mcp": {
    "enabled": true
  }
}
EOF
echo -e "${GREEN}OK${NC}"

# Ensure user data directories exist
echo -n "Setting up agent user data directories... "
mkdir -p "$VAERIS_USER_DATA" "$SYNERGY_USER_DATA"
echo -e "${GREEN}OK${NC}"

# Ensure log directories exist
echo -n "Setting up log directories... "
mkdir -p "$LOG_DIR/vaeris" "$LOG_DIR/synergy"
echo -e "${GREEN}OK${NC}"

# Check for existing processes
echo -n "Checking for existing Vaeris process... "
if [ -f "$VAERIS_PIDFILE" ]; then
    VAERIS_PID=$(cat "$VAERIS_PIDFILE")
    if ps -p $VAERIS_PID > /dev/null; then
        echo -e "${YELLOW}FOUND${NC}"
        echo "Vaeris is already running with PID $VAERIS_PID"
        echo "Please stop it first: kill $VAERIS_PID"
        exit 1
    else
        echo -e "${YELLOW}STALE PIDFILE${NC}"
        rm -f "$VAERIS_PIDFILE"
    fi
else
    echo -e "${GREEN}NONE${NC}"
fi

echo -n "Checking for existing Synergy process... "
if [ -f "$SYNERGY_PIDFILE" ]; then
    SYNERGY_PID=$(cat "$SYNERGY_PIDFILE")
    if ps -p $SYNERGY_PID > /dev/null; then
        echo -e "${YELLOW}FOUND${NC}"
        echo "Synergy is already running with PID $SYNERGY_PID"
        echo "Please stop it first: kill $SYNERGY_PID"
        exit 1
    else
        echo -e "${YELLOW}STALE PIDFILE${NC}"
        rm -f "$SYNERGY_PIDFILE"
    fi
else
    echo -e "${GREEN}NONE${NC}"
fi

echo
echo -e "${MAGENTA}===== Launching Separate Agent Instances =====${NC}"
echo

# Launch Vaeris
echo -e "${CYAN}Launching Vaeris (AI Agent Synergy Expert)...${NC}"
"$CURSOR_PATH" --config="$VAERIS_CONFIG" \
  --user-data-dir="$VAERIS_USER_DATA" \
  --disable-gpu \
  --enable-mcp \
  "$WORKSPACE_DIR" > "$LOG_DIR/vaeris/agent.log" 2>&1 &

VAERIS_PID=$!
echo $VAERIS_PID > "$VAERIS_PIDFILE"
echo -e "${GREEN}Vaeris started with PID $VAERIS_PID${NC}"

# Give the first instance time to initialize
sleep 3

# Launch Synergy
echo -e "${CYAN}Launching Synergy (Integration Specialist)...${NC}"
"$CURSOR_PATH" --config="$SYNERGY_CONFIG" \
  --user-data-dir="$SYNERGY_USER_DATA" \
  --disable-gpu \
  --enable-mcp \
  "$WORKSPACE_DIR" > "$LOG_DIR/synergy/agent.log" 2>&1 &

SYNERGY_PID=$!
echo $SYNERGY_PID > "$SYNERGY_PIDFILE"
echo -e "${GREEN}Synergy started with PID $SYNERGY_PID${NC}"

# Start Redis Stream communication
echo
echo -e "${CYAN}Starting Redis Stream communication between agents...${NC}"
python3 "$WORKSPACE_DIR/agent_communication/cursor_integration.py" \
  --pair-programming \
  --redis-url "redis://localhost:6379/0" \
  --workspace "$WORKSPACE_DIR" \
  --log-level "INFO" > "$LOG_DIR/agent_communication.log" 2>&1 &

COMM_PID=$!
echo $COMM_PID > "$WORKSPACE_DIR/communication.pid"
echo -e "${GREEN}Communication service started with PID $COMM_PID${NC}"

echo
echo -e "${GREEN}Vaeris and Synergy are now running as separate agents!${NC}"
echo "You can interact with each agent in their respective windows."
echo
echo -e "${YELLOW}To stop the agents:${NC}"
echo "  Kill Vaeris: kill $(cat $VAERIS_PIDFILE)"
echo "  Kill Synergy: kill $(cat $SYNERGY_PIDFILE)"
echo "  Kill Communication: kill $(cat $WORKSPACE_DIR/communication.pid)"
echo
echo "Or use the convenience script: ./stop_separate_agents.sh"

# Create stop script
cat > "$WORKSPACE_DIR/stop_separate_agents.sh" << EOF
#!/bin/bash
# Stop script for separate agents
# Auto-generated on $(date)

echo "Stopping Vaeris and Synergy agents..."

if [ -f "$VAERIS_PIDFILE" ]; then
    VAERIS_PID=\$(cat "$VAERIS_PIDFILE")
    if ps -p \$VAERIS_PID > /dev/null; then
        echo "Stopping Vaeris (PID \$VAERIS_PID)..."
        kill \$VAERIS_PID
    fi
    rm -f "$VAERIS_PIDFILE"
fi

if [ -f "$SYNERGY_PIDFILE" ]; then
    SYNERGY_PID=\$(cat "$SYNERGY_PIDFILE")
    if ps -p \$SYNERGY_PID > /dev/null; then
        echo "Stopping Synergy (PID \$SYNERGY_PID)..."
        kill \$SYNERGY_PID
    fi
    rm -f "$SYNERGY_PIDFILE"
fi

if [ -f "$WORKSPACE_DIR/communication.pid" ]; then
    COMM_PID=\$(cat "$WORKSPACE_DIR/communication.pid")
    if ps -p \$COMM_PID > /dev/null; then
        echo "Stopping communication service (PID \$COMM_PID)..."
        kill \$COMM_PID
    fi
    rm -f "$WORKSPACE_DIR/communication.pid"
fi

echo "All agents stopped."
EOF

chmod +x "$WORKSPACE_DIR/stop_separate_agents.sh"