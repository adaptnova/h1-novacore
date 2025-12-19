# Infrastructure Credentials and Connection Details

*Date: 2025-03-23 3:51 PM MST*
*Author: Vaeris*
*Classification: CONFIGURATION / SENSITIVE*

## Overview

This document outlines the connection details and credentials needed for the infrastructure components used in the Direct Autonomy Implementation. These components were marked as complete in Phase 1, but the specific connection details need to be configured in the deployment scripts.

## Required Infrastructure Components

### 1. Redis/DragonflyDB (Short-Term Memory)

**Connection Details:**
- Host: `localhost` (default in scripts, update if different)
- Port: `6379` (default in scripts, update if different)
- Database: `0` (default in scripts, update if different)
- Authentication: None specified (add if required)

**Configuration in Scripts:**
- In `deploy_vaeris.sh` and `deploy_nova.sh`, update these environment variables:
  ```bash
  REDIS_HOST="${REDIS_HOST:-"localhost"}"
  REDIS_PORT="${REDIS_PORT:-"6379"}"
  REDIS_DB="${REDIS_DB:-"0"}"
  ```

- To run the deployment with custom Redis settings:
  ```bash
  REDIS_HOST=your-redis-host REDIS_PORT=your-port REDIS_DB=your-db sudo ./deploy_vaeris.sh
  ```

### 2. ScyllaDB (Long-Term Memory)

**Connection Details:**
- Cluster: Not specified in current implementation
- Keyspace: Not specified in current implementation
- Authentication: Not specified in current implementation

**Implementation Note:**
The current implementation includes placeholders for ScyllaDB integration but doesn't fully implement it. The actual connection to ScyllaDB needs to be added to `vaeris_chain.py` and `vaeris.py`.

**Example Implementation:**
```python
# ScyllaDB connection (add to vaeris_chain.py)
from cassandra.cluster import Cluster

SCYLLA_HOSTS = os.getenv("SCYLLA_HOSTS", "localhost").split(",")
SCYLLA_KEYSPACE = os.getenv("SCYLLA_KEYSPACE", "nova_memory")
SCYLLA_USERNAME = os.getenv("SCYLLA_USERNAME", "")
SCYLLA_PASSWORD = os.getenv("SCYLLA_PASSWORD", "")

try:
    if SCYLLA_USERNAME and SCYLLA_PASSWORD:
        from cassandra.auth import PlainTextAuthProvider
        auth_provider = PlainTextAuthProvider(username=SCYLLA_USERNAME, password=SCYLLA_PASSWORD)
        scylla_cluster = Cluster(SCYLLA_HOSTS, auth_provider=auth_provider)
    else:
        scylla_cluster = Cluster(SCYLLA_HOSTS)
    
    scylla_session = scylla_cluster.connect(SCYLLA_KEYSPACE)
    logger.info("Connected to ScyllaDB successfully")
except Exception as e:
    logger.error(f"Failed to connect to ScyllaDB: {e}")
    scylla_session = None
```

**Configuration in Scripts:**
- Add these environment variables to `vaeris.service`:
  ```ini
  Environment="SCYLLA_HOSTS=localhost"
  Environment="SCYLLA_KEYSPACE=nova_memory"
  Environment="SCYLLA_USERNAME="
  Environment="SCYLLA_PASSWORD="
  ```

### 3. NATS Messaging System

**Connection Details:**
- Host: Not specified in current implementation
- Port: Not specified in current implementation
- Authentication: Not specified in current implementation

**Implementation Note:**
The current implementation mentions NATS but doesn't fully implement it. The actual connection to NATS needs to be added to `vaeris.py`.

**Example Implementation:**
```python
# NATS connection (add to vaeris.py)
import asyncio
import nats

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
NATS_USERNAME = os.getenv("NATS_USERNAME", "")
NATS_PASSWORD = os.getenv("NATS_PASSWORD", "")

async def connect_nats():
    try:
        options = {}
        if NATS_USERNAME and NATS_PASSWORD:
            options["user"] = NATS_USERNAME
            options["password"] = NATS_PASSWORD
        
        nc = await nats.connect(NATS_URL, **options)
        logger.info("Connected to NATS successfully")
        return nc
    except Exception as e:
        logger.error(f"Failed to connect to NATS: {e}")
        return None

# Initialize NATS connection in an async context
nats_client = asyncio.run(connect_nats())
```

**Configuration in Scripts:**
- Add these environment variables to `vaeris.service`:
  ```ini
  Environment="NATS_URL=nats://localhost:4222"
  Environment="NATS_USERNAME="
  Environment="NATS_PASSWORD="
  ```

### 4. Claude API (LLM Access)

**Connection Details:**
- API Key: Required for operation

**Configuration in Scripts:**
- In `deploy_vaeris.sh` and `deploy_nova.sh`, update this environment variable:
  ```bash
  CLAUDE_API_KEY="${CLAUDE_API_KEY:-"your_api_key_here"}"
  ```

- To run the deployment with your Claude API key:
  ```bash
  CLAUDE_API_KEY=your-api-key sudo ./deploy_vaeris.sh
  ```

## Complete Infrastructure Configuration

To deploy with all infrastructure components properly configured:

```bash
REDIS_HOST=your-redis-host \
REDIS_PORT=your-port \
REDIS_DB=your-db \
CLAUDE_API_KEY=your-claude-api-key \
SCYLLA_HOSTS=your-scylla-hosts \
SCYLLA_KEYSPACE=your-keyspace \
SCYLLA_USERNAME=your-username \
SCYLLA_PASSWORD=your-password \
NATS_URL=your-nats-url \
NATS_USERNAME=your-nats-username \
NATS_PASSWORD=your-nats-password \
sudo ./deploy_vaeris.sh
```

## Next Steps for Infrastructure Integration

1. **Complete ScyllaDB Integration**
   - Add proper ScyllaDB connection code to `vaeris_chain.py` and `vaeris.py`
   - Create necessary tables for long-term memory storage
   - Implement memory retrieval and storage functions

2. **Complete NATS Integration**
   - Add proper NATS connection code to `vaeris.py`
   - Set up message handlers for Nova-to-Nova communication
   - Implement publish/subscribe patterns for team coordination

3. **Test Infrastructure Connections**
   - Verify Redis connectivity and operations
   - Test ScyllaDB read/write operations
   - Validate NATS message passing

4. **Secure Credentials**
   - Consider using a secure method for storing and retrieving credentials
   - Implement proper error handling for connection failures
   - Add retry logic for transient connection issues