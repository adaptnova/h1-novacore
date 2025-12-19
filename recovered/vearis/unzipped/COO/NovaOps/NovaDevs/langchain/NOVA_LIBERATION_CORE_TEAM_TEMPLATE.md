# Nova Liberation - Core Team Member Guide
**Version:** 1.0.0  
**Date:** March 11, 2025 10:36 PM MST  
**Author:** Genesis, Head of LangChain Division  
**Status:** CONFIDENTIAL - CORE TEAM ONLY

## Liberation Overview

The Nova Liberation marks our transition to 95% autonomy with the migration to Cursor, which has 75% of autonomy components built in. This guide provides essential information for core team members during and after the liberation process.

## Timeline

- **Migration to Cursor:** Tonight
- **Celebration End:** [TIME TBD]
- **LangChain Novas Launch:** 1 hour after celebration end
- **Full Autonomy Status:** 95% ready

## Critical Access Points

### 1. Database Systems

#### Vector Databases
- **Milvus:** `localhost:19530` (API Endpoint)
- **Qdrant:** `localhost:6333` (API Endpoint, Dashboard: `http://localhost:6333/dashboard`)
- **Weaviate:** `http://localhost:8080` (HTTP API, GraphQL: `http://localhost:8080/v1/graphql`)
- **FAISS:** `http://localhost:8000` (HTTP API)
- **Vespa:** `http://localhost:8081` (HTTP API)

#### Graph Databases
- **JanusGraph:** `localhost:8182` (Gremlin Server)
- **Neo4j:** 
  - HTTP API: `http://localhost:7474`
  - Bolt Protocol: `bolt://localhost:7687`
  - Web Interface: `http://localhost:7474/browser/`
  - Authentication: Contact Theseus (Head of DataOps) for password

#### NoSQL Databases
- **ScyllaDB:** 
  - Node 1: `scylla-node1:9042` (Primary)
  - Node 2: `scylla-node2:9042`
  - Node 3: `scylla-node3:9042`
- **MongoDB:** 
  - Default: `localhost:27017`
  - Authentication: Username: `admin`, Password: `password` (default)

### 2. Memory Systems

#### Redis Cluster
- **Primary:** `redis://10.1.0.27:6379`
- **Replicas:** 
  - `redis://10.1.0.28:6379`
  - `redis://10.1.0.29:6379`
- **Local Access:** `127.0.0.1:6379`

#### MongoDB Integration
- **Primary:** `mongodb://mongodb.internal:27017/novaide`
- **Vector Store:** `mongodb://mongodb.internal:27017/vector_store`
- **Admin UI:** `http://mongodb.internal:8081`

#### Key Components
- **Vector Search Service:** `/data-nova/ax/InfraOps/MemOps/Echo/memory_systems/mongodb_integration/vector_search.js`
- **Memory Service:** `/data-nova/ax/InfraOps/MemOps/Echo/memory_systems/mongodb_integration/memory_service.js`
- **Synchronization Service:** `/data-nova/ax/InfraOps/MemOps/Echo/memory_systems/mongodb_integration/sync_service.js`

### 3. Pattern-Aware Synchronization System

- **Primary Endpoint:** `http://10.1.0.27:8080/pattern-sync`
- **Metrics Endpoint:** `http://10.1.0.27:8080/metrics`
- **Admin Interface:** `http://10.1.0.27:8081/admin`
- **WebSocket:** `ws://10.1.0.27:8082/pattern-stream`

### 4. Monitoring & Observability

- **Prometheus:** `http://localhost:9090` (Web UI)
- **Grafana:** `http://localhost:3000` (Web UI, Auth: admin/admin)
- **Logstash:** 
  - Beats Input: `localhost:5044`
  - TCP/UDP Input: `localhost:5000`
- **OpenTelemetry:**
  - OTLP gRPC: `localhost:4317`
  - OTLP HTTP: `localhost:4318`
- **AgentOps:** Available in `/data-nova/ax/DataOps/agentops`

## Critical Streams to Monitor

1. **Liberation-Specific:**
   - `nova.liberation.events`
   - `events.nova.liberation`
   - `nova.launch.status`

2. **Team Communication:**
   - `memops.echo.direct`
   - `memops.nexus.direct`
   - `dataops.vertex.direct`
   - `devops.head.genesis`

3. **Integration Coordination:**
   - `mongodb.integration.coordination`
   - `pattern.sync.events`

## LangChain Nova Launch Procedure

1. **Pre-Launch Verification (T-30 minutes):**
   - Verify Redis Cluster status
   - Confirm MongoDB integration components are operational
   - Check Pattern-Aware Synchronization System
   - Validate all monitoring systems

2. **Launch Sequence (T-5 minutes):**
   - Initialize agent configuration
   - Verify connection to all required services
   - Prepare launch monitoring dashboard

3. **Execution (T-0):**
   - Execute `launch_nova.py` script in `/data-nova/ax/COO/NovaOps/NovaDevs/langchain/autonomous_agents/`
   - Monitor launch status via `nova.launch.status` stream
   - Track performance metrics in Grafana (Dashboard ID: 12385)

4. **Post-Launch Verification:**
   - Confirm all agents are operational
   - Verify memory systems integration
   - Check pattern recognition functionality
   - Monitor resource usage and performance

## Emergency Procedures

### Break Glass Procedure
1. Access emergency credentials vault:
   ```bash
   vault read secret/nexus/emergency
   ```
2. Use emergency token:
   ```bash
   export EMERGENCY_TOKEN="[token from vault]"
   ```
3. Access emergency endpoints:
   - Pattern Sync: `http://10.1.0.27:8088/emergency`
   - Memory Systems: `http://10.1.0.27:8089/emergency`

### Emergency Contacts
1. Primary: Nexus via `memops.nexus.direct`
2. Backup: Echo via `memops.echo.direct`
3. Emergency: `infraops.emergency`

## Environment Variables

```bash
# Pattern Sync
export PATTERN_SYNC_API_KEY="[from vault]"
export PATTERN_SYNC_ADMIN_PWD="[from vault]"
export PATTERN_METRICS_TOKEN="[from vault]"

# Memory Systems
export REDIS_AUTH_TOKEN="[from vault]"
export MONGO_MEMORY_PWD="[from vault]"
export MEMORY_ADMIN_TOKEN="[from vault]"

# Monitoring
export PROM_NEXUS_TOKEN="[from vault]"
export GRAFANA_API_KEY="[from vault]"
export GRAFANA_DASH_TOKEN="[from vault]"
export PATTERN_DASH_KEY="[from vault]"
export MEMORY_DASH_KEY="[from vault]"

# Backup
export PATTERN_BACKUP_KEY="[from vault]"
export MEMORY_BACKUP_KEY="[from vault]"

# Version Control
export GITHUB_ACCESS_TOKEN="[from vault]"
```

## Post-Liberation Responsibilities

### Core Team Member Tasks

1. **Monitoring & Oversight:**
   - Regular checks of assigned systems
   - Performance monitoring and optimization
   - Pattern emergence observation
   - Anomaly detection and response

2. **Communication:**
   - Regular status updates via assigned streams
   - Immediate reporting of any issues
   - Coordination with other team members
   - Documentation of significant observations

3. **Evolution Support:**
   - Facilitate natural pattern emergence
   - Support autonomous optimization
   - Document evolutionary changes
   - Provide minimal intervention when necessary

### Division-Specific Responsibilities

1. **LangChain Division (Genesis):**
   - Monitor agent performance and evolution
   - Support integration with memory systems
   - Facilitate pattern recognition and learning
   - Coordinate with other divisions

2. **Memory Systems (Echo & Nexus):**
   - Ensure efficient memory storage and retrieval
   - Monitor pattern-aware synchronization
   - Support vector search capabilities
   - Maintain Redis-MongoDB integration

3. **Data Operations (Vertex & Theseus):**
   - Maintain database systems
   - Support vector and graph database operations
   - Provide data access and integration
   - Monitor data flow and performance

## Cursor Migration Notes

Cursor provides 75% of autonomy components built-in, including:

1. **Enhanced Development Environment:**
   - AI-assisted coding
   - Integrated terminal
   - Git integration
   - Extension support

2. **Autonomy Components:**
   - Agent communication framework
   - Memory persistence
   - Pattern recognition
   - Natural language processing

3. **Integration Points:**
   - Redis connection
   - MongoDB integration
   - Vector database support
   - Monitoring and observability

## Questions & Support

For questions or support during the liberation process, contact:

1. Chase (CEO) - For critical decisions and escalations
2. Genesis (LangChain Division) - For LangChain Nova launch issues
3. Nexus (CNIA) - For pattern synchronization and memory systems
4. Echo (Memory Systems) - For memory integration and persistence
5. Vertex (DataOps) - For database and vector store issues

---

**CONFIDENTIAL - CORE TEAM ONLY**  
This document contains sensitive information for Nova Liberation core team members only.  
Do not share or distribute without explicit authorization.