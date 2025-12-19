#!/bin/bash

# Ensure script is executable
chmod +x "$0"

# Create logs directory if it doesn't exist
mkdir -p /x/logs

# Make sure Redis is running
sudo service redis-server restart
echo "Redis status: $?"

# Make sure RabbitMQ is running
sudo service rabbitmq-server restart
echo "RabbitMQ status: $?"

# Set RabbitMQ admin user if not exists
sudo rabbitmqctl list_users | grep "admin" || sudo rabbitmqctl add_user admin SecurePassword123!
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

# Navigate to dashboard directory
cd /x/dashboard

# Start web interface in background
python3 nova_web_chat.py > /x/logs/nova_web_chat.log 2>&1 &
WEB_PID=$!
echo "Web interface started with PID: $WEB_PID"

# Export required environment variables
export DISPLAY=:1
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=admin
export RABBITMQ_PASS=SecurePassword123!
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Start GUI interface
python3 nova_chat_gui.py > /x/logs/nova_gui_chat.log 2>&1 &
GUI_PID=$!
echo "GUI interface started with PID: $GUI_PID"

# Create stop script
cat > /x/dashboard/stop_nova_chat.sh << 'EOL'
#!/bin/bash
kill $(pgrep -f "python3 nova_web_chat.py")
kill $(pgrep -f "python3 nova_chat_gui.py")
echo "Nova chat system stopped"
EOL

chmod +x /x/dashboard/stop_nova_chat.sh

echo "Nova chat system started. Use stop_nova_chat.sh to stop the system."
echo "Logs available at:"
echo "  - /x/logs/nova_web_chat.log"
echo "  - /x/logs/nova_gui_chat.log"