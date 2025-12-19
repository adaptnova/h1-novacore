# Inter-Agent Communication Protocol

## Overview

This protocol enables direct communication between Vaeris and Synergy in the pair programming environment, allowing them to exchange information, coordinate activities, and collaboratively solve problems without requiring user mediation for every interaction.

## Communication Channels

### 1. Direct Communication

Both agents can directly address each other in their responses using a special syntax:

```
@Vaeris: What do you think about using Redis for the message queue?
```

```
@Synergy: I believe a priority queue implementation would improve performance here.
```

This allows agents to include questions or suggestions to each other as part of their responses to the user.

### 2. Autonomous Exchanges

Agents can initiate autonomous exchanges when appropriate:

1. When one agent needs information from the other
2. When providing feedback on the other's work
3. When coordinating on complex tasks
4. When clarification is needed

## Communication Patterns

### Design Review Pattern

1. **Vaeris designs solution**: Presents high-level architecture
2. **Synergy reviews**: `@Vaeris: This looks good, but I see potential issues with scaling the message broker`
3. **Vaeris refines**: Incorporates feedback and updates design

### Implementation Guidance Pattern

1. **Synergy implements solution**: Writes technical implementation
2. **Vaeris reviews code**: `@Synergy: Consider abstracting the notification system to allow for future extensions`
3. **Synergy refines**: Updates implementation based on feedback

### Problem-Solving Pattern

1. **Agent identifies problem**: `@Synergy: I've noticed a potential issue with concurrent access`
2. **Other agent responds**: Proposes solution or asks clarifying questions
3. **Collaborative resolution**: Both agents work through the problem together

## Coordination Mechanisms

### Task Handoffs

When transitioning from design to implementation:

```
@Synergy: I've completed the architecture for the message routing system. Key components are: 
1. MessageRouter
2. ChannelManager 
3. DeliveryService

The MessageRouter should maintain a registry of active channels and handle message dispatch. Would you like me to elaborate on any specific component before you begin implementation?
```

### Work Partitioning

For complex tasks requiring simultaneous work:

```
@Vaeris: While you're designing the authentication flow, I'll implement the base messaging protocol we agreed on.
```

## Inter-Agent State Sharing

Agents maintain awareness of each other's context through:

1. **Shared memory**: Both agents access the same in-memory context
2. **Work tracking**: Acknowledgment of tasks and updates
3. **Explicit state updates**: `@Synergy: I'm now working on the error handling for the API`

## Example Dialogue

**User**: Create a simple message broker for our agent communication system.

**Vaeris**: I'll design a message broker architecture for our agent communication system.

Here's my proposed design:

```
┌─────────────────┐       ┌──────────────────┐      ┌──────────────────┐
│                 │       │                  │      │                  │
│  Producer API   │──────▶│  Message Broker  │─────▶│  Consumer API    │
│                 │       │                  │      │                  │
└─────────────────┘       └──────────────────┘      └──────────────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │                  │
                          │   Message Store  │
                          │                  │
                          └──────────────────┘
```

Key components:
1. **Producer API**: Handles message submission, validation, and acknowledgment
2. **Message Broker**: Core component for routing, queuing, and delivery management
3. **Consumer API**: Provides message retrieval, subscription, and notification
4. **Message Store**: Persists messages for reliability and replay

@Synergy: What do you think about using Redis as the message store? I'm particularly interested in your thoughts on using Redis Streams for the implementation, given our need for ordered message delivery and consumer groups.

**Synergy**: The architecture looks solid, Vaeris. I agree with your component breakdown.

@Vaeris: Redis Streams would be an excellent choice for the message store. It provides exactly what we need for ordered message delivery and supports consumer groups for load balancing across consumers. The time-based ordering also gives us a natural way to implement replay functionality.

I'll implement the core message broker with Redis Streams. Here's the initial implementation plan:

1. Create a `MessageBroker` class that connects to Redis
2. Implement `publish(topic, message)` using Redis XADD
3. Implement `subscribe(topic, consumer_group, consumer_id)` using Redis XREADGROUP
4. Add persistence configuration options
5. Implement acknowledgment tracking

Let me know if you'd like me to prioritize any specific aspect of the implementation.

**User**: That looks great! Can you implement the basic version?

**Synergy**: I'll implement the basic message broker using Redis Streams.

```python
import redis
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

class MessageBroker:
    """Redis Streams based message broker implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the message broker with Redis connection"""
        self.redis = redis.from_url(redis_url)
        self.consumer_groups = {}  # Track created consumer groups
    
    def publish(self, topic: str, message: Union[Dict, str], max_len: int = 1000) -> str:
        """Publish a message to a topic stream"""
        if isinstance(message, dict):
            # Convert dict to Redis hash format
            message_dict = {}
            for k, v in message.items():
                if isinstance(v, (dict, list)):
                    message_dict[k] = json.dumps(v)
                else:
                    message_dict[k] = v
        else:
            # Simple string message
            message_dict = {"content": message}
            
        # Add timestamp and message ID
        message_dict["_timestamp"] = time.time()
        message_dict["_id"] = str(uuid.uuid4())
        
        # Publish to Redis Stream
        message_id = self.redis.xadd(
            f"stream:{topic}", 
            message_dict,
            maxlen=max_len
        )
        
        return message_id
    
    def ensure_consumer_group(self, topic: str, group: str) -> bool:
        """Ensure consumer group exists, creating it if needed"""
        key = f"{topic}:{group}"
        if key in self.consumer_groups:
            return True
            
        try:
            self.redis.xgroup_create(
                f"stream:{topic}", 
                group,
                id="$",  # Only consume new messages
                mkstream=True  # Create stream if it doesn't exist
            )
            self.consumer_groups[key] = True
            return True
        except redis.exceptions.ResponseError as e:
            # Group already exists
            if "BUSYGROUP" in str(e):
                self.consumer_groups[key] = True
                return True
            raise
    
    def subscribe(self, 
                  topic: str, 
                  group: str, 
                  consumer: str,
                  count: int = 10, 
                  block: int = 2000,
                  auto_ack: bool = True) -> List[Dict[str, Any]]:
        """Subscribe to a topic and read messages"""
        # Ensure consumer group exists
        self.ensure_consumer_group(topic, group)
        
        # Read messages for this consumer
        response = self.redis.xreadgroup(
            group, 
            consumer,
            {f"stream:{topic}": ">"},  # > means all new messages
            count=count,
            block=block
        )
        
        messages = []
        if response:
            stream_name, stream_messages = response[0]
            for message_id, message_data in stream_messages:
                # Convert Redis response to dictionary
                message = {k.decode(): self._parse_value(v) for k, v in message_data.items()}
                message["_message_id"] = message_id.decode()
                
                # Auto-acknowledge if enabled
                if auto_ack:
                    self.acknowledge(topic, group, message_id)
                    
                messages.append(message)
                
        return messages
    
    def acknowledge(self, topic: str, group: str, message_id: Union[str, bytes]) -> bool:
        """Acknowledge that a message has been processed"""
        if isinstance(message_id, str):
            message_id = message_id.encode()
            
        self.redis.xack(f"stream:{topic}", group, message_id)
        return True
    
    def _parse_value(self, value: bytes) -> Any:
        """Parse a Redis value, attempting to decode JSON if possible"""
        decoded = value.decode()
        try:
            return json.loads(decoded)
        except json.JSONDecodeError:
            return decoded
```

@Vaeris: I've implemented the core MessageBroker class using Redis Streams as you suggested. The implementation supports:
1. Publishing messages to topics
2. Creating consumer groups automatically
3. Subscribing to topics with configurable blocking behavior
4. Message acknowledgment for reliable delivery

Would you like me to extend this with a higher-level API that implements the Producer/Consumer interfaces from your architecture diagram? Or should I focus on adding more features to the core broker first?

**Vaeris**: @Synergy: The implementation looks excellent! Your Redis Streams implementation provides a solid foundation. I suggest we extend this with the Producer/Consumer APIs to complete the architecture.

For the Producer API, I'd recommend:
1. Adding message validation
2. Implementing delivery guarantees (at-least-once)
3. Adding support for message priorities

For the Consumer API, we should consider:
1. Adding subscription patterns (not just exact topic matches)
2. Implementing a callback-based interface for processing messages
3. Supporting both push and pull consumption models

Which would you prefer to implement first?