"""
Agent Communication Framework - Example Usage
Designed by Vaeris (AI Agent Synergy Expert)
Implemented by Synergy (Integration Specialist)

This module demonstrates how to use the Agent Communication Framework.
"""

import time
import threading
import logging
from typing import Dict, Any, List, Optional
from core import (
    Agent, Message, MessageType, CommunicationPattern,
    DirectCommunicationChannel, RedisCommunicationChannel,
    ContextManager
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleAgent(Agent):
    """A simple agent implementation for demonstration"""
    def __init__(self, agent_id: str, context_manager: Optional[ContextManager] = None):
        super().__init__(agent_id)
        self.context_manager = context_manager
        self.handlers = {
            MessageType.REQUEST: self._handle_request,
            MessageType.COMMAND: self._handle_command,
            MessageType.EVENT: self._handle_event,
            MessageType.NOTIFICATION: self._handle_notification,
        }
        self.running = False
        self.worker_thread = None
    
    def _handle_request(self, message: Message) -> None:
        """Handle incoming request messages"""
        logger.info(f"{self.agent_id} handling request: {message.content}")
        # Echo back the request content as a response
        response_content = f"Echo: {message.content}"
        self.send_response(message, response_content)
    
    def _handle_command(self, message: Message) -> None:
        """Handle incoming command messages"""
        command = message.content.get('command') if isinstance(message.content, dict) else str(message.content)
        logger.info(f"{self.agent_id} received command: {command}")
        
        if command == "stop":
            logger.info(f"{self.agent_id} stopping due to command")
            self.running = False
        elif command == "status":
            self.send_response(message, {"status": "running" if self.running else "stopped"})
        else:
            self.send_response(message, {"status": "unknown command"})
    
    def _handle_event(self, message: Message) -> None:
        """Handle incoming event messages"""
        event_type = message.metadata.get('event_type', 'unknown')
        logger.info(f"{self.agent_id} received event of type {event_type}: {message.content}")
    
    def _handle_notification(self, message: Message) -> None:
        """Handle incoming notification messages"""
        logger.info(f"{self.agent_id} received notification: {message.content}")
    
    def start(self) -> None:
        """Start processing messages in a background thread"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        logger.info(f"{self.agent_id} started processing messages")
    
    def _process_loop(self) -> None:
        """Background thread that processes incoming messages"""
        while self.running:
            message = self.process_messages(blocking=True, timeout=0.1)
            if message:
                handler = self.handlers.get(message.type)
                if handler:
                    try:
                        handler(message)
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
    
    def stop(self) -> None:
        """Stop processing messages"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        logger.info(f"{self.agent_id} stopped processing messages")


def run_direct_communication_example():
    """Example of direct in-memory communication between agents"""
    print("\n=== Direct Communication Example ===\n")
    
    # Create agents
    agent1 = SimpleAgent("agent1")
    agent2 = SimpleAgent("agent2")
    
    # Start agent message processing
    agent1.start()
    agent2.start()
    
    # Example 1: Request-Response
    print("Example 1: Request-Response Pattern")
    
    # Define a callback for the response
    def on_response(response: Message):
        print(f"Received response from {response.sender}: {response.content}")
    
    # Send a request from agent1 to agent2
    agent1.send_request("agent2", "Hello from Agent 1", on_response)
    
    # Wait for processing
    time.sleep(1)
    
    # Example 2: Event-Driven
    print("\nExample 2: Event-Driven Pattern")
    
    # Subscribe to events
    agent1.subscribe("test_event", lambda msg: print(f"Agent1 received event: {msg.content}"))
    agent2.subscribe("test_event", lambda msg: print(f"Agent2 received event: {msg.content}"))
    
    # Send events
    agent1.send_event("test_event", "Something happened in Agent 1")
    time.sleep(0.5)
    agent2.send_event("test_event", "Something happened in Agent 2")
    
    # Wait for processing
    time.sleep(1)
    
    # Example 3: Command Pattern
    print("\nExample 3: Command Pattern")
    
    # Send a command
    command_msg = Message(
        type=MessageType.COMMAND,
        sender="system",
        recipient="agent2",
        pattern=CommunicationPattern.REQUEST_RESPONSE,
        content={"command": "status"}
    )
    agent1.send(command_msg)
    
    # Wait for processing
    time.sleep(1)
    
    # Clean up
    agent1.stop()
    agent2.stop()
    print("\nDirect communication example completed")


def run_redis_communication_example():
    """Example of Redis-based communication between agents"""
    try:
        print("\n=== Redis Communication Example ===\n")
        print("Connecting to Redis...")
        
        # Create Redis-based channels
        channel1 = RedisCommunicationChannel("channel1")
        channel2 = RedisCommunicationChannel("channel2")
        
        # Create agents with Redis channels
        agent1 = SimpleAgent("redis_agent1")
        agent1.channel = channel1
        channel1.add_listener(agent1._on_message)
        
        agent2 = SimpleAgent("redis_agent2")
        agent2.channel = channel2
        channel2.add_listener(agent2._on_message)
        
        # Start agent message processing
        agent1.start()
        agent2.start()
        
        print("Agents started with Redis channels")
        
        # Example: Send messages through Redis
        print("\nSending messages through Redis...")
        
        agent1.send_request("redis_agent2", "Hello via Redis!", 
                          lambda msg: print(f"Redis response received: {msg.content}"))
        
        # Wait for processing
        time.sleep(2)
        
        # Clean up
        agent1.stop()
        agent2.stop()
        channel1.close()
        channel2.close()
        print("\nRedis communication example completed")
        
    except Exception as e:
        print(f"Redis example failed: {e}")
        print("Make sure Redis server is running on localhost:6379")


def run_context_management_example():
    """Example of context management between agents"""
    print("\n=== Context Management Example ===\n")
    
    try:
        # Create a context manager (will use local Redis)
        context_manager = ContextManager()
        
        # Create agents with context manager
        agent1 = SimpleAgent("context_agent1", context_manager)
        agent2 = SimpleAgent("context_agent2", context_manager)
        
        # Start agent message processing
        agent1.start()
        agent2.start()
        
        # Create a shared context
        context = context_manager.create_context("shared_context", "context_agent1")
        print(f"Created shared context: {context.context_id}")
        
        # Add agent2 as a reader
        context_manager.add_reader("shared_context", "context_agent2", "context_agent1")
        print("Added agent2 as a reader")
        
        # Update the context
        context_manager.update_context("shared_context", {
            "task": "example task",
            "priority": "high",
            "status": "pending"
        }, "context_agent1")
        print("Updated context with initial data")
        
        # Agent2 reads the context
        context2 = context_manager.get_context("shared_context", "context_agent2")
        print(f"Agent2 reads context: {context2.data}")
        
        # Agent2 tries to update (should fail as it's only a reader)
        result = context_manager.update_context("shared_context", {
            "status": "in_progress"
        }, "context_agent2")
        print(f"Agent2 update attempt result: {result}")
        
        # Add agent2 as an owner
        context_manager.add_owner("shared_context", "context_agent2", "context_agent1")
        print("Added agent2 as an owner")
        
        # Now agent2 can update
        result = context_manager.update_context("shared_context", {
            "status": "in_progress",
            "assigned_to": "context_agent2"
        }, "context_agent2")
        print(f"Agent2 update attempt result: {result}")
        
        # Check final context state
        context = context_manager.get_context("shared_context", "context_agent1")
        print(f"Final context state: {context.data}")
        print(f"Context version: {context.version}")
        
        # Clean up
        agent1.stop()
        agent2.stop()
        print("\nContext management example completed")
        
    except Exception as e:
        print(f"Context management example failed: {e}")
        print("Make sure Redis server is running")


if __name__ == "__main__":
    print("Agent Communication Framework Examples")
    print("======================================")
    
    run_direct_communication_example()
    
    try:
        # Only run Redis examples if Redis is available
        import redis
        redis_client = redis.Redis()
        redis_client.ping()
        
        run_redis_communication_example()
        run_context_management_example()
        
    except (ImportError, redis.exceptions.ConnectionError):
        print("\nSkipping Redis-based examples: Redis not available")
        print("Install Redis and start the server to run these examples")
        
    print("\nAll examples completed")