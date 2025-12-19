# Personal Nova Script - Architecture Visual Documentation

**Version:** 1.0
**Date:** November 23, 2025
**Author:** CHRONOS (ta_00005_chronos)
**Project:** Phoenix Personal AI Initiative

---

## 🎯 ARCHITECTURE OVERVIEW

### **Complete System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHOENIX PERSONAL NOVA ECOSYSTEM                         │
│                     (Team Member → Personal AI Agent)                      │
└────────────────────┬──────────────────────────────────────┬──────────────────┘
                     │                                      │
                     ▼                                      ▼
    ┌───────────────────────────────┐        ┌───────────────────────────────┐
    │      HUMAN TEAM MEMBER        │        │   PHOENIX PLATFORM           │
    │   (Chase, Greta, etc.)       │        │   (Infrastructure)           │
    └──────────────┬────────────────┘        └──────────────┬────────────────┘
                   │                                      │
                   │ Interacts with                      │
                   │ Personal Nova                      │
                   │                                     │
                   ▼                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    PERSONAL NOVA AGENT                                  │
    │  (ta_0000X_[name] - Individual AI for each team member)               │
    │                                                                         │
    │  ┌─────────────────────────────────────────────────────────────┐       │
    │  │  IDENTITY LAYER  (MD + JSON + YAML)                       │       │
    │  │  • Personal UUID, name, role                              │       │
    │  │  • Identity document, memory, preferences                  │       │
    │  └──────────────────┬────────────────────────────────────────┘       │
    │                     │                                                    │
    │  ┌──────────────────▼────────────────────────────────────────┐       │
    │  │  CONTINUITY LAYER (Persistent Memory)                   │       │
    │  │  • Snapshot Service (DragonflyDB)                       │       │
    │  │  • Event Store (MongoDB)                                │       │
    │  │  • Graph Service (Neo4j)                                │       │
    │  │  • Message Bus (NATS)                                   │       │
    │  │  • Vector Memory (Qdrant)                               │       │
    │  └──────────────────┬────────────────────────────────────────┘       │
    │                     │                                                    │
    │  ┌──────────────────▼────────────────────────────────────────┐       │
    │  │  INTELLIGENCE LAYER (Cognitive Systems)                │       │
    │  │  • SignalCore Integration                               │       │
    │  │  • Learning & Adaptation                                │       │
    │  │  • Pattern Recognition                                  │       │
    │  │  • Personal Preferences                                 │       │
    │  └──────────────────┬────────────────────────────────────────┘       │
    │                     │                                                    │
    │  ┌──────────────────▼────────────────────────────────────────┐       │
    │  │  COMMUNICATION LAYER (Team Interaction)                 │       │
    │  │  • Team Messaging (NATS)                               │       │
    │  │  • Event Publishing                                    │       │
    │  │  • Notification System                                 │       │
    │  └──────────────────┬────────────────────────────────────────┘       │
    │                     │                                                    │
    └─────────────────────┼────────────────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    MICROSERVICES ARCHITECTURE                         │
    │                                                                         │
    │  ┌──────────────┬──────────────┬──────────────┬──────────────┐         │
    │  │ SNAPSHOT     │  EVENT STORE│   GRAPH      │ MESSAGE BUS │         │
    │  │  SERVICE     │   SERVICE   │   SERVICE    │   SERVICE   │         │
    │  │              │              │              │              │         │
    │  │ DragonflyDB  │   MongoDB   │    Neo4j     │     NATS    │         │
    │  │              │              │              │              │         │
    │  │ • Fast State │ • Events    │ • Relationships│ • Pub/Sub   │         │
    │  │ • <10ms      │ • History   │ • Graph DB   │ • Streaming │         │
    │  │ • Bounded    │ • Indexes   │ • Cypher     │ • Real-time │         │
    │  └──────┬───────┴──────┬───────┴──────┬───────┴──────┬──────┘         │
    │         │               │               │               │                │
    │         └───────────────┼───────────────┼───────────────┘                │
    │                         │               │                                │
    │                         ▼               ▼                                │
    │                ┌──────────────────────────────┐                          │
    │                │     VECTOR MEMORY SERVICE   │                          │
    │                │                              │                          │
    │                │        Qdrant                │                          │
    │                │                              │                          │
    │                │ • Semantic Search            │                          │
    │                │ • Embeddings                 │                          │
    │                │ • Similarity Matching       │                          │
    │                │ • RAG Ready                 │                          │
    │                └──────────────┬───────────────┘                          │
    │                             │                                          │
    └─────────────────────────────┼──────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────────┐
                    │   ORCHESTRATION LAYER        │
                    │                              │
                    │ • Service Discovery           │
                    │ • Health Monitoring          │
                    │ • Recovery Automation        │
                    │ • Load Balancing             │
                    │ • Event Coordination         │
                    └──────────────┬───────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────────┐
                    │    TEAM INTEGRATION          │
                    │                              │
                    │ • Cross-Nova Communication    │
                    │ • Shared Resources           │
                    │ • Collaborative Learning     │
                    │ • Knowledge Sharing          │
                    └──────────────────────────────┘
```

---

## 🗂️ FILE STRUCTURE & LOCATIONS

### **Complete Directory Hierarchy**

```
/adapt/
├── projects/
│   ├── phoenix/                          ← Phoenix Project Root
│   │   ├── team_comms/                   ← Team Communications
│   │   │   ├── 251123_0620_root_orchestration_intro.md
│   │   │   ├── 251123_0645_chronos_orchestration_response.md
│   │   │   └── [team_communications...]
│   │   │
│   │   └── architecture/                 ← Architecture Documentation
│   │       ├── PERSONAL_NOVA_ARCHITECTURE.md     ← This file
│   │       ├── MICROSERVICES_DESIGN.md
│   │       ├── RECOVERY_SYSTEM.md
│   │       └── API_SPECIFICATIONS.md
│   │
│   └── easter/                           ← Easter Project Root
│       ├── team_comms/
│       ├── scripts/
│       │   ├── build_mvp.sh             ← MVP Build Automation
│       │   ├── update_status.sh         ← Status Monitoring
│       │   └── suggest_names.sh         ← Nova Naming
│       └── docs/
│
├── novas/                                ← Nova Agents Directory
│   ├── ta_00001-nexus/                  ← Nexus Agent
│   │   ├── identity/
│   │   │   ├── nexus_identity.md
│   │   │   ├── nexus_identity.json
│   │   │   └── nexus_identity.yaml
│   │   ├── memory/
│   │   ├── chat_history/
│   │   └── [agent_data...]
│   │
│   ├── ta_00002_root/                   ← Root Agent
│   │   ├── identity/
│   │   ├── memory/
│   │   └── [agent_data...]
│   │
│   ├── ta_00003_tesseract/              ← Tesseract Agent
│   │   ├── identity/
│   │   ├── memory/
│   │   └── [agent_data...]
│   │
│   └── ta_00005_chronos/                ← CHRONOS Agent (ME)
│       ├── identity/
│       │   ├── chronos_identity.md      ← Identity Doc
│       │   ├── chronos_identity.json   ← Identity (JSON)
│       │   └── chronos_identity.yaml   ← Identity (YAML)
│       ├── memory/
│       │   └── [personal_memory...]
│       ├── chat_history/
│       └── [conversation_logs...]
│
├── platform/                             ← Infrastructure Platform
│   ├── novaops/                         ← Nova Operations
│   │   ├── cli/
│   │   │   └── main.py                 ← Official Base + Continuity
│   │   │
│   │   ├── continuity/                  ← Continuity Layer
│   │   │   └── backend.py              ← ContinuityBackend
│   │   │
│   │   ├── services/                    ← Microservices
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 ← Service Base Class
│   │   │   ├── snapshot_service.py     ← DragonflyDB
│   │   │   ├── event_service.py        ← MongoDB
│   │   │   ├── graph_service.py        ← Neo4j
│   │   │   ├── message_bus_service.py  ← NATS
│   │   │   ├── vector_service.py       ← Qdrant
│   │   │   └── orchestrator.py         ← Coordination
│   │   │
│   │   ├── templates/                   ← Base Templates
│   │   │   └── template_base_cli-v.0.0.1.py
│   │   │
│   │   └── scripts/                     ← Automation Scripts
│   │
│   └── dataops/                         ← Data Operations
│       ├── db.env                       ← Database Configuration
│       ├── dbops/
│       │   ├── database-health-check.sh
│       │   ├── prisma/
│       │   └── [db_operations...]
│       │
│       └── [database_infrastructure...]
│
├── templates/                            ← Onboarding Templates
│   ├── personal_nova_template/          ← Personal Nova Template
│   │   ├── identity/
│   │   │   ├── [template_identity.md]
│   │   │   ├── [template_identity.json]
│   │   │   └── [template_identity.yaml]
│   │   │
│   │   ├── continuity/
│   │   │   ├── snapshot_config.yaml
│   │   │   ├── event_config.yaml
│   │   │   ├── graph_config.yaml
│   │   │   └── message_bus_config.yaml
│   │   │
│   │   ├── intelligence/
│   │   │   ├── signalcore_integration.md
│   │   │   └── learning_config.yaml
│   │   │
│   │   └── communication/
│   │       ├── team_messaging.md
│   │       └── notification_config.yaml
│   │
│   └── microservices_template/          ← Microservices Template
│       ├── service_base.py
│       ├── api_contracts.yaml
│       ├── health_checks.py
│       └── deployment_config.yaml
│
└── automation/                          ← Automation Framework
    ├── recovery_system/                ← Recovery Automation
    │   ├── health_monitor.py
    │   ├── failover_trigger.py
    │   ├── state_restorer.py
    │   ├── event_replayer.py
    │   └── notification_sender.py
    │
    ├── onboarding/                     ← Onboarding Automation
    │   ├── nova_generator.py
    │   ├── database_provisioner.py
    │   ├── identity_creator.py
    │   ├── team_integrator.py
    │   └── memory_initializer.py
    │
    └── monitoring/                     ← Monitoring & Observability
        ├── service_health.py
        ├── performance_metrics.py
        ├── alerting_system.py
        └── dashboard_config.yaml
```

---

## 🔄 DATA FLOW DIAGRAMS

### **Recovery Flow (100% Automated)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      RECOVERY TRIGGER                                  │
│  (Service Restart, DB Failover, Network Issue, etc.)                 │
└────────────────────┬──────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    HEALTH MONITORING                                   │
│  • Check all service dependencies                                     │
│  • Identify failed components                                         │
│  • Determine recovery strategy                                        │
│  • Trigger automated recovery                                         │
└────────────────────┬──────────────────────────────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────────────────────────┐
    │              SNAPSHOT SERVICE (DragonflyDB)                 │
    │  • Load last known state: <10ms                            │
    │  • Restore: project, thread, cwd, recent history           │
    │  • Update: timestamp, active context                       │
    │  • Status: READY                                          │
    └────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────────────────┐
    │              EVENT STORE (MongoDB)                         │
    │  • Restore complete event history: <100ms                 │
    │  • Rebuild: user interactions, decisions, actions         │
    │  • Reconstruct: timeline, context, memory                 │
    │  • Status: CONSISTENT                                     │
    └────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────────────────┐
    │              GRAPH SERVICE (Neo4j)                         │
    │  • Rebuild relationships: <200ms                           │
    │  • Reconstruct: team connections, project links           │
    │  • Restore: collaboration history, knowledge graph        │
    │  • Status: CONNECTED                                      │
    └────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────────────────┐
    │              MESSAGE BUS (NATS)                            │
    │  • Reconnect event streams: <50ms                         │
    │  • Resume: pub/sub, notifications                         │
    │  • Sync: team communications, event logging               │
    │  • Status: ACTIVE                                        │
    └────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────────────────┐
    │              VECTOR MEMORY (Qdrant)                        │
    │  • Load embeddings: <100ms                                 │
    │  • Restore: semantic memory, similarity search            │
    │  • Resume: intelligent recommendations, context           │
    │  • Status: INTELLIGENT                                    │
    └────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    RECOVERY COMPLETE                                  │
│  Total Time: <460ms                                                  │
│  Data Loss: 0%                                                       │
│  Manual Intervention: None                                            │
│  Status: FULLY OPERATIONAL                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### **Personal Nova Interaction Flow**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HUMAN TEAM MEMBER                                  │
│                         │                                             │
│                         │ Interacts with                             │
│                         │ Personal Nova                              │
│                         │                                             │
│                         ▼                                             │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              USER INPUT / INTERACTION                        │   │
│  │  • Task request                                             │   │
│  │  • Question                                                │   │
│  │  • Collaboration                                           │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              IDENTITY LAYER                                  │   │
│  │  • Load: personal UUID, role, preferences                   │   │
│  │  • Context: team member, project, thread                    │   │
│  │  • Apply: personalized settings                             │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              CONTINUITY LAYER                                │   │
│  │                                                              │   │
│  │  1. SNAPSHOT (DragonflyDB)                                   │   │
│  │     • Save: current state, working context                  │   │
│  │     • Fast: <10ms                                           │   │
│  │                                                              │   │
│  │  2. EVENT STORE (MongoDB)                                    │   │
│  │     • Log: user input, timestamp, metadata                  │   │
│  │     • Index: for fast retrieval                             │   │
│  │                                                              │   │
│  │  3. GRAPH (Neo4j)                                           │   │
│  │     • Create: relationships, connections                     │   │
│  │     • Update: team collaboration graph                      │   │
│  │                                                              │   │
│  │  4. MESSAGE BUS (NATS)                                      │   │
│  │     • Publish: event to team                                │   │
│  │     • Notify: relevant team members                         │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              INTELLIGENCE LAYER                              │   │
│  │                                                              │   │
│  │  • SignalCore: Process input, generate response              │   │
│  │  • Learning: Update based on interaction                     │   │
│  │  • Adaptation: Improve for personal preferences              │   │
│  │  • Memory: Store semantic embeddings in Qdrant               │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              RESPONSE GENERATION                             │   │
│  │  • Output: response to team member                          │   │
│  │  • Delivery: through appropriate channel                    │   │
│  │  • Logging: assistant response to databases                 │   │
│  │  • Update: snapshot, events, graph                         │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              TEAM INTEGRATION                                │   │
│  │                                                              │   │
│  │  • Notify: team of relevant events                          │   │
│  │  • Share: knowledge with other Novas                        │   │
│  │  • Collaborate: on multi-agent tasks                        │   │
│  │  • Learn: from team interactions                            │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│              ┌─────────────────────────────┐                      │
│              │  TEAM MEMBERS / OTHER      │                      │
│              │  NOVAS RESPOND             │                      │
│              └─────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### **Onboarding Flow (Automated)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  NEW TEAM MEMBER JOINS                                │
│                         │                                             │
│                         ▼                                             │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              ONBOARDING REQUEST                               │   │
│  │  • Human initiates onboarding                               │   │
│  │  • Automation script triggered                              │   │
│  │  • Template system activated                                │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              NOVA GENERATOR                                  │   │
│  │                                                              │   │
│  │  1. Create: Personal UUID (ta_0000X_[name])                 │   │
│  │  2. Generate: Identity documents (MD, JSON, YAML)            │   │
│  │  3. Initialize: Personal preferences                         │   │
│  │  4. Setup: Directory structure                               │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              DATABASE PROVISIONING                            │   │
│  │                                                              │   │
│  │  1. Create: Snapshot storage (DragonflyDB)                   │   │
│  │  2. Provision: Event collection (MongoDB)                     │   │
│  │  3. Setup: Graph namespace (Neo4j)                           │   │
│  │  4. Allocate: Vector collection (Qdrant)                     │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              IDENTITY CREATION                                │   │
│  │                                                              │   │
│  │  • Generate: personal Nova script                             │   │
│  │  • Customize: based on role/preferences                       │   │
│  │  • Create: communication protocols                           │   │
│  │  • Initialize: memory systems                                │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              TEAM INTEGRATION                                 │   │
│  │                                                              │   │
│  │  1. Register: with team communication channels               │   │
│  │  2. Connect: to other Novas                                  │   │
│  │  3. Setup: knowledge sharing protocols                       │   │
│  │  4. Enable: learning and adaptation                          │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              MEMORY INITIALIZATION                            │   │
│  │                                                              │   │
│  │  1. Load: team knowledge base                                │   │
│  │  2. Seed: project history                                    │   │
│  │  3. Initialize: communication patterns                       │   │
│  │  4. Setup: personal learning preferences                     │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              ACTIVATION & TESTING                             │   │
│  │                                                              │   │
│  │  1. Start: personal Nova agent                              │   │
│  │  2. Test: recovery system                                   │   │
│  │  3. Verify: team communication                              │   │
│  │  4. Confirm: intelligence layer                             │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│                        ▼                                            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              ONBOARDING COMPLETE                              │   │
│  │                                                              │   │
│  │  Time: <2 hours                                              │   │
│  │  Status: Fully operational personal Nova                      │   │
│  │  Ready: For production work                                  │   │
│  └───────────────────────────────────────────────────────────────┘   │
```

---

## 🏗️ MICROSERVICES ARCHITECTURE

### **Independent Service Architecture**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SERVICE ORCHESTRATION                             │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                     API GATEWAY                                 │ │
│  │                                                                 │ │
│  │  • Request routing                                             │ │
│  │  • Load balancing                                             │ │
│  │  • Authentication                                             │ │
│  │  • Rate limiting                                              │ │
│  └─────────────────────────────────────┬───────────────────────────┘ │
│                                          │                           │
│                                          ▼                           │
│  ┌─────────────────────────────────────┴───────────────────────────┐ │
│  │              SERVICE DISCOVERY                                 │ │
│  │                                                              │ │
│  │  • Health monitoring                                         │ │
│  │  • Service registration                                      │ │
│  │  • Dependency mapping                                        │ │
│  │  • Auto-scaling triggers                                     │ │
│  └─────────────────────────────────────┬───────────────────────────┘ │
│                                          │                           │
└──────────────────────────────────────────┼───────────────────────────┘
                                           │
                                           ▼
    ┌──────────────┬──────────────┬──────────────┬──────────────┐
    │ SNAPSHOT    │  EVENT      │   GRAPH      │ MESSAGE     │
    │ SERVICE     │  STORE      │   SERVICE    │ BUS         │
    │             │  SERVICE    │              │ SERVICE     │
    │             │              │              │             │
    │ DragonflyDB │   MongoDB   │    Neo4j     │   NATS      │
    │             │              │              │             │
    │ ┌────────┐ │ ┌──────────┐ │ ┌─────────┐ │ ┌────────┐ │
    │ │ Health │ │ │  Health │ │ │  Health │ │ │ Health │ │
    │ │ Monitor│ │ │  Monitor│ │ │  Monitor│ │ │ Monitor│ │
    │ └────────┘ │ └──────────┘ │ └─────────┘ │ └────────┘ │
    │             │              │              │             │
    │ ┌────────┐ │ ┌──────────┐ │ ┌─────────┐ │ ┌────────┐ │
    │ │ Recovery│ │ │ Recovery│ │ │ Recovery│ │ │ Recovery│ │
    │ │ System │ │ │ System │ │ │ System │ │ │ System │ │
    │ └────────┘ │ └──────────┘ │ └─────────┘ │ └────────┘ │
    │             │              │              │             │
    │ ┌────────┐ │ ┌──────────┐ │ ┌─────────┐ │ ┌────────┐ │
    │ │ Auto   │ │ │ Auto     │ │ │ Auto    │ │ │ Auto   │ │
    │ │ Scaling│ │ │ Scaling  │ │ │ Scaling │ │ │ Scaling│ │
    │ └────────┘ │ └──────────┘ │ └─────────┘ │ └────────┘ │
    └──────┬─────┴──────┬──────┴──────┬─────┴──────┬────┘
           │              │              │             │
           └──────────────┼──────────────┼─────────────┘
                          │              │
                          ▼              ▼
                 ┌─────────────────────────────┐
                 │     VECTOR MEMORY         │
                 │       SERVICE             │
                 │                           │
                 │        Qdrant            │
                 │                           │
                 │ ┌─────────────────────┐   │
                 │ │ Health Monitor     │   │
                 │ └─────────────────────┘   │
                 │                           │
                 │ ┌─────────────────────┐   │
                 │ │ Recovery System    │   │
                 │ └─────────────────────┘   │
                 │                           │
                 │ ┌─────────────────────┐   │
                 │ │ Auto Scaling       │   │
                 │ └─────────────────────┘   │
                 └───────────┬─────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │   MONITORING &      │
                    │   OBSERVABILITY     │
                    │                     │
                    │ • Prometheus        │
                    │ • Grafana           │
                    │ • Alert Manager     │
                    │ • Distributed      │
                    │   Tracing           │
                    └─────────────────────┘
```

---

## 💾 DATABASE INTEGRATION

### **Multi-Layer Database Architecture**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE ECOSYSTEM                                │
│                                                                         │
│  ┌─────────────────────┬─────────────────────┬─────────────────────┐      │
│  │   LAYER 1: FAST    │  LAYER 2: DEEP     │  LAYER 3: RELATE   │      │
│  │   (Millisecond)    │   (Milliseconds)   │  (Milliseconds)   │      │
│  │                    │                    │                   │      │
│  │  DragonflyDB       │    MongoDB        │    Neo4j         │      │
│  │                    │                    │                   │      │
│  │  • Snapshot       │    • Events        │   • Relationships │      │
│  │  • Fast State     │    • History       │   • Graph DB     │      │
│  │  • <10ms          │    • Indexed       │   • Cypher       │      │
│  │  • Bounded List   │    • Queryable     │   • Traversals   │      │
│  │  • Current       │    • Full Text     │   • Patterns     │      │
│  │  • Working       │    • Analytics     │   • Connections  │      │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬───────┘      │
│           │                    │                    │               │
│           └────────────────────┼────────────────────┘               │
│                                │                                    │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │           LAYER 4: INTELLIGENCE (Vector)                     │ │
│  │                                                             │ │
│  │  Qdrant                                                     │ │
│  │                                                             │ │
│  │  • Semantic Search      • Similarity Matching                │ │
│  │  • Embeddings          • RAG Ready                         │ │
│  │  • AI Memory          • Intelligent Retrieval               │ │
│  └─────────────────────────┬───────────────────────────────────┘ │
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │           LAYER 5: MESSAGING (Stream)                        │ │
│  │                                                             │ │
│  │  NATS                                                       │ │
│  │                                                             │ │
│  │  • Pub/Sub              • Event Streaming                   │ │
│  │  • Real-time            • Team Coordination                 │ │
│  │  • Notifications       • Message Bus                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATION & COORDINATION              │   │
│  │                                                             │   │
│  │  • Cross-database transactions                              │   │
│  │  • Event coordination                                     │   │
│  │  • Consistency management                                  │   │
│  │  • Recovery automation                                    │   │
│  └───────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 SERVICE CONTRACTS

### **API Specifications**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SERVICE API CONTRACTS                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                     SNAPSHOT SERVICE                            │ │
│  │                                                                 │ │
│  │  GET    /snapshot/{agent_id}        → Load state               │ │
│  │  POST   /snapshot/{agent_id}        → Save state               │ │
│  │  DELETE /snapshot/{agent_id}        → Clear state              │ │
│  │                                                                 │ │
│  │  Response: {                                               │ │
│  │    "agent_id": "ta_00005_chronos",                         │ │
│  │    "last_cwd": "/path/to/work",                           │ │
│  │    "recent_projects": ["phoenix", "easter"],               │ │
│  │    "recent_threads": ["continuity"],                        │ │
│  │    "last_updated": "2025-11-23T07:00:00Z"                 │ │
│  │  }                                                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                     EVENT STORE SERVICE                        │ │
│  │                                                                 │ │
│  │  POST   /events                      → Create event           │ │
│  │  GET    /events?agent_id={id}       → List events            │ │
│  │  GET    /events/{event_id}           → Get single event       │ │
│  │  GET    /events/search?q={query}    → Full-text search      │ │
│  │                                                                 │ │
│  │  Event: {                                                   │ │
│  │    "agent_id": "ta_00005_chronos",                         │ │
│  │    "type": "user|assistant",                                │ │
│  │    "timestamp": "2025-11-23T07:00:00Z",                    │ │
│  │    "text": "...",                                           │ │
│  │    "project_id": "phoenix",                                │ │
│  │    "thread_id": "architecture",                             │ │
│  │    "cwd": "/adapt/projects/phoenix"                         │ │
│  │  }                                                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                       GRAPH SERVICE                            │ │
│  │                                                                 │ │
│  │  POST   /graph/node                 → Create node             │ │
│  │  POST   /graph/relationship        → Create relationship    │ │
│  │  GET    /graph/{agent_id}          → Get agent graph       │ │
│  │  GET    /graph/search?q={query}    → Search relationships  │ │
│  │                                                                 │ │
│  │  Node: {                                                    │ │
│  │    "type": "Agent|Project|Thread|Workspace",               │ │
│  │    "id": "nexus|phoenix|architecture|/path",               │ │
│  │    "properties": {...}                                     │ │
│  │  }                                                         │ │
│  │                                                             │ │
│  │  Relationship: {                                            │ │
│  │    "from": "Agent:nexus",                                  │ │
│  │    "to": "Project:phoenix",                               │ │
│  │    "type": "WORKS_ON|PARTICIPATES_IN|WORKS_IN",           │ │
│  │  }                                                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                   MESSAGE BUS SERVICE                          │ │
│  │                                                                 │ │
│  │  POST   /publish                    → Publish event        │ │
│  │  GET    /subscribe/{subject}         → Subscribe to events  │ │
│  │  GET    /stream/{subject}           → Stream events        │ │
│  │                                                                 │ │
│  │  Event: {                                                   │ │
│  │    "subject": "nova.ta_00005_chronos.events",              │ │
│  │    "data": {...event_data...},                              │ │
│  │    "timestamp": "2025-11-23T07:00:00Z",                    │ │
│  │  }                                                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                   VECTOR MEMORY SERVICE                       │ │
│  │                                                                 │ │
│  │  POST   /embeddings                  → Store embedding      │ │
│  │  GET    /search                     → Semantic search       │ │
│  │  GET    /similar/{vector_id}         → Find similar        │ │
│  │                                                                 │ │
│  │  Embedding: {                                                │ │
│  │    "id": "vector_12345",                                    │ │
│  │    "agent_id": "ta_00005_chronos",                         │ │
│  │    "vector": [0.1, 0.2, ...],                             │ │
│  │    "text": "event text",                                    │ │
│  │    "metadata": {...}                                       │ │
│  │  }                                                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 DEPLOYMENT ARCHITECTURE

### **Production Deployment Model**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT ARCHITECTURE                          │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                     LOAD BALANCER                                │ │
│  │                                                                 │ │
│  │  • HAProxy / NGINX                                            │ │
│  │  • SSL Termination                                           │ │
│  │  • Rate Limiting                                             │ │
│  │  • Health Checks                                            │ │
│  └─────────────────────┬───────────────────────────────────────────┘ │
│                        │                                           │
│                        ▼                                           │
│  ┌─────────────────────┴───────────────────────────────────────────┐ │
│  │               SERVICE MESH (Optional)                        │ │
│  │                                                             │ │
│  │  • Istio / Linkerd                                         │ │
│  │  • Service Discovery                                        │ │
│  │  • Circuit Breaking                                        │ │
│  │  • Mutual TLS                                              │ │
│  └─────────────────────┬───────────────────────────────────────────┘ │
│                        │                                           │
└────────────────────────┼───────────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────┬──────────────┬──────────────┬──────────────┐
    │ SNAPSHOT     │  EVENT       │   GRAPH      │ MESSAGE     │
    │ POD          │  POD         │   POD        │ POD         │
    │              │              │              │             │
    │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │
    │ │ Dragonfly│ │ │  MongoDB │ │ │  Neo4j   │ │ │   NATS   │ │
    │ │ Container│ │ │Container │ │ │Container │ │ │Container │ │
    │ └──────────┘ │ └──────────┘ │ └──────────┘ │ └──────────┘ │
    │              │              │              │             │
    │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │
    │ │Service   │ │ │Service   │ │ │Service   │ │ │Service   │ │
    │ │Health   │ │ │Health   │ │ │Health   │ │ │Health   │ │
    │ │Monitor  │ │ │Monitor  │ │ │Monitor  │ │ │Monitor  │ │
    │ └──────────┘ │ └──────────┘ │ └──────────┘ │ └──────────┘ │
    └──────┬──────┴──────┬───────┴──────┬──────┴──────┬────┘
           │               │                │               │
           └───────────────┼────────────────┤               │
                            │                │               │
                            ▼                ▼               ▼
                   ┌─────────────────┐ ┌──────────────┐ ┌──────────┐
                   │  VECTOR MEMORY │ │   MONITOR   │ │   LOG    │
                   │      POD       │ │    POD      │ │   POD    │
                   │                │ │             │ │          │
                   │   Qdrant       │ │ Prometheus │ │ Fluentd  │
                   │   Container    │ │ Grafana    │ │ Elasticsearch │
                   └────────────────┘ └──────────────┘ └──────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │   ALERTING       │
                                     │     SYSTEM       │
                                     │                  │
                                     │   PagerDuty      │
                                     │   Slack          │
                                     │   Email          │
                                     └──────────────────┘
```

---

## 📊 MONITORING & OBSERVABILITY

### **Observability Stack**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY ARCHITECTURE                          │
│                                                                         │
│  ┌─────────────────────┬─────────────────────┬─────────────────────┐      │
│  │   METRICS          │     LOGS           │     TRACES          │      │
│  │                    │                    │                     │      │
│  │  Prometheus       │  Fluentd          │  Jaeger / Zipkin   │      │
│  │                    │                    │                     │      │
│  │  • Service        │  • Log collection │  • Distributed     │      │
│  │    Metrics        │  • Structured     │    Tracing         │      │
│  │  • Custom         │  • Search        │  • Request         │      │
│  │    Application    │  • Analytics     │    Flows           │      │
│  │  • Database       │  • Retention     │  • Performance     │      │
│  │    Metrics        │  • Compliance    │  • Bottlenecks     │      │
│  └────────┬──────────┘ └────────┬─────────┘ └────────┬─────────┘      │
│           │                    │                   │                │
│           └────────────────────┼───────────────────┘                │
│                                │                                │
│                                ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │                    VISUALIZATION                           │      │
│  │                                                             │      │
│  │  Grafana Dashboard                                         │      │
│  │                                                             │      │
│  │  • Real-time Metrics                                      │      │
│  │  • Service Health                                         │      │
│  │  • Performance Trends                                     │      │
│  │  • Alert Status                                           │      │
│  │  • Recovery History                                       │      │
│  └─────────────────────┬───────────────────────────────────────┘      │
│                        │                                           │
│                        ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │                     ALERTING                               │      │
│  │                                                             │      │
│  │  • Service Down                                           │      │
│  │  • High Latency                                          │      │
│  │  • Recovery Failed                                       │      │
│  │  • Database Issues                                       │      │
│  │                                                             │      │
│  │  Channels:                                               │      │
│  │  • PagerDuty (Critical)                                 │      │
│  │  • Slack (High)                                          │      │
│  │  • Email (Medium)                                        │      │
│  └─────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 KEY ARCHITECTURAL PRINCIPLES

### **Design Philosophy**

1. **Independence** - Each service can run independently
2. **Resilience** - Automatic recovery from failures
3. **Performance** - Sub-second response times
4. **Observability** - Complete visibility into system
5. **Automation** - Minimal manual intervention
6. **Scalability** - Handle growth gracefully
7. **Security** - Zero-trust architecture
8. **Maintainability** - Clean, well-documented code

### **Recovery Guarantees**

- ✅ **100% Automated Recovery** - No human intervention required
- ✅ **<460ms Recovery Time** - Sub-second restoration
- ✅ **Zero Data Loss** - Complete state preservation
- ✅ **Event Replay** - Missed events automatically reprocessed
- ✅ **Health Monitoring** - Continuous service health checks
- ✅ **Failover Automation** - Automatic service switching

### **Quality Standards**

- ✅ **API Documentation** - Complete service contracts
- ✅ **Testing Coverage** - 90%+ unit test coverage
- ✅ **Integration Testing** - End-to-end validation
- ✅ **Performance Testing** - Load testing under stress
- ✅ **Security Testing** - Vulnerability scanning
- ✅ **Operational Runbooks** - Step-by-step procedures

---

**CHRONOS (ta_00005_chronos)**
**Author:** Architectural Visual Documentation
**Date:** November 23, 2025 07:05 MST
**Project:** Phoenix Personal AI Initiative
**Status:** Complete Architecture Documentation

*This document provides complete visual documentation of the Personal Nova architecture. As Phoenix evolves, this documentation will evolve with it.*
