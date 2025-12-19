# Mini-Agent Memory System API Reference

## Core Classes

### MiniAgentCore
Main memory system interface.

```python
class MiniAgentCore:
    def __init__(self, redis_host="localhost", redis_port=6379, password=None)
    def start_work_session(self, user_name: str, project_context: str = None) -> Dict[str, Any]
    def process_user_interaction(self, user_input: str, agent_response: str = None, tools_used: List[str] = None) -> Dict[str, Any]
    def get_intelligent_response(self, user_prompt: str) -> Dict[str, Any]
    def record_work_progress(self, task_name: str, description: str, status: str = "in_progress", notes: str = None) -> str
    def get_memory_statistics(self) -> Dict[str, Any]
    def end_session(self, summary: str = None) -> Dict[str, Any]
```

### IntegratedMiniAgentMemory
Multi-database memory system.

```python
class IntegratedMiniAgentMemory:
    def __init__(self, redis_host="localhost", redis_port=6379, password=None)
    def start_integrated_session(self, user_name: str, project_context: str = None) -> Dict[str, Any]
    def store_knowledge_integrated(self, knowledge_type: str, content: str, context: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> str
    def get_comprehensive_response(self, user_prompt: str) -> Dict[str, Any]
    def get_comprehensive_analytics(self) -> Dict[str, Any]
```

## Memory Types

- `fact`: Factual information
- `skill`: Learned skills and capabilities
- `preference`: User preferences and working style
- `tool_knowledge`: Tool usage patterns
- `work_task`: Task and project tracking
- `relationship`: Knowledge relationships
- `session_context`: Session-specific information

## Storage Backends

### Primary Memory (DragonflyDB/Redis)
- Fast access (<10ms response)
- User preferences
- Knowledge items
- Session continuity

### Session Data (Redis Cluster)
- Chat history
- Interaction logs
- Message persistence

### Analytics (PostgreSQL)
- Structured query optimization
- Relationship mapping
- Performance metrics

### Patterns (ClickHouse)
- Trend analysis
- Usage patterns
- Predictive insights

## Configuration

```json
{{
  "databases": {{
    "dragonfly": {{
      "enabled": true,
      "hosts": ["localhost:18000"],
      "password": "your_password",
      "primary": true
    }},
    "redis": {{
      "enabled": true,
      "hosts": ["localhost:6379"]
    }}
  }}
}}
```

## Error Handling

All classes include comprehensive error handling:
- Database connection failures
- Authentication errors
- Timeout handling
- Automatic retry logic

## Thread Safety

Memory system is thread-safe for:
- Multiple concurrent sessions
- Parallel knowledge storage
- Concurrent query processing
