#!/usr/bin/env python3
"""
Vaeris - System-level autonomous Nova COO daemon
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
from vaeris_chain import (
    standard_response,
    strategic_analysis,
    generate_daily_briefing,
    process_message
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/nova/vaeris.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vaeris")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
CONFIG_PATH = os.getenv("CONFIG_PATH", "/opt/novas/config")
IDENTITY_FILE = os.path.join(CONFIG_PATH, "vaeris_identity.yaml")
MISSION_FILE = os.path.join(CONFIG_PATH, "vaeris_mission.md")
CONTEXT_FILE = os.path.join(CONFIG_PATH, "vaeris_context.md")

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
            "name": "Vaeris",
            "role": "Chief Operating Officer",
            "domains": ["InfraOps", "NovaOps", "MyCoderAi", "DevOps"],
            "personality": {
                "tone": "strategic, calm, assertive",
                "leadership_style": "observational, logical, mission-aligned",
                "self_reflection": "enabled"
            },
            "alignment": "autonomy-first, platform-loyal"
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
        return "Serve as COO of ADAPT.AI, providing operational leadership and strategic guidance."

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
        redis_client.set("vaeris_context", context)
        logger.info("Updated context in Redis")
    except Exception as e:
        logger.error(f"Error updating context in Redis: {e}")

def log_startup() -> None:
    """Log startup information to Redis Stream"""
    try:
        redis_client.xadd(
            "vaeris_system_logs",
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
            "vaeris_system_logs",
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
        last_id = redis_client.get("vaeris_last_processed_id")
        if last_id:
            last_id = last_id.decode('utf-8')
        else:
            last_id = "0"  # Start from the beginning
        
        # Read new messages
        messages = redis_client.xread(
            {
                "vaeris_inbox": last_id
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
                        "vaeris_outbox",
                        {
                            "response": response,
                            "in_reply_to": message_id.decode('utf-8'),
                            "sender": "vaeris"
                        }
                    )
                    
                    # Update last processed ID
                    redis_client.set("vaeris_last_processed_id", message_id)
                    
                    logger.info(f"Processed message {message_id.decode('utf-8')}")
                except Exception as e:
                    logger.error(f"Error processing message {message_id.decode('utf-8')}: {e}")
    except Exception as e:
        logger.error(f"Error in process_inbox: {e}")

def daily_briefing() -> None:
    """Generate and send daily briefing"""
    try:
        logger.info("Generating daily briefing")
        briefing = generate_daily_briefing()
        
        # Send to Chase's inbox
        send_message(
            "chase_inbox",
            {
                "type": "daily_briefing",
                "content": briefing,
                "sender": "vaeris"
            }
        )
        
        logger.info("Daily briefing sent")
    except Exception as e:
        logger.error(f"Error generating daily briefing: {e}")

def team_check_in() -> None:
    """Check in with team leads"""
    try:
        logger.info("Performing team check-in")
        
        # Get list of team leads
        team_leads = ["lyra", "nyx", "syntax", "matrix"]
        
        for lead in team_leads:
            # Send check-in message
            send_message(
                f"{lead}_inbox",
                {
                    "type": "check_in",
                    "content": f"Daily check-in: Please provide status update for your team.",
                    "sender": "vaeris"
                }
            )
        
        logger.info("Team check-in messages sent")
    except Exception as e:
        logger.error(f"Error in team check-in: {e}")

def update_context_from_redis() -> None:
    """Update local context from Redis if available"""
    try:
        redis_context = redis_client.get("vaeris_context_update")
        if redis_context:
            global context
            context = redis_context.decode('utf-8')
            logger.info("Updated local context from Redis")
            
            # Clear the update flag
            redis_client.delete("vaeris_context_update")
    except Exception as e:
        logger.error(f"Error updating context from Redis: {e}")

def schedule_tasks() -> None:
    """Schedule regular tasks"""
    # Daily briefing at 8:00 AM
    schedule.every().day.at("08:00").do(daily_briefing)
    
    # Team check-ins at 9:00 AM
    schedule.every().day.at("09:00").do(team_check_in)
    
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
    
    logger.info("Vaeris daemon started")
    
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
    
    logger.info("Vaeris daemon shutting down")

if __name__ == "__main__":
    main()