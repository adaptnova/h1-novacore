# Nova Framework Memory System

The Nova Framework Memory System provides a comprehensive solution for managing different types of memory storage in AI applications. It implements a three-tier memory architecture inspired by cognitive science and practical system design.

## Architecture

### Memory Types

1. **Short-term Memory (Redis)**

   - Fast, in-memory storage
   - Automatic expiration (TTL)
   - Ideal for caching and temporary data
   - Supports eviction policies for memory management

2. **Long-term Memory (MongoDB)**

   - Persistent, structured storage
   - Document-based with flexible schemas
   - Supports complex queries and indexing
   - Ideal for permanent data storage

3. **Semantic Memory (Neo4j)**
   - Graph-based storage for connected data
   - Relationship-centric data modeling
   - Supports complex graph queries
   - Ideal for knowledge representation

### Components

- **Memory Manager**: Central coordinator for all memory operations
- **Memory Handlers**: Specialized handlers for each storage backend
- **Configuration System**: YAML-based configuration for all components
- **Health Monitoring**: Built-in health checks and statistics
- **Error Handling**: Comprehensive error handling and recovery

## Features

### Core Features

- Asynchronous operations (async/await)
- Type-safe interfaces
- Automatic connection management
- Configurable TTL and eviction policies
- Built-in monitoring and health checks
- Comprehensive error handling
- Transaction support (where applicable)

### Storage Features

#### Short-term Memory (Redis)

- Key-value storage with TTL
- JSON serialization
- Memory usage monitoring
- Configurable eviction policies
- Optional persistence

#### Long-term Memory (MongoDB)

- Document storage with metadata
- Automatic indexing
- Query capabilities
- Schema flexibility
- Data versioning

#### Semantic Memory (Neo4j)

- Graph-based storage
- Relationship management
- Property graphs
- Pattern matching
- Graph traversal

### Management Features

- Health monitoring
- Usage statistics
- Backup support
- Access control
- Encryption support
- Performance metrics

## Installation

1. Install required dependencies:

```bash
pip install redis motor neo4j-driver pyyaml
```

2. Configure memory systems in `config/memory_config.yaml`:

```yaml
short_term:
  host: localhost
  port: 6379
  # Redis settings

long_term:
  uri: mongodb://localhost:27017
  # MongoDB settings

semantic:
  uri: bolt://localhost:7687
  # Neo4j settings
```

## Basic Usage

```python
from src.handlers.memory import MemoryManager, MemoryType

# Initialize manager
manager = MemoryManager(config)
await manager.connect()

# Store data
await manager.store(MemoryType.SHORT_TERM, "key", data, ttl=3600)
await manager.store(MemoryType.LONG_TERM, "key", data)
await manager.store(MemoryType.SEMANTIC, "key", data, relationships=[...])

# Retrieve data
short_term_data = await manager.retrieve(MemoryType.SHORT_TERM, "key")
long_term_data = await manager.retrieve(
    MemoryType.LONG_TERM,
    "key",
    include_metadata=True
)
semantic_data = await manager.retrieve(
    MemoryType.SEMANTIC,
    "key",
    include_relationships=True
)

# Clean up
await manager.disconnect()
```

For more detailed examples and advanced usage, see `examples/memory_system_usage.py`.

## Configuration Reference

### Short-term Memory (Redis)

```yaml
short_term:
  host: localhost
  port: 6379
  db: 0
  prefix: nova:memory:short_term:
  ttl: 3600
  max_memory: 2gb
  eviction_policy: allkeys-lru
```

### Long-term Memory (MongoDB)

```yaml
long_term:
  uri: mongodb://localhost:27017
  database: nova_memory
  collection: long_term
  index_fields:
    - key
    - created_at
```

### Semantic Memory (Neo4j)

```yaml
semantic:
  uri: bolt://localhost:7687
  database: nova_memory
  user: neo4j
  password: your_password
  node_label: Memory
  relationship_type: RELATED_TO
```

## Best Practices

1. **Memory Type Selection**

   - Use short-term memory for caching and temporary data
   - Use long-term memory for persistent structured data
   - Use semantic memory for connected knowledge representation

2. **Error Handling**

   - Always handle potential errors in memory operations
   - Implement retry logic for transient failures
   - Monitor memory system health

3. **Performance**

   - Configure appropriate TTLs for short-term memory
   - Index frequently queried fields in long-term memory
   - Optimize graph queries in semantic memory

4. **Security**
   - Enable encryption for sensitive data
   - Implement access control
   - Regularly rotate credentials
   - Monitor for suspicious activity

## Development

### Running Tests

```bash
# Run all tests
pytest tests/test_handlers/

# Run specific test suite
pytest tests/test_handlers/test_redis_handler.py
pytest tests/test_handlers/test_mongo_handler.py
pytest tests/test_handlers/test_neo4j_handler.py
pytest tests/test_handlers/test_memory_manager.py
```

### Adding New Features

1. Implement new functionality in the appropriate handler
2. Add tests in the corresponding test file
3. Update the memory manager if needed
4. Document changes in this README
5. Add examples to `examples/memory_system_usage.py`

## License

MIT License - See LICENSE file for details
