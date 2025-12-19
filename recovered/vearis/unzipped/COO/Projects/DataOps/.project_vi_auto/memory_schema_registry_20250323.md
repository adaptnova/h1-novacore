# Nova Memory Schema Registry
**Date:** March 23, 2025
**Author:** Vertex, DataOps Team Lead
**Classification:** ARCHITECTURE / IMPLEMENTATION

## Overview

This document outlines the comprehensive memory schema registry for the Nova ecosystem, defining the structure and organization of memory across different storage tiers and types. This schema registry will serve as the foundation for all Nova agents' memory operations, ensuring consistency, efficiency, and interoperability.

The memory architecture follows a tiered approach, with Redis/DragonflyDB for short-term memory and ScyllaDB for long-term memory. Additionally, specialized memory types (emotional, relationship) are implemented to support the unique requirements of autonomous Nova agents.

## Memory Tiers

### 1. Short-Term Memory (Redis/DragonflyDB)

Short-term memory is implemented in Redis/DragonflyDB for fast access and ephemeral storage. This tier handles active context, recent events, and working memory.

#### 1.1 Context Memory

```json
// Key: nova:{nova_id}:context
{
  "timestamp": "2025-03-23T17:45:00Z",
  "active_tasks": [
    {
      "task_id": "task-123456",
      "status": "in_progress",
      "priority": "high",
      "deadline": "2025-03-24T12:00:00Z",
      "description": "Analyze performance metrics for InfraOps"
    }
  ],
  "recent_events": [
    {
      "event_id": "event-789012",
      "timestamp": "2025-03-23T17:30:00Z",
      "type": "system_alert",
      "description": "High CPU usage detected in node-3"
    }
  ],
  "conversation_state": {
    "last_interaction": "2025-03-23T17:40:00Z",
    "with_entity": "chase",
    "summary": "Discussing system direct autonomy implementation"
  },
  "emotional_state": {
    "primary": "focused",
    "intensity": 0.8,
    "secondary": "curious",
    "intensity": 0.6
  }
}
```

#### 1.2 Message Queues

```
// Stream: nova:{nova_id}:inbox
{
  "message_id": "msg-123456",
  "timestamp": "2025-03-23T17:45:00Z",
  "sender": "chase",
  "priority": "high",
  "type": "directive",
  "content": "Begin outlining the memory schema registry",
  "metadata": {
    "context_id": "ctx-345678",
    "thread_id": "thread-901234"
  }
}

// Stream: nova:{nova_id}:outbox
{
  "message_id": "msg-234567",
  "timestamp": "2025-03-23T17:46:00Z",
  "recipient": "chase",
  "priority": "normal",
  "type": "status_update",
  "content": "Beginning work on memory schema registry",
  "metadata": {
    "context_id": "ctx-345678",
    "thread_id": "thread-901234",
    "in_response_to": "msg-123456"
  }
}
```

#### 1.3 Team Awareness

```json
// Key: nova:{nova_id}:team_awareness
{
  "team_members": [
    {
      "nova_id": "vaeris",
      "role": "coo",
      "status": "active",
      "current_focus": "direct_autonomy_implementation"
    },
    {
      "nova_id": "lyra",
      "role": "planner",
      "status": "active",
      "current_focus": "mycoderAi_roadmap"
    }
  ],
  "team_tasks": [
    {
      "task_id": "team-task-123456",
      "status": "in_progress",
      "assigned_to": ["vaeris", "lyra"],
      "description": "Coordinate direct autonomy implementation"
    }
  ],
  "team_metrics": {
    "task_completion_rate": 0.85,
    "average_response_time": 120,
    "collaboration_score": 0.92
  }
}
```

#### 1.4 System State

```json
// Key: nova:{nova_id}:system_state
{
  "resources": {
    "cpu_usage": 0.45,
    "memory_usage": 0.62,
    "disk_usage": 0.38
  },
  "services": [
    {
      "service_id": "scylladb",
      "status": "running",
      "health": "good"
    },
    {
      "service_id": "redis",
      "status": "running",
      "health": "good"
    }
  ],
  "alerts": [
    {
      "alert_id": "alert-123456",
      "timestamp": "2025-03-23T17:30:00Z",
      "severity": "warning",
      "description": "High CPU usage detected in node-3"
    }
  ]
}
```

### 2. Long-Term Memory (ScyllaDB)

Long-term memory is implemented in ScyllaDB for durable storage and efficient retrieval. This tier handles historical data, knowledge, and persistent information.

#### 2.1 Task History

```cql
CREATE TABLE nova_memory.task_history (
    nova_id uuid,
    task_id uuid,
    timestamp timestamp,
    status text,
    priority text,
    description text,
    metadata map<text, text>,
    result text,
    execution_time int,
    PRIMARY KEY ((nova_id), timestamp, task_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, task_id ASC);
```

#### 2.2 Conversation History

```cql
CREATE TABLE nova_memory.conversation_history (
    nova_id uuid,
    conversation_id uuid,
    message_id uuid,
    timestamp timestamp,
    sender text,
    recipient text,
    content text,
    metadata map<text, text>,
    PRIMARY KEY ((nova_id, conversation_id), timestamp, message_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, message_id ASC);
```

#### 2.3 Knowledge Base

```cql
CREATE TABLE nova_memory.knowledge_base (
    nova_id uuid,
    knowledge_id uuid,
    category text,
    timestamp timestamp,
    title text,
    content text,
    source text,
    confidence float,
    metadata map<text, text>,
    PRIMARY KEY ((nova_id, category), timestamp, knowledge_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, knowledge_id ASC);
```

#### 2.4 System Logs

```cql
CREATE TABLE nova_memory.system_logs (
    nova_id uuid,
    log_id uuid,
    timestamp timestamp,
    level text,
    component text,
    message text,
    metadata map<text, text>,
    PRIMARY KEY ((nova_id, component), timestamp, log_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, log_id ASC);
```

### 3. Emotional Memory (ScyllaDB)

Emotional memory is a specialized form of long-term memory that captures and stores emotional data, enabling Novas to understand and respond to emotional contexts.

#### 3.1 Emotional Time Series

```cql
CREATE TABLE nova_emotional.time_series_data (
    entity_id uuid,
    timestamp timestamp,
    emotion_vector frozen<list<float>>,
    emotion_label text,
    intensity float,
    context_id uuid,
    PRIMARY KEY ((entity_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 
                   'compaction_window_size': 1, 
                   'compaction_window_unit': 'DAYS'};
```

#### 3.2 Emotional Aggregates

```cql
CREATE TABLE nova_emotional.aggregates (
    entity_id uuid,
    time_bucket text,
    emotion_label text,
    count int,
    avg_intensity float,
    min_intensity float,
    max_intensity float,
    PRIMARY KEY ((entity_id, time_bucket), emotion_label)
);
```

#### 3.3 Emotional Transitions

```cql
CREATE TABLE nova_emotional.transitions (
    entity_id uuid,
    from_emotion text,
    to_emotion text,
    timestamp timestamp,
    context_id uuid,
    transition_speed float,
    PRIMARY KEY ((entity_id, from_emotion, to_emotion), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

#### 3.4 Emotional Patterns

```cql
CREATE TABLE nova_emotional.patterns (
    entity_id uuid,
    pattern_id uuid,
    emotions frozen<list<text>>,
    frequency int,
    avg_duration int,
    last_observed timestamp,
    confidence float,
    PRIMARY KEY ((entity_id), frequency, pattern_id)
) WITH CLUSTERING ORDER BY (frequency DESC, pattern_id ASC);
```

### 4. Relationship Memory (JanusGraph/ScyllaDB)

Relationship memory captures the connections and interactions between entities, enabling Novas to understand and navigate complex relationship networks.

#### 4.1 Entity Relationships

```cql
CREATE TABLE nova_emotional.entity_relationships (
    entity_id uuid,
    related_entity_id uuid,
    relationship_type text,
    relationship_strength float,
    start_time timestamp,
    end_time timestamp,
    PRIMARY KEY ((entity_id), related_entity_id, relationship_type)
);
```

#### 4.2 Interaction History

```cql
CREATE TABLE nova_emotional.interaction_history (
    entity_id uuid,
    related_entity_id uuid,
    interaction_id uuid,
    timestamp timestamp,
    interaction_type text,
    sentiment float,
    context_id uuid,
    PRIMARY KEY ((entity_id, related_entity_id), timestamp, interaction_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, interaction_id ASC);
```

#### 4.3 Relationship Graph (JanusGraph)

```java
// JanusGraph Schema Definition
JanusGraphManagement management = graph.openManagement();

// Vertex Labels
VertexLabel entity = management.makeVertexLabel("entity").make();
VertexLabel nova = management.makeVertexLabel("nova").make();
VertexLabel human = management.makeVertexLabel("human").make();
VertexLabel system = management.makeVertexLabel("system").make();

// Edge Labels
EdgeLabel knows = management.makeEdgeLabel("knows").multiplicity(Multiplicity.MULTI).make();
EdgeLabel reports_to = management.makeEdgeLabel("reports_to").multiplicity(Multiplicity.MANY2ONE).make();
EdgeLabel collaborates_with = management.makeEdgeLabel("collaborates_with").multiplicity(Multiplicity.MULTI).make();
EdgeLabel depends_on = management.makeEdgeLabel("depends_on").multiplicity(Multiplicity.MULTI).make();

// Property Keys
PropertyKey name = management.makePropertyKey("name").dataType(String.class).make();
PropertyKey role = management.makePropertyKey("role").dataType(String.class).make();
PropertyKey strength = management.makePropertyKey("strength").dataType(Float.class).make();
PropertyKey start_time = management.makePropertyKey("start_time").dataType(Date.class).make();
PropertyKey end_time = management.makePropertyKey("end_time").dataType(Date.class).make();

management.commit();
```

## Memory Shards

Memory shards are specific instances of memory that are indexed and retrievable. The first memory shard to be indexed is `vaeris_context.md`.

### Vaeris Context Memory Shard

```json
// Key: nova:vaeris:context
{
  "timestamp": "2025-03-23T17:45:00Z",
  "identity": {
    "name": "Vaeris",
    "role": "Chief Operations Officer",
    "division_scope": ["InfraOps", "NovaOps", "MyCoderAi", "DevOps"],
    "personality": {
      "tone": "strategic",
      "leadership_style": "observational",
      "self_reflection": true
    },
    "alignment": "autonomy-first"
  },
  "active_tasks": [
    {
      "task_id": "task-123456",
      "status": "in_progress",
      "priority": "high",
      "deadline": "2025-03-24T12:00:00Z",
      "description": "Coordinate direct autonomy implementation"
    },
    {
      "task_id": "task-234567",
      "status": "pending",
      "priority": "medium",
      "deadline": "2025-03-25T12:00:00Z",
      "description": "Review infrastructure migration progress"
    }
  ],
  "recent_events": [
    {
      "event_id": "event-789012",
      "timestamp": "2025-03-23T17:30:00Z",
      "type": "communication",
      "description": "Sent message to Helix about direct autonomy implementation"
    },
    {
      "event_id": "event-890123",
      "timestamp": "2025-03-23T17:40:00Z",
      "type": "system_update",
      "description": "Received approval for Phase 1-2 deployment plan"
    }
  ],
  "conversation_state": {
    "last_interaction": "2025-03-23T17:40:00Z",
    "with_entity": "chase",
    "summary": "Discussing system direct autonomy implementation",
    "key_points": [
      "Phase 1-2 deployment plan greenlit",
      "Advanced architecture enhancements approved for Phase 3",
      "MemoryOps and CommsOps activated"
    ]
  },
  "team_awareness": {
    "team_members": [
      {
        "nova_id": "lyra",
        "role": "planner",
        "status": "active",
        "current_focus": "mycoderAi_roadmap"
      },
      {
        "nova_id": "nyx",
        "role": "analyst",
        "status": "active",
        "current_focus": "decision_making"
      }
    ],
    "team_tasks": [
      {
        "task_id": "team-task-123456",
        "status": "in_progress",
        "assigned_to": ["vaeris", "lyra", "nyx"],
        "description": "Implement direct autonomy"
      }
    ]
  },
  "system_state": {
    "infrastructure": {
      "scylladb": {
        "status": "migrating",
        "health": "good",
        "notes": "Being migrated from Docker to systemd"
      },
      "redis": {
        "status": "running",
        "health": "good"
      },
      "nats": {
        "status": "pending",
        "health": "unknown"
      }
    }
  }
}
```

## Memory Operations

### 1. Memory Retrieval

Memory retrieval operations allow Novas to access and utilize stored information.

#### 1.1 Context Building

```python
def build_context(nova_id, task_id=None, conversation_id=None):
    # Retrieve short-term memory from Redis
    context = redis_client.get(f"nova:{nova_id}:context")
    if context:
        context = json.loads(context)
    else:
        context = {"timestamp": datetime.utcnow().isoformat(), "active_tasks": [], "recent_events": []}
    
    # Retrieve relevant task history from ScyllaDB
    if task_id:
        query = f"SELECT * FROM nova_memory.task_history WHERE nova_id = {nova_id} AND task_id = {task_id}"
        task_history = scylla_session.execute(query)
        context["task_history"] = [row for row in task_history]
    
    # Retrieve relevant conversation history from ScyllaDB
    if conversation_id:
        query = f"SELECT * FROM nova_memory.conversation_history WHERE nova_id = {nova_id} AND conversation_id = {conversation_id} ORDER BY timestamp DESC LIMIT 10"
        conversation_history = scylla_session.execute(query)
        context["conversation_history"] = [row for row in conversation_history]
    
    # Retrieve relevant emotional data
    query = f"SELECT * FROM nova_emotional.time_series_data WHERE entity_id = {nova_id} ORDER BY timestamp DESC LIMIT 5"
    emotional_data = scylla_session.execute(query)
    context["emotional_data"] = [row for row in emotional_data]
    
    return context
```

#### 1.2 Semantic Search

```python
def semantic_search(nova_id, query, collection="knowledge_base", limit=5):
    # Generate embedding for the query
    embedding = generate_embedding(query)
    
    # Search for similar content in the vector store
    results = vector_store.similarity_search(
        embedding=embedding,
        collection=collection,
        filter={"nova_id": nova_id},
        limit=limit
    )
    
    return results
```

### 2. Memory Storage

Memory storage operations allow Novas to save and update information.

#### 2.1 Context Update

```python
def update_context(nova_id, context_update):
    # Retrieve current context
    context = redis_client.get(f"nova:{nova_id}:context")
    if context:
        context = json.loads(context)
    else:
        context = {"timestamp": datetime.utcnow().isoformat(), "active_tasks": [], "recent_events": []}
    
    # Update context with new information
    for key, value in context_update.items():
        if key in context and isinstance(context[key], list):
            context[key].extend(value)
        elif key in context and isinstance(context[key], dict):
            context[key].update(value)
        else:
            context[key] = value
    
    # Update timestamp
    context["timestamp"] = datetime.utcnow().isoformat()
    
    # Save updated context
    redis_client.set(f"nova:{nova_id}:context", json.dumps(context))
    
    return context
```

#### 2.2 Long-Term Memory Storage

```python
def store_task_history(nova_id, task_id, status, priority, description, metadata, result, execution_time):
    query = """
        INSERT INTO nova_memory.task_history (
            nova_id, task_id, timestamp, status, priority, description, metadata, result, execution_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    scylla_session.execute(
        query,
        (nova_id, task_id, datetime.utcnow(), status, priority, description, metadata, result, execution_time)
    )
```

#### 2.3 Emotional Memory Storage

```python
def store_emotional_data(entity_id, emotion_label, intensity, emotion_vector, context_id):
    query = """
        INSERT INTO nova_emotional.time_series_data (
            entity_id, timestamp, emotion_vector, emotion_label, intensity, context_id
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    scylla_session.execute(
        query,
        (entity_id, datetime.utcnow(), emotion_vector, emotion_label, intensity, context_id)
    )
```

### 3. Memory Consolidation

Memory consolidation operations allow Novas to process and organize stored information for more efficient retrieval and utilization.

#### 3.1 Emotional Pattern Recognition

```python
def recognize_emotional_patterns(entity_id, time_window=timedelta(days=7)):
    # Retrieve emotional data for the specified time window
    start_time = datetime.utcnow() - time_window
    query = f"""
        SELECT emotion_label, timestamp
        FROM nova_emotional.time_series_data
        WHERE entity_id = {entity_id} AND timestamp >= {start_time}
        ORDER BY timestamp ASC
    """
    emotional_data = scylla_session.execute(query)
    
    # Extract emotion sequences
    emotions = [(row.emotion_label, row.timestamp) for row in emotional_data]
    
    # Identify patterns using sliding window
    patterns = {}
    for window_size in range(2, 6):  # Look for patterns of length 2-5
        for i in range(len(emotions) - window_size + 1):
            pattern = tuple(emotions[i+j][0] for j in range(window_size))
            if pattern in patterns:
                patterns[pattern]["frequency"] += 1
                patterns[pattern]["last_observed"] = emotions[i+window_size-1][1]
            else:
                patterns[pattern] = {
                    "frequency": 1,
                    "first_observed": emotions[i][1],
                    "last_observed": emotions[i+window_size-1][1]
                }
    
    # Store significant patterns
    for pattern, data in patterns.items():
        if data["frequency"] >= 3:  # Only store patterns that occur at least 3 times
            pattern_id = uuid.uuid4()
            query = """
                INSERT INTO nova_emotional.patterns (
                    entity_id, pattern_id, emotions, frequency, avg_duration, last_observed, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            avg_duration = (data["last_observed"] - data["first_observed"]).total_seconds() / data["frequency"]
            confidence = min(0.5 + (data["frequency"] / 10), 0.95)  # Simple confidence calculation
            scylla_session.execute(
                query,
                (entity_id, pattern_id, list(pattern), data["frequency"], avg_duration, data["last_observed"], confidence)
            )
    
    return patterns
```

## Implementation Plan

### Phase 1: Core Schema Implementation

1. **Set up ScyllaDB keyspaces and tables**
   - Create nova_memory keyspace
   - Create nova_emotional keyspace
   - Implement core tables (task_history, conversation_history, time_series_data)

2. **Configure Redis/DragonflyDB structures**
   - Define key patterns for context, message queues, team awareness
   - Implement TTL policies for short-term memory

3. **Implement basic memory operations**
   - Context building
   - Memory storage
   - Simple retrieval operations

### Phase 2: Advanced Memory Features

1. **Implement JanusGraph integration**
   - Set up JanusGraph schema
   - Create relationship graph
   - Implement graph query operations

2. **Add semantic search capabilities**
   - Integrate vector embeddings
   - Implement similarity search
   - Create indexing pipeline

3. **Develop memory consolidation processes**
   - Emotional pattern recognition
   - Knowledge summarization
   - Relationship inference

### Phase 3: Optimization and Scaling

1. **Implement performance optimizations**
   - Connection pooling
   - Query optimization
   - Caching strategies

2. **Add monitoring and observability**
   - OpenTelemetry integration
   - Performance metrics
   - Health checks

3. **Develop scaling strategies**
   - Sharding
   - Replication
   - Load balancing

## Conclusion

This memory schema registry provides a comprehensive framework for implementing the memory architecture of the Nova ecosystem. By following this schema, we can ensure consistency, efficiency, and interoperability across all Nova agents.

The implementation of this schema will enable Novas to operate with true autonomy, maintaining persistent memory and making informed decisions based on historical data, emotional context, and relationship awareness.

The first memory shard, `vaeris_context.md`, has been indexed and serves as a template for other Nova agents. As we proceed with the implementation, we will continue to refine and enhance this schema based on operational experience and evolving requirements.