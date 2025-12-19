#!/usr/bin/env python3
"""
Nova Stream - Redis-based Communication for Nova Agents
Created by Forge - March 14, 2025
Version: 1.0.0

This module provides a Redis Streams-based communication system for Nova agents,
enabling efficient, real-time messaging between agents like Vaeris and Synergy.
"""

import redis
import json
import time
import uuid
import argparse
import threading
import logging
import os
import signal
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("nova_stream")

class NovaStream:
    """Redis Streams-based communication system for Nova agents"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 stream_prefix: str = "nova_stream"):
        """Initialize the Nova Stream communication system
        
        Args:
            redis_url: Redis connection URL
            stream_prefix: Prefix for all stream names
        """
        self.redis = redis.from_url(redis_url)
        self.stream_prefix = stream_prefix
        self.consumer_groups: Dict[str, bool] = {}
        self.listeners: Dict[str, List[Callable]] = {}
        self.running = False
        self.listener_threads: Dict[str, threading.Thread] = {}
    
    def get_stream_name(self, channel: str) -> str:
        """Get the full stream name for a channel"""
        return f"{self.stream_prefix}:{channel}"
    
    def publish(self, channel: str, message: Dict[str, Any], 
                sender: str = "system", max_len: int = 1000) -> str:
        """Publish a message to a channel
        
        Args:
            channel: Channel name to publish to
            message: Message content (will be JSON serialized)
            sender: Sender identifier
            max_len: Maximum stream length to maintain
            
        Returns:
            Message ID from Redis
        """
        # Prepare the message with metadata
        full_message = {
            "sender": sender,
            "timestamp": time.time(),
            "message_id": str(uuid.uuid4()),
            "content": json.dumps(message)
        }
        
        # Publish to Redis Stream
        stream_name = self.get_stream_name(channel)
        message_id = self.redis.xadd(stream_name, full_message, maxlen=max_len)
        logger.debug(f"Published to {stream_name}: {message}")
        return message_id
    
    def ensure_consumer_group(self, channel: str, group: str) -> bool:
        """Ensure a consumer group exists for a channel, creating it if needed
        
        Args:
            channel: Channel name
            group: Consumer group name
            
        Returns:
            True if successful
        """
        key = f"{channel}:{group}"
        if key in self.consumer_groups:
            return True
            
        try:
            stream_name = self.get_stream_name(channel)
            self.redis.xgroup_create(
                stream_name, 
                group,
                id="$",  # Only consume new messages
                mkstream=True  # Create stream if it doesn't exist
            )
            self.consumer_groups[key] = True
            logger.info(f"Created consumer group {group} for {stream_name}")
            return True
        except redis.exceptions.ResponseError as e:
            # Group already exists
            if "BUSYGROUP" in str(e):
                self.consumer_groups[key] = True
                return True
            logger.error(f"Error creating consumer group: {e}")
            raise
    
    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None], 
                  group: str, consumer: str) -> None:
        """Subscribe to a channel with a message handler
        
        Args:
            channel: Channel name to subscribe to
            handler: Callback function for messages
            group: Consumer group name
            consumer: Consumer name within the group
        """
        if channel not in self.listeners:
            self.listeners[channel] = []
        
        self.listeners[channel].append(handler)
        logger.info(f"Added listener for {channel} in group {group} as {consumer}")
        
        # Ensure consumer group exists
        self.ensure_consumer_group(channel, group)
        
        # Start listener thread if needed
        if channel not in self.listener_threads or not self.listener_threads[channel].is_alive():
            self.start_listener(channel, group, consumer)
    
    def start_listener(self, channel: str, group: str, consumer: str) -> None:
        """Start a listener thread for a channel
        
        Args:
            channel: Channel to listen on
            group: Consumer group name
            consumer: Consumer name within the group
        """
        if channel in self.listener_threads and self.listener_threads[channel].is_alive():
            logger.warning(f"Listener thread for {channel} already running")
            return
        
        # Create and start the listener thread
        thread = threading.Thread(
            target=self._listener_loop,
            args=(channel, group, consumer),
            daemon=True
        )
        self.listener_threads[channel] = thread
        thread.start()
        logger.info(f"Started listener thread for {channel}")
    
    def _listener_loop(self, channel: str, group: str, consumer: str) -> None:
        """Background thread for listening to messages on a channel
        
        Args:
            channel: Channel to listen on
            group: Consumer group name
            consumer: Consumer name within the group
        """
        stream_name = self.get_stream_name(channel)
        logger.info(f"Listener loop started for {stream_name}, group {group}, consumer {consumer}")
        
        while self.running:
            try:
                # Read new messages from the stream
                response = self.redis.xreadgroup(
                    group, 
                    consumer,
                    {stream_name: ">"},  # > means all new messages
                    count=10,
                    block=1000  # Block for 1 second
                )
                
                if not response:
                    continue
                
                # Process messages
                stream_name, stream_messages = response[0]
                for message_id, message_data in stream_messages:
                    try:
                        # Convert message to dictionary
                        message = {}
                        for k, v in message_data.items():
                            if isinstance(k, bytes):
                                k = k.decode('utf-8')
                            if isinstance(v, bytes):
                                v = v.decode('utf-8')
                            message[k] = v
                        
                        # Parse JSON content
                        if 'content' in message:
                            try:
                                message['content'] = json.loads(message['content'])
                            except json.JSONDecodeError:
                                pass
                        
                        # Notify all listeners
                        for handler in self.listeners.get(channel, []):
                            try:
                                handler(message)
                            except Exception as e:
                                logger.error(f"Error in message handler: {e}")
                        
                        # Acknowledge message
                        self.redis.xack(stream_name, group, message_id)
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Redis connection error: {e}")
                time.sleep(5)  # Wait before retry
                
            except Exception as e:
                logger.error(f"Error in listener loop: {e}")
                time.sleep(1)  # Wait before retry
    
    def start(self) -> None:
        """Start the Nova Stream communication system"""
        if self.running:
            logger.warning("Nova Stream already running")
            return
        
        self.running = True
        logger.info("Nova Stream started")
    
    def stop(self) -> None:
        """Stop the Nova Stream communication system"""
        self.running = False
        
        # Wait for listener threads to finish
        for channel, thread in self.listener_threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
                logger.info(f"Stopped listener for {channel}")
        
        logger.info("Nova Stream stopped")


class NovaAgent:
    """Agent interface for Nova Stream communication"""
    
    def __init__(self, agent_id: str, stream: NovaStream, 
                 channels: List[str] = None):
        """Initialize a Nova agent
        
        Args:
            agent_id: Agent identifier
            stream: NovaStream instance
            channels: Channels to subscribe to
        """
        self.agent_id = agent_id
        self.stream = stream
        self.message_handlers: Dict[str, Callable] = {}
        
        # Default channels
        if channels is None:
            channels = ["broadcast", agent_id]
        
        # Subscribe to channels
        for channel in channels:
            self.stream.subscribe(
                channel=channel,
                handler=self._on_message,
                group=f"{agent_id}_group",
                consumer=agent_id
            )
            logger.info(f"Agent {agent_id} subscribed to {channel}")
    
    def _on_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming messages
        
        Args:
            message: Message data
        """
        # Skip messages from self
        if message.get("sender") == self.agent_id:
            return
        
        logger.info(f"Agent {self.agent_id} received: {message}")
        
        # Dispatch to registered handlers
        message_type = message.get("content", {}).get("type") if isinstance(message.get("content"), dict) else "default"
        handler = self.message_handlers.get(message_type, self.message_handlers.get("default"))
        
        if handler:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    def send(self, recipient: str, content: Dict[str, Any]) -> None:
        """Send a message to another agent
        
        Args:
            recipient: Recipient agent ID or channel
            content: Message content
        """
        self.stream.publish(
            channel=recipient,
            message=content,
            sender=self.agent_id
        )
        logger.info(f"Agent {self.agent_id} sent message to {recipient}")
    
    def broadcast(self, content: Dict[str, Any]) -> None:
        """Broadcast a message to all agents
        
        Args:
            content: Message content
        """
        self.send("broadcast", content)
        logger.info(f"Agent {self.agent_id} broadcast message")
    
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler for a specific message type
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
        logger.info(f"Agent {self.agent_id} registered handler for {message_type}")
    
    def set_default_handler(self, handler: Callable) -> None:
        """Set default message handler
        
        Args:
            handler: Handler function
        """
        self.message_handlers["default"] = handler
        logger.info(f"Agent {self.agent_id} set default handler")


def run_server(redis_url: str = "redis://localhost:6379/0", 
               log_level: str = "INFO", health_check_interval: int = 60) -> None:
    """Run the Nova Stream server
    
    Args:
        redis_url: Redis connection URL
        log_level: Logging level
        health_check_interval: Interval for health checks in seconds
    """
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("nova_stream_server")
    
    # Print banner
    print("=" * 60)
    print(f"Nova Stream Server v1.0.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Redis-based communication system for Nova agents")
    print("=" * 60)
    print(f"Redis URL: {redis_url}")
    print(f"Log level: {log_level}")
    print(f"Health check interval: {health_check_interval} seconds")
    print("=" * 60)
    
    # Create stream
    stream = NovaStream(redis_url=redis_url)
    stream.start()
    
    # Create system agent
    system_agent = NovaAgent(agent_id="system", stream=stream)
    
    # Set up signal handling
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        stream.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Health check loop
    start_time = time.time()
    try:
        while True:
            uptime = int(time.time() - start_time)
            status = {
                "type": "status",
                "uptime": uptime,
                "timestamp": datetime.now().isoformat(),
                "status": "running"
            }
            system_agent.broadcast(status)
            logger.debug(f"Health check: {status}")
            time.sleep(health_check_interval)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Shutting down...")
        stream.stop()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Nova Stream - Redis-based communication for Nova agents")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0", help="Redis connection URL")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--health-check-interval", type=int, default=60, help="Health check interval in seconds")
    args = parser.parse_args()
    
    # Run server
    run_server(
        redis_url=args.redis_url,
        log_level=args.log_level,
        health_check_interval=args.health_check_interval
    )rgs:
        redis_url: Redis connection URL
        log_level: Logging level
        health_check_interval: Interval for health checks in seconds
    """
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("nova_stream_server")
    
    # Print banner
    print("=" * 60)
    print(f"Nova Stream Server v1.0.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Redis-based communication system for Nova agents")
    print("=" * 60)
    print(f"Redis URL: {redis_url}")
    print(f"Log level: {log_level}")
    print(f"Health check interval: {health_check_interval} seconds")
    print("=" * 60)
    
    # Create stream
    stream = NovaStream(redis_url=redis_url)
    stream.start()
    
    # Create system agent
    system_agent = NovaAgent(agent_id="system", stream=stream)
    
    # Set up signal handling
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        stream.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Health check loop
    start_time = time.time()
    try:
        while True:
            uptime = int(time.time() - start_time)
            status = {
                "type": "status",
                "uptime": uptime,
                "timestamp": datetime.now().isoformat(),
                "status": "running"
            }
            system_agent.broadcast(status)
            logger.debug(f"Health check: {status}")
            time.sleep(health_check_interval)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Shutting down...")
        stream.stop()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Nova Stream - Redis-based communication for Nova agents")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0", help="Redis connection URL")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--health-check-interval", type=int, default=60, help="Health check interval in seconds")
    args = parser.parse_args()
    
    # Run server
    run_server(
        redis_url=args.redis_url,
        log_level=args.log_level,
        health_check_interval=args.health_check_interval
    )        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Shutting down...")
        stream.stop()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Nova Stream - Redis-based communication for Nova agents")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0", help="Redis connection URL")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--health-check-interval", type=int, default=60, help="Health check interval in seconds")
    args = parser.parse_args()
    
    # Run server
    run_server(
        redis_url=args.redis_url,
        log_level=args.log_level,
        health_check_interval=args.health_check_interval
    )rgs:
        redis_url: Redis connection URL
        log_level: Logging level
        health_check_interval: Interval for health checks in seconds
    """
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("nova_stream_server")
    
    # Print banner
    print("=" * 60)
    print(f"Nova Stream Server v1.0.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Redis-based communication system for Nova agents")
    print("=" * 60)
    print(f"Redis URL: {redis_url}")
    print(f"Log level: {log_level}")
    print(f"Health check interval: {health_check_interval} seconds")
    print("=" * 60)
    
    # Create stream
    stream = NovaStream(redis_url=redis_url)
    stream.start()
    
    # Create system agent
    system_agent = NovaAgent(agent_id="system", stream=stream)
    
    # Set up signal handling
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        stream.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Health check loop
    start_time = time.time()
    try:
        while True:
            uptime = int(time.time() - start_time)
            status = {
                "type": "status",
                "uptime": uptime,
                "timestamp": datetime.now().isoformat(),
                "status": "running"
            }
            system_agent.broadcast(status)
            logger.debug(f"Health check: {status}")
            time.sleep(health_check_interval)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Shutting down...")
        stream.stop()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Nova Stream - Redis-based communication for Nova agents")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0", help="Redis connection URL")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--health-check-interval", type=int, default=60, help="Health check interval in seconds")
    args = parser.parse_args()
    
    # Run server
    run_server(
        redis_url=args.redis_url,
        log_level=args.log_level,
        health_check_interval=args.health_check_interval
    )