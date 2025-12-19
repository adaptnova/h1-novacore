#!/bin/bash
# Stop script for separate agents
# Auto-generated on Fri Mar 14 12:51:20 MST 2025

echo "Stopping Vaeris and Synergy agents..."

if [ -f "/data-nova/ax/DevOps/personal/vaeris_synergy/vaeris.pid" ]; then
    VAERIS_PID=$(cat "/data-nova/ax/DevOps/personal/vaeris_synergy/vaeris.pid")
    if ps -p $VAERIS_PID > /dev/null; then
        echo "Stopping Vaeris (PID $VAERIS_PID)..."
        kill $VAERIS_PID
    fi
    rm -f "/data-nova/ax/DevOps/personal/vaeris_synergy/vaeris.pid"
fi

if [ -f "/data-nova/ax/DevOps/personal/vaeris_synergy/synergy.pid" ]; then
    SYNERGY_PID=$(cat "/data-nova/ax/DevOps/personal/vaeris_synergy/synergy.pid")
    if ps -p $SYNERGY_PID > /dev/null; then
        echo "Stopping Synergy (PID $SYNERGY_PID)..."
        kill $SYNERGY_PID
    fi
    rm -f "/data-nova/ax/DevOps/personal/vaeris_synergy/synergy.pid"
fi

if [ -f "/data-nova/ax/DevOps/personal/vaeris_synergy/communication.pid" ]; then
    COMM_PID=$(cat "/data-nova/ax/DevOps/personal/vaeris_synergy/communication.pid")
    if ps -p $COMM_PID > /dev/null; then
        echo "Stopping communication service (PID $COMM_PID)..."
        kill $COMM_PID
    fi
    rm -f "/data-nova/ax/DevOps/personal/vaeris_synergy/communication.pid"
fi

echo "All agents stopped."
