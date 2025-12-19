"""
NovaSynth Messaging Adapter

Integrates with RabbitMQ-based Nova Communication Infrastructure for framework
messaging. Handles message routing, state synchronization, and framework
communication through the established messaging system.

Created by Cosmos
Version: 0.1.0
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

import aio_pika
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageConfig(BaseModel):
    """Configuration for messaging system."""
    service_name: str
    rabbitmq_url: str
    exchange_name: str = "nova_framework_exchange"
    queue_prefix: str = "nova_framework"
    routing_key_prefix: str = "framework"

class MessageMetadata(BaseModel):
    """Metadata for framework messages."""
    message_id: str
    timestamp: datetime
    source_framework: str
    target_framework: str
    message_type: str
    priority: str
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

class FrameworkMessage(BaseModel):
    """Message format for framework communication."""
    metadata: MessageMetadata
    content: Dict
    state_data: Optional[Dict] = None
    memory_data: Optional[Dict] = None
    tools_data: Optional[Dict] = None

class MessagingAdapter:
    """Adapter for RabbitMQ-based framework communication."""

    def __init__(self, config: MessageConfig):
        self.config = config
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.message_handlers: Dict[str, callable] = {}
        logger.info(f"Initialized messaging adapter for {config.service_name}")

    async def connect(self) -> None:
        """Connect to RabbitMQ server."""
        try:
            # Connect to RabbitMQ
            self.connection = await aio_pika.connect_robust(
                self.config.rabbitmq_url
            )

            # Create channel
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                self.config.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            # Declare queue
            queue_name = f"{self.config.queue_prefix}.{self.config.service_name}"
            self.queue = await self.channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": 3600000,  # 1 hour
                    "x-dead-letter-exchange": "nova_dlx"
                }
            )

            # Bind queue to exchange
            routing_key = f"{self.config.routing_key_prefix}.{self.config.service_name}"
            await self.queue.bind(self.exchange, routing_key)

            logger.info(f"Connected to RabbitMQ: {self.config.service_name}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def start_consuming(self) -> None:
        """Start consuming messages."""
        try:
            await self.queue.consume(self._process_message)
            logger.info(f"Started consuming messages: {self.config.service_name}")
        except Exception as e:
            logger.error(f"Failed to start consuming: {str(e)}")
            raise

    async def send_message(
        self,
        target_framework: str,
        message_type: str,
        content: Dict,
        priority: str = "normal",
        state_data: Optional[Dict] = None,
        memory_data: Optional[Dict] = None,
        tools_data: Optional[Dict] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> None:
        """Send message to target framework."""
        try:
            # Create message
            message = FrameworkMessage(
                metadata=MessageMetadata(
                    message_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    source_framework=self.config.service_name,
                    target_framework=target_framework,
                    message_type=message_type,
                    priority=priority,
                    correlation_id=correlation_id,
                    reply_to=reply_to
                ),
                content=content,
                state_data=state_data,
                memory_data=memory_data,
                tools_data=tools_data
            )

            # Create routing key
            routing_key = f"{self.config.routing_key_prefix}.{target_framework}"

            # Send message
            await self.exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message.dict()).encode(),
                    content_type="application/json",
                    content_encoding="utf-8",
                    priority=self._get_priority_value(priority),
                    message_id=message.metadata.message_id,
                    timestamp=int(message.metadata.timestamp.timestamp()),
                    correlation_id=correlation_id,
                    reply_to=reply_to,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=routing_key
            )

            logger.info(
                f"Sent message to {target_framework}: "
                f"{message.metadata.message_id}"
            )

        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise

    async def register_handler(
        self,
        message_type: str,
        handler: callable
    ) -> None:
        """Register handler for message type."""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for {message_type}")

    async def _process_message(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        """Process incoming message."""
        async with message.process():
            try:
                # Parse message
                body = json.loads(message.body.decode())
                framework_message = FrameworkMessage(**body)

                # Get handler
                handler = self.message_handlers.get(
                    framework_message.metadata.message_type
                )

                if handler:
                    # Handle message
                    await handler(framework_message)
                    logger.info(
                        f"Processed message: {framework_message.metadata.message_id}"
                    )
                else:
                    logger.warning(
                        f"No handler for message type: "
                        f"{framework_message.metadata.message_type}"
                    )

            except Exception as e:
                logger.error(f"Failed to process message: {str(e)}")
                # Requeue message
                await message.reject(requeue=True)

    def _get_priority_value(self, priority: str) -> int:
        """Convert priority string to integer value."""
        priorities = {
            "low": 1,
            "normal": 5,
            "high": 8,
            "critical": 10
        }
        return priorities.get(priority.lower(), 5)

    async def close(self) -> None:
        """Close connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Closed RabbitMQ connection")

# Example usage:
async def main():
    # Create config
    config = MessageConfig(
        service_name="test_framework",
        rabbitmq_url="amqp://guest:guest@localhost/"
    )

    # Create adapter
    adapter = MessagingAdapter(config)

    # Connect
    await adapter.connect()

    # Register handler
    async def handle_message(message: FrameworkMessage):
        logger.info(f"Received message: {message.metadata.message_id}")

    await adapter.register_handler("test_type", handle_message)

    # Start consuming
    await adapter.start_consuming()

    # Send test message
    await adapter.send_message(
        "target_framework",
        "test_type",
        {"key": "value"},
        priority="high"
    )

    # Wait for messages
    try:
        await asyncio.Future()  # run forever
    finally:
        await adapter.close()

if __name__ == "__main__":
    asyncio.run(main())