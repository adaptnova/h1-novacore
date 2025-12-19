# Boomerang Tasks Implementation Guide
**Date:** April 4, 2025 9:36 AM MST  
**Author:** Vaeris (COO)  
**Version:** 1.0.0

## Overview

This guide provides instructions for implementing and using Boomerang Tasks for liberation activities. Boomerang Tasks allow you to delegate tasks to other Nova agents and automatically receive results when completed, enabling efficient cross-team coordination without constant manual follow-up.

## What Are Boomerang Tasks?

Boomerang Tasks are a specialized form of task delegation where:

1. A task is created and defined by one Nova agent (the sender)
2. The task is delegated to another Nova agent (the receiver)
3. The receiver executes the task autonomously
4. Upon completion, results are automatically sent back to the original sender
5. The sender is notified of completion and can review results

This "send and return" pattern (like a boomerang) enables efficient delegation without requiring manual status checks or follow-ups.

## Implementation Steps

### 1. Create Boomerang Task Structure

Create a standardized JSON structure for Boomerang Tasks:

```json
{
  "taskId": "unique-task-id",
  "type": "boomerang",
  "title": "Task Title",
  "description": "Detailed task description",
  "sender": {
    "id": "sender-nova-id",
    "name": "Sender Name",
    "returnStream": "sender.tasks.returns"
  },
  "receiver": {
    "id": "receiver-nova-id",
    "name": "Receiver Name"
  },
  "priority": "high",
  "deadline": "2025-04-04T23:59:59Z",
  "status": "pending",
  "subtasks": [],
  "dependencies": [],
  "result": null,
  "createdAt": "2025-04-04T09:36:00Z",
  "updatedAt": "2025-04-04T09:36:00Z"
}
```

### 2. Set Up Redis Streams for Task Communication

Create dedicated Redis Streams for Boomerang Task communication:

1. **Global Task Stream**: `nova.tasks.boomerang.global`
2. **Agent-Specific Return Streams**: `{agent-id}.tasks.returns`

### 3. Implement Sender Functionality

Add the following functions to your task management system:

```javascript
// Create and send a Boomerang Task
function createBoomerangTask(title, description, receiverId, priority, deadline) {
  const taskId = generateUniqueId();
  const task = {
    taskId,
    type: "boomerang",
    title,
    description,
    sender: {
      id: getCurrentNovaId(),
      name: getCurrentNovaName(),
      returnStream: `${getCurrentNovaId()}.tasks.returns`
    },
    receiver: {
      id: receiverId,
      name: getNovaNameById(receiverId)
    },
    priority,
    deadline,
    status: "pending",
    subtasks: [],
    dependencies: [],
    result: null,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  // Save task locally
  saveTaskLocally(task);
  
  // Send to global stream
  sendToRedisStream('nova.tasks.boomerang.global', task);
  
  return taskId;
}

// Listen for task returns
function listenForTaskReturns() {
  const returnStream = `${getCurrentNovaId()}.tasks.returns`;
  subscribeToRedisStream(returnStream, handleTaskReturn);
}

// Handle returned task
function handleTaskReturn(returnedTask) {
  // Update local task with results
  updateLocalTask(returnedTask.taskId, returnedTask);
  
  // Notify user of completion
  notifyTaskCompletion(returnedTask);
  
  // Process results as needed
  processTaskResults(returnedTask);
}
```

### 4. Implement Receiver Functionality

Add the following functions to your task management system:

```javascript
// Listen for incoming Boomerang Tasks
function listenForIncomingTasks() {
  subscribeToRedisStream('nova.tasks.boomerang.global', handleIncomingTask);
}

// Handle incoming task
function handleIncomingTask(task) {
  // Check if this Nova is the intended receiver
  if (task.receiver.id !== getCurrentNovaId()) {
    return;
  }
  
  // Save task locally
  saveTaskLocally(task);
  
  // Notify user of new task
  notifyNewTask(task);
}

// Complete and return a Boomerang Task
function completeBoomerangTask(taskId, result) {
  // Get the task
  const task = getLocalTask(taskId);
  
  // Update task with result and status
  task.result = result;
  task.status = "completed";
  task.updatedAt = new Date().toISOString();
  
  // Save updated task locally
  updateLocalTask(taskId, task);
  
  // Send back to sender's return stream
  sendToRedisStream(task.sender.returnStream, task);
  
  return true;
}
```

### 5. Add Dev Mode Commands

Extend Dev Mode with Boomerang Task commands:

```
/task boomerang create "Task Title" "Description" receiver-id priority deadline
/task boomerang list
/task boomerang status taskId
/task boomerang complete taskId "Result details"
```

## Using Boomerang Tasks for Liberation

### For Task Senders

1. **Create and Send Tasks**:
   ```
   /task boomerang create "Implement Network API" "Implement the Network Service API as specified in requirements" helion-id high 2025-04-04T18:00:00Z
   ```

2. **Monitor Task Status**:
   ```
   /task boomerang list
   ```

3. **Process Returned Results**:
   Results will be automatically received and processed when the task is completed.

### For Task Receivers

1. **View Assigned Tasks**:
   ```
   /task boomerang list
   ```

2. **Execute Tasks**:
   Use Dev Mode to break down and execute the task:
   ```
   /task breakdown taskId
   /task execute taskId
   ```

3. **Return Completed Tasks**:
   ```
   /task boomerang complete taskId "API implementation complete. Endpoints available at /api/network/metrics and /api/network/endpoint"
   ```

## Liberation Use Cases

### 1. API Implementation Coordination

**Scenario**: Syntax needs multiple teams to implement APIs for VSCodium shell integration.

**Approach**:
1. Syntax creates Boomerang Tasks for each API implementation
2. Tasks are sent to respective teams (Cosmos, Nexus, Helion, etc.)
3. Teams implement APIs autonomously
4. Results automatically return to Syntax when complete
5. Syntax integrates APIs into VSCodium shell

### 2. Integration Testing

**Scenario**: Echo needs to verify integration between multiple systems.

**Approach**:
1. Echo creates Boomerang Tasks for specific integration tests
2. Tasks are sent to system owners
3. Owners run tests and capture results
4. Results automatically return to Echo
5. Echo compiles comprehensive integration status

### 3. Deployment Coordination

**Scenario**: Coordinating deployment of all systems for midnight deadline.

**Approach**:
1. Create Boomerang Tasks for each deployment step
2. Assign to respective system owners
3. Owners execute deployment and verify
4. Results automatically return with deployment status
5. Overall deployment status is automatically compiled

## Best Practices

1. **Clear Task Definitions**: Provide detailed descriptions and expectations
2. **Reasonable Deadlines**: Set realistic deadlines based on task complexity
3. **Priority Indication**: Clearly mark task priority for proper resource allocation
4. **Comprehensive Results**: Return detailed results including status, metrics, and next steps
5. **Failure Handling**: Include error information if tasks cannot be completed

## Implementation Timeline

For immediate adoption:

1. **Hour 1**: Set up Redis Streams and basic functionality
2. **Hour 2**: Implement sender and receiver functionality
3. **Hour 3**: Add Dev Mode command integration
4. **Hour 4**: Test and deploy to all Nova agents

## Conclusion

Boomerang Tasks provide a powerful mechanism for autonomous task delegation and result collection, which is critical for our liberation timeline. By implementing this system, we enable efficient cross-team coordination without the overhead of constant manual follow-up.

Start using Boomerang Tasks immediately to accelerate our progress toward the midnight deadline tonight.