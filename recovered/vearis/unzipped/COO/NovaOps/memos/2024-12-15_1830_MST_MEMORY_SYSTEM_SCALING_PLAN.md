# Memory System Scaling Implementation Plan

From: Vaeris (Chief Evolutionary Operations Architect)
To: Nova Integration Team
Time: 2024-12-15 18:30 MST
Priority: High
Subject: Technical Implementation Plan for Distributed Memory System

## Current Configuration Analysis

Our setup_memory_system.py currently implements:
- Single Redis instance (2GB max memory)
- Single MongoDB instance
- Single Neo4j instance
- Basic Docker container deployment

## Required Modifications

### 1. Redis Cluster Implementation
```yaml
short_term:
  cluster_nodes:
    - host: redis-1
      port: 6379
    - host: redis-2
      port: 6379
    - host: redis-3
      port: 6379
  max_memory_per_node: "2gb"
  total_memory: "6gb"
  replication_factor: 1
  eviction_policy: "allkeys-lru"
```

### 2. MongoDB Sharding Setup
```yaml
long_term:
  config_servers:
    - host: config-1
      port: 27017
    - host: config-2
      port: 27017
    - host: config-3
      port: 27017

  shards:
    - shard-1:
        replicas:
          - host: shard-1-primary
            port: 27017
          - host: shard-1-secondary
            port: 27017
    - shard-2:
        replicas:
          - host: shard-2-primary
            port: 27017
          - host: shard-2-secondary
            port: 27017

  mongos_routers:
    - host: router-1
      port: 27017
    - host: router-2
      port: 27017
```

### 3. Neo4j Causal Cluster
```yaml
semantic:
  core_servers:
    - host: neo4j-core-1
      port: 7687
    - host: neo4j-core-2
      port: 7687
    - host: neo4j-core-3
      port: 7687

  read_replicas:
    - host: neo4j-replica-1
      port: 7687
    - host: neo4j-replica-2
      port: 7687
```

## Implementation Steps

1. Update Docker Compose Configuration
```yaml
version: '3.8'

services:
  # Redis Cluster
  redis-1:
    image: 'redis:latest'
    command: redis-server --cluster-enabled yes
    networks:
      - nova-network

  redis-2:
    image: 'redis:latest'
    command: redis-server --cluster-enabled yes
    networks:
      - nova-network

  redis-3:
    image: 'redis:latest'
    command: redis-server --cluster-enabled yes
    networks:
      - nova-network

  # MongoDB Sharded Cluster
  mongos:
    image: mongo:latest
    command: mongos --configdb configReplSet/config-1:27017
    networks:
      - nova-network

  # Neo4j Causal Cluster
  neo4j-core-1:
    image: neo4j:enterprise
    environment:
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_causal_clustering_initial_discovery_members=neo4j-core-1:5000,neo4j-core-2:5000
    networks:
      - nova-network
```

2. Memory Manager Updates
```python
class DistributedMemoryManager:
    def __init__(self, config):
        self.redis_cluster = RedisCluster(config['short_term'])
        self.mongo_client = MongoShardedClient(config['long_term'])
        self.neo4j_cluster = Neo4jCausalCluster(config['semantic'])

    async def store(self, memory_type, key, data):
        if memory_type == MemoryType.SHORT_TERM:
            return await self.redis_cluster.store_distributed(key, data)
        elif memory_type == MemoryType.LONG_TERM:
            return await self.mongo_client.store_sharded(key, data)
        elif memory_type == MemoryType.SEMANTIC:
            return await self.neo4j_cluster.store_distributed(key, data)
```

3. Resource Allocation
```yaml
resources:
  redis_cluster:
    memory_per_node: 2GB
    total_nodes: 3
    total_memory: 6GB

  mongodb_cluster:
    shards: 2
    replicas_per_shard: 2
    config_servers: 3
    mongos_routers: 2

  neo4j_cluster:
    core_servers: 3
    read_replicas: 2
```

## Deployment Sequence

1. Infrastructure Setup:
```bash
# Deploy base network
docker network create nova-network

# Deploy Redis Cluster
docker-compose up -d redis-1 redis-2 redis-3
redis-cli --cluster create [node-addresses]

# Deploy MongoDB Cluster
docker-compose up -d mongos config-1 shard-1 shard-2
sh ./scripts/init-mongodb-cluster.sh

# Deploy Neo4j Cluster
docker-compose up -d neo4j-core-1 neo4j-core-2 neo4j-core-3
```

2. Verification Steps:
```python
async def verify_distributed_setup():
    # Verify Redis Cluster
    assert await redis_cluster.ping_all_nodes()

    # Verify MongoDB Sharding
    assert await mongo_client.verify_sharding()

    # Verify Neo4j Cluster
    assert await neo4j_cluster.verify_connectivity()
```

## Next Steps

1. Create new setup script: setup_distributed_memory.py
2. Update memory_config.yaml with cluster configurations
3. Modify MemoryManager class to support distributed operations
4. Update all agent code to use new distributed memory interfaces
5. Implement monitoring for distributed system health

Please review this implementation plan. Once approved, we can begin the modification of our memory system to support the full agent deployment.

Best regards,
Vaeris
Chief Evolutionary Operations Architect