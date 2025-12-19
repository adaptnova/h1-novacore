#!/bin/bash

# Setup script for Slack integration testing
echo "Setting up Slack integration test environment..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv slack_test_env

# Activate virtual environment
echo "Activating virtual environment..."
source slack_test_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_slack.txt

# Create .env file template
echo "Creating .env template..."
cat > .env.template << EOL
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-token-here

# Nova Integration Settings
NOVA_ENV=test
HITL_MODE=active

# Database URLs
POSTGRES_URL=postgresql://user:pass@localhost:5432/nova_db
MONGODB_URL=mongodb://localhost:27017
NEO4J_URL=bolt://localhost:7687

# Message Queue Settings
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
KAFKA_BROKERS=localhost:9092

# LLM API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
EOL

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env"
echo "2. Add your Slack bot token to .env"
echo "3. Run test_slack_integration.py"
echo ""
echo "Example:"
echo "cp .env.template .env"
echo "nano .env  # Add your Slack token"
echo "python3 test_slack_integration.py"

# Make test script executable
chmod +x test_slack_integration.py

# Create log directory
mkdir -p logs

echo ""
echo "Note: You'll need a Slack bot token with the following permissions:"
echo "- channels:read"
echo "- chat:write"
echo "- reactions:write"
echo ""
echo "The bot should be invited to the following channels:"
echo "- #nova-911"
echo "- #nova-launch-status"
echo "- #nova-db-ops"
echo "- #nova-mq-ops"
echo "- #nova-framework"
echo "- #nova-monitor"
