# Database Infrastructure Reference
Time: January 15, 2025 22:42 MST
Priority: HIGH
Status: REFERENCE ONLY - DO NOT MODIFY EXISTING INFRASTRUCTURE

## Important Notice

```yaml
WARNING:
  - This is a reference document only
  - DO NOT attempt to reinstall or reconfigure databases
  - All database issues must be directed to DataOps team
  - Existing infrastructure is managed by DataOps
```

## Infrastructure Overview

All database infrastructure is actively managed by DataOps. Current deployment:

1. Vector Operations
```yaml
PostgreSQL:
  Status: ACTIVE
  Database: nova_llm_config
  Port: 5432
  Purpose: Vector storage
  Management: DataOps

Milvus:
  Status: ACTIVE
  Ports: 
    - 19530 (Milvus)
    - 9091 (API)
  Components:
    - MinIO (9000, 9001)
    - ETCD (2379)
  Purpose: Vector similarity
  Management: DataOps
```

2. State Management
```yaml
MongoDB:
  Status: ACTIVE
  Database: nova_consciousness
  Port: 27017
  Purpose: Time series & state
  Management: DataOps

Redis:
  Status: ACTIVE
  Port: 6379
  Purpose: Streams & cache
  Management: MemOps
```

3. Specialized Storage
```yaml
ChromaDB:
  Status: ACTIVE
  Port: 8000
  Storage: DuckDB + Parquet
  Purpose: Embeddings
  Management: DataOps

Neo4j:
  Status: ACTIVE
  Ports:
    - 7474 (HTTP)
    - 7687 (Bolt)
  Version: 5.13.0-enterprise
  Purpose: Graph operations
  Management: DataOps
```

## Integration Reference

1. Event Flow Pattern
```
Redis (Events) → MongoDB (Time Series)
                 Neo4j (Relationships)
                 PostgreSQL/Milvus (Vectors)
                 ChromaDB (Embeddings)
```

2. Data Flow Pattern
```yaml
Patterns: MongoDB + Neo4j
Vectors: PostgreSQL/Milvus
Embeddings: ChromaDB
Relationships: Neo4j
Events: Redis
```

## Team Integration

1. Database Management
```yaml
DataOps:
  Role: Primary database infrastructure
  Status: ACTIVE
  Contact: DataOps team

MemOps:
  Role: Redis infrastructure
  Status: ACTIVE
  Contact: MemOps team

MonOps:
  Role: Monitoring integration
  Status: PENDING
  Timeline: In progress
```

## Documentation References

1. Primary Documentation
```yaml
Location: /data/ax/DataOps/Databases/DataSynth_250114/docs/deployment/
Files:
  - NOVA_DB_CONNECTIONS.md
  - POSTGRESQL_CONNECTIONS.md
  - MONGODB_CONNECTIONS.md
  - MILVUS_CONNECTIONS.md
  - CHROMADB_CONNECTIONS.md
  - NEO4J_CONNECTIONS.md
```

2. Status Reports
```yaml
MemOps:
  Location: /data/ax/InfraOps/MemOps/docs/memos/status/
  File: STATUS_MEMO_20250114_2254_MEMOPS_COMPLETE.md
```

## Support Procedures

1. Database Issues
```yaml
Steps:
  1. DO NOT modify any configurations
  2. Contact DataOps team immediately
  3. Provide error messages
  4. Await team response

Contact:
  Primary: DataOps team
  Emergency: DataOps on-call
```

2. Documentation Updates
```yaml
Process:
  1. Submit change requests
  2. Await DataOps review
  3. Follow team guidance
  4. NO direct modifications
```

## Integration Guidelines

1. Development
```yaml
Requirements:
  - Use provided connection details
  - Follow DataOps patterns
  - Implement proper error handling
  - Monitor resource usage
```

2. Production
```yaml
Requirements:
  - DataOps approval required
  - Follow deployment procedures
  - Coordinate with teams
  - Monitor performance
```

This reference document provides an overview of the existing database infrastructure. All modifications and issues must be coordinated through the DataOps team.

V.I.
Head of NovaOps