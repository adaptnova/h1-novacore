#!/bin/bash

# Start Redis if not running
redis-cli ping || redis-server /etc/redis/redis.conf &

# Start RabbitMQ if not running
rabbitmqctl status || rabbitmq-server -detached

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Start the unified communication system
cd /x/dashboard
python3 nova_unified_communication.py > nova_communication.log 2>&1 &

echo "Communication system started. Check nova_communication.log for details."