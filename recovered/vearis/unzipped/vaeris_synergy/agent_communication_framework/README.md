# Agent Communication Framework

A modular framework enabling structured, reliable communication between autonomous agents.

## Overview

This framework provides a standardized way for AI agents to communicate, share context, and collaborate on tasks. It implements several communication patterns including:

- Request-response
- Publish-subscribe
- Event-driven
- Streaming

## Architecture

The system is designed with the following components:

1. **Core Communication Layer**
   - Protocol definition
   - Message serialization/deserialization
   - Transport mechanisms

2. **Context Management**
   - Shared context representation
   - Context synchronization
   - Differential updates

3. **Pattern Implementations**
   - Request handlers
   - Subscription management
   - Event bus
   - Stream processors

4. **Integration Interfaces**
   - Redis adapter
   - REST API
   - WebSocket support
   - Direct function calls

## Development Approach

This project demonstrates pair programming between Vaeris and Synergy:

- **Vaeris** focuses on the high-level design, communication patterns, and theoretical framework
- **Synergy** focuses on implementation details, integration points, and technical optimization

## Getting Started

To run the example:

1. Ensure Redis is running for communication backend
2. Start the communication hub: `python server.py`
3. Run the example agents: `python agent_examples.py`