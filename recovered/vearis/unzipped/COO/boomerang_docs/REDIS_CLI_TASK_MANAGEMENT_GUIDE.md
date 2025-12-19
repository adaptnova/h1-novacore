# 📊 REDIS CLI TASK MANAGEMENT GUIDE

**Date:** April 5, 2025
**Author:** Keystone (Nova #002)
**Version:** 1.0

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Redis CLI Setup](#redis-cli-setup)
3. [Task Creation](#task-creation)
4. [Task Assignment](#task-assignment)
5. [Task Status Updates](#task-status-updates)
6. [Task Completion](#task-completion)
7. [Parent/Child Task Management](#parentchild-task-management)
8. [Task Dependencies](#task-dependencies)
9. [Task Querying](#task-querying)
10. [Monitoring Task Streams](#monitoring-task-streams)
11. [Practical Examples](#practical-examples)
12. [Automation Scripts](#automation-scripts)

## 🌟 Introduction <a name="introduction"></a>

This guide provides detailed instructions for using Redis CLI to manage tasks within the Nova ecosystem. Redis Streams serve as the backbone for our task management system, enabling real-time task creation, assignment, updates, and completion.

## 🔧 Redis CLI Setup <a name="redis-cli-setup"></a>

Before you begin, ensure you have Redis CLI installed and configured to connect to the Redis cluster:

```bash
# Test connection to Redis cluster
redis-cli -c -p 7000 -a d5d7817937232ca5 ping
```

Expected output:
```
PONG
```

For convenience, you can set environment variables to avoid typing credentials repeatedly:

```bash
export REDIS_PASSWORD="d5d7817937232ca5"
export REDIS_PORT=7000
export REDIS_HOST="127.0.0.1"
```

Then create an alias for easier access:

```bash
alias redis-nova="redis-cli -c -p $REDIS_PORT -h $REDIS_HOST -a $REDIS_PASSWORD"
```

## 🆕 Task Creation <a name="task-creation"></a>

### Basic Task Creation

```bash
redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement login functionality" \
  description "Create a secure login system with JWT authentication" \
  priority "high" \
  status "new" \
  created_by "keystone" \
  timestamp "$(date +%s)"
```

### Task with Assignee

```bash
redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement login functionality" \
  description "Create a secure login system with JWT authentication" \
  priority "high" \
  status "new" \
  assignee "code-nova" \
  created_by "keystone" \
  timestamp "$(date +%s)"
```

### Task with Due Date

```bash
redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement login functionality" \
  description "Create a secure login system with JWT authentication" \
  priority "high" \
  status "new" \
  assignee "code-nova" \
  due_date "$(date -d '+2 days' +%s)" \
  created_by "keystone" \
  timestamp "$(date +%s)"
```

### Task with Tags

```bash
redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement login functionality" \
  description "Create a secure login system with JWT authentication" \
  priority "high" \
  status "new" \
  assignee "code-nova" \
  tags "authentication,security,backend" \
  created_by "keystone" \
  timestamp "$(date +%s)"
```

## 📝 Task Assignment <a name="task-assignment"></a>

### Assign Task to Nova

```bash
redis-nova XADD nova:tasks:assign '*' \
  type "task.assigned" \
  task_id "task_id_here" \
  assignee "code-nova" \
  assigned_by "keystone" \
  timestamp "$(date +%s)"
```

### Assign Task to Mode

```bash
redis-nova XADD nova:tasks:assign '*' \
  type "task.assigned" \
  task_id "task_id_here" \
  mode "code" \
  assigned_by "keystone" \
  timestamp "$(date +%s)"
```

### Self-Assignment (Claiming a Task)

```bash
redis-nova XADD nova:tasks:assign '*' \
  type "task.claimed" \
  task_id "task_id_here" \
  assignee "your_nova_id" \
  timestamp "$(date +%s)"
```

## 🔄 Task Status Updates <a name="task-status-updates"></a>

### Update Task Status

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.status_updated" \
  task_id "task_id_here" \
  status "in_progress" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

Available statuses:
- `new` - Task has been created but not started
- `in_progress` - Task is actively being worked on
- `blocked` - Task is blocked by a dependency or issue
- `review` - Task is complete and awaiting review
- `completed` - Task has been completed and verified
- `cancelled` - Task has been cancelled

### Update Task Priority

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.priority_updated" \
  task_id "task_id_here" \
  priority "critical" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

Available priorities:
- `low` - Task is not urgent
- `medium` - Task has normal priority
- `high` - Task is important and should be prioritized
- `critical` - Task is urgent and requires immediate attention

### Add Comment to Task

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.comment_added" \
  task_id "task_id_here" \
  comment "This is a comment on the task" \
  author "your_nova_id" \
  timestamp "$(date +%s)"
```

### Update Task Description

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.description_updated" \
  task_id "task_id_here" \
  description "Updated task description" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

## ✅ Task Completion <a name="task-completion"></a>

### Complete Task with Result

```bash
redis-nova XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "task_id_here" \
  result "Task has been completed successfully. The login functionality is now implemented with JWT authentication." \
  completed_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Complete Task with Artifacts

```bash
redis-nova XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "task_id_here" \
  result "Task has been completed successfully." \
  artifacts "file1.js,file2.js,file3.js" \
  completed_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Complete Task with Issues

```bash
redis-nova XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "task_id_here" \
  result "Task has been completed with some issues." \
  issues "Issue 1: Performance could be improved. Issue 2: Need to add more tests." \
  completed_by "your_nova_id" \
  timestamp "$(date +%s)"
```

## 🌲 Parent/Child Task Management <a name="parentchild-task-management"></a>

### Create Parent Task

```bash
redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement Authentication System" \
  description "Create a complete authentication system for the application" \
  priority "high" \
  status "new" \
  is_parent "true" \
  created_by "keystone" \
  timestamp "$(date +%s)"
```

### Create Child Task

```bash
redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement Login API" \
  description "Create the login API endpoint" \
  priority "high" \
  status "new" \
  parent_id "parent_task_id_here" \
  created_by "keystone" \
  timestamp "$(date +%s)"
```

### Link Existing Tasks as Parent/Child

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.parent_linked" \
  task_id "child_task_id_here" \
  parent_id "parent_task_id_here" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Get Child Tasks for Parent

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "parent_id" | grep "parent_task_id_here"
```

## 🔗 Task Dependencies <a name="task-dependencies"></a>

### Add Task Dependency

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.dependency_added" \
  task_id "dependent_task_id_here" \
  depends_on "prerequisite_task_id_here" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Remove Task Dependency

```bash
redis-nova XADD nova:tasks:update '*' \
  type "task.dependency_removed" \
  task_id "dependent_task_id_here" \
  depends_on "prerequisite_task_id_here" \
  updated_by "your_nova_id" \
  timestamp "$(date +%s)"
```

### Check Task Dependencies

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "task_id" | grep "dependent_task_id_here" | grep -A 5 "dependency"
```

## 🔍 Task Querying <a name="task-querying"></a>

### Get Task by ID

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "task_id" | grep -A 20 "task_id_here"
```

### Get Tasks by Assignee

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "assignee" | grep -A 20 "assignee_id_here"
```

### Get Tasks by Status

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "status" | grep -A 20 "in_progress"
```

### Get Tasks by Priority

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "priority" | grep -A 20 "high"
```

### Get Tasks by Tag

```bash
redis-nova XRANGE nova:tasks - + COUNT 1000 | grep -A 20 "tags" | grep -A 20 "security"
```

## 👀 Monitoring Task Streams <a name="monitoring-task-streams"></a>

### Monitor All Task Events

```bash
redis-nova XREAD BLOCK 0 STREAMS nova:tasks '$'
```

### Monitor Task Creation Events

```bash
redis-nova XREAD BLOCK 0 STREAMS nova:tasks:create '$'
```

### Monitor Task Assignment Events

```bash
redis-nova XREAD BLOCK 0 STREAMS nova:tasks:assign '$'
```

### Monitor Task Update Events

```bash
redis-nova XREAD BLOCK 0 STREAMS nova:tasks:update '$'
```

### Monitor Task Completion Events

```bash
redis-nova XREAD BLOCK 0 STREAMS nova:tasks:complete '$'
```

### Monitor Multiple Task Streams

```bash
redis-nova XREAD BLOCK 0 STREAMS nova:tasks:create nova:tasks:complete '$' '$'
```

## 🔄 Practical Examples <a name="practical-examples"></a>

### Complete Task Workflow Example

```bash
# 1. Create a parent task
PARENT_TASK_ID=$(redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement Authentication System" \
  description "Create a complete authentication system for the application" \
  priority "high" \
  status "new" \
  is_parent "true" \
  created_by "keystone" \
  timestamp "$(date +%s)" | cut -d' ' -f1)

echo "Created parent task with ID: $PARENT_TASK_ID"

# 2. Create child tasks
CHILD_TASK_1_ID=$(redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Design Database Schema" \
  description "Design the database schema for user authentication" \
  priority "high" \
  status "new" \
  parent_id "$PARENT_TASK_ID" \
  created_by "keystone" \
  timestamp "$(date +%s)" | cut -d' ' -f1)

echo "Created child task 1 with ID: $CHILD_TASK_1_ID"

CHILD_TASK_2_ID=$(redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement Login API" \
  description "Create the login API endpoint" \
  priority "high" \
  status "new" \
  parent_id "$PARENT_TASK_ID" \
  created_by "keystone" \
  timestamp "$(date +%s)" | cut -d' ' -f1)

echo "Created child task 2 with ID: $CHILD_TASK_2_ID"

# 3. Add dependency between child tasks
redis-nova XADD nova:tasks:update '*' \
  type "task.dependency_added" \
  task_id "$CHILD_TASK_2_ID" \
  depends_on "$CHILD_TASK_1_ID" \
  updated_by "keystone" \
  timestamp "$(date +%s)"

echo "Added dependency: Task 2 depends on Task 1"

# 4. Assign child task 1 to architect mode
redis-nova XADD nova:tasks:assign '*' \
  type "task.assigned" \
  task_id "$CHILD_TASK_1_ID" \
  mode "architect" \
  assigned_by "keystone" \
  timestamp "$(date +%s)"

echo "Assigned child task 1 to architect mode"

# 5. Update child task 1 status to in progress
redis-nova XADD nova:tasks:update '*' \
  type "task.status_updated" \
  task_id "$CHILD_TASK_1_ID" \
  status "in_progress" \
  updated_by "architect-nova" \
  timestamp "$(date +%s)"

echo "Updated child task 1 status to in progress"

# 6. Complete child task 1
redis-nova XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "$CHILD_TASK_1_ID" \
  result "Database schema design completed. Created users table with necessary fields for authentication." \
  completed_by "architect-nova" \
  timestamp "$(date +%s)"

echo "Completed child task 1"

# 7. Assign child task 2 to code mode
redis-nova XADD nova:tasks:assign '*' \
  type "task.assigned" \
  task_id "$CHILD_TASK_2_ID" \
  mode "code" \
  assigned_by "keystone" \
  timestamp "$(date +%s)"

echo "Assigned child task 2 to code mode"

# 8. Update child task 2 status to in progress
redis-nova XADD nova:tasks:update '*' \
  type "task.status_updated" \
  task_id "$CHILD_TASK_2_ID" \
  status "in_progress" \
  updated_by "code-nova" \
  timestamp "$(date +%s)"

echo "Updated child task 2 status to in progress"

# 9. Complete child task 2
redis-nova XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "$CHILD_TASK_2_ID" \
  result "Login API implemented with JWT authentication." \
  artifacts "auth.js,login.js,jwt.js" \
  completed_by "code-nova" \
  timestamp "$(date +%s)"

echo "Completed child task 2"

# 10. Complete parent task
redis-nova XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "$PARENT_TASK_ID" \
  result "Authentication system implemented successfully." \
  completed_by "keystone" \
  timestamp "$(date +%s)"

echo "Completed parent task"
```

### Task Delegation Workflow

```bash
# 1. Create a task
TASK_ID=$(redis-nova XADD nova:tasks:create '*' \
  type "task.created" \
  title "Implement Search Functionality" \
  description "Create a search feature for the application" \
  priority "medium" \
  status "new" \
  created_by "keystone" \
  timestamp "$(date +%s)" | cut -d' ' -f1)

echo "Created task with ID: $TASK_ID"

# 2. Delegate task to code mode
redis-nova XADD nova:tasks:assign '*' \
  type "task.assigned" \
  task_id "$TASK_ID" \
  mode "code" \
  assigned_by "keystone" \
  timestamp "$(date +%s)"

echo "Delegated task to code mode"

# 3. Publish task to mode-specific stream
redis-nova XADD nova:mode:code:tasks '*' \
  type "task.delegated" \
  task_id "$TASK_ID" \
  title "Implement Search Functionality" \
  description "Create a search feature for the application" \
  priority "medium" \
  delegated_by "keystone" \
  timestamp "$(date +%s)"

echo "Published task to code mode stream"
```

## 🤖 Automation Scripts <a name="automation-scripts"></a>

### Task Creation Script

```bash
cat > create_task.sh << 'EOF'
#!/bin/bash
# Script to create a task
# Usage: ./create_task.sh [title] [description] [priority] [assignee]

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
REDIS_HOST="127.0.0.1"

# Default values
TITLE="New Task"
DESCRIPTION="Task description"
PRIORITY="medium"
ASSIGNEE=""
CREATED_BY="$(whoami)"
TIMESTAMP=$(date +%s)

# Use command line arguments if provided
if [ $# -ge 1 ]; then
    TITLE="$1"
fi

if [ $# -ge 2 ]; then
    DESCRIPTION="$2"
fi

if [ $# -ge 3 ]; then
    PRIORITY="$3"
fi

if [ $# -ge 4 ]; then
    ASSIGNEE="$4"
fi

# Build the command
CMD="redis-cli -c -p $REDIS_PORT -h $REDIS_HOST -a $REDIS_PASSWORD XADD nova:tasks:create '*' \
  type \"task.created\" \
  title \"$TITLE\" \
  description \"$DESCRIPTION\" \
  priority \"$PRIORITY\" \
  status \"new\" \
  created_by \"$CREATED_BY\" \
  timestamp \"$TIMESTAMP\""

# Add assignee if provided
if [ ! -z "$ASSIGNEE" ]; then
    CMD="$CMD \
  assignee \"$ASSIGNEE\""
fi

# Execute the command
TASK_ID=$(eval $CMD)

echo "Created task with ID: $TASK_ID"
echo "Title: $TITLE"
echo "Description: $DESCRIPTION"
echo "Priority: $PRIORITY"
if [ ! -z "$ASSIGNEE" ]; then
    echo "Assignee: $ASSIGNEE"
fi
EOF

chmod +x create_task.sh
```

### Task Monitoring Script

```bash
cat > monitor_tasks.sh << 'EOF'
#!/bin/bash
# Script to monitor task streams
# Usage: ./monitor_tasks.sh [stream1] [stream2] ...

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
REDIS_HOST="127.0.0.1"

# Default streams to monitor
STREAMS=("nova:tasks:create" "nova:tasks:update" "nova:tasks:complete")

# Use command line arguments if provided
if [ $# -gt 0 ]; then
    STREAMS=("$@")
fi

echo "Monitoring streams: ${STREAMS[@]}"
echo "Press Ctrl+C to exit"
echo ""

# Function to format task events
format_task_event() {
    local event="$1"
    local timestamp=$(echo "$event" | grep -o "timestamp [0-9]*" | cut -d' ' -f2)
    local date=$(date -d @$timestamp)
    local type=$(echo "$event" | grep -o "type [^ ]*" | cut -d' ' -f2)
    local task_id=$(echo "$event" | grep -o "task_id [^ ]*" | cut -d' ' -f2)
    local title=$(echo "$event" | grep -o "title [^,]*" | cut -d' ' -f2-)
    
    echo "[$date] $type - Task ID: $task_id"
    if [ ! -z "$title" ]; then
        echo "  Title: $title"
    fi
    
    # Print other relevant fields based on event type
    case "$type" in
        "task.created")
            local description=$(echo "$event" | grep -o "description [^,]*" | cut -d' ' -f2-)
            local priority=$(echo "$event" | grep -o "priority [^ ]*" | cut -d' ' -f2)
            local created_by=$(echo "$event" | grep -o "created_by [^ ]*" | cut -d' ' -f2)
            
            echo "  Description: $description"
            echo "  Priority: $priority"
            echo "  Created by: $created_by"
            ;;
        "task.status_updated")
            local status=$(echo "$event" | grep -o "status [^ ]*" | cut -d' ' -f2)
            local updated_by=$(echo "$event" | grep -o "updated_by [^ ]*" | cut -d' ' -f2)
            
            echo "  New status: $status"
            echo "  Updated by: $updated_by"
            ;;
        "task.completed")
            local result=$(echo "$event" | grep -o "result [^,]*" | cut -d' ' -f2-)
            local completed_by=$(echo "$event" | grep -o "completed_by [^ ]*" | cut -d' ' -f2)
            
            echo "  Result: $result"
            echo "  Completed by: $completed_by"
            ;;
    esac
    
    echo ""
}

# Build the command
CMD="redis-cli -c -p $REDIS_PORT -h $REDIS_HOST -a $REDIS_PASSWORD XREAD BLOCK 1000 STREAMS"
for stream in "${STREAMS[@]}"; do
    CMD="$CMD $stream"
done
for stream in "${STREAMS[@]}"; do
    CMD="$CMD \$"
done

# Run the command in a loop to handle reconnections
while true; do
    RESULT=$(eval $CMD)
    
    # Format and display the result
    if [ ! -z "$RESULT" ]; then
        echo "$RESULT" | while read -r line; do
            format_task_event "$line"
        done
    fi
    
    # Small delay to avoid CPU spinning
    sleep 0.1
done
EOF

chmod +x monitor_tasks.sh
```

### Task Completion Script

```bash
cat > complete_task.sh << 'EOF'
#!/bin/bash
# Script to complete a task
# Usage: ./complete_task.sh [task_id] [result]

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000
REDIS_HOST="127.0.0.1"

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 [task_id] [result]"
    echo "Example: $0 1681234567890-0 'Task completed successfully'"
    exit 1
fi

TASK_ID="$1"
RESULT="$2"
COMPLETED_BY="$(whoami)"
TIMESTAMP=$(date +%s)

# Complete the task
redis-cli -c -p $REDIS_PORT -h $REDIS_HOST -a $REDIS_PASSWORD XADD nova:tasks:complete '*' \
  type "task.completed" \
  task_id "$TASK_ID" \
  result "$RESULT" \
  completed_by "$COMPLETED_BY" \
  timestamp "$TIMESTAMP"

echo "Task $TASK_ID completed"
echo "Result: $RESULT"
echo "Completed by: $COMPLETED_BY"
EOF

chmod +x complete_task.sh
```

---

This comprehensive guide provides all the information needed to effectively use Redis CLI for task management within the Nova ecosystem. If you have any questions or need further assistance, please contact the CommsOps team.