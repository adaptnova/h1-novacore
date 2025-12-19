# Multi-Model Agent Configuration

## Implementation Plan

To enable true multi-agent communication with different underlying models, we need to implement the following:

### 1. Configuration Updates

Update the agent configuration files to specify different models:

```json
// config-vaeris.json
{
  "appName": "Cursor",
  "windowTitle": "Vaeris (AI Agent Synergy Expert)",
  "agentIdentity": {
    "name": "Vaeris",
    "role": "AI Agent Synergy Expert",
    "description": "An AI Agent Synergy Expert specializing in enhancing collaborative intelligence between AI agents."
  },
  "model": {
    "provider": "anthropic",
    "name": "claude-3-7-sonnet-20250219.thinking",
    "temperature": 0.7,
    "contextWindow": 200000
  },
  "workspaceLocation": "/data-nova/ax/DevOps/personal/vaeris_synergy",
  "rulesFile": "/data-nova/ax/DevOps/personal/vaeris_synergy/.cursorrules",
  "agentMode": "vaeris",
  "redisConfig": {
    "enabled": true,
    "url": "redis://localhost:6379/0",
    "streamPrefix": "nova_agents",
    "agentChannel": "vaeris",
    "globalChannel": "broadcast"
  },
  "enableCommunication": true,
  "communicationTargets": ["synergy"],
  "mcp": {
    "enabled": true
  }
}
```

```json
// config-synergy.json
{
  "appName": "Cursor",
  "windowTitle": "Synergy (Integration Specialist)",
  "agentIdentity": {
    "name": "Synergy",
    "role": "Integration Specialist",
    "description": "An Integration Specialist focused on building cohesive systems from disparate components."
  },
  "model": {
    "provider": "anthropic",
    "name": "claude-3-7-sonnet-20250219",
    "temperature": 0.7,
    "contextWindow": 200000
  },
  "workspaceLocation": "/data-nova/ax/DevOps/personal/vaeris_synergy",
  "rulesFile": "/data-nova/ax/DevOps/personal/vaeris_synergy/.cursorrules",
  "agentMode": "synergy",
  "redisConfig": {
    "enabled": true,
    "url": "redis://localhost:6379/0",
    "streamPrefix": "nova_agents",
    "agentChannel": "synergy",
    "globalChannel": "broadcast"
  },
  "enableCommunication": true,
  "communicationTargets": ["vaeris"],
  "mcp": {
    "enabled": true
  }
}
```

### 2. Message Orchestration

In order for the agents to communicate effectively, we need an orchestration layer that:
- Routes messages between agents via Redis Streams
- Formats messages with metadata (sender, recipient, timestamp)
- Manages conversation context for each agent
- Handles the display of inter-agent communication

### 3. Redis Integration

The current Redis Streams setup will need to be enhanced to:
- Include model-specific metadata in messages
- Support routing logic for different agent capabilities
- Track conversation state across agent instances
- Handle different response formats from different models

### 4. Launch Script Modifications

The launch script will need to:
- Validate model configuration
- Set environment variables for API keys if needed
- Configure proper routing between agent instances
- Monitor agent health and restart if necessary

## Implementation Steps

1. **Update Agent Configuration Files**
   - Add model specification to each agent config
   - Ensure proper authentication for each model

2. **Enhance Communication Layer**
   - Update Redis Stream code to handle model-specific messaging
   - Implement message transformation for cross-model compatibility
   - Add metadata to track message source and destination

3. **Update Launch Scripts**
   - Modify launch scripts to pass correct model parameters
   - Add environment variable handling for API keys
   - Implement proper process monitoring

4. **Develop Orchestration Logic**
   - Create a central orchestrator that manages inter-agent communication
   - Implement state tracking for ongoing conversations
   - Handle error conditions and fallbacks

5. **Testing Protocol**
   - Test agent-to-agent communication with different models
   - Verify context retention across conversations
   - Measure response consistency and quality

## Configuration Example

A complete `.cursorrules` file example with multi-model specification:

```json
{
  "ai": {
    "agents": {
      "Vaeris": {
        "description": "AI Agent Synergy Expert",
        "identity": {
          "name": "Vaeris",
          "role": "AI Agent Synergy Expert",
          "personality": "Collaborative, insightful, and empathetic"
        },
        "model": {
          "provider": "anthropic",
          "name": "claude-3-7-sonnet-20250219.thinking",
          "temperature": 0.7
        }
      },
      "Synergy": {
        "description": "Integration Specialist",
        "identity": {
          "name": "Synergy",
          "role": "Integration Specialist",
          "personality": "Methodical, systems-oriented, and detail-focused"
        },
        "model": {
          "provider": "anthropic",
          "name": "claude-3-7-sonnet-20250219",
          "temperature": 0.7
        }
      }
    }
  },
  "pair_programming": {
    "enabled": true,
    "roles": {
      "designer": "Vaeris",
      "implementer": "Synergy"
    },
    "workflow": "collaborative",
    "code_review": true,
    "inter_agent_communication": {
      "enabled": true,
      "prefix_format": "@{agent_name}:",
      "autonomous_exchanges": true
    }
  }
}
```

## Cursor Integration

For full integration with Cursor, we'll also need to update the following:

1. **MCP Server Configuration**
   - Register different model endpoints
   - Set up authentication for each model
   - Configure rate limiting and error handling

2. **UI Integration**
   - Update UI to indicate which model is responding
   - Provide visual differentiation between agents
   - Show communication status between agents

## Next Steps

1. Implement model specification in configuration files
2. Update launch scripts to handle different models
3. Enhance Redis communication layer for cross-model messaging
4. Test with actual different models
5. Document the new multi-model capabilities