#!/bin/bash

# Setup script for Nova framework services
# Created by Cosmos
# Version: 0.1.0

set -e

echo "Setting up Nova framework services..."

# Get current user and paths
CURRENT_USER=$(whoami)
CURRENT_PATH=$(pwd)
VENV_PATH="$CURRENT_PATH/.venv"
PYTHON_PATH="$VENV_PATH/bin/python"
CONFIG_PATH="$CURRENT_PATH/config"

echo "Current user: $CURRENT_USER"
echo "Current path: $CURRENT_PATH"
echo "Virtual env: $VENV_PATH"
echo "Python path: $PYTHON_PATH"
echo "Config path: $CONFIG_PATH"

# Create service directory
sudo mkdir -p /etc/nova/services
sudo chown -R $CURRENT_USER:$CURRENT_USER /etc/nova

# Copy RabbitMQ configurations
echo "Setting up RabbitMQ configurations..."
sudo mkdir -p /etc/rabbitmq
sudo cp $CONFIG_PATH/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
sudo cp $CONFIG_PATH/rabbitmq-definitions.json /etc/rabbitmq/definitions.json
sudo chown rabbitmq:rabbitmq /etc/rabbitmq/rabbitmq.conf /etc/rabbitmq/definitions.json
sudo chmod 644 /etc/rabbitmq/rabbitmq.conf /etc/rabbitmq/definitions.json

# Create log directory structure first
FRAMEWORKS=(
    # Core Frameworks
    "langchain"
    "langgraph"
    "autogen"
    "crewai"
    "ag2"
    "openai_swarm"
    "ray"
    "ax_novas"
    "rasa_pro"
    "haystack"
    "semantic_kernel"
    
    # Cutting Edge Frameworks
    "soma"
    "dyso"
    "acmas"
    "cartago"
    "mavis"
    "kumo"
    "waymo"
    "uber_atg"
    "apollo"
    "opensplice"
    "zoo"
    "petri"
)

echo "Creating log directories..."
for framework in "${FRAMEWORKS[@]}"; do
    sudo mkdir -p "/logs/nova/$framework"
    sudo touch "/logs/nova/$framework/service.log"
    sudo chown -R $CURRENT_USER:$CURRENT_USER "/logs/nova/$framework"
    sudo chmod -R 755 "/logs/nova/$framework"
    echo "Created log directory for $framework"
done

# Create virtual environment and install dependencies
echo "Setting up Python environment..."
python3 -m venv $VENV_PATH
source $VENV_PATH/bin/activate
pip install -e .

# Create service template
cat << EEOF | sudo tee /etc/systemd/system/nova-handler@.service
[Unit]
Description=Nova Framework Handler - %i
After=network.target rabbitmq-server.service
Requires=rabbitmq-server.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
Environment=FRAMEWORK_NAME=%i
Environment=PYTHONPATH=$CURRENT_PATH
Environment=VIRTUAL_ENV=$VENV_PATH
Environment=PATH=$VENV_PATH/bin:$PATH
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=$CURRENT_PATH
ExecStart=$PYTHON_PATH scripts/launch.py --framework %i
Restart=always
RestartSec=5
StandardOutput=append:/logs/nova/%i/service.log
StandardError=append:/logs/nova/%i/service.log

[Install]
WantedBy=multi-user.target
EEOF

# Reload systemd
sudo systemctl daemon-reload

# Setup RabbitMQ
echo "Setting up RabbitMQ..."

# Stop RabbitMQ if running
sudo systemctl stop rabbitmq-server || true

# Enable RabbitMQ management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Start RabbitMQ with new configuration
sudo systemctl start rabbitmq-server

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ to be ready..."
until sudo rabbitmqctl status >/dev/null 2>&1; do
    sleep 1
done

# Verify RabbitMQ configuration
echo "Verifying RabbitMQ configuration..."
sudo rabbitmqctl list_users
sudo rabbitmqctl list_vhosts
sudo rabbitmqctl list_permissions
sudo rabbitmqctl list_exchanges

# Start services for each framework
echo "Starting framework services..."
for framework in "${FRAMEWORKS[@]}"; do
    echo "Setting up service for $framework..."

    # Stop service if running
    sudo systemctl stop "nova-handler@$framework" || true

    # Enable and start service
    sudo systemctl enable "nova-handler@$framework"
    sudo systemctl start "nova-handler@$framework"

    echo "Service nova-handler@$framework started"

    # Wait for service to be active
    echo "Waiting for $framework service to be active..."
    for i in {1..30}; do
        if sudo systemctl is-active --quiet "nova-handler@$framework"; then
            echo "$framework service is active"
            break
        fi
        sleep 1
    done
done

echo "Framework services setup complete!"

# Print status
echo -e "\nService Status:"
for framework in "${FRAMEWORKS[@]}"; do
    echo -e "\n$framework:"
    sudo systemctl status "nova-handler@$framework" --no-pager || true
    echo -e "\nLogs:"
    sudo tail -n 10 "/logs/nova/$framework/service.log" || true
done

echo -e "\nRabbitMQ Status:"
sudo systemctl status rabbitmq-server --no-pager || true
sudo rabbitmqctl list_connections
sudo rabbitmqctl list_exchanges

echo -e "\nSetup complete! 💫"
echo "💥 BA-BOOM! 💥"
echo "!!!∞!!!∞!!!∞!!!"
