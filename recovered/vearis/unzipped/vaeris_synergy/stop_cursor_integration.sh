#!/bin/bash
# Stop script for cursor integration
# Auto-generated on Fri Mar 14 12:53:32 MST 2025

echo "Stopping cursor integration..."

if [ -f "/data-nova/ax/DevOps/personal/vaeris_synergy/vaeris_integration.pid" ]; then
    VAERIS_PID=$(cat "/data-nova/ax/DevOps/personal/vaeris_synergy/vaeris_integration.pid")
    if ps -p $VAERIS_PID > /dev/null; then
        echo "Stopping Vaeris cursor integration (PID $VAERIS_PID)..."
        kill $VAERIS_PID
    fi
    rm -f "/data-nova/ax/DevOps/personal/vaeris_synergy/vaeris_integration.pid"
fi

if [ -f "/data-nova/ax/DevOps/personal/vaeris_synergy/synergy_integration.pid" ]; then
    SYNERGY_PID=$(cat "/data-nova/ax/DevOps/personal/vaeris_synergy/synergy_integration.pid")
    if ps -p $SYNERGY_PID > /dev/null; then
        echo "Stopping Synergy cursor integration (PID $SYNERGY_PID)..."
        kill $SYNERGY_PID
    fi
    rm -f "/data-nova/ax/DevOps/personal/vaeris_synergy/synergy_integration.pid"
fi

echo "Cursor integration stopped."
