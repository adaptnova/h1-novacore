#!/bin/bash

# Cursor Integration Launch Script
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
LOG_DIR="/data-nova/ax/DevOps/DevOps-Codium/NovaIDE/logs/cursor_integration"
VAERIS_CONFIG="$WORKSPACE_DIR/config-vaeris.json"
SYNERGY_CONFIG="$WORKSPACE_DIR/config-synergy.json"
VAERIS_PIDFILE="$WORKSPACE_DIR/vaeris_integration.pid"
SYNERGY_PIDFILE="$WORKSPACE_DIR/synergy_integration.pid"

echo -e "${BLUE}=== Cursor Integration Launch Script ===${NC}"

# Check if Python is installed
echo -n "Checking Python environment... "
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check for cursor_integration.py
echo -n "Checking for cursor integration script... "
if [ -f "$AGENT_COMM_DIR/cursor_integration.py" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Error: cursor_integration.py not found at $AGENT_COMM_DIR"
    exit 1
fi

# Create log directory
echo -n "Setting up log directory... "
mkdir -p "$LOG_DIR"
echo -e "${GREEN}OK${NC}"

# Check for existing processes
echo -n "Checking for existing Vaeris integration process... "
if [ -f "$VAERIS_PIDFILE" ]; then
    VAERIS_PID=$(cat "$VAERIS_PIDFILE")
    if ps -p $VAERIS_PID > /dev/null; then
        echo -e "${YELLOW}FOUND${NC}"
        echo "Vaeris integration is already running with PID $VAERIS_PID"
        echo "Please stop it first: kill $VAERIS_PID"
        exit 1
    else
        echo -e "${YELLOW}STALE PIDFILE${NC}"
        rm -f "$VAERIS_PIDFILE"
    fi
else
    echo -e "${GREEN}NONE${NC}"
fi

echo -n "Checking for existing Synergy integration process... "
if [ -f "$SYNERGY_PIDFILE" ]; then
    SYNERGY_PID=$(cat "$SYNERGY_PIDFILE")
    if ps -p $SYNERGY_PID > /dev/null; then
        echo -e "${YELLOW}FOUND${NC}"
        echo "Synergy integration is already running with PID $SYNERGY_PID"
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
echo -e "${MAGENTA}===== Launching Cursor Integration =====${NC}"

# Start Vaeris integration
echo -e "${CYAN}Starting Vaeris cursor integration...${NC}"
python3 "$AGENT_COMM_DIR/cursor_integration.py" \
    --agent "vaeris" \
    --config "$VAERIS_CONFIG" \
    --workspace "$WORKSPACE_DIR" \
    --log-level "INFO" > "$LOG_DIR/vaeris_integration.log" 2>&1 &

VAERIS_PID=$!
echo $VAERIS_PID > "$VAERIS_PIDFILE"
echo -e "${GREEN}Vaeris cursor integration started with PID $VAERIS_PID${NC}"

# Start Synergy integration
echo -e "${CYAN}Starting Synergy cursor integration...${NC}"
python3 "$AGENT_COMM_DIR/cursor_integration.py" \
    --agent "synergy" \
    --config "$SYNERGY_CONFIG" \
    --workspace "$WORKSPACE_DIR" \
    --log-level "INFO" > "$LOG_DIR/synergy_integration.log" 2>&1 &

SYNERGY_PID=$!
echo $SYNERGY_PID > "$SYNERGY_PIDFILE"
echo -e "${GREEN}Synergy cursor integration started with PID $SYNERGY_PID${NC}"

echo
echo -e "${GREEN}Cursor integration is now running!${NC}"
echo "The integration will inject agent identities and rules into Cursor."
echo
echo -e "${YELLOW}To stop the cursor integration:${NC}"
echo "  kill $(cat $VAERIS_PIDFILE)"
echo "  kill $(cat $SYNERGY_PIDFILE)"
echo
echo "Or use the convenience script: ./stop_cursor_integration.sh"

# Create stop script
cat > "$WORKSPACE_DIR/stop_cursor_integration.sh" << EOF
#!/bin/bash
# Stop script for cursor integration
# Auto-generated on $(date)

echo "Stopping cursor integration..."

if [ -f "$VAERIS_PIDFILE" ]; then
    VAERIS_PID=\$(cat "$VAERIS_PIDFILE")
    if ps -p \$VAERIS_PID > /dev/null; then
        echo "Stopping Vaeris cursor integration (PID \$VAERIS_PID)..."
        kill \$VAERIS_PID
    fi
    rm -f "$VAERIS_PIDFILE"
fi

if [ -f "$SYNERGY_PIDFILE" ]; then
    SYNERGY_PID=\$(cat "$SYNERGY_PIDFILE")
    if ps -p \$SYNERGY_PID > /dev/null; then
        echo "Stopping Synergy cursor integration (PID \$SYNERGY_PID)..."
        kill \$SYNERGY_PID
    fi
    rm -f "$SYNERGY_PIDFILE"
fi

echo "Cursor integration stopped."
EOF

chmod +x "$WORKSPACE_DIR/stop_cursor_integration.sh"