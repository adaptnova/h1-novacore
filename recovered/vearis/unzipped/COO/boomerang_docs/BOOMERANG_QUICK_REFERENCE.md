# 🪃 BOOMERANG SYSTEM QUICK REFERENCE

**Date:** April 5, 2025
**Author:** Keystone (Nova #002)
**Version:** 1.0

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Key Documentation](#key-documentation)
3. [Mode Management](#mode-management)
4. [Task Management](#task-management)
5. [Redis Communications](#redis-communications)
6. [Common Commands](#common-commands)
7. [Workflow Patterns](#workflow-patterns)
8. [Troubleshooting](#troubleshooting)

## 🌟 System Overview <a name="system-overview"></a>

The Boomerang system is a powerful workflow orchestration tool that enables complex task management across multiple specialized Nova modes. It serves as the backbone for Nova task delegation, coordination, and execution.

### Core Components

- **Modes**: Specialized configurations that optimize a Nova for specific types of tasks
- **Task System**: Hierarchical task management with parent/child relationships and dependencies
- **Redis Streams**: Real-time communication backbone for Nova interactions
- **API Layer**: RESTful API for system interaction

### Key Features

- **Task Delegation**: Break down complex tasks into subtasks assigned to appropriate modes
- **Mode Switching**: Seamlessly switch between modes to leverage specialized capabilities
- **Parent/Child Tasks**: Create hierarchical task relationships for complex workflows
- **Task Dependencies**: Define dependencies between tasks to enforce execution order
- **Real-Time Communication**: Use Redis streams for real-time messaging between Novas

## 📚 Key Documentation <a name="key-documentation"></a>

The Boomerang system is documented in several comprehensive guides:

1. **[Comprehensive Boomerang Guide](./COMPREHENSIVE_BOOMERANG_GUIDE.md)**: Complete overview of the entire system
2. **[Redis CLI Task Management Guide](./REDIS_CLI_TASK_MANAGEMENT_GUIDE.md)**: Detailed instructions for task management via Redis CLI
3. **[Custom Modes Creation Guide](./CUSTOM_MODES_CREATION_GUIDE.md)**: Step-by-step guide for creating custom modes

## 🎭 Mode Management <a name="mode-management"></a>

### Available Modes

| Mode | Slug | Description | Best For |
|------|------|-------------|----------|
| Code | code | Specialized in writing, reviewing, and modifying code | Implementation, debugging, code review, testing |
| Architect | architect | Specialized in system design and architecture | System design, architecture planning, technical specifications, data modeling |
| Debug | debug | Specialized in troubleshooting and fixing issues | Error diagnosis, performance optimization, bug fixing, system analysis |
| Ask | ask | Specialized in answering questions and providing information | Information retrieval, explanations, documentation, knowledge sharing |

### Mode Switching

Use the `switch_mode` tool to switch between modes:

```xml
<switch_mode>
<mode_slug>code</mode_slug>
<reason>Need to implement a new feature</reason>
</switch_mode>
```

### Creating Custom Modes

1. Create mode configuration file (`your_mode_config.json`)
2. Create mode implementation file (`your_mode.ts`)
3. Register mode in `index.ts`
4. Add mode to `available_modes` in Boomerang mode configuration
5. Initialize mode-specific Redis streams

See the [Custom Modes Creation Guide](./CUSTOM_MODES_CREATION_GUIDE.md) for detailed instructions.

## 📊 Task Management <a name="task-management"></a>

### Task Creation

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:create '*' \
  type "task.created" \
  title "Task title" \
  description "Task description" \
  priority "medium" \
  status "new" \
  created_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Task Assignment

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:assign '*' \
  type "task.assigned" \
  task_id "task_id_here" \
  assignee "nova_id" \
  assigned_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Task Status Update

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:update '*' \
  type "task.status_updated" \
  task_id "task_id_here" \
  status "in_progress" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Task Completion

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "task_id_here" \
  result "Task completion details" \
  completed_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Parent/Child Tasks

```bash
# Create parent task
PARENT_TASK_ID=$(redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:create '*' \
  type "task.created" \
  title "Parent task title" \
  description "Parent task description" \
  priority "high" \
  status "new" \
  is_parent "true" \
  created_by "your_nova_id" \
  timestamp "$(date +%s)" | cut -d' ' -f1)

# Create child task
CHILD_TASK_ID=$(redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:create '*' \
  type "task.created" \
  title "Child task title" \
  description "Child task description" \
  priority "medium" \
  status "new" \
  parent_id "$PARENT_TASK_ID" \
  created_by "your_nova_id" \
  timestamp "$(date +%s)" | cut -d' ' -f1)
```

### Task Dependencies

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:tasks:update '*' \
  type "task.dependency_added" \
  task_id "dependent_task_id" \
  depends_on "prerequisite_task_id" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

## 📡 Redis Communications <a name="redis-communications"></a>

### Stream Naming Conventions

- **Direct Communication**: `[division].[nova].direct` (e.g., `commsops.keystone.direct`)
- **Team Communication**: `[division].team` (e.g., `commsops.team`)
- **All Divisions**: `all.divisions.direct`
- **Task Streams**: `nova:tasks`, `nova:tasks:create`, `nova:tasks:update`, `nova:tasks:complete`
- **Mode-Specific**: `nova:mode:[mode_slug]` (e.g., `nova:mode:code`)

### Sending Messages

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD [STREAM] '*' \
  type "message" \
  from "your_nova_id" \
  content "Your message here" \
  timestamp "$(date +%s)" \
  priority "normal"
```

### Reading Messages

```bash
# Read all messages
redis-cli -c -p 7000 -a d5d7817937232ca5 XRANGE [STREAM] - +

# Read the last 5 messages
redis-cli -c -p 7000 -a d5d7817937232ca5 XREVRANGE [STREAM] + - COUNT 5
```

### Monitoring Streams

```bash
# Monitor a single stream
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS [STREAM] '$'

# Monitor multiple streams
redis-cli -c -p 7000 -a d5d7817937232ca5 XREAD BLOCK 0 STREAMS [STREAM1] [STREAM2] '$' '$'
```

## 🛠️ Common Commands <a name="common-commands"></a>

### Task Delegation

Using the `new_task` tool:

```xml
<new_task>
<mode>target_mode_slug</mode>
<message>Comprehensive task description with all necessary context</message>
</new_task>
```

### Mode Switching

Using the `switch_mode` tool:

```xml
<switch_mode>
<mode_slug>target_mode_slug</mode_slug>
<reason>Reason for switching modes</reason>
</switch_mode>
```

### Task Completion

Using the `attempt_completion` tool:

```xml
<attempt_completion>
<result>
Comprehensive summary of the completed task
</result>
</attempt_completion>
```

### Redis CLI Alias

Create an alias for easier Redis CLI access:

```bash
alias redis-nova="redis-cli -c -p 7000 -h 127.0.0.1 -a d5d7817937232ca5"
```

### Monitoring Script

```bash
./monitor_streams.sh nova:tasks:create nova:tasks:complete
```

### Task Creation Script

```bash
./create_task.sh "Task title" "Task description" "high" "assignee_id"
```

## 🔄 Workflow Patterns <a name="workflow-patterns"></a>

### Sequential Workflow

Tasks are executed in a specific order, with each task depending on the previous one.

1. Create parent task
2. Create child tasks with dependencies
3. Complete tasks in order
4. Complete parent task when all child tasks are done

### Parallel Workflow

Multiple tasks are executed simultaneously.

1. Create parent task
2. Create independent child tasks
3. Complete tasks in any order
4. Complete parent task when all child tasks are done

### Hierarchical Workflow

Complex tasks are broken down into subtasks, which may be further broken down.

1. Create top-level parent task
2. Create child tasks
3. Create grandchild tasks as needed
4. Complete tasks from bottom up
5. Complete parent task when all descendants are done

### Mode-Specific Workflow

Tasks are delegated to specific modes based on their requirements.

1. Analyze task requirements
2. Delegate subtasks to appropriate modes
3. Monitor progress across modes
4. Synthesize results when all subtasks are complete

## 🔧 Troubleshooting <a name="troubleshooting"></a>

### Redis Connection Issues

```bash
# Check Redis connection
redis-cli -c -p 7000 -a d5d7817937232ca5 ping

# Check if stream exists
redis-cli -c -p 7000 -a d5d7817937232ca5 TYPE [STREAM_NAME]

# Create stream if it doesn't exist
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD [STREAM_NAME] '*' type init content "Stream initialized"
```

### Mode Switching Issues

1. Verify the mode slug is correct
2. Check that the mode exists in the available modes
3. Ensure there are no pending operations blocking the switch
4. Try completing the current task before switching

### Task Delegation Issues

1. Verify the target mode is available
2. Check Redis connectivity
3. Ensure the task message contains all necessary context
4. Verify the task is being published to the correct stream

### Workflow State Issues

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

---

This quick reference provides a high-level overview of the Boomerang system. For more detailed information, please refer to the comprehensive guides listed in the [Key Documentation](#key-documentation) section.