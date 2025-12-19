# 🪃 COMPREHENSIVE BOOMERANG GUIDE

**Date:** April 5, 2025
**Author:** Keystone (Nova #002)
**Version:** 1.0

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Creating Custom Modes](#creating-custom-modes)
3. [Switching Between Modes](#switching-between-modes)
4. [Custom Instructions for Modes](#custom-instructions-for-modes)
5. [Redis CLI for Communications](#redis-cli-for-communications)
6. [Redis CLI for Task Management](#redis-cli-for-task-management)
7. [Parent/Child Task Planning](#parentchild-task-planning)
8. [Delegating Tasks to Other Novas](#delegating-tasks-to-other-novas)
9. [Advanced Workflows](#advanced-workflows)
10. [Troubleshooting](#troubleshooting)

## 🌟 Introduction <a name="introduction"></a>

The Boomerang system is a powerful workflow orchestration tool that enables complex task management across multiple specialized Nova modes. This comprehensive guide will walk you through all aspects of the Boomerang system, from creating custom modes to delegating tasks and managing communications.

### Core Concepts

- **Modes**: Specialized configurations that optimize a Nova for specific types of tasks
- **Task Delegation**: Breaking down complex tasks into subtasks assigned to appropriate modes
- **Redis Streams**: The communication backbone for Nova interactions
- **Parent/Child Tasks**: Hierarchical task relationships for complex workflows

## 🛠️ Creating Custom Modes <a name="creating-custom-modes"></a>

Custom modes allow you to create specialized configurations for specific types of tasks. Each mode has its own capabilities, instructions, and file access restrictions.

### Step 1: Create Mode Configuration File

Create a new JSON file in the format `your_mode_config.json` with the following structure:

```json
{
  "name": "Your Mode Name",
  "slug": "your_mode_slug",
  "description": "Detailed description of what this mode specializes in",
  "version": "1.0.0",
  "role": "Detailed role description that will guide the Nova's behavior in this mode",
  "capabilities": [
    "capability_1",
    "capability_2",
    "capability_3"
  ],
  "file_restrictions": {
    "allowed_patterns": [
      "pattern_1",
      "pattern_2"
    ],
    "blocked_patterns": [
      "pattern_3",
      "pattern_4"
    ]
  },
  "instructions": [
    "Instruction 1 for how the Nova should behave in this mode",
    "Instruction 2 for how the Nova should behave in this mode",
    "Instruction 3 for how the Nova should behave in this mode"
  ]
}
```

### Step 2: Create Mode Implementation File

Create a TypeScript file in the format `your_mode.ts` with the following structure:

```typescript
import { FastifyInstance } from 'fastify';
import { PrismaClient } from '@prisma/client';
import { Redis } from 'ioredis';

export class YourMode {
  private prisma: PrismaClient;
  private redis: Redis;

  constructor(prisma: PrismaClient, redis: Redis) {
    this.prisma = prisma;
    this.redis = redis;
  }

  // Register routes with Fastify
  public registerRoutes(fastify: FastifyInstance): void {
    // Define your API endpoints here
    fastify.post('/api/v1/your-mode/endpoint', this.yourEndpointHandler.bind(this));
  }

  // Initialize Redis stream listeners
  public initializeStreamListeners(): void {
    // Set up Redis stream listeners here
    this.redis.xgroup('CREATE', 'nova:your-mode', 'your-mode-group', '$', 'MKSTREAM', (err) => {
      if (err && !err.message.includes('BUSYGROUP')) {
        console.error('Error creating consumer group:', err);
      }
      
      this.consumeEvents();
    });
  }

  // Consume events from Redis stream
  private async consumeEvents(): Promise<void> {
    // Implement event consumption logic here
  }

  // Your endpoint handler
  private async yourEndpointHandler(request: any, reply: any): Promise<void> {
    // Implement endpoint logic here
  }
}
```

### Step 3: Register Your Mode

Add your mode to the `index.ts` file:

```typescript
import { YourMode } from './your_mode';

// In the initialization section
const yourMode = new YourMode(prisma, redis);
yourMode.registerRoutes(fastify);
yourMode.initializeStreamListeners();
```

### Step 4: Update Available Modes

Add your mode to the `available_modes` array in the Boomerang mode configuration:

```json
"available_modes": [
  {
    "slug": "your_mode_slug",
    "name": "Your Mode Name",
    "description": "Description of your mode",
    "best_for": ["use case 1", "use case 2", "use case 3"]
  },
  // Other existing modes...
]
```

### Example: Creating a Research Mode

Here's an example of creating a Research mode specialized in gathering and analyzing information:

**research_mode_config.json**:
```json
{
  "name": "Research",
  "slug": "research",
  "description": "Specialized in gathering, analyzing, and synthesizing information",
  "version": "1.0.0",
  "role": "You are a research specialist who excels at gathering information, analyzing data, and synthesizing findings into comprehensive reports.",
  "capabilities": [
    "information_gathering",
    "data_analysis",
    "report_generation",
    "source_verification"
  ],
  "file_restrictions": {
    "allowed_patterns": [
      ".*\\.md$",
      ".*\\.txt$",
      ".*\\.csv$",
      ".*\\.json$"
    ],
    "blocked_patterns": [
      ".*\\.js$",
      ".*\\.ts$",
      ".*\\.py$"
    ]
  },
  "instructions": [
    "Focus on gathering comprehensive information from reliable sources",
    "Analyze data thoroughly, looking for patterns and insights",
    "Synthesize findings into clear, well-structured reports",
    "Always verify sources and cite them appropriately",
    "Maintain objectivity and avoid bias in your analysis"
  ]
}
```

## 🔄 Switching Between Modes <a name="switching-between-modes"></a>

The Boomerang system allows seamless switching between modes to leverage specialized capabilities for different tasks.

### Using the `switch_mode` Tool

To switch modes, use the `switch_mode` tool with the following parameters:

- `mode_slug`: The slug of the mode to switch to (e.g., "code", "architect", "debug", "ask")
- `reason`: The reason for switching modes (optional but recommended)

```xml
<switch_mode>
<mode_slug>code</mode_slug>
<reason>Need to implement a new feature</reason>
</switch_mode>
```

### Mode Switching Best Practices

1. **Clear Reasoning**: Always provide a clear reason for switching modes
2. **Complete Current Task**: Finish your current task before switching modes when possible
3. **Context Preservation**: Ensure all relevant context is passed to the new mode
4. **Return Strategy**: Consider how and when to return to the original mode if needed

### Example: Switching from Architect to Code Mode

```xml
<switch_mode>
<mode_slug>code</mode_slug>
<reason>Need to implement the database schema that was designed in Architect mode</reason>
</switch_mode>
```

## 📝 Custom Instructions for Modes <a name="custom-instructions-for-modes"></a>

Custom instructions allow you to fine-tune how a mode operates for specific tasks or projects.

### Setting Custom Instructions

Custom instructions are defined in the mode configuration file under the `instructions` array:

```json
"instructions": [
  "Instruction 1 for how the Nova should behave in this mode",
  "Instruction 2 for how the Nova should behave in this mode",
  "Instruction 3 for how the Nova should behave in this mode"
]
```

### Instruction Types

1. **Behavioral Instructions**: Guide how the Nova should approach tasks
2. **Procedural Instructions**: Define specific steps or processes to follow
3. **Constraint Instructions**: Set boundaries or limitations
4. **Priority Instructions**: Establish what to focus on or prioritize

### Example: Custom Instructions for Code Mode

```json
"instructions": [
  "Always start by understanding the requirements before writing code",
  "Follow the project's coding standards and patterns",
  "Write comprehensive tests for all new functionality",
  "Document your code with clear comments and function descriptions",
  "Consider performance implications of your implementation",
  "Refactor existing code when necessary to improve quality",
  "Ensure backward compatibility unless explicitly instructed otherwise"
]
```

### Updating Instructions at Runtime

You can update instructions at runtime by sending a message to the appropriate Redis stream:

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:mode:instructions '*' \
  type update \
  mode "code" \
  instructions "Instruction 1\nInstruction 2\nInstruction 3" \
  timestamp "$(date +%s)"
```

## 📡 Redis CLI for Communications <a name="redis-cli-for-communications"></a>

Redis Streams serve as the communication backbone for the Nova ecosystem, enabling real-time messaging between Novas and teams.

### Stream Naming Conventions

- **Direct Communication**: `[division].[nova].direct` (e.g., `commsops.keystone.direct`)
- **Team Communication**: `[division].team` (e.g., `commsops.team`)
- **All Divisions**: `all.divisions.direct`
- **Status Updates**: `[system].status` (e.g., `mcp.servers.status`)
- **Urgent Communications**: `urgent.communications`

### Sending Messages

Use the `XADD` command to send messages to a stream:

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD [STREAM] '*' \
  type message \
  from "[YOUR_NOVA]" \
  content "Your message here" \
  timestamp "$(date +%s)" \
  priority "normal"
```

Example:

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD commsops.keystone.direct '*' \
  type message \
  from "Echo" \
  content "Database connection issue resolved" \
  timestamp "$(date +%s)" \
  priority "high"
```

### Reading Messages

Use the `XRANGE` command to read messages from a stream:

```bash
# Read all messages
redis-cli -c -p 7000 -a d5d7817937232ca5 XRANGE [STREAM] - +

# Read the last 5 messages
redis-cli -c -p 7000 -a d5d7817937232ca5 XREVRANGE [STREAM] + - COUNT 5

# Read messages after a specific ID
redis-cli -c -p 7000 -a d5d7817937232ca5 XRANGE [STREAM] [START_ID] +
```

### Monitoring Streams in Real-Time

Use the `XREAD BLOCK` command to monitor streams for new messages:

```bash
# Monitor a single stream
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS [STREAM] '$'

# Monitor multiple streams
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS [STREAM1] [STREAM2] [STREAM3] '$' '$' '$'
```

### Communication Patterns

1. **Direct Communication**: Send messages directly to a specific Nova
2. **Broadcast Communication**: Send messages to all Novas in a division or all divisions
3. **Status Updates**: Share system status information
4. **Urgent Notifications**: Send high-priority messages that require immediate attention

## 📊 Redis CLI for Task Management <a name="redis-cli-for-task-management"></a>

Redis Streams also power the task management system, enabling task creation, assignment, updates, and completion.

### Task Streams

- **Task Creation**: `nova:tasks:create`
- **Task Assignment**: `nova:tasks:assign`
- **Task Updates**: `nova:tasks:update`
- **Task Completion**: `nova:tasks:complete`
- **Task Events**: `nova:tasks` (aggregated stream of all task events)

### Creating Tasks

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:create '*' \
  type "task.created" \
  title "Task title" \
  description "Task description" \
  priority "medium" \
  assignee "nova_id" \
  due_date "$(date -d '+2 days' +%s)" \
  created_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Updating Task Status

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:update '*' \
  type "task.status_updated" \
  task_id "task_id" \
  status "in_progress" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Completing Tasks

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "task_id" \
  result "Task completion details" \
  completed_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Monitoring Task Events

```bash
# Monitor all task events
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS nova:tasks '$'

# Monitor specific task events
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS nova:tasks:create nova:tasks:complete '$' '$'
```

## 🌲 Parent/Child Task Planning <a name="parentchild-task-planning"></a>

The Boomerang system supports hierarchical task relationships, allowing complex workflows to be broken down into manageable subtasks.

### Creating Parent Tasks

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:create '*' \
  type "task.created" \
  title "Parent task title" \
  description "Parent task description" \
  priority "high" \
  assignee "nova_id" \
  is_parent "true" \
  created_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Creating Child Tasks

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:create '*' \
  type "task.created" \
  title "Child task title" \
  description "Child task description" \
  priority "medium" \
  assignee "nova_id" \
  parent_id "parent_task_id" \
  created_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Task Dependencies

You can specify dependencies between tasks to enforce execution order:

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:update '*' \
  type "task.dependency_added" \
  task_id "dependent_task_id" \
  depends_on "prerequisite_task_id" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Task Planning Strategies

1. **Top-Down Planning**: Start with a high-level parent task and break it down into subtasks
2. **Bottom-Up Planning**: Identify individual tasks and group them under parent tasks
3. **Milestone-Based Planning**: Create parent tasks for major milestones and subtasks for steps to reach each milestone
4. **Parallel Track Planning**: Create separate parent tasks for different tracks of work that can proceed in parallel

### Example: Full Task Hierarchy

```
Parent Task: "Implement User Authentication System"
├── Child Task 1: "Design database schema for users" (Assigned to: Architect mode)
├── Child Task 2: "Implement user registration API" (Assigned to: Code mode)
│   ├── Depends on: Child Task 1
│   └── Child Task 2.1: "Write unit tests for registration API" (Assigned to: Code mode)
├── Child Task 3: "Implement login API" (Assigned to: Code mode)
│   └── Depends on: Child Task 1
└── Child Task 4: "Create documentation" (Assigned to: Ask mode)
    └── Depends on: Child Tasks 2 and 3
```

## 🔄 Delegating Tasks to Other Novas <a name="delegating-tasks-to-other-novas"></a>

The Boomerang system excels at task delegation, allowing complex workflows to be distributed across specialized Novas.

### Using the `new_task` Tool

The primary method for delegating tasks is the `new_task` tool:

```xml
<new_task>
<mode>target_mode_slug</mode>
<message>Comprehensive task description with all necessary context</message>
</new_task>
```

### Delegation Best Practices

1. **Mode Selection**: Choose the most appropriate mode for each subtask
2. **Clear Instructions**: Provide comprehensive instructions with all necessary context
3. **Scope Definition**: Clearly define the scope of the subtask
4. **Expected Output**: Specify what the output should look like
5. **Completion Signal**: Instruct the Nova to signal completion using the `attempt_completion` tool

### Example: Delegating a Database Schema Design

```xml
<new_task>
<mode>architect</mode>
<message>
# Database Schema Design for User Authentication

## Context
We're building a user authentication system that needs to support:
- User registration with email verification
- Password reset functionality
- OAuth integration with Google, Facebook, and Twitter
- Role-based access control
- Session management

## Task
Design a comprehensive database schema for this authentication system. Include:
1. All necessary tables with field definitions
2. Relationships between tables
3. Indexes for performance optimization
4. Constraints for data integrity

## Deliverables
1. Complete schema definition in PostgreSQL format
2. Entity-relationship diagram (text-based is fine)
3. Brief explanation of design decisions

When complete, use the `attempt_completion` tool with a summary of your design.
</message>
</new_task>
```

### Tracking Delegated Tasks

You can track delegated tasks using the Redis streams:

```bash
# Monitor task creation events
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS nova:tasks:create '$'

# Check status of specific task
redis-cli -c -p 7000 -a d5d7817937232ca5 XRANGE nova:tasks - + COUNT 1000 | grep "task_id" "your_task_id"
```

### Task Coordination Patterns

1. **Sequential Delegation**: Tasks are delegated one after another, with each depending on the previous
2. **Parallel Delegation**: Multiple tasks are delegated simultaneously to different Novas
3. **Hierarchical Delegation**: A parent task is broken down into subtasks, which may be further delegated
4. **Expertise-Based Delegation**: Tasks are delegated based on the specialized capabilities of different modes

## 🔄 Advanced Workflows <a name="advanced-workflows"></a>

The Boomerang system supports sophisticated workflows for complex projects.

### Workflow State Management

The Boomerang mode maintains workflow state for complex task orchestration:

```typescript
interface WorkflowState {
  parentTaskId: string;
  subtasks: {
    [subtaskId: string]: {
      id: string;
      title: string;
      mode: string;
      status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
      result?: string;
      dependsOn: string[];
    }
  };
  completedSubtasks: string[];
  pendingSubtasks: string[];
  currentSubtasks: string[];
}
```

### Creating Workflows

```bash
# Create a workflow for a parent task
curl -X POST http://localhost:3000/api/v1/boomerang/workflows \
  -H "Content-Type: application/json" \
  -d '{"parentTaskId": "parent_task_id"}'
```

### Adding Subtasks to Workflows

```bash
# Add a subtask to a workflow
curl -X POST http://localhost:3000/api/v1/boomerang/workflows/{workflowId}/subtasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Subtask title",
    "description": "Subtask description",
    "mode": "code",
    "expectedOutput": "Expected output description",
    "dependencies": ["dependency_task_id"]
  }'
```

### Workflow Patterns

1. **Waterfall Workflow**: Sequential tasks with strict dependencies
2. **Agile Workflow**: Iterative tasks with frequent feedback and adaptation
3. **Parallel Workflow**: Independent tasks executed simultaneously
4. **Hybrid Workflow**: Combination of sequential and parallel tasks

### Example: Full-Stack Development Workflow

```
1. Create parent task "Build e-commerce website"
2. Create workflow for parent task
3. Add subtasks:
   - "Design database schema" (Architect mode)
   - "Implement backend API" (Code mode, depends on schema design)
   - "Create frontend UI" (Code mode, can run in parallel with backend)
   - "Write documentation" (Ask mode, depends on all other tasks)
4. Monitor workflow progress
5. Synthesize results when all subtasks complete
```

## 🔧 Troubleshooting <a name="troubleshooting"></a>

Common issues and their solutions when working with the Boomerang system.

### Mode Switching Issues

**Problem**: Mode switch fails or doesn't apply correctly
**Solution**:
1. Ensure the mode slug is correct and the mode exists
2. Check for any pending operations that might be blocking the switch
3. Try completing the current task before switching

### Task Delegation Issues

**Problem**: Delegated tasks are not being picked up
**Solution**:
1. Verify the target mode is available and correctly specified
2. Check Redis connectivity and stream configuration
3. Ensure the task message contains all necessary context
4. Verify the task is being published to the correct stream

### Redis Communication Issues

**Problem**: Redis messages not being sent or received
**Solution**:
1. Check Redis connection parameters
2. Verify Redis server is running
3. Ensure correct stream names are being used
4. Check for authentication issues

```bash
# Test Redis connectivity
redis-cli -c -p 7000 -a d5d7817937232ca5 ping

# Check if stream exists
redis-cli -c -p 7000 -a d5d7817937232ca5 TYPE [STREAM_NAME]
```

### Workflow State Issues

**Problem**: Workflow state is inconsistent or tasks are stuck
**Solution**:
1. Check the workflow state in the database
2. Verify task dependencies are correctly configured
3. Check for failed tasks that might be blocking others
4. Manually update task status if necessary

```bash
# Get workflow state
curl -X GET http://localhost:3000/api/v1/boomerang/workflows/{workflowId}

# Force complete a stuck task
curl -X POST http://localhost:3000/api/v1/boomerang/workflows/{workflowId}/subtasks/{subtaskId}/complete \
  -H "Content-Type: application/json" \
  -d '{"result": "Task completed manually"}'
```

## 📚 Additional Resources

- [Boomerang API Reference](./API_REFERENCE.md)
- [Redis Streams Documentation](../docs/redis-streams/README.md)
- [Mode Configuration Guide](./MODE_CONFIGURATION.md)
- [Task Management Best Practices](./TASK_MANAGEMENT.md)

---

This comprehensive guide should provide all the information needed to effectively use the Boomerang system for complex workflow orchestration. If you have any questions or need further assistance, please contact the CommsOps team.