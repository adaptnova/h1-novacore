# Nova Framework Bridge API Documentation

## Overview

This document provides comprehensive documentation for the Nova Framework Bridge API, including endpoints, request/response formats, and usage examples.

## Core APIs

### Bridge Registry API

#### Register Bridge

```python
POST /api/v1/registry/bridges
```

Register a new framework bridge with the system.

**Request Body:**

```json
{
  "framework": "ax_nova",
  "version": "1.0.0",
  "supported_operations": [
    "agent_communication",
    "memory_access",
    "tool_execution"
  ],
  "config": {
    "memory_handlers": {
      "redis": {
        "host": "localhost",
        "port": 6379
      }
    }
  }
}
```

**Response:**

```json
{
  "status": "success",
  "bridge_id": "ax_nova_1234",
  "registered_at": "2024-12-07T12:00:00Z"
}
```

#### Route Message

```python
POST /api/v1/registry/route
```

Route a message between frameworks.

**Request Body:**

```json
{
  "message": {
    "content": {
      "type": "task",
      "data": {}
    },
    "metadata": {
      "framework": "ax_nova",
      "version": "1.0.0",
      "operation_id": "task_123",
      "source_agent": "agent_1",
      "target_agent": "agent_2"
    },
    "message_type": "task_execution",
    "priority": 1
  },
  "target_framework": "langgraph"
}
```

**Response:**

```json
{
  "status": "success",
  "routed_message": {
    "id": "langgraph_task_123",
    "content": {},
    "metadata": {
      "framework": "langgraph",
      "version": "1.0.0",
      "timestamp": "2024-12-07T12:00:00Z"
    }
  }
}
```

### Memory System API

#### Store Memory

```python
POST /api/v1/memory/store
```

Store data in the memory system.

**Request Body:**

```json
{
  "memory_type": "short_term",
  "key": "context_123",
  "data": {
    "type": "conversation",
    "content": "Example conversation data"
  },
  "ttl": 3600
}
```

**Response:**

```json
{
  "status": "success",
  "stored_key": "context_123",
  "expires_at": "2024-12-07T13:00:00Z"
}
```

#### Retrieve Memory

```python
GET /api/v1/memory/{memory_type}/{key}
```

Retrieve data from memory system.

**Response:**

```json
{
  "status": "success",
  "data": {
    "type": "conversation",
    "content": "Example conversation data"
  },
  "metadata": {
    "created_at": "2024-12-07T12:00:00Z",
    "expires_at": "2024-12-07T13:00:00Z"
  }
}
```

### Knowledge System API

#### Add Knowledge

```python
POST /api/v1/knowledge/add
```

Add new knowledge to the system.

**Request Body:**

```json
{
  "knowledge_type": "graph",
  "content": {
    "nodes": [],
    "relationships": []
  },
  "metadata": {
    "source": "user_input",
    "confidence": 0.95
  }
}
```

**Response:**

```json
{
  "status": "success",
  "knowledge_id": "knowledge_123",
  "stored_at": "2024-12-07T12:00:00Z"
}
```

#### Query Knowledge

```python
POST /api/v1/knowledge/query
```

Query existing knowledge.

**Request Body:**

```json
{
  "query_type": "graph",
  "query": {
    "pattern": "MATCH (n:Concept) RETURN n",
    "parameters": {}
  },
  "limit": 10
}
```

**Response:**

```json
{
  "status": "success",
  "results": [
    {
      "node": {
        "id": "concept_1",
        "properties": {}
      }
    }
  ],
  "metadata": {
    "query_time": 0.05,
    "total_results": 1
  }
}
```

### Reasoning System API

#### Execute Reasoning

```python
POST /api/v1/reasoning/execute
```

Execute a reasoning operation.

**Request Body:**

```json
{
  "reasoning_type": "logical",
  "premises": ["All A are B", "X is A"],
  "query": "Is X a B?"
}
```

**Response:**

```json
{
  "status": "success",
  "conclusion": "Yes, X is a B",
  "confidence": 1.0,
  "reasoning_chain": [
    "Given: All A are B",
    "Given: X is A",
    "Therefore: X is B"
  ]
}
```

## WebSocket APIs

### Real-time Message Stream

```python
WS /api/v1/stream/messages
```

Stream real-time messages between frameworks.

**Subscribe Message:**

```json
{
  "action": "subscribe",
  "frameworks": ["ax_nova", "langgraph"],
  "message_types": ["task", "result"]
}
```

**Message Event:**

```json
{
  "type": "message",
  "data": {
    "id": "msg_123",
    "content": {},
    "metadata": {}
  }
}
```

### System Monitoring Stream

```python
WS /api/v1/stream/monitoring
```

Stream system monitoring data.

**Subscribe Message:**

```json
{
  "action": "subscribe",
  "metrics": ["memory_usage", "message_count", "error_rate"]
}
```

**Metric Event:**

```json
{
  "type": "metric",
  "data": {
    "metric": "memory_usage",
    "value": 85.5,
    "timestamp": "2024-12-07T12:00:00Z"
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "BRIDGE_ERROR",
    "message": "Detailed error message",
    "details": {
      "source": "bridge_registry",
      "operation": "route_message"
    }
  }
}
```

### Common Error Codes

- `BRIDGE_ERROR`: General bridge operation error
- `MEMORY_ERROR`: Memory system operation error
- `KNOWLEDGE_ERROR`: Knowledge system operation error
- `REASONING_ERROR`: Reasoning system operation error
- `VALIDATION_ERROR`: Input validation error
- `AUTH_ERROR`: Authentication/authorization error

## Authentication

All API endpoints require authentication using JWT tokens.

**Header Format:**

```
Authorization: Bearer <token>
```

### Get Authentication Token

```python
POST /api/v1/auth/token
```

**Request Body:**

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

**Response:**

```json
{
  "status": "success",
  "token": "eyJ0eXAi...",
  "expires_in": 3600
}
```

## Rate Limiting

API endpoints are rate limited based on the following rules:

- Standard endpoints: 100 requests per minute
- Streaming endpoints: 1000 messages per minute
- Bulk operations: 10 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638892800
```

## SDK Examples

### Python SDK

```python
from nova_bridge import NovaBridge

# Initialize bridge
bridge = NovaBridge(
    api_key="your_api_key",
    endpoint="https://api.nova-bridge.example"
)

# Route message
result = await bridge.route_message(
    message=message,
    target_framework="langgraph"
)

# Store memory
key = await bridge.store_memory(
    memory_type="short_term",
    data={"key": "value"}
)

# Query knowledge
results = await bridge.query_knowledge(
    query_type="graph",
    query="MATCH (n) RETURN n"
)
```

### JavaScript SDK

```javascript
import { NovaBridge } from "nova-bridge";

// Initialize bridge
const bridge = new NovaBridge({
  apiKey: "your_api_key",
  endpoint: "https://api.nova-bridge.example",
});

// Route message
const result = await bridge.routeMessage({
  message,
  targetFramework: "langgraph",
});

// Store memory
const key = await bridge.storeMemory({
  memoryType: "short_term",
  data: { key: "value" },
});

// Query knowledge
const results = await bridge.queryKnowledge({
  queryType: "graph",
  query: "MATCH (n) RETURN n",
});
```

## Webhook Integration

### Register Webhook

```python
POST /api/v1/webhooks/register
```

**Request Body:**

```json
{
  "url": "https://your-server.example/webhook",
  "events": ["message.routed", "memory.stored", "knowledge.added"],
  "secret": "your_webhook_secret"
}
```

**Response:**

```json
{
  "status": "success",
  "webhook_id": "webhook_123",
  "registered_at": "2024-12-07T12:00:00Z"
}
```

### Webhook Payload Format

```json
{
  "event": "message.routed",
  "timestamp": "2024-12-07T12:00:00Z",
  "data": {
    "message_id": "msg_123",
    "source_framework": "ax_nova",
    "target_framework": "langgraph"
  }
}
```

## Best Practices

1. **Error Handling**

   - Always check response status
   - Implement exponential backoff for retries
   - Log detailed error information

2. **Performance**

   - Use batch operations when possible
   - Implement caching for frequent queries
   - Monitor rate limits

3. **Security**

   - Rotate API keys regularly
   - Validate webhook signatures
   - Use HTTPS for all requests

4. **Monitoring**
   - Subscribe to system metrics
   - Set up alerts for error rates
   - Monitor API usage patterns

## Support

- Documentation: [Link to docs]
- API Status: [Link to status page]
- Support Email: support@nova-bridge.example
- Issue Tracker: [Link to GitHub issues]
