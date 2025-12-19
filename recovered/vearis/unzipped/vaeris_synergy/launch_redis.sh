#!/bin/bash

# Redis Launch Script for Nova Agent Communication
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

echo -e "${BLUE}=== Redis Launch Script ===${NC}"

# Check if Redis is already running
echo -n "Checking if Redis is already running... "
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo -e "${GREEN}YES${NC}"
    echo "Redis is already running, no need to start it."
    exit 0
fi
echo -e "${YELLOW}NO${NC}"

# Check for redis-server
echo -n "Checking for redis-server... "
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}NOT FOUND${NC}"
    echo "Redis server is not installed. Installing..."
    sudo apt-get update && sudo apt-get install -y redis-server
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Redis server.${NC}"
        echo "Please install it manually: sudo apt-get install redis-server"
        exit 1
    fi
    echo -e "${GREEN}Redis server installed successfully.${NC}"
fi

# Check if systemd service is enabled
echo -n "Checking Redis systemd service... "
if systemctl is-enabled redis-server &> /dev/null || systemctl is-enabled redis &> /dev/null; then
    echo -e "${GREEN}ENABLED${NC}"
    # Start Redis using systemd
    echo -n "Starting Redis using systemd... "
    if systemctl is-enabled redis-server &> /dev/null; then
        sudo systemctl start redis-server
    else
        sudo systemctl start redis
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}SUCCESS${NC}"
    else
        echo -e "${RED}FAILED${NC}"
        echo "Failed to start Redis using systemd."
        echo "Will try starting Redis directly."
    fi
else
    echo -e "${YELLOW}NOT ENABLED${NC}"
    echo "Redis systemd service is not enabled."
fi

# Verify Redis is running
echo -n "Verifying Redis is running... "
sleep 2  # Give Redis a moment to start

if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}SUCCESS${NC}"
    echo -e "Redis is now ${GREEN}running${NC} and ready for agent communication."
else
    echo -e "${RED}FAILED${NC}"
    echo "Could not verify Redis is running. Trying to start it directly..."
    
    # Start Redis directly
    echo -n "Starting Redis directly... "
    redis-server --daemonize yes
    
    sleep 2  # Give Redis a moment to start
    
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}SUCCESS${NC}"
        echo -e "Redis is now ${GREEN}running${NC} and ready for agent communication."
    else
        echo -e "${RED}FAILED${NC}"
        echo "All attempts to start Redis have failed."
        echo "Please check Redis installation and configuration."
        exit 1
    fi
fi

echo
echo -e "${MAGENTA}===== Redis for Nova Stream Communication =====${NC}"
echo "Redis is now running and available for Nova agent communication."
echo "You can now start the Nova Stream communication system with:"
echo -e "${CYAN}./launch_redis_stream.sh${NC}"
echo
echo -e "${YELLOW}To stop Redis:${NC} sudo systemctl stop redis"
echo