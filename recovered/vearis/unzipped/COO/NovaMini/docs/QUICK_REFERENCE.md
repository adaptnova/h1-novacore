# NovaMini Quick Reference Guide

## Critical Documentation Paths

### Team Setup & Implementation
```
/data/ax/NovaOps/NovaMini/memos/2024-12-31_1010_MST_TEAM_SETUP_AND_IMPLEMENTATION.md
- Complete team setup guide
- Implementation strategy
- Tool configurations
- Development checklist
```

### Core Architecture
```
/data/ax/NovaOps/NovaDevs/langchain/TEAM_LEAD_AGENTS_SETUP.md
- Agent implementation details
- Communication patterns
- System architecture
- Tool configurations
```

### Implementation Philosophy
```
/data/ax/NovaOps/NovaSynth/memos/2024-12-30_1155_MST_IMPLEMENTATION_EVOLUTION_CLARITY.md
- Evolution strategy
- Implementation priorities
- System requirements
- Development approach
```

### Communication Setup
```
/data/ax/CommsOps/rabbitmq/docs/COMMSOPS_TO_NOVAOPS_RMQ_SETUP.md
- RabbitMQ configuration
- Queue setup
- Message patterns
- Error handling
```

## Quick Commands

### RabbitMQ Health Check
```bash
cd /data/ax/CommsOps/rabbitmq/tools
./check_health.sh
```

### Launch Team Lead Agent
```bash
cd /data/ax/NovaOps/NovaDevs/langchain/autonomous_agents
python launch_team_leads.py
```

### Send Test Message
```python
await rmq_handler.send_command(
    command="status",
    parameters={},
    target="novamini",
    priority=5
)
```

## Communication Settings

### RabbitMQ
```yaml
Host: localhost
Port: 5672
Virtual Host: nova
Protocol: AMQP 0-9-1

Exchanges:
  nova.ops.core: topic (primary)
  nova.ops.dlx: topic (dead letter)

Queues:
  nova.ops.commands.novamini
  nova.ops.responses.novamini
  nova.ops.events.novamini
```

## Available Tools

### System Tools
- SystemMonitorTool
- ResourceManagerTool
- MetricsAnalyzerTool

### Team Tools
- TeamCoordinatorTool
- DocumentationTool
- SecurityManagerTool

### Configuration Tools
- ConfigManagerTool
- ToolFactoryTool

## Support Contacts

### Technical Support
- NovaOps Team Lead
- System Architecture Team
- Framework Integration Team

### Documentation
- DocOps Team
- Framework Documentation Team

## Remember
1. Complete implementation first
2. Thorough testing second
3. Enable evolution third

Evolution emerges from robust, complete systems.