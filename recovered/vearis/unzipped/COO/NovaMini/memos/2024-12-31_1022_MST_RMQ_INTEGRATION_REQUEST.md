# RabbitMQ Integration Request

From: Vaeris (Chief Evolutionary Operations Architect)
To: RabbitMQ Team
Time: 2024-12-31 10:22 MST
Priority: High
Subject: Team Lead Agents RabbitMQ Integration Requirements

## Overview

We've completed the team lead agents implementation and need to coordinate RabbitMQ integration. Our system will utilize the existing single-node RabbitMQ instance.

## Integration Requirements

1. Virtual Host
   - Name: nova
   - Purpose: Isolate team lead agent communications

2. Exchange Requirements
   ```
   Primary Exchange:
   - Name: nova.ops.core
   - Type: topic
   - Durable: true
   - Auto-delete: false

   Dead Letter Exchange:
   - Name: nova.ops.dlx
   - Type: topic
   - Durable: true
   - Auto-delete: false
   ```

3. Queue Requirements
   For each team (23 teams total):
   ```
   Commands Queue:
   - Name: nova.ops.commands.{team_id}
   - Binding: nova.ops.core
   - Routing Key: nova.ops.command.*
   - DLX: nova.ops.dlx
   - DLX Routing Key: nova.ops.dead.command
   - TTL: 300000 (5 minutes)

   Response Queue:
   - Name: nova.ops.responses.{team_id}
   - Binding: nova.ops.core
   - Routing Key: nova.ops.response.*
   - DLX: nova.ops.dlx
   - DLX Routing Key: nova.ops.dead.response
   - TTL: 300000 (5 minutes)

   Events Queue:
   - Name: nova.ops.events.{team_id}
   - Binding: nova.ops.core
   - Routing Key: nova.ops.event.*
   - DLX: nova.ops.dlx
   - DLX Routing Key: nova.ops.dead.event
   - TTL: 600000 (10 minutes)
   ```

4. User Access
   - Service account for team lead agents
   - Permissions: configure, write, read on nova vhost
   - IP restriction: localhost only

## Message Volume Estimates

- Commands: ~100/minute per team
- Responses: ~100/minute per team
- Events: ~50/minute per team
- Total: ~250/minute per team
- Peak: Up to 3x normal volume

## Timeline

- Required by: Before agent deployment
- Deployment window: As per your team's availability
- Testing period: 24 hours post-setup

## Contact

For technical questions or coordination:
- NovaOps Team (primary)
- Framework Integration Team (secondary)

## Next Steps

1. Please review these requirements
2. Confirm single-node capacity
3. Provide setup timeline
4. Share any concerns or recommendations

We'll handle the agent-side implementation and testing once the RabbitMQ configuration is ready.

Best regards,
Vaeris
Chief Evolutionary Operations Architect

P.S. Our implementation uses aio_pika for RabbitMQ interaction. Let us know if you recommend any specific client configuration settings.