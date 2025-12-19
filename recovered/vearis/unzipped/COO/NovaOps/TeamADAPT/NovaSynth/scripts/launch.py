"""
NovaSynth Launch Script

Initializes and launches the framework synthesis system with RabbitMQ integration.
Sets up all necessary components for framework communication and evolution.

Created by Cosmos
Version: 0.1.0
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime

from src.novasynth import NovaSynth
from src.protocols.messaging_adapter import MessagingAdapter, MessageConfig
from src.adapters.framework_adapters import FrameworkBridge
from src.state.state_manager import StateManager
from src.resources.resource_manager import ResourceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('novasynth_launch.log')
    ]
)
logger = logging.getLogger(__name__)

async def launch_framework(framework_name: str):
    """Launch a specific framework service."""
    try:
        logger.info(f"Launching framework: {framework_name}")

        # Initialize components
        novasynth = NovaSynth()
        messaging = MessagingAdapter(
            MessageConfig(
                service_name=framework_name,
                rabbitmq_url="amqp://nova:nova@localhost/"
            )
        )
        bridge = FrameworkBridge()
        state_manager = StateManager()
        resource_manager = ResourceManager()

        # Connect messaging
        await messaging.connect()
        logger.info(f"Connected to RabbitMQ: {framework_name}")

        # Register framework
        await bridge.register_framework(framework_name, framework_name)
        await novasynth.add_framework(framework_name)
        logger.info(f"Registered framework: {framework_name}")

        # Start components
        await messaging.start_consuming()
        await novasynth.start()

        logger.info(f"Framework {framework_name} launched successfully")

        # Keep service running
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error launching framework {framework_name}: {str(e)}")
        sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Launch NovaSynth framework service")
    parser.add_argument(
        "--framework",
        type=str,
        required=True,
        help="Name of the framework to launch"
    )
    return parser.parse_args()

async def main():
    """Launch framework service."""
    args = parse_args()
    await launch_framework(args.framework)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Launch interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)