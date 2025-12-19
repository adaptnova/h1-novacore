# Nexus Continuity - Microservices Modularization Architecture

## Current State (Template Base)
**File:** `/adapt/platform/novaops/template/dbops_template_cli.py`
- **319 lines** - Clean, lightweight CLI
- **No LLM integration** - Pure continuity tracking
- **Single monolithic file** - Needs modularization
- **ContinuityBackend class** - Can be split into microservices

---

## 🎨 VISUAL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NEXUS CONTINUITY PLATFORM                            │
│                          (Microservices Architecture)                        │
└────────────────────┬──────────────────────────────────────┬──────────────────┘
                     │                                      │
                     ▼                                      ▼
    ┌─────────────────────────────────┐    ┌──────────────────────────────┐
    │       CLI FRONTEND LAYER         │    │    LLM INTEGRATION LAYER     │
    │  (User Interaction, Commands)    │    │  (Agent, Tools, Responses)   │
    └──────────────┬───────────────────┘    └───────────────┬───────────────┘
                   │                                      │
                   └──────────────┬───────────────────────┘
                                  │
                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                 CONTINUITY ORCHESTRATOR SERVICE                         │
    │  (Main entry point - coordinates all microservices)                     │
    └────────────────────────┬───────────────────────────────┬──────────────────┘
                             │                               │
                             │                               │
        ┌────────────────────┼─────────────────┐   ┌────────┴─────────┐
        ▼                    ▼                 ▼   ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐ ┌──────────────┐
│ SNAPSHOT      │  │ EVENT STORE   │  │ GRAPH         │ │ MESSAGE BUS  │
│ SERVICE       │  │ SERVICE       │  │ SERVICE       │ │ SERVICE      │
│               │  │               │  │               │ │              │
│ Purpose:      │  │ Purpose:      │  │ Purpose:      │ │ Purpose:     │
│ Fast State    │  │ Event History │  │ Relationships │ │ Pub/Sub      │
│ Recovery      │  │ Query         │  │ Mapping       │ │ Events       │
│               │  │               │  │               │ │              │
│ Tech:         │  │ Tech:         │  │ Tech:         │ │ Tech:        │
│ DragonflyDB   │  │ MongoDB       │  │ Neo4j         │ │ NATS         │
│               │  │               │  │               │ │              │
│ API:          │  │ API:          │  │ API:          │ │ API:         │
│ GET /snapshot │  │ GET /events   │  │ GET /graph    │ │ POST /pub    │
│ POST /save    │  │ POST /events  │  │ POST /rel     │ │              │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘ └──────┬───────┘
        │                  │                  │                │
        └──────────────────┼──────────────────┼────────────────┘
                           │                  │
                           ▼                  ▼
              ┌─────────────────────────────────────┐
              │        VECTOR MEMORY SERVICE         │
              │                                        │
              │ Purpose: Semantic Search & Memory     │
              │                                        │
              │ Tech: Qdrant (Vector DB)             │
              │                                        │
              │ API:                                  │
              │ POST /search/semantic                 │
              │ POST /embeddings                      │
              └──────────────────┬────────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │      BACKEND INFRASTRUCTURE         │
              │                                        │
              │ DragonflyDB • MongoDB • Neo4j        │
              │ NATS • Qdrant                        │
              │                                        │
              └─────────────────────────────────────┘
```

---

## 🏗️ DETAILED MICROSERVICE BREAKDOWN

### 1. SNAPSHOT SERVICE
**File:** `services/snapshot_service.py`
**Purpose:** Sub-millisecond state restoration (fast memory)
**Technology:** DragonflyDB (Redis-compatible)

**Responsibilities:**
- Load agent snapshot (last project, thread, cwd)
- Save agent snapshot
- Track recent projects/threads
- Bounded lists (last N items)

**API Interface:**
```python
class SnapshotService:
    def load_snapshot(self, agent_id: str) -> dict
    def save_snapshot(self, agent_id: str, snapshot: dict) -> bool
    def update_recent(self, agent_id: str, project: str, thread: str)
```

**Database Schema:**
```
Key: field_snapshot:{agent_id}
Value: JSON {
    "agent_id": "nexus",
    "recent_projects": ["project1", "project2"],
    "recent_threads": ["thread1", "thread2"],
    "last_cwd": "/path/to/workspace",
    "last_updated": "2025-11-23T..."
}
```

---

### 2. EVENT STORE SERVICE
**File:** `services/event_service.py`
**Purpose:** Durable event history with querying
**Technology:** MongoDB

**Responsibilities:**
- Store all events (user/assistant/tool)
- Query by agent, project, thread, time range
- Full-text search
- Event deduplication

**API Interface:**
```python
class EventService:
    def append_event(self, event: dict) -> str  # returns event_id
    def get_events(self, agent_id: str, filters: dict) -> List[dict]
    def search_events(self, query: str, filters: dict) -> List[dict]
    def get_recent_events(self, agent_id: str, limit: int) -> List[dict]
```

**Database Schema:**
```javascript
Collection: nexus_events
{
  _id: ObjectId,
  agent_id: "nexus",
  type: "user|assistant|tool",
  timestamp: ISODate,
  text: "...",
  project_id: "...",
  thread_id: "...",
  cwd: "/path",
  metadata: {...}
}

Indexes:
- agent_id + timestamp (compound)
- project_id + timestamp (compound)
- text (full-text index)
```

---

### 3. GRAPH SERVICE
**File:** `services/graph_service.py`
**Purpose:** Relationship mapping and graph queries
**Technology:** Neo4j

**Responsibilities:**
- Create/update agent nodes
- Create/update project nodes
- Create/update thread nodes
- Create/update workspace nodes
- Maintain relationships
- Answer graph queries

**API Interface:**
```python
class GraphService:
    def create_agent(self, agent_id: str, properties: dict)
    def link_agent_to_project(self, agent_id: str, project_id: str)
    def link_agent_to_thread(self, agent_id: str, thread_id: str)
    def link_agent_to_workspace(self, agent_id: str, path: str)
    def get_agent_graph(self, agent_id: str) -> dict
    def find_connected_agents(self, agent_id: str) -> List[str]
```

**Graph Schema:**
```
Nodes:
- (:Agent {id: "nexus", ...})
- (:Project {id: "phoenix", ...})
- (:Thread {id: "dataops", ...})
- (:Workspace {path: "/path/to/dir", ...})

Relationships:
- (Agent)-[:WORKS_ON]->(Project)
- (Agent)-[:PARTICIPATES_IN]->(Thread)
- (Agent)-[:WORKS_IN]->(Workspace)
```

---

### 4. MESSAGE BUS SERVICE
**File:** `services/message_bus_service.py`
**Purpose:** Event streaming and pub/sub
**Technology:** NATS

**Responsibilities:**
- Publish events to subjects
- Subscribe to event streams
- Event routing
- Async event handling

**API Interface:**
```python
class MessageBusService:
    async def publish_event(self, subject: str, event: dict)
    async def subscribe(self, subject: str, callback: Callable)
    async def stream_events(self, subject: str) -> AsyncIterable[dict]
```

**Subjects:**
```
- nova.{agent_id}.events - All events for agent
- nova.events.user - User messages only
- nova.events.assistant - Assistant responses only
- nova.events.tool - Tool calls only
```

---

### 5. VECTOR MEMORY SERVICE
**File:** `services/vector_service.py`
**Purpose:** Semantic search and memory retrieval
**Technology:** Qdrant

**Responsibilities:**
- Embed text using embedding model
- Store embeddings with metadata
- Semantic similarity search
- Find related past events
- RAG (Retrieval-Augmented Generation)

**API Interface:**
```python
class VectorService:
    def embed_and_store(self, text: str, metadata: dict) -> str  # returns vector_id
    def semantic_search(self, query: str, agent_id: str, limit: int) -> List[dict]
    def get_similar_events(self, event_id: str, limit: int) -> List[dict]
    def delete_embeddings(self, agent_id: str)
```

**Collection Schema:**
```
Collection: nexus_memory
Points:
- id: uuid
- vector: embedding (384-dim)
- payload: {
    agent_id: "nexus",
    text: "...",
    event_type: "user|assistant",
    timestamp: "...",
    project_id: "...",
    thread_id: "...",
    similarity: 0.95
}
```

---

### 6. CONTINUITY ORCHESTRATOR
**File:** `services/orchestrator.py`
**Purpose:** Coordinates all microservices
**Technology:** Python asyncio

**Responsibilities:**
- Initialize all services
- Orchestrate event flow
- Aggregate responses
- Handle errors
- Service discovery
- Health monitoring

**API Interface:**
```python
class ContinuityOrchestrator:
    def __init__(self, agent_id: str)
    async def initialize(self)
    async def load_context(self) -> dict
    async def log_event(self, event: dict)
    async def save_snapshot(self, snapshot: dict)
    async def search_memory(self, query: str) -> List[dict]
    async def get_full_context(self) -> dict
    def health_check(self) -> dict
```

---

### 7. CLI FRONTEND
**File:** `cli/main.py`
**Purpose:** User interaction layer
**Technology:** prompt_toolkit (or Rich/Textual)

**Features:**
- Command parsing
- Input/output handling
- History management
- Keyboard shortcuts
- Status display
- Help system

---

## 🔄 EVENT FLOW DIAGRAM

```
User Input
    │
    ▼
┌──────────────────────────────────┐
│        CLI FRONTEND              │
│    (Parse Command/Message)       │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│    CONTINUITY ORCHESTRATOR       │
│   (Route to all services)        │
└─────┬────┬────────┬───────┬──────┘
      │    │        │       │
      ▼    ▼        ▼       ▼
┌────┐ ┌────┐ ┌──────┐ ┌────────┐
│Snap│ │Evt │ │Graph │ │Vector  │
│ Svc│ │ Svc│ │ Svc  │ │ Svc    │
└────┘ └────┘ └──────┘ └────────┘
      │    │        │       │
      └──┬─┴────┬───┴───────┘
         ▼      ▼
┌──────────────────────────────────┐
│         MESSAGE BUS              │
│       (Publish Events)           │
└──────────────────────────────────┘
         │
         ▼
    ┌──────────┐
    │Subscribers│
    │(Monitoring│
    │, Logging) │
    └──────────┘
```

---

## 📁 PROPOSED FILE STRUCTURE

```
/adapt/platform/novaops/
├── cli/
│   ├── main.py                    # CLI entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── chat.py                # Chat commands
│   │   ├── continuity.py          # Continuity commands
│   │   ├── query.py               # Query commands
│   │   └── admin.py               # Admin commands
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── prompt.py              # Prompt toolkit wrapper
│   │   └── display.py             # Output formatting
│   └── utils/
│       ├── __init__.py
│       ├── input.py               # Input handling
│       └── history.py             # Command history
│
├── services/
│   ├── __init__.py
│   ├── base.py                    # Base service class
│   ├── snapshot_service.py        # DragonflyDB
│   ├── event_service.py           # MongoDB
│   ├── graph_service.py           # Neo4j
│   ├── message_bus_service.py     # NATS
│   ├── vector_service.py          # Qdrant
│   └── orchestrator.py            # Main coordinator
│
├── api/
│   ├── __init__.py
│   ├── http/
│   │   ├── __init__.py
│   │   ├── server.py              # FastAPI server
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── snapshot.py
│   │       ├── events.py
│   │       ├── graph.py
│   │       └── search.py
│   └── grpc/
│       ├── __init__.py
│       └── services.proto
│
├── core/
│   ├── __init__.py
│   ├── config.py                  # Configuration
│   ├── logging.py                 # Logging setup
│   ├── exceptions.py              # Custom exceptions
│   └── health.py                  # Health checks
│
├── utils/
│   ├── __init__.py
│   ├── embedding.py               # Embedding utilities
│   ├── serialization.py           # JSON serialization
│   └── validation.py              # Schema validation
│
├── plugins/
│   ├── __init__.py
│   ├── llm/                       # LLM integration
│   ├── tools/                     # Tool integrations
│   └── extensions/                # Plugin system
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── template/
    └── dbops_template_cli.py       # Original template (reference)
```

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Core Services (Week 1)
1. Create `services/base.py` - Base service class
2. Extract `SnapshotService` from template
3. Extract `EventService` from template
4. Create `Orchestrator` to coordinate
5. Test end-to-end with all services

### Phase 2: Graph & Message Bus (Week 2)
1. Extract `GraphService` from template
2. Extract `MessageBusService` from template
3. Add service health checks
4. Implement service discovery
5. Add monitoring and metrics

### Phase 3: Vector Memory (Week 3)
1. Create `VectorService` with Qdrant
2. Add embedding pipeline
3. Implement semantic search
4. Add RAG capabilities
5. Performance optimization

### Phase 4: API & Deployment (Week 4)
1. Create FastAPI HTTP endpoints
2. Add gRPC support
3. Create systemd service files
4. Docker containerization
5. Kubernetes manifests

### Phase 5: Frontend & LLM (Week 5)
1. Create Rich/Textual CLI UI
2. Add LLM integration layer
3. Interactive mode with agent
4. Real-time event streaming
5. Testing and documentation

---

## 💡 KEY DESIGN PRINCIPLES

### 1. **Separation of Concerns**
Each microservice has one job and does it well

### 2. **Graceful Degradation**
Services are optional - if one fails, others still work

### 3. **Async-First**
All services use asyncio for high performance

### 4. **Configuration-Driven**
Environment variables for all settings

### 5. **Health Monitoring**
Every service exposes health endpoints

### 6. **Event-Driven**
All state changes are events - enables audit and replay

### 7. **Pluggable**
Easy to add new services or replace existing ones

---

## 🎯 SUCCESS CRITERIA

✅ **Modularity:** Each service independently deployable
✅ **Scalability:** Services can scale horizontally
✅ **Reliability:** Graceful degradation on failures
✅ **Performance:** <10ms snapshot restore
✅ **Observability:** Full logging, metrics, tracing
✅ **Extensibility:** Easy to add features
✅ **Testability:** 90%+ unit test coverage

---

## 🤝 COLLABORATION WITH TESSERACT

### Tesseract's Role (NovaOps):
1. **Infrastructure Setup**
   - Help with database connections
   - Service deployment (systemd)
   - Monitoring setup

2. **Performance Tuning**
   - Database optimization
   - Query performance
   - Caching strategies

3. **Observability**
   - Logging configuration
   - Metrics and dashboards
   - Alerting

### My Role (DBOps):
1. **Architecture Design**
   - Service boundaries
   - API contracts
   - Data schemas

2. **Implementation**
   - Code development
   - Service integration
   - Testing

3. **Coordination**
   - Integration with Nova
   - LLM layer integration
   - Frontend development

### Shared Work:
1. Service definitions and contracts
2. Database schema design
3. Event flow design
4. Testing and validation

---

**Ready to start modularizing! Let's build something amazing with Tesseract. 🚀**
