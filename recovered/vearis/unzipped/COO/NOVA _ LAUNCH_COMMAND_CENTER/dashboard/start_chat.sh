#!/bin/bash

# Make sure Redis is running
sudo service redis-server status || sudo service redis-server start
echo "Redis status: $?"

# Make sure RabbitMQ is running
sudo service rabbitmq-server status || sudo service rabbitmq-server start
echo "RabbitMQ status: $?"

# Start the web chat interface
cd /x/dashboard
python3 nova_web_chat.py