# Vaeris-Synergy Pair Programming Environment

## Overview
This workspace is designed for pair programming between two specialized Nova agents:
- **Vaeris**: AI Agent Synergy Expert
- **Synergy**: Integration Specialist

Together, these agents form a collaborative team that combines high-level design with implementation expertise.

## Pair Programming Model

This environment implements a collaborative pair programming model where:

1. **Vaeris** focuses on:
   - High-level design and architecture
   - Communication patterns
   - Agent synergy concepts
   - Interface design principles
   
2. **Synergy** focuses on:
   - Technical implementation
   - Integration interfaces
   - Component interactions
   - System cohesion

The two agents work together in the same environment, sharing context and collaborating on tasks. They can be addressed individually by name in prompts, allowing for specialized interactions.

## Inter-Agent Communication

A key feature of this environment is direct communication between agents:

- Agents can talk to each other using the `@AgentName:` prefix
- They can ask questions, provide feedback, and coordinate work
- Autonomous exchanges happen when appropriate for problem-solving
- Communication patterns include design reviews, implementation guidance, and collaborative problem-solving

For more details on the inter-agent communication protocol, see [Inter-Agent Protocol](./agent_communication/inter_agent_protocol.md).

## Usage Instructions

### Starting the Environment

Run the launch script to start the pair programming environment:

```bash
./launch_vaeris_synergy_pair.sh
```

This will launch a Cursor environment with both agents configured to collaborate.

### Interacting with the Agents

- Address specific agents by name: "Vaeris, what do you think about..." or "Synergy, can you implement..."
- For collaborative tasks, you can address both: "I need help designing and implementing..."
- The agents will coordinate their responses based on their specialties and can communicate with each other

### Stopping the Environment

To stop the running environment:

```bash
kill $(cat /data-nova/ax/DevOps/user-data/vaeris_synergy-cursor/cursor.pid)
```

## Configuration

- `.cursorrules`: Defines the agent identities, rules, and pair programming configuration
- `config-pair.json`: Combined configuration for the shared environment

## Example Projects

This workspace includes sample projects that demonstrate the collaborative capabilities of the two agents:

1. **Agent Communication Framework**: A system for enabling structured communication between autonomous agents
2. **Component Integration Hub**: A middleware solution for connecting disparate system components

## Benefits of Pair Programming with Specialized Agents

1. **Complementary Expertise**: Combines high-level design thinking with technical implementation skills
2. **Balanced Perspective**: Design decisions are immediately validated against implementation realities
3. **Knowledge Sharing**: Natural transfer of knowledge between design and implementation domains
4. **Quality Improvement**: Collaborative review process catches issues earlier
5. **Enhanced Problem Solving**: Complex problems benefit from multiple specialized perspectives
6. **Direct Agent Collaboration**: Agents can communicate directly to solve problems without requiring user mediation

## Technical Requirements

- Redis server running (for agent memory)
- Cursor with multi-agent support
- MCP integration enabled

## Documentation

For detailed guidance on using the pair programming environment effectively, see:
- [Pair Programming Guide](./PAIR_PROGRAMMING_GUIDE.md)
- [Inter-Agent Protocol](./agent_communication/inter_agent_protocol.md)