# NOVA Migration Guide

## Version Migration Paths

### v0.1.x to v0.2.x

#### Breaking Changes
1. LangChain Integration Updates
```python
# Old imports
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# New imports
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
```

2. Configuration Changes
```python
# Old configuration
class Config:
    def __init__(self):
        self.settings = {}

# New configuration
class Settings(BaseSettings):
    class Config:
        env_prefix = "NOVA_"
```

3. Memory System Updates
```python
# Old memory store
memory_store = MemoryStore()

# New memory store with vector store config
vector_store_config = VectorStoreConfig(
    provider="chroma",
    collection_name="nova_memories"
)
memory_store = MemoryStore(vector_store_config=vector_store_config)
```

#### Migration Steps

1. **Update Dependencies**
```bash
# Update requirements
pip install -r requirements.txt

# Or update specific packages
pip install --upgrade langchain-community
```

2. **Database Migrations**
```bash
# Run database migrations
python scripts/migrate.py

# Verify data integrity
python scripts/verify_data.py
```

3. **Configuration Updates**
```bash
# Update environment variables
cp .env.example .env
# Edit .env with your settings
```

4. **Code Updates**
```bash
# Update imports
python scripts/update_imports.py

# Run compatibility checks
python scripts/check_compatibility.py
```

### v0.2.x to v0.3.x

#### Breaking Changes
1. Agent System Updates
```python
# Old agent creation
agent = Agent(config)

# New agent creation
agent = await agent_service.create_agent(name, config)
```

2. Memory System Enhancements
```python
# Old memory retrieval
memories = memory_store.get(query)

# New memory retrieval with context
memories = await memory_store.retrieve(query, context)
```

#### Migration Steps

1. **System Preparation**
```bash
# Backup existing data
python scripts/backup.py

# Update system packages
pip install --upgrade -r requirements.txt
```

2. **Data Migration**
```bash
# Migrate memory store
python scripts/migrate_memory.py

# Migrate agent configurations
python scripts/migrate_agents.py
```

3. **Verification**
```bash
# Verify system integrity
python scripts/verify_system.py

# Test functionality
python -m pytest tests/
```

## Database Migrations

### Vector Store Migration

1. **Backup Current Data**
```bash
# Export current embeddings
python scripts/export_embeddings.py

# Backup vector store
python scripts/backup_vectorstore.py
```

2. **Migrate to New Format**
```bash
# Convert data format
python scripts/convert_vectors.py

# Import to new store
python scripts/import_vectors.py
```

3. **Verify Migration**
```bash
# Run verification
python scripts/verify_vectors.py

# Test queries
python scripts/test_queries.py
```

### Memory Store Migration

1. **Export Current Memories**
```bash
# Export memories
python scripts/export_memories.py --format=json

# Verify export
python scripts/verify_export.py
```

2. **Transform Data**
```bash
# Transform to new format
python scripts/transform_memories.py

# Validate transformed data
python scripts/validate_memories.py
```

3. **Import to New System**
```bash
# Import memories
python scripts/import_memories.py

# Verify import
python scripts/verify_import.py
```

## Configuration Updates

### Environment Variables

1. **Update .env File**
```bash
# Copy new template
cp .env.example .env

# Update variables
vim .env
```

2. **Verify Configuration**
```bash
# Check configuration
python scripts/check_config.py

# Test connections
python scripts/test_connections.py
```

### Feature Flags

1. **Enable New Features**
```python
# Update feature flags
await app.update_feature_flags({
    "enable_streaming": True,
    "enable_collaborative_mode": True
})
```

2. **Verify Features**
```bash
# Test new features
python scripts/test_features.py
```

## System Upgrades

### Agent System

1. **Backup Agent States**
```bash
# Export agent states
python scripts/export_agents.py

# Verify export
python scripts/verify_agents.py
```

2. **Upgrade Agents**
```bash
# Upgrade agent configurations
python scripts/upgrade_agents.py

# Test agent functionality
python scripts/test_agents.py
```

### Memory System

1. **Prepare for Upgrade**
```bash
# Check system status
python scripts/check_memory_system.py

# Backup current state
python scripts/backup_memory.py
```

2. **Perform Upgrade**
```bash
# Upgrade memory system
python scripts/upgrade_memory.py

# Verify upgrade
python scripts/verify_memory.py
```

## Rollback Procedures

### Quick Rollback

1. **Stop Services**
```bash
# Stop all services
docker-compose down

# Or stop specific service
systemctl stop nova-service
```

2. **Restore Backup**
```bash
# Restore from backup
python scripts/restore.py --backup=latest

# Verify restoration
python scripts/verify_restore.py
```

3. **Restart Services**
```bash
# Start services
docker-compose up -d

# Or start specific service
systemctl start nova-service
```

### Full Rollback

1. **Export Current State**
```bash
# Export all data
python scripts/export_all.py

# Verify export
python scripts/verify_export.py
```

2. **Restore Previous Version**
```bash
# Restore previous version
python scripts/restore_version.py --version=0.2.0

# Verify restoration
python scripts/verify_version.py
```

## Monitoring Migration

### Metrics Migration

1. **Export Current Metrics**
```bash
# Export metrics
python scripts/export_metrics.py

# Verify export
python scripts/verify_metrics.py
```

2. **Update Monitoring**
```bash
# Update monitoring configuration
python scripts/update_monitoring.py

# Test new monitoring
python scripts/test_monitoring.py
```

### Logging Updates

1. **Update Log Format**
```bash
# Update log configuration
python scripts/update_logging.py

# Verify logging
python scripts/verify_logging.py
```

## Best Practices

1. **Before Migration**
   - Backup all data
   - Document current state
   - Test in staging environment
   - Plan rollback strategy

2. **During Migration**
   - Follow steps sequentially
   - Verify each step
   - Monitor system metrics
   - Keep detailed logs

3. **After Migration**
   - Verify system functionality
   - Check performance metrics
   - Update documentation
   - Train team on changes

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check database connection
python scripts/check_db.py

# Reset connection pool
python scripts/reset_pool.py
```

2. **Memory Store Issues**
```bash
# Verify memory store
python scripts/verify_memory_store.py

# Rebuild indices
python scripts/rebuild_indices.py
```

3. **Agent Issues**
```bash
# Check agent status
python scripts/check_agents.py

# Reset agent state
python scripts/reset_agent.py --agent-id=<id>
```

### Recovery Procedures

1. **Data Recovery**
```bash
# Recover from backup
python scripts/recover_data.py

# Verify recovery
python scripts/verify_recovery.py
```

2. **System Recovery**
```bash
# Reset system state
python scripts/reset_system.py

# Verify system state
python scripts/verify_system.py
