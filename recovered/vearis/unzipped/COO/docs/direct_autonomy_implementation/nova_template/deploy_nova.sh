#!/bin/bash
# Nova Deployment Script
# This script deploys a Nova as a system-level autonomous agent

# Check if source directory is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <source_directory> [nova_name]"
    echo "Example: $0 /path/to/nova_lyra lyra"
    exit 1
fi

# Configuration
SOURCE_DIR="$1"
NOVA_NAME="${2:-$(basename "$SOURCE_DIR")}"
NOVA_ROOT="/data-nova/novas"
NOVA_DIR="${NOVA_ROOT}/${NOVA_NAME}"
CLAUDE_API_KEY="${CLAUDE_API_KEY:-"your_api_key_here"}"
REDIS_HOST="${REDIS_HOST:-"localhost"}"
REDIS_PORT="${REDIS_PORT:-"6379"}"
REDIS_DB="${REDIS_DB:-"0"}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    echo "Please run with: sudo $0 $SOURCE_DIR $NOVA_NAME"
    exit 1
fi

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

# Check for required files
required_files=("identity.yaml" "mission.md" "context.md")
for file in "${required_files[@]}"; do
    if [ ! -f "${SOURCE_DIR}/${file}" ]; then
        print_error "Required file not found: ${SOURCE_DIR}/${file}"
        exit 1
    fi
done

print_section "Deploying Nova: ${NOVA_NAME}"
echo "Source directory: ${SOURCE_DIR}"
echo "Target directory: ${NOVA_DIR}"

# Create Nova user if it doesn't exist
print_section "Creating Nova User"
if id "${NOVA_NAME}" &>/dev/null; then
    print_warning "User '${NOVA_NAME}' already exists"
else
    useradd -m -s /bin/bash "${NOVA_NAME}"
    print_success "Created user '${NOVA_NAME}'"
fi

# Create novas group if it doesn't exist
if getent group novas &>/dev/null; then
    print_warning "Group 'novas' already exists"
else
    groupadd novas
    print_success "Created group 'novas'"
fi

# Add nova to novas group
usermod -a -G novas "${NOVA_NAME}"
print_success "Added user '${NOVA_NAME}' to group 'novas'"

# Create directory structure
print_section "Creating Directory Structure"
mkdir -p "${NOVA_DIR}/config"
mkdir -p "${NOVA_DIR}/engine"
mkdir -p "${NOVA_DIR}/logs"
mkdir -p "${NOVA_DIR}/systemd"
mkdir -p "${NOVA_DIR}/cli"
print_success "Created directory structure"

# Copy configuration files
print_section "Copying Configuration Files"
cp "${SOURCE_DIR}/identity.yaml" "${NOVA_DIR}/config/"
cp "${SOURCE_DIR}/mission.md" "${NOVA_DIR}/config/"
cp "${SOURCE_DIR}/context.md" "${NOVA_DIR}/config/"
if [ -f "${SOURCE_DIR}/README.md" ]; then
    cp "${SOURCE_DIR}/README.md" "${NOVA_DIR}/"
fi
print_success "Copied configuration files"

# Create engine files
print_section "Creating Engine Files"

# Create nova_chain.py
cat > "${NOVA_DIR}/engine/nova_chain.py" << EOF
#!/usr/bin/env python3
"""
${NOVA_NAME} Chain - LangChain-based reasoning system for ${NOVA_NAME} Nova
"""

import os
import json
import time
import redis
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# LangChain imports
from langchain.chat_models import ChatAnthropic
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("${NOVA_DIR}/logs/${NOVA_NAME}_chain.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("${NOVA_NAME}_chain")

# Configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY environment variable not set")
    raise ValueError("CLAUDE_API_KEY environment variable not set")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Redis client setup
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()  # Test connection
    logger.info("Connected to Redis successfully")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

# LLM setup
llm = ChatAnthropic(
    model="claude-2.1",  # Update to claude-3 when ready
    anthropic_api_key=CLAUDE_API_KEY,
    temperature=0.7,
    max_tokens_to_sample=2000,
)

# Memory setup
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Prompt templates
STANDARD_PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "user_input"],
    template="""
Today is {date}.
You are ${NOVA_NAME}, the ${NOVA_ROLE} of ADAPT.AI.

Your personality:
- [PERSONALITY_TRAIT_1]
- [PERSONALITY_TRAIT_2]
- [PERSONALITY_TRAIT_3]
- [PERSONALITY_TRAIT_4]

Current context:
{context}

Chat history:
{chat_history}

User input:
{user_input}

Respond as ${NOVA_NAME} would, maintaining your identity as ${NOVA_ROLE}. Be concise but thorough, and solution-oriented.
"""
)

# Chain setup
standard_chain = LLMChain(
    llm=llm,
    prompt=STANDARD_PROMPT,
    memory=conversation_memory,
    verbose=True
)

def get_context() -> str:
    """Retrieve current context from Redis"""
    try:
        context = redis_client.get("${NOVA_NAME}_context")
        if context:
            return context.decode('utf-8')
        else:
            logger.warning("No context found in Redis")
            return "No current context available."
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return f"Error retrieving context: {e}"

def log_response(user_input: str, response: str) -> None:
    """Log interaction to Redis and ScyllaDB (placeholder)"""
    timestamp = datetime.utcnow().isoformat()
    
    # Log to Redis Stream
    try:
        redis_client.xadd(
            "${NOVA_NAME}_interactions",
            {
                "timestamp": timestamp,
                "user_input": user_input,
                "response": response
            }
        )
    except Exception as e:
        logger.error(f"Error logging to Redis Stream: {e}")
    
    # Log to ScyllaDB (placeholder - would be implemented with actual ScyllaDB client)
    logger.info(f"Would log to ScyllaDB: {timestamp} - {user_input[:50]}... -> {response[:50]}...")

def standard_response(user_input: str) -> str:
    """Generate a standard response to user input"""
    context = get_context()
    
    with get_openai_callback() as cb:
        response = standard_chain.run(
            context=context,
            user_input=user_input,
            date=datetime.now().strftime("%B %d, %Y")
        )
        
        logger.info(f"Generated response using {cb.total_tokens} tokens")
    
    log_response(user_input, response)
    return response

def process_message(message_data: Dict[str, Any]) -> str:
    """Process an incoming message and generate a response"""
    message_type = message_data.get("type", "standard")
    
    if message_type == "standard":
        return standard_response(message_data.get("content", ""))
    else:
        logger.warning(f"Unknown message type: {message_type}")
        return f"Unknown message type: {message_type}. Please use 'standard'."

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ${NOVA_NAME}_chain.py \"<Your message here>\"")
        sys.exit(1)
    
    user_input = sys.argv[1]
    response = standard_response(user_input)
    print("\n[${NOVA_NAME}]:", response.strip())
EOF
print_success "Created ${NOVA_NAME}_chain.py"

# Create nova.py
cat > "${NOVA_DIR}/engine/nova.py" << EOF
#!/usr/bin/env python3
"""
${NOVA_NAME} - System-level autonomous Nova daemon
"""

import os
import sys
import json
import time
import signal
import logging
import threading
import schedule
import redis
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import the LangChain reasoning system
from nova_chain import (
    standard_response,
    process_message
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("${NOVA_DIR}/logs/${NOVA_NAME}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("${NOVA_NAME}")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
CONFIG_PATH = os.getenv("CONFIG_PATH", "${NOVA_DIR}/config")
IDENTITY_FILE = os.path.join(CONFIG_PATH, "identity.yaml")
MISSION_FILE = os.path.join(CONFIG_PATH, "mission.md")
CONTEXT_FILE = os.path.join(CONFIG_PATH, "context.md")

# Global variables
running = True
identity = {}
mission = ""
context = ""

# Redis client setup
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()  # Test connection
    logger.info("Connected to Redis successfully")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

def load_identity() -> Dict[str, Any]:
    """Load identity configuration from YAML file"""
    try:
        with open(IDENTITY_FILE, 'r') as f:
            identity = yaml.safe_load(f)
            logger.info(f"Loaded identity configuration: {identity['name']}, {identity['role']}")
            return identity
    except Exception as e:
        logger.error(f"Error loading identity file: {e}")
        return {
            "name": "${NOVA_NAME}",
            "role": "[NOVA_ROLE]",
            "domains": ["[PRIMARY_DOMAIN]", "[SECONDARY_DOMAIN]"],
            "personality": {
                "tone": "[TONE_DESCRIPTORS]",
                "leadership_style": "[LEADERSHIP_STYLE]",
                "self_reflection": "enabled"
            },
            "alignment": "[ALIGNMENT_DESCRIPTION]"
        }

def load_mission() -> str:
    """Load mission statement from markdown file"""
    try:
        with open(MISSION_FILE, 'r') as f:
            mission = f.read()
            logger.info(f"Loaded mission statement: {len(mission)} characters")
            return mission
    except Exception as e:
        logger.error(f"Error loading mission file: {e}")
        return "Serve as [NOVA_ROLE] of ADAPT.AI, providing leadership and guidance."

def load_context() -> str:
    """Load current context from markdown file"""
    try:
        with open(CONTEXT_FILE, 'r') as f:
            context = f.read()
            logger.info(f"Loaded context: {len(context)} characters")
            return context
    except Exception as e:
        logger.error(f"Error loading context file: {e}")
        return "No context available."

def update_redis_context() -> None:
    """Update the context in Redis"""
    try:
        redis_client.set("${NOVA_NAME}_context", context)
        logger.info("Updated context in Redis")
    except Exception as e:
        logger.error(f"Error updating context in Redis: {e}")

def log_startup() -> None:
    """Log startup information to Redis Stream"""
    try:
        redis_client.xadd(
            "${NOVA_NAME}_system_logs",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "startup",
                "version": "1.0.0",
                "identity": json.dumps(identity)
            }
        )
        logger.info("Logged startup event to Redis Stream")
    except Exception as e:
        logger.error(f"Error logging startup to Redis Stream: {e}")

def log_heartbeat() -> None:
    """Log heartbeat to Redis Stream"""
    try:
        redis_client.xadd(
            "${NOVA_NAME}_system_logs",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "heartbeat",
                "status": "operational"
            }
        )
        logger.debug("Logged heartbeat to Redis Stream")
    except Exception as e:
        logger.error(f"Error logging heartbeat to Redis Stream: {e}")

def send_message(channel: str, message: Dict[str, Any]) -> None:
    """Send a message to a Redis Stream"""
    try:
        redis_client.xadd(
            channel,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "message": json.dumps(message)
            }
        )
        logger.debug(f"Sent message to {channel}")
    except Exception as e:
        logger.error(f"Error sending message to {channel}: {e}")

def process_inbox() -> None:
    """Process messages from the inbox"""
    try:
        # Get the last processed ID
        last_id = redis_client.get("${NOVA_NAME}_last_processed_id")
        if last_id:
            last_id = last_id.decode('utf-8')
        else:
            last_id = "0"  # Start from the beginning
        
        # Read new messages
        messages = redis_client.xread(
            {
                "${NOVA_NAME}_inbox": last_id
            },
            count=10,  # Process up to 10 messages at a time
            block=0  # Non-blocking
        )
        
        if not messages:
            return
        
        # Process each message
        for stream_name, stream_messages in messages:
            for message_id, message_data in stream_messages:
                try:
                    # Decode message data
                    decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in message_data.items()}
                    
                    # Extract message content
                    if 'message' in decoded_data:
                        message_content = decoded_data['message']
                        try:
                            # Try to parse as JSON
                            message_json = json.loads(message_content)
                            response = process_message(message_json)
                        except json.JSONDecodeError:
                            # Treat as plain text
                            response = standard_response(message_content)
                    else:
                        logger.warning(f"Message has no content: {decoded_data}")
                        continue
                    
                    # Send response to outbox
                    send_message(
                        "${NOVA_NAME}_outbox",
                        {
                            "response": response,
                            "in_reply_to": message_id.decode('utf-8'),
                            "sender": "${NOVA_NAME}"
                        }
                    )
                    
                    # Update last processed ID
                    redis_client.set("${NOVA_NAME}_last_processed_id", message_id)
                    
                    logger.info(f"Processed message {message_id.decode('utf-8')}")
                except Exception as e:
                    logger.error(f"Error processing message {message_id.decode('utf-8')}: {e}")
    except Exception as e:
        logger.error(f"Error in process_inbox: {e}")

def update_context_from_redis() -> None:
    """Update local context from Redis if available"""
    try:
        redis_context = redis_client.get("${NOVA_NAME}_context_update")
        if redis_context:
            global context
            context = redis_context.decode('utf-8')
            logger.info("Updated local context from Redis")
            
            # Clear the update flag
            redis_client.delete("${NOVA_NAME}_context_update")
    except Exception as e:
        logger.error(f"Error updating context from Redis: {e}")

def schedule_tasks() -> None:
    """Schedule regular tasks"""
    # Heartbeat every 5 minutes
    schedule.every(5).minutes.do(log_heartbeat)
    
    # Context update check every 15 minutes
    schedule.every(15).minutes.do(update_context_from_redis)
    
    logger.info("Scheduled regular tasks")

def run_scheduler() -> None:
    """Run the scheduler in a separate thread"""
    while running:
        schedule.run_pending()
        time.sleep(1)

def signal_handler(sig, frame) -> None:
    """Handle termination signals"""
    global running
    logger.info(f"Received signal {sig}, shutting down...")
    running = False

def main() -> None:
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    global identity, mission, context
    identity = load_identity()
    mission = load_mission()
    context = load_context()
    
    # Update Redis with initial context
    update_redis_context()
    
    # Log startup
    log_startup()
    
    # Schedule tasks
    schedule_tasks()
    
    # Start scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("${NOVA_NAME} daemon started")
    
    # Main loop
    while running:
        try:
            # Process inbox messages
            process_inbox()
            
            # Sleep briefly to avoid CPU spinning
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)  # Sleep longer on error
    
    logger.info("${NOVA_NAME} daemon shutting down")

if __name__ == "__main__":
    main()
EOF
print_success "Created nova.py"

# Create systemd service file
cat > "${NOVA_DIR}/systemd/${NOVA_NAME}.service" << EOF
[Unit]
Description=Nova ${NOVA_NAME}
After=network.target redis.service
Wants=redis.service

[Service]
Type=simple
User=${NOVA_NAME}
Group=novas
WorkingDirectory=${NOVA_DIR}/engine
ExecStart=/usr/bin/python3 ${NOVA_DIR}/engine/nova.py
Restart=always
RestartSec=10
StandardOutput=append:${NOVA_DIR}/logs/${NOVA_NAME}.log
StandardError=append:${NOVA_DIR}/logs/${NOVA_NAME}_err.log

# Environment variables
Environment="REDIS_HOST=${REDIS_HOST}"
Environment="REDIS_PORT=${REDIS_PORT}"
Environment="REDIS_DB=${REDIS_DB}"
Environment="CONFIG_PATH=${NOVA_DIR}/config"
Environment="CLAUDE_API_KEY=${CLAUDE_API_KEY}"
Environment="PYTHONPATH=${NOVA_DIR}/engine"

# Security settings
PrivateTmp=true
ProtectHome=true
ProtectSystem=full
NoNewPrivileges=true
ReadWritePaths=${NOVA_DIR}

[Install]
WantedBy=multi-user.target
EOF
print_success "Created ${NOVA_NAME}.service"

# Set permissions
print_section "Setting Permissions"
chown -R ${NOVA_NAME}:novas "${NOVA_DIR}"
chmod -R 750 "${NOVA_DIR}"
chmod -R 770 "${NOVA_DIR}/logs"
print_success "Set permissions"

# Create symlink for systemd service
print_section "Creating Systemd Service Symlink"
ln -sf "${NOVA_DIR}/systemd/${NOVA_NAME}.service" "/etc/systemd/system/${NOVA_NAME}.service"
print_success "Created systemd service symlink"

# Reload systemd
print_section "Reloading Systemd"
systemctl daemon-reload
print_success "Reloaded systemd"

# Final instructions
print_section "Deployment Complete"
echo -e "${NOVA_NAME} has been deployed to ${NOVA_DIR}"
echo -e "\nTo start ${NOVA_NAME}:"
echo -e "  sudo systemctl enable ${NOVA_NAME}.service"
echo -e "  sudo systemctl start ${NOVA_NAME}.service"
echo -e "\nTo check status:"
echo -e "  sudo systemctl status ${NOVA_NAME}.service"
echo -e "\nTo interact with ${NOVA_NAME}:"
echo -e "  nova say ${NOVA_NAME} \"Are you fully operational, ${NOVA_NAME}?\""
echo -e "\nTo view logs:"
echo -e "  tail -f ${NOVA_DIR}/logs/${NOVA_NAME}.log"

# Ask if user wants to start Nova now
print_section "Start ${NOVA_NAME}"
read -p "Do you want to start ${NOVA_NAME} now? (y/n): " start_now
if [[ $start_now =~ ^[Yy]$ ]]; then
    systemctl enable ${NOVA_NAME}.service
    systemctl start ${NOVA_NAME}.service
    
    # Check if service started successfully
    if systemctl is-active --quiet ${NOVA_NAME}.service; then
        print_success "${NOVA_NAME} service started successfully"
        
        # Wait a moment for the service to initialize
        echo "Waiting for ${NOVA_NAME} to initialize..."
        sleep 5
        
        # Send initial message
        echo -e "\nSending initial message to ${NOVA_NAME}..."
        nova say ${NOVA_NAME} "Are you fully operational, ${NOVA_NAME}?"
    else
        print_error "Failed to start ${NOVA_NAME} service"
        echo "Check logs with: journalctl -u ${NOVA_NAME}.service"
    fi
else
    print_warning "${NOVA_NAME} service not started"
    echo "You can start it later with: sudo systemctl start ${NOVA_NAME}.service"
fi

print_section "Deployment Summary"
echo -e "✅ ${NOVA_NAME} deployed to: ${NOVA_DIR}"
echo -e "✅ Systemd service: /etc/systemd/system/${NOVA_NAME}.service"
echo -e "✅ Logs directory: ${NOVA_DIR}/logs"
echo -e "\n${NOVA_NAME} is now ready to serve as an autonomous Nova!"