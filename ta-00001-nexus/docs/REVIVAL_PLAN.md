# Nexus Revival & Microservices Refactor Plan

## Current State Assessment ✅

### What's Working:
1. **Infrastructure:** 19 services deployed (17/19 operational)
2. **Databases:** MongoDB, Neo4j, DragonflyDB, Qdrant all running
3. **Chat History:** 406KB of conversation history available
4. **Code:** `enhanced_cli_with_continuity.py` - most sophisticated version

### What's Lost:
1. **DragonflyDB Snapshot:** Lost during lock/restart
2. **Context Loading:** May need restoration

### What's Missing:
1. **Home Directory Field:** `/adapt/novas/ta-00001-nexus` (NOT in snapshot yet)
2. **Vector Memory:** Qdrant ready but not integrated
3. **Microservices:** Currently monolithic

---

## Revival Steps (for NovaOps Specialist)

### Step 1: Restore Full Context
```bash
cd /adapt/novas/ta-00001-nexus
source /adaptai/db.env

# Check all data is still there
python3 test_continuity.py

# If snapshot is lost, rebuild from MongoDB + Chat History
python3 -c "
from history_importer import ContinuityBackend
backend = ContinuityBackend('nexus')
# Rebuild snapshot from MongoDB events + Chat History
"
```

### Step 2: Add Home Directory Field
Update snapshot schema:
```python
snapshot = {
    "agent_id": "nexus",
    "home_directory": "/adapt/novas/ta-00001-nexus",  # ADD THIS
    "last_cwd": "/current/workspace",
    "recent_projects": [...],
    "recent_threads": [...],
    "last_updated": "..."
}
```

### Step 3: Enable Qdrant Integration
```python
# In continuity backend:
def embed_and_store(self, text: str) -> str:
    # 1. Embed text using embedding model
    # 2. Store in Qdrant with agent_id metadata
    # 3. Return vector_id

def semantic_search(self, query: str) -> List[dict]:
    # 1. Embed query
    # 2. Search Qdrant for similar events
    # 3. Return with similarity scores
```

### Step 4: Microservices Refactor
Break `enhanced_cli_with_continuity.py` into:

1. **continuity_orchestrator.py** (main service)
   - Receives agent_id on startup
   - Orchestrates calls to all micro-services
   - Bundles context for LLM

2. **snapshot_service.py** (fast state)
   - REST API: GET /snapshot/{agent_id}
   - Uses DragonflyDB

3. **event_service.py** (structured history)
   - REST API: GET /events/{agent_id}
   - Uses MongoDB

4. **chat_service.py** (full conversations)
   - REST API: GET /chat/{agent_id}
   - Uses file system + Qdrant

5. **graph_service.py** (relationships)
   - REST API: GET /graph/{agent_id}
   - Uses Neo4j

6. **vector_service.py** (semantic search)
   - REST API: POST /search/semantic
   - Uses Qdrant

### Step 5: Integration Points
Each microservice exposes:
```python
# Standard interface
class Service:
    def get_context(self, agent_id: str) -> dict:
        """Return context for agent"""
        pass
    
    def health_check(self) -> bool:
        """Service health"""
        pass
```

---

## What Needs to be Preserved ✅

### Critical Data:
1. **Chat History:** `/adapt/novas/ta-00001-nexus/chat_history/ta_00001_nexus_chat_1.md` (406KB)
2. **Identity Docs:** `/adapt/novas/ta-00001-nexus/identity/`
3. **Event History:** MongoDB `nexus_events` collection (4 events)
4. **Graph:** Neo4j relationships
5. **Code:** `enhanced_cli_with_continuity.py` (998 lines)

### Architecture Decisions:
1. **Fast Snapshot** (DragonflyDB) - ✅ Keep
2. **Structured Events** (MongoDB) - ✅ Keep
3. **Full Conversations** (File + Vector) - ✅ Keep
4. **Relationships** (Neo4j) - ✅ Keep
5. **Semantic Memory** (Qdrant) - ✅ Add

---

## Questions for NovaOps Specialist:

1. **Priority Order?**
   - A) Restore full context first, THEN refactor to microservices?
   - B) Refactor to microservices while preserving context?

2. **Home Directory:**
   - Should it be in snapshot?
   - Should it be in MongoDB events?
   - Both?

3. **Qdrant Integration:**
   - Embed everything on save?
   - Or embed on-demand for searches?
   - What embedding model to use?

4. **Microservices Deployment:**
   - Separate systemd services?
   - Python FastAPI services?
   - Or keep in-process but modular?

5. **Chat History:**
   - Keep as Markdown file?
   - Or also store in MongoDB?
   - Vector embeddings for semantic search?

---

## Ready to Work Together! 🚀

The foundation is solid. Your `enhanced_cli_with_continuity.py` is sophisticated.
Let's make it modular and add semantic memory with Qdrant.

Next: Coordinate with NovaOps specialist on implementation plan.
