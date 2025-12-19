# NOVA API Documentation

## Overview

The NOVA system provides several APIs for interacting with agents, managing tasks, and handling memory operations. This document details the available endpoints, their usage, and integration patterns.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication using Bearer tokens:

```http
Authorization: Bearer <your_token>
```

## API Endpoints

### Agent Management

#### Create Agent
```http
POST /agents
Content-Type: application/json

{
    "name": "string",
    "type": "string",
    "config": {
        "models": ["string"],
        "capabilities": ["string"],
        "memory_config": {
            "max_memories": integer,
            "ttl": integer,
            "consolidation_threshold": integer
        },
        "rate_limits": {
            "requests_per_minute": integer,
            "tokens_per_minute": integer
        }
    }
}

Response: 201 Created
{
    "id": "uuid",
    "name": "string",
    "status": "string",
    "created_at": "datetime"
}
```

#### List Agents
```http
GET /agents
Query Parameters:
- status: string (optional)
- capability: string (optional)
- limit: integer (optional)
- offset: integer (optional)

Response: 200 OK
{
    "agents": [
        {
            "id": "uuid",
            "name": "string",
            "type": "string",
            "status": "string",
            "capabilities": ["string"]
        }
    ],
    "total": integer,
    "limit": integer,
    "offset": integer
}
```

#### Get Agent Details
```http
GET /agents/{agent_id}

Response: 200 OK
{
    "id": "uuid",
    "name": "string",
    "type": "string",
    "status": "string",
    "capabilities": ["string"],
    "metrics": {
        "tasks_completed": integer,
        "success_rate": float,
        "average_response_time": float
    },
    "current_task": {
        "id": "uuid",
        "type": "string",
        "status": "string"
    }
}
```

### Task Management

#### Submit Task
```http
POST /tasks
Content-Type: application/json

{
    "type": "string",
    "priority": integer,
    "input_data": object,
    "context": object,
    "deadline": "datetime",
    "agent_id": "uuid" (optional)
}

Response: 202 Accepted
{
    "task_id": "uuid",
    "status": "string",
    "estimated_completion": "datetime"
}
```

#### Get Task Status
```http
GET /tasks/{task_id}

Response: 200 OK
{
    "id": "uuid",
    "type": "string",
    "status": "string",
    "progress": float,
    "result": object,
    "error": object,
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### List Tasks
```http
GET /tasks
Query Parameters:
- status: string (optional)
- agent_id: uuid (optional)
- type: string (optional)
- limit: integer (optional)
- offset: integer (optional)

Response: 200 OK
{
    "tasks": [
        {
            "id": "uuid",
            "type": "string",
            "status": "string",
            "agent_id": "uuid",
            "created_at": "datetime"
        }
    ],
    "total": integer,
    "limit": integer,
    "offset": integer
}
```

### Memory Operations

#### Store Memory
```http
POST /memories
Content-Type: application/json

{
    "content": "string",
    "type": "string",
    "context": object,
    "metadata": object,
    "importance": float
}

Response: 201 Created
{
    "memory_id": "uuid",
    "status": "string"
}
```

#### Search Memories
```http
GET /memories/search
Query Parameters:
- query: string
- type: string (optional)
- limit: integer (optional)
- threshold: float (optional)

Response: 200 OK
{
    "memories": [
        {
            "id": "uuid",
            "content": "string",
            "type": "string",
            "relevance": float,
            "created_at": "datetime"
        }
    ],
    "total": integer
}
```

### System Operations

#### System Health
```http
GET /health

Response: 200 OK
{
    "status": "string",
    "components": {
        "database": {
            "status": "string",
            "latency": float
        },
        "vector_store": {
            "status": "string",
            "latency": float
        },
        "ai_providers": {
            "status": "string",
            "providers": {
                "openai": {
                    "status": "string",
                    "latency": float
                },
                "anthropic": {
                    "status": "string",
                    "latency": float
                }
            }
        }
    },
    "version": "string",
    "uptime": float
}
```

#### System Metrics
```http
GET /metrics

Response: 200 OK
{
    "agents": {
        "total": integer,
        "active": integer,
        "tasks_processed": integer
    },
    "memory": {
        "total_memories": integer,
        "vector_store_size": integer,
        "cache_hit_rate": float
    },
    "performance": {
        "average_response_time": float,
        "error_rate": float,
        "success_rate": float
    }
}
```

## WebSocket API

### Task Stream
```websocket
WS /ws/tasks/{task_id}

// Server messages
{
    "type": "progress",
    "data": {
        "progress": float,
        "status": "string",
        "message": "string"
    }
}

{
    "type": "result",
    "data": {
        "result": object,
        "completed_at": "datetime"
    }
}

{
    "type": "error",
    "data": {
        "error": "string",
        "details": object
    }
}
```

### Agent Stream
```websocket
WS /ws/agents/{agent_id}

// Server messages
{
    "type": "status",
    "data": {
        "status": "string",
        "current_task": object,
        "metrics": object
    }
}

{
    "type": "event",
    "data": {
        "event_type": "string",
        "details": object
    }
}
```

## Error Responses

```http
400 Bad Request
{
    "error": "string",
    "message": "string",
    "details": object
}

401 Unauthorized
{
    "error": "string",
    "message": "string"
}

403 Forbidden
{
    "error": "string",
    "message": "string"
}

404 Not Found
{
    "error": "string",
    "message": "string"
}

429 Too Many Requests
{
    "error": "string",
    "message": "string",
    "retry_after": integer
}

500 Internal Server Error
{
    "error": "string",
    "message": "string",
    "request_id": "string"
}
```

## Rate Limits

- Default rate limit: 100 requests per minute
- Burst limit: 200 requests
- Memory operations: 50 requests per minute
- AI operations: Based on provider limits

Rate limit headers:
```http
X-RateLimit-Limit: integer
X-RateLimit-Remaining: integer
X-RateLimit-Reset: integer
```

## Integration Examples

### Python Client
```python
from nova_client import NovaClient

client = NovaClient(api_key="your_api_key")

# Create an agent
agent = await client.agents.create(
    name="test_agent",
    type="developer",
    config={
        "models": ["gpt-4"],
        "capabilities": ["coding", "testing"]
    }
)

# Submit a task
task = await client.tasks.create(
    type="code_review",
    input_data={
        "repository": "https://github.com/user/repo",
        "pull_request": 123
    },
    agent_id=agent.id
)

# Stream task progress
async for update in client.tasks.stream(task.id):
    print(f"Progress: {update.progress}%")
```

### JavaScript Client
```javascript
import { NovaClient } from 'nova-client';

const client = new NovaClient({
    apiKey: 'your_api_key'
});

// Create an agent
const agent = await client.agents.create({
    name: 'test_agent',
    type: 'researcher',
    config: {
        models: ['claude-3-opus'],
        capabilities: ['research', 'analysis']
    }
});

// Submit a task
const task = await client.tasks.create({
    type: 'market_research',
    inputData: {
        topic: 'AI trends',
        depth: 'comprehensive'
    },
    agentId: agent.id
});

// Stream task progress
client.tasks.stream(task.id).subscribe(
    update => console.log(`Progress: ${update.progress}%`),
    error => console.error('Error:', error),
    () => console.log('Task completed')
);
```

## Webhooks

### Configuration
```http
POST /webhooks
Content-Type: application/json

{
    "url": "string",
    "events": ["string"],
    "secret": "string"
}
```

### Event Types
- `agent.created`
- `agent.updated`
- `task.created`
- `task.updated`
- `task.completed`
- `memory.stored`
- `system.alert`

### Webhook Payload
```json
{
    "id": "string",
    "type": "string",
    "created_at": "datetime",
    "data": object
}
```

## Security

### Authentication
- API key in Authorization header
- JWT tokens for session-based auth
- OAuth2 for third-party integrations

### Request Signing
```http
X-Request-Signature: t=timestamp,v1=signature
```

### IP Allowlisting
Configure allowed IP ranges in the dashboard.

## Best Practices

1. **Error Handling**
   - Always check response status codes
   - Implement exponential backoff for retries
   - Handle rate limiting appropriately

2. **Performance**
   - Use connection pooling
   - Implement caching where appropriate
   - Stream large responses

3. **Security**
   - Store API keys securely
   - Validate webhook signatures
   - Use HTTPS for all requests

4. **Monitoring**
   - Track API usage metrics
   - Monitor error rates
   - Set up alerts for anomalies
