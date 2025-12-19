"""
Agent Communication Framework - Core Module
Designed by Vaeris (AI Agent Synergy Expert)
Implemented by Synergy (Integration Specialist)

This module provides the core communication primitives for the agent communication framework.
"""

import json
import uuid
import time
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Union
import redis
import threading
import queue
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Message Types
class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    NOTIFICATION = "notification"
    STREAM_DATA = "stream_data"
    STREAM_END = "stream_end"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    CONTEXT_UPDATE = "context_update"

# Communication Patterns
class CommunicationPattern(Enum):
    REQUEST_RESPONSE = "request_response"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    EVENT_DRIVEN = "event_driven"
    STREAMING = "streaming"
    DIRECT = "direct"

@dataclass
class Message:
    """Base message structure for all communications"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.NOTIFICATION
    sender: str = "unknown"
    recipient: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    pattern: CommunicationPattern = CommunicationPattern.DIRECT
    content: Any = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for serialization"""
        result = asdict(self)
        result["type"] = self.type.value
        result["pattern"] = self.pattern.value
        return result
    
    def to_json(self) -> str:
        """Serialize the message to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a message from a dictionary"""
        # Convert string type/pattern to enum values
        if "type" in data and isinstance(data["type"], str):
            data["type"] = MessageType(data["type"])
        if "pattern" in data and isinstance(data["pattern"], str):
            data["pattern"] = CommunicationPattern(data["pattern"])
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create a message from a JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def create_response(self, content: Any = None, error: Optional[str] = None) -> 'Message':
        """Create a response message for this message"""
        if error:
            return Message(
                type=MessageType.ERROR,
                sender=self.recipient or "system",
                recipient=self.sender,
                pattern=self.pattern,
                content={"error": error, "original_content": self.content},
                correlation_id=self.id,
                metadata={"error": True}
            )
        else:
            return Message(
                type=MessageType.RESPONSE,
                sender=self.recipient or "system",
                recipient=self.sender,
                pattern=self.pattern,
                content=content,
                correlation_id=self.id
            )

class CommunicationChannel:
    """Base class for communication channels"""
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.listeners: List[Callable[[Message], None]] = []
    
    def add_listener(self, listener: Callable[[Message], None]) -> None:
        """Add a message listener to this channel"""
        self.listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[Message], None]) -> None:
        """Remove a message listener from this channel"""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def notify_listeners(self, message: Message) -> None:
        """Notify all listeners about a new message"""
        for listener in self.listeners:
            try:
                listener(message)
            except Exception as e:
                logger.error(f"Error in listener: {e}")
    
    def send(self, message: Message) -> None:
        """Send a message through this channel"""
        raise NotImplementedError("Subclasses must implement send()")

class RedisCommunicationChannel(CommunicationChannel):
    """Redis-based communication channel implementation"""
    def __init__(self, channel_id: str, redis_client: redis.Redis = None, **redis_kwargs):
        super().__init__(channel_id)
        self.redis = redis_client or redis.Redis(**redis_kwargs)
        self.pubsub = self.redis.pubsub()
        
        # Create a thread for message processing
        self.running = True
        self.thread = threading.Thread(target=self._message_loop)
        self.thread.daemon = True
        
        # Subscribe to the channel
        self.pubsub.subscribe(channel_id)
        self.thread.start()
    
    def _message_loop(self) -> None:
        """Background thread for processing Redis messages"""
        while self.running:
            message = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message and message['type'] == 'message':
                try:
                    data = message['data'].decode('utf-8')
                    msg = Message.from_json(data)
                    self.notify_listeners(msg)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
    
    def send(self, message: Message) -> None:
        """Send a message through Redis"""
        self.redis.publish(self.channel_id, message.to_json())
    
    def close(self) -> None:
        """Close the Redis connection and stop the background thread"""
        self.running = False
        self.thread.join(timeout=1.0)
        self.pubsub.unsubscribe()
        self.pubsub.close()

class DirectCommunicationChannel(CommunicationChannel):
    """In-memory direct communication channel implementation"""
    channels: Dict[str, 'DirectCommunicationChannel'] = {}
    
    @classmethod
    def get_channel(cls, channel_id: str) -> 'DirectCommunicationChannel':
        """Get or create a channel by ID"""
        if channel_id not in cls.channels:
            cls.channels[channel_id] = DirectCommunicationChannel(channel_id)
        return cls.channels[channel_id]
    
    def send(self, message: Message) -> None:
        """Send a message directly to listeners"""
        self.notify_listeners(message)
        # If this is a request-response pattern, also notify the recipient's channel
        if (message.pattern == CommunicationPattern.REQUEST_RESPONSE and 
                message.recipient and message.recipient != self.channel_id):
            recipient_channel = self.get_channel(message.recipient)
            recipient_channel.notify_listeners(message)

class Agent:
    """Base class for communicating agents"""
    def __init__(self, agent_id: str, channel: Optional[CommunicationChannel] = None):
        self.agent_id = agent_id
        self.channel = channel or DirectCommunicationChannel.get_channel(agent_id)
        self.channel.add_listener(self._on_message)
        self.request_callbacks: Dict[str, Callable[[Message], None]] = {}
        self.subscriptions: Dict[str, Callable[[Message], None]] = {}
        self.message_queue = queue.Queue()
        logger.info(f"Agent {agent_id} initialized")
    
    def _on_message(self, message: Message) -> None:
        """Handle incoming messages"""
        # If the message is intended for this agent or broadcast
        if message.recipient is None or message.recipient == self.agent_id:
            logger.debug(f"{self.agent_id} received: {message.to_dict()}")
            
            # Check for request callbacks
            if (message.type == MessageType.RESPONSE and 
                    message.correlation_id in self.request_callbacks):
                callback = self.request_callbacks.pop(message.correlation_id)
                callback(message)
            
            # Check for subscriptions
            if message.type == MessageType.EVENT:
                event_type = message.metadata.get('event_type')
                if event_type and event_type in self.subscriptions:
                    self.subscriptions[event_type](message)
            
            # Add to queue for processing
            self.message_queue.put(message)
    
    def send(self, message: Message) -> None:
        """Send a message from this agent"""
        if message.sender == "unknown":
            message.sender = self.agent_id
        logger.debug(f"{self.agent_id} sending: {message.to_dict()}")
        self.channel.send(message)
    
    def send_request(self, recipient: str, content: Any, 
                     callback: Callable[[Message], None], 
                     metadata: Dict[str, Any] = None) -> str:
        """Send a request and register a callback for the response"""
        message = Message(
            type=MessageType.REQUEST,
            sender=self.agent_id,
            recipient=recipient,
            pattern=CommunicationPattern.REQUEST_RESPONSE,
            content=content,
            metadata=metadata or {}
        )
        self.request_callbacks[message.id] = callback
        self.send(message)
        return message.id
    
    def send_response(self, request: Message, content: Any = None, 
                     error: Optional[str] = None) -> None:
        """Send a response to a request"""
        response = request.create_response(content, error)
        self.send(response)
    
    def send_event(self, event_type: str, content: Any, 
                   metadata: Dict[str, Any] = None) -> None:
        """Send an event notification"""
        meta = metadata or {}
        meta['event_type'] = event_type
        message = Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            pattern=CommunicationPattern.EVENT_DRIVEN,
            content=content,
            metadata=meta
        )
        self.send(message)
    
    def subscribe(self, event_type: str, callback: Callable[[Message], None]) -> None:
        """Subscribe to an event type"""
        self.subscriptions[event_type] = callback
        logger.info(f"{self.agent_id} subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str) -> None:
        """Unsubscribe from an event type"""
        if event_type in self.subscriptions:
            del self.subscriptions[event_type]
            logger.info(f"{self.agent_id} unsubscribed from event: {event_type}")
    
    def process_messages(self, blocking: bool = False, 
                         timeout: Optional[float] = None) -> Optional[Message]:
        """Process the next message in the queue"""
        try:
            if blocking:
                message = self.message_queue.get(block=True, timeout=timeout)
                self.message_queue.task_done()
                return message
            else:
                if not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    self.message_queue.task_done()
                    return message
                return None
        except queue.Empty:
            return None
    
    def process_all_messages(self) -> List[Message]:
        """Process all messages in the queue"""
        messages = []
        while not self.message_queue.empty():
            message = self.message_queue.get_nowait()
            self.message_queue.task_done()
            messages.append(message)
        return messages
    
    def close(self) -> None:
        """Clean up resources"""
        if hasattr(self.channel, 'close'):
            self.channel.close()


# Context Management System
@dataclass
class AgentContext:
    """Shared context for agent communication"""
    context_id: str
    version: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    owners: List[str] = field(default_factory=list)
    readers: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the context to a dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Serialize the context to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentContext':
        """Create a context from a dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentContext':
        """Create a context from a JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update(self, updates: Dict[str, Any], agent_id: str) -> bool:
        """Update the context data if the agent has permission"""
        if agent_id not in self.owners:
            logger.warning(f"Agent {agent_id} attempted to update context without permission")
            return False
        
        self.data.update(updates)
        self.version += 1
        self.updated_at = time.time()
        return True
    
    def get(self, key: str, default: Any = None, agent_id: str = None) -> Any:
        """Get a context value if the agent has permission"""
        if agent_id and agent_id not in self.owners and agent_id not in self.readers:
            logger.warning(f"Agent {agent_id} attempted to read context without permission")
            return None
        return self.data.get(key, default)


class ContextManager:
    """Manager for shared contexts between agents"""
    def __init__(self, redis_client: redis.Redis = None, **redis_kwargs):
        self.redis = redis_client or redis.Redis(**redis_kwargs)
        self.contexts: Dict[str, AgentContext] = {}
        
    def create_context(self, context_id: str, owner: str) -> AgentContext:
        """Create a new context with the specified owner"""
        context = AgentContext(context_id=context_id, owners=[owner])
        self.contexts[context_id] = context
        self._save_context(context)
        return context
    
    def get_context(self, context_id: str, agent_id: str) -> Optional[AgentContext]:
        """Get a context by ID if the agent has permission"""
        # Try local cache first
        if context_id in self.contexts:
            context = self.contexts[context_id]
            if agent_id in context.owners or agent_id in context.readers:
                return context
            else:
                logger.warning(f"Agent {agent_id} attempted to access context without permission")
                return None
        
        # Try to load from Redis
        context_json = self.redis.get(f"context:{context_id}")
        if context_json:
            context = AgentContext.from_json(context_json.decode('utf-8'))
            self.contexts[context_id] = context
            if agent_id in context.owners or agent_id in context.readers:
                return context
            else:
                logger.warning(f"Agent {agent_id} attempted to access context without permission")
                return None
        
        return None
    
    def update_context(self, context_id: str, updates: Dict[str, Any], 
                       agent_id: str) -> bool:
        """Update a context if the agent has permission"""
        context = self.get_context(context_id, agent_id)
        if not context:
            return False
        
        if context.update(updates, agent_id):
            self._save_context(context)
            return True
        return False
    
    def add_owner(self, context_id: str, owner: str, agent_id: str) -> bool:
        """Add an owner to a context if the requesting agent has permission"""
        context = self.get_context(context_id, agent_id)
        if not context or agent_id not in context.owners:
            return False
        
        if owner not in context.owners:
            context.owners.append(owner)
            self._save_context(context)
        return True
    
    def add_reader(self, context_id: str, reader: str, agent_id: str) -> bool:
        """Add a reader to a context if the requesting agent has permission"""
        context = self.get_context(context_id, agent_id)
        if not context or agent_id not in context.owners:
            return False
        
        if reader not in context.readers:
            context.readers.append(reader)
            self._save_context(context)
        return True
    
    def _save_context(self, context: AgentContext) -> None:
        """Save a context to Redis"""
        self.redis.set(f"context:{context.context_id}", context.to_json())