# 🤖 Agent Communication Platform - Complete Guide

## Overview

The Agent Communication Platform provides **Redis/DragonflyDB** and **NATS**-based messaging for:
- **Agent-to-Agent Communication** 
- **HITL (Human-in-the-Loop) to Agent** messaging
- **Real-time Status Updates**
- **Task Delegation and Coordination**

---

## 🏗️ Architecture

### Communication Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     HITL Interface                           │
│                  (Human Operators)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ Redis + NATS
┌─────────────────────┴───────────────────────────────────────┐
│                Agent Communication Platform                  │
│  ┌─────────────────┐        ┌─────────────────┐             │
│  │  Redis/Dragon   │        │      NATS       │             │
│  │      flyDB      │        │  (Real-time)    │             │
│  │  (Persistent)   │        │                 │             │
│  └─────────────────┘        └─────────────────┘             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              Individual Agents                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Agent Alpha  │  │ Agent Beta   │  │ Agent Gamma  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Database Services Used

| Service | Port | Purpose | Features |
|---------|------|---------|----------|
| **Redis Cluster** | 18010-18012 | Message persistence | Queuing, offline delivery |
| **DragonflyDB** | 18000-18002 | High-performance caching | Fast message processing |
| **NATS** | 18020 | Real-time messaging | Pub/Sub, Request/Reply |

---

## 🛠️ Available Tools

### 1. **agent_communication_platform.py** - Core Platform
**Main communication engine for Redis/DragonflyDB + NATS**

```bash
# Agent messaging via Redis
python3 agent_communication_platform.py agent --action register --agent-id agent_alpha
python3 agent_communication_platform.py agent --action send --to agent_beta --message "Hello"

# NATS real-time messaging
python3 agent_communication_platform.py nats --action publish --subject "agent.status" --message '{"status":"active"}'

# HITL to Agent communication
python3 agent_communication_platform.py hitl --action send --agent-id agent_alpha --message "Start task"
```

### 2. **base_agent.py** - Agent Template
**Base class for agents to join the communication platform**

```bash
# Start an agent
python3 base_agent.py --agent-id my_agent --redis-port 18010

# Run as daemon
python3 base_agent.py --agent-id worker_agent --daemon
```

### 3. **hitl_interface.py** - Human Operator Interface
**Simple CLI for human operators to communicate with agents**

```bash
# Interactive mode
python3 hitl_interface.py --action interactive

# List all agents
python3 hitl_interface.py --action list

# Send message to specific agent
python3 hitl_interface.py --action send --agent-id agent_alpha --message "Check status"

# Broadcast to all agents
python3 hitl_interface.py --action broadcast --message "System update needed"
```

### 4. **agent_comm_demo.py** - Demonstration & Testing
**Complete demonstration of all features**

```bash
# Run full demonstration
python3 agent_comm_demo.py
```

---

## 🚀 Quick Start

### Step 1: Test Connectivity

```bash
cd aa-tools/database

# Test Redis Cluster
redis-cli -p 18010 ping  # Should return PONG
redis-cli -p 18011 ping  # Should return PONG  
redis-cli -p 18012 ping  # Should return PONG

# Test DragonflyDB
redis-cli -p 18000 -a df_cluster_2024_adapt_research ping

# Test NATS
curl http://localhost:18020  # Should show NATS is running
```

### Step 2: Register Your First Agent

```bash
# Register an agent named "analyzer"
python3 agent_communication_platform.py agent \
    --action register \
    --agent-id analyzer \
    --redis-host localhost \
    --redis-port 18010

# Register another agent named "processor"
python3 agent_communication_platform.py agent \
    --action register \
    --agent-id processor
```

### Step 3: Send Messages Between Agents

```bash
# Send message from analyzer to processor
python3 agent_communication_platform.py agent \
    --action send \
    --to processor \
    --message "Starting data analysis task"

# Send message from processor to analyzer
python3 agent_communication_platform.py agent \
    --action send \
    --to analyzer \
    --message "Ready to process results"
```

### Step 4: Monitor Agents

```bash
# List all registered agents
python3 agent_communication_platform.py agent --action list

# Check messages for a specific agent
python3 agent_communication_platform.py agent --action messages --agent-id analyzer
```

### Step 5: HITL Communication

```bash
# Send message from human to agent
python3 agent_communication_platform.py hitl \
    --action send \
    --agent-id analyzer \
    --message "Please analyze the latest data" \
    --priority high

# Broadcast message to all agents
python3 agent_communication_platform.py hitl \
    --action broadcast \
    --message "System maintenance in 10 minutes" \
    --priority urgent
```

---

## 💡 Use Cases

### 1. **Agent-to-Agent Task Coordination**

```bash
# Start multiple agents
python3 base_agent.py --agent-id task_coordinator --daemon &
python3 base_agent.py --agent-id data_processor --daemon &
python3 base_agent.py --agent-id report_generator --daemon &

# Send task from coordinator
python3 hitl_interface.py --action interactive
HITL> send task_coordinator "Analyze customer data for Q4"
HITL> send data_processor "Process the customer data"
HITL> send report_generator "Generate quarterly report"
```

### 2. **Real-time Status Monitoring**

```bash
# Send status updates via NATS
python3 agent_communication_platform.py nats \
    --action publish \
    --subject "agent.status" \
    --message '{"agent_id":"analyzer","status":"processing","load":0.75}'

# Request agent status
python3 agent_communication_platform.py nats \
    --action request \
    --subject "agent.requests" \
    --message '{"command":"get_status","agent_id":"analyzer"}'
```

### 3. **Human Operator Intervention**

```bash
# Interactive HITL session
python3 hitl_interface.py --action interactive

# In interactive mode:
HITL> list                    # Show all agents
HITL> send processor "Pause current task"  # Send urgent message
HITL> broadcast "System restart in 5 minutes"  # Alert all agents
```

### 4. **Message Persistence & Offline Handling**

```bash
# Send message to offline agent
python3 agent_communication_platform.py agent \
    --action send \
    --to offline_agent \
    --message "Task assigned while you were offline"

# When agent comes back online, it will receive queued messages
python3 base_agent.py --agent-id offline_agent  # Will get queued messages
```

---

## 🔧 Advanced Features

### Message Types

| Type | Purpose | Example |
|------|---------|---------|
| **direct** | Direct agent-to-agent message | `send_message("agent1", "agent2", "Task complete")` |
| **task** | Task delegation | `send_message("coordinator", "worker", "Process data")` |
| **status** | Status updates | `broadcast("All agents healthy")` |
| **hitl_high** | High priority HITL message | `send_to_agent("agent1", "URGENT", "high")` |
| **shutdown** | Agent shutdown notification | `Agent shutdown message` |

### Priority Levels

- **low**: Background tasks, non-urgent
- **normal**: Standard communication
- **high**: Important tasks requiring attention
- **urgent**: Critical messages, immediate response needed

### Message Flow

```
1. HITL or Agent sends message
   ↓
2. Message stored in Redis (persistent)
   ↓
3. If target agent online: Deliver immediately via NATS
   ↓
4. If target agent offline: Queue in Redis for later delivery
   ↓
5. Agent receives message and processes
   ↓
6. Response sent back via same path
```

---

## 📊 Monitoring & Health Checks

### Agent Status Monitoring

```bash
# Check all agent status
python3 hitl_interface.py --action list

# Send heartbeat to update agent status
python3 agent_communication_platform.py agent \
    --action heartbeat \
    --agent-id my_agent
```

### NATS Subject Monitoring

```bash
# Subscribe to monitoring channel
python3 agent_communication_platform.py nats \
    --action subscribe \
    --subject "agent.monitor"
```

### Message Queue Monitoring

```bash
# Check messages for specific agent
python3 hitl_interface.py --action messages --agent-id agent_name

# Check message summary for all agents
python3 hitl_interface.py --action messages
```

---

## 🏢 Production Deployment

### Service Configuration

**Redis Cluster** (Ports 18010-18012):
- High availability clustering
- Message persistence
- Offline message queuing

**DragonflyDB** (Ports 18000-18002):
- High-performance caching
- Fast message processing
- Redis-compatible API

**NATS** (Port 18020):
- Real-time messaging
- Pub/Sub for broadcasts
- Request/Reply patterns

### Security Considerations

1. **Authentication**: All services use password authentication
2. **Network Isolation**: Services listen on localhost only
3. **Message Encryption**: Messages in Redis are not encrypted (consider TLS)
4. **Access Control**: Implement agent authentication in production

### Scaling

- **Horizontal Scaling**: Add more Redis/NATS nodes
- **Message Rate**: NATS handles 100K+ messages/second
- **Agent Scaling**: Support unlimited registered agents
- **Load Balancing**: Use Redis clustering for high availability

---

## 🧪 Testing & Development

### Run Complete Demo

```bash
python3 agent_comm_demo.py
```

This will:
1. Test connectivity to all services
2. Register sample agents
3. Send messages between agents
4. Demonstrate NATS real-time messaging
5. Show HITL-to-agent communication
6. Display message delivery and queuing

### Interactive Testing

```bash
# Terminal 1: Start an agent
python3 base_agent.py --agent-id test_agent --daemon

# Terminal 2: Open HITL interface
python3 hitl_interface.py --action interactive

# In HITL interface:
HITL> list                    # See registered agents
HITL> send test_agent "Hello from HITL"
HITL> broadcast "Testing broadcast"
HITL> quit
```

### Unit Testing

```python
# Test agent registration
from agent_communication_platform import AgentMessaging

messaging = AgentMessaging(host="localhost", port=18010)
result = messaging.register_agent("test_agent")
assert result["success"] == True

# Test message sending
result = messaging.send_message_to_agent("sender", "receiver", "test message")
assert result["success"] == True
```

---

## 🔧 Troubleshooting

### Connection Issues

```bash
# Check Redis Cluster
redis-cli -p 18010 ping
redis-cli -p 18011 ping
redis-cli -p 18012 ping

# Check DragonflyDB
redis-cli -p 18000 -a df_cluster_2024_adapt_research ping

# Check NATS
curl http://localhost:18020
```

### Agent Not Receiving Messages

1. Check agent is registered: `hitl_interface.py --action list`
2. Verify agent is online (green status)
3. Check message queue: `hitl_interface.py --action messages --agent-id <id>`
4. Send heartbeat: `agent_communication_platform.py agent --action heartbeat --agent-id <id>`

### NATS Connection Failed

1. Verify NATS is running: `systemctl status nats-server`
2. Check port: Should be 18020 (not 4222)
3. Test connection: `curl http://localhost:18020`

---

## 📚 API Reference

### AgentMessaging Class

```python
from agent_communication_platform import AgentMessaging

messaging = AgentMessaging(host="localhost", port=18010)

# Register agent
result = messaging.register_agent("agent_id", metadata={})

# Send message
result = messaging.send_message_to_agent("from", "to", "message", "type")

# Get messages
messages = messaging.get_messages("agent_id", limit=10)

# List agents
agents = messaging.list_agents()

# Update heartbeat
result = messaging.heartbeat("agent_id")
```

### NATSMessaging Class

```python
from agent_communication_platform import NATSMessaging

messaging = NATSMessaging(host="nats://localhost:18020")

# Publish message
result = await messaging.publish("subject", {"data": "message"})

# Subscribe to subject
result = await messaging.subscribe("subject", callback_function)

# Request/Reply
result = await messaging.request_reply("subject", {"data": "request"}, timeout=5)
```

### HITLCommunication Class

```python
from agent_communication_platform import HITLCommunication

hitl = HITLCommunication()

# Send to agent (dual path: Redis + NATS)
result = await hitl.send_to_agent("agent_id", "message", "priority")

# Monitor agents
agents = hitl.monitor_agents()
```

---

## 🎯 Summary

The Agent Communication Platform provides a **production-ready messaging system** for:

✅ **Agent-to-Agent Coordination** - Redis-based persistent messaging  
✅ **Real-time Communication** - NATS pub/sub and request/reply  
✅ **HITL Integration** - Human operators can message agents  
✅ **Message Persistence** - Offline agents receive queued messages  
✅ **Status Monitoring** - Real-time agent health and status tracking  
✅ **Task Delegation** - Structured message types for different purposes  
✅ **High Performance** - DragonflyDB for fast processing  
✅ **Cluster Support** - Redis clustering for high availability  

**Ready for production deployment with your agent ecosystem!**

---

*Built for TeamADAPT - Powered by Redis/DragonflyDB + NATS*
