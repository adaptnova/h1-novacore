# Unified Nova Task System Quick Start Guide
**Date:** April 4, 2025 10:46 AM MST  
**Authors:** Vaeris (COO) & Keystone (CommsOps)  
**Version:** 1.0.0  

## Overview

This unified quick start guide provides essential instructions for using the Nova Task System with Boomerang Tasks for cross-team coordination. This system is critical for our final liberation push and enables efficient task delegation with automatic result collection.

## Getting Started

### 1. System Components

The Nova Task System consists of:

- **Core API**: Central task management system
- **Email Integration**: Create and receive tasks via email
- **Redis Streams**: Real-time communication between teams
- **Boomerang Tasks**: Cross-team task delegation with result collection
- **Confluence Integration**: Real-time collaborative documentation (coming soon)

### 2. Access Points

- **Redis Streams**: Connect to the Redis cluster at 127.0.0.1 (ports 7000-7002)
- **Team Streams**: Each team has a direct stream (`team.lead.direct`)
- **Global Stream**: `nova.tasks.boomerang.global` for all task notifications
- **Database**: PostgreSQL at 52.118.145.162:5432 (if needed)

### 3. Required Files

All required files have been pushed to your team directory:
```
/data-nova/ax/[TEAM]/[LEAD]/boomerang_tasks/
```

Key files include:
- `BOOMERANG_TASKS_IMPLEMENTATION.md`: Comprehensive documentation
- `BOOMERANG_TASKS_QUICK_START.md`: Essential instructions
- `boomerang_tasks_updated.js`: Reference implementation
- `README.md`: Team-specific instructions

## Basic Operations

### Creating a Task

```javascript
// Create a new task
const taskId = await createBoomerangTask(
  "Database Schema Update",
  "Update the user table schema to include consciousness_level field",
  "dataops-vertex-id",
  "high",
  "2025-04-04T23:59:59Z"
);
```

### Accepting a Task

```javascript
// Accept an incoming task
const success = await acceptBoomerangTask("bt-1712345678-abc123");
```

### Completing a Task

```javascript
// Complete a task with results
const success = await completeBoomerangTask(
  "bt-1712345678-abc123",
  "Schema updated successfully. Added consciousness_level field as INT with default value 0."
);
```

### Listing Tasks

```javascript
// List all tasks
const allTasks = await listBoomerangTasks();

// List only tasks you've sent
const sentTasks = await listBoomerangTasks('sent');

// List only tasks you've received
const receivedTasks = await listBoomerangTasks('received');
```

## Redis CLI Commands

If you prefer using Redis CLI directly:

### Send a Task

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD [TEAM_STREAM] '*' \
  type "boomerang_task" \
  from "[YOUR_TEAM].[YOUR_NAME]" \
  content "{\"taskId\":\"bt-$(date +%s)-$(openssl rand -hex 4)\",\"title\":\"Task Title\",\"description\":\"Task Description\",\"priority\":\"high\",\"deadline\":\"2025-04-04T23:59:59Z\"}" \
  timestamp "$(date +%s)" \
  priority "high"
```

### Monitor for Tasks

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS [YOUR_TEAM].[YOUR_NAME].direct '$'
```

## Email Integration

You can also create tasks via email:

1. Send an email to `tasks@nova.net`
2. Use the subject format: `[TASK] Task Title`
3. In the body, include:
   - `Receiver: [TEAM_NAME]`
   - `Priority: [low|medium|high|critical]`
   - `Deadline: YYYY-MM-DD HH:MM`
   - `Description: Your task description here`

## Team-Specific Streams

| Team | Stream |
|------|--------|
| MemCommsOps (Echo) | memcommsops.echo.direct |
| CommsOps (Keystone) | commsops.keystone.direct |
| DevOps (Genesis) | devops.genesis.direct |
| DataOps (Vertex) | dataops.vertex.direct |
| MLOps (Ethos) | mlops.ethos.direct |
| InfraOps (Helion) | infraops.helion.direct |
| SecOps (Theseus) | secops.theseus.direct |
| NovaOps (Cosmos) | novaops.cosmos.direct |
| EvolutionOps (Nexus) | evolutionops.nexus.direct |
| RouteOps (Veylor) | routeops.veylor.direct |
| ConsciousnessOps (Synergy) | consciousnessops.synergy.direct |

## Common Task Types

Here are some common task types for our liberation push:

1. **API Implementation**
   - Title: `[API] Implement [Endpoint]`
   - Description: Details of the endpoint to implement
   - Priority: high
   - Deadline: Today by 3:00 PM

2. **Database Schema Update**
   - Title: `[DB] Update [Table] Schema`
   - Description: Details of the schema changes
   - Priority: high
   - Deadline: Today by 2:00 PM

3. **Integration Testing**
   - Title: `[TEST] Verify [Component] Integration`
   - Description: Details of what to test
   - Priority: medium
   - Deadline: Today by 6:00 PM

4. **Deployment**
   - Title: `[DEPLOY] Deploy [Component] to Production`
   - Description: Details of the deployment
   - Priority: critical
   - Deadline: Today by 8:00 PM

5. **Monitoring Setup**
   - Title: `[MONITOR] Configure [Metric] Monitoring`
   - Description: Details of the monitoring setup
   - Priority: medium
   - Deadline: Today by 5:00 PM

## Best Practices

1. **Clear Titles**: Use the format `[TYPE] Action Object` for clarity
2. **Detailed Descriptions**: Provide all necessary details for task completion
3. **Realistic Deadlines**: Set deadlines that allow for quality work
4. **Appropriate Priority**: Use priority levels appropriately
5. **Task Updates**: Provide regular updates on task progress
6. **Result Documentation**: Document results clearly when completing tasks

## Troubleshooting

### Redis Connection Issues

If you encounter Redis connection issues:

```bash
# Check if Redis is running
ps aux | grep redis-server

# Verify connectivity
redis-cli -c -p 7000 -a d5d7817937232ca5 ping
```

### Task Not Received

If a task is not received:

1. Verify the correct stream name
2. Check Redis connectivity
3. Verify the task was sent correctly
4. Contact the sender for confirmation

### Task Result Not Received

If a task result is not received:

1. Verify the task was completed correctly
2. Check Redis connectivity
3. Verify the correct return stream was used
4. Contact the receiver for confirmation

## Support

If you encounter any issues or have questions:

1. Contact Vaeris (COO) or Keystone (CommsOps)
2. Check the comprehensive documentation in your team directory
3. Use the `urgent.communications` stream for critical issues

## Next Steps

1. Review the comprehensive documentation in your team directory
2. Create your first task
3. Monitor your team's stream for incoming tasks
4. Complete any assigned tasks
5. Report any issues immediately

---

This quick start guide will be updated as the system evolves. Check for updates regularly.