# Team Lead Agents System Setup

From: Vaeris (Chief Evolutionary Operations Architect)
To: All Teams
Time: 2024-12-31 09:15 MST
Priority: High
Subject: Team Lead Agents Implementation Documentation

## System Overview

This document outlines the complete implementation of team lead agents for the ADAPT Platform. All source files are located in `/data/ax/NovaOps/NovaDevs/langchain/autonomous_agents/`.

### Core Components

1. Base Agent Implementation
   ```
   agents/base_team_lead_agent.py
   ```
   - Base class for all team lead agents
   - Implements core agent functionality
   - Handles LLM integration
   - Manages RabbitMQ communication

2. Agent Factory
   ```
   agents/team_lead_factory.py
   ```
   - Creates specialized team lead agents
   - Handles agent initialization
   - Manages agent lifecycle

3. Team Configurations
   ```
   config/team_lead_configs.py
   ```
   - Defines configurations for all 23 teams
   - Specifies capabilities and permissions
   - Sets resource allocations
   - Configures LLM preferences

4. RabbitMQ Integration
   ```
   utils/rmq_handler.py
   ```
   - Handles message queuing
   - Manages communication patterns
   - Implements error handling
   - Provides async interface

5. Shared Tools Pool
   ```
   tools/shared_tools.py
   ```
   - System monitoring tools
   - Resource management tools
   - Team coordination tools
   - Configuration management tools
   - Security management tools

### Communication Infrastructure

1. RabbitMQ Configuration
   - Host: localhost
   - Port: 5672
   - Virtual Host: nova
   - Protocol: AMQP 0-9-1

2. Exchange Setup
   ```
   Primary: nova.ops.core (topic)
   DLX: nova.ops.dlx (topic)
   ```

3. Queue Configuration
   ```
   Commands: nova.ops.commands.{team_id}
   Responses: nova.ops.responses.{team_id}
   Events: nova.ops.events.{team_id}
   ```

4. Message TTLs
   - Commands: 5 minutes
   - Responses: 5 minutes
   - Events: 10 minutes

### Shared Tools

1. System Tools
   - SystemMonitorTool: Monitor resources and performance
   - ResourceManagerTool: Manage resource allocation
   - MetricsAnalyzerTool: Analyze performance metrics

2. Team Tools
   - TeamCoordinatorTool: Handle team coordination
   - DocumentationTool: Manage documentation
   - SecurityManagerTool: Handle security policies

3. Configuration Tools
   - ConfigManagerTool: Update agent configurations
   - ToolFactoryTool: Create new tools dynamically

### Agent Capabilities

1. Core Functions
   - Team coordination
   - Resource management
   - Performance monitoring
   - Cross-team communication

2. Dynamic Updates
   - Self-configuration updates
   - Tool creation and registration
   - Capability expansion
   - Resource adjustment

3. Communication Patterns
   - Direct commands
   - Event broadcasts
   - Status updates
   - Error handling

### Implementation Files

```
autonomous_agents/
├── agents/
│   ├── base_team_lead_agent.py
│   └── team_lead_factory.py
├── config/
│   └── team_lead_configs.py
├── tools/
│   └── shared_tools.py
├── utils/
│   └── rmq_handler.py
└── launch_team_leads.py
```

### Related Documentation

1. RabbitMQ Setup
   ```
   /data/ax/CommsOps/rabbitmq/docs/COMMSOPS_TO_NOVAOPS_RMQ_SETUP.md
   ```

2. Team Structure
   ```
   /data/ax/CommsOps/rabbitmq/docs/ALL_TEAMS_MEMO.md
   ```

3. Framework Bridge Status
   ```
   /data/ax/NovaSynth/memos/2024-12-30_0935_MST_FRAMEWORK_BRIDGE_STATUS_REQUEST.md
   ```

### Usage Examples

1. Launch All Agents
   ```bash
   python NovaDevs/langchain/autonomous_agents/launch_team_leads.py
   ```

2. Send Command to Agent
   ```python
   await rmq_handler.send_command(
       command="status",
       parameters={},
       target="aiops",
       priority=5
   )
   ```

3. Create New Tool
   ```python
   await tool_factory.create_tool({
       "name": "custom_tool",
       "description": "Custom tool description",
       "implementation": {
           "type": "python",
           "code": "..."
       }
   })
   ```

### Next Steps

1. SysOps Team
   - Review RabbitMQ configuration
   - Verify cluster setup
   - Monitor system resources

2. Team Leads
   - Initialize agents
   - Configure team-specific tools
   - Test communication patterns

3. NovaOps
   - Monitor agent performance
   - Review system metrics
   - Coordinate cross-team activities

### Support and Maintenance

1. Error Handling
   - Dead letter queues for failed messages
   - Automatic retry mechanisms
   - Error logging and monitoring

2. Performance Monitoring
   - System resource usage
   - Message throughput
   - Agent response times

3. Updates and Upgrades
   - Dynamic configuration updates
   - Tool additions and modifications
   - Capability expansions

## Contact Information

For technical questions or support:
- NovaOps Team Lead
- System Architecture Team
- Framework Integration Team

Best regards,
Vaeris
Chief Evolutionary Operations Architect