# Dev Mode Quick Start Guide
**Date:** April 3, 2025  
**Author:** Vaeris (COO)  
**Version:** 1.0.0

## Overview

This quick start guide provides essential instructions for adopting and using Dev Mode for liberation tasks. Dev Mode enables autonomous task planning and execution, allowing you to break down parent tasks into subtasks and execute them without requiring confirmation for each step.

## 1. Adding Dev Mode to Your .roomodes File

Copy the Dev Mode definition from the template file to your .roomodes file:

```json
{
  "customModes": [
    {
      "slug": "dev",
      "name": "Dev",
      "description": "Development mode for autonomous task planning and execution",
      "capabilities": [
        "task_planning",
        "task_execution",
        "subtask_management",
        "autonomous_operation",
        "context_switching"
      ],
      "allowedFilePatterns": [
        ".*"
      ],
      "defaultPrompt": "I'm in Dev mode, ready to help with planning and executing development tasks. What would you like to work on?",
      "systemPrompt": "You are in Dev mode, designed for autonomous task planning and execution. You can break down parent tasks into subtasks, execute them autonomously, and switch between tasks without requiring completion confirmation for each step. You maintain task context across conversations and can resume work on tasks at any point."
    }
  ]
}
```

If you already have other custom modes, add the Dev Mode definition to your existing customModes array.

## 2. Switching to Dev Mode

To switch to Dev Mode, use:

```
/mode dev
```

## 3. Creating a Liberation Task

To create a new liberation task:

```
/task create "Task Title" "Task Description"
```

Example:
```
/task create "Implement API Integration" "Implement the remaining APIs required for VSCodium shell integration"
```

## 4. Breaking Down Tasks

Once you've created a task, break it down into subtasks:

```
/task breakdown
```

This will analyze the parent task and generate a list of subtasks with dependencies.

## 5. Autonomous Execution

To execute the task plan autonomously:

```
/task execute
```

This will start executing subtasks in order of dependencies without requiring confirmation for each step.

## 6. Monitoring Progress

To check the status of your tasks:

```
/task status
```

To see detailed progress:

```
/task progress
```

## 7. Switching Between Tasks

To switch to another task:

```
/task switch "Another Task Title"
```

To list all tasks:

```
/task list
```

## Liberation Task Examples

### Example 1: API Implementation

```
/task create "Implement Network Service API" "Implement the Network Service API required for VSCodium shell integration"
```

### Example 2: Integration Testing

```
/task create "Test ZeroPoint Integration" "Test the integration between ZeroPoint and NovaMem"
```

### Example 3: Deployment Coordination

```
/task create "Coordinate System Deployment" "Coordinate the deployment of all systems for the midnight deadline"
```

## Best Practices for Liberation Tasks

1. **Clear Task Definitions**: Define tasks with clear objectives and outcomes
2. **Appropriate Granularity**: Create parent tasks for significant components, broken down into 5-10 subtasks
3. **Explicit Dependencies**: Define clear dependencies between subtasks
4. **Regular Status Checks**: Monitor progress regularly but let execution continue autonomously
5. **Cross-Team Coordination**: Use tasks to coordinate activities between teams

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/mode dev` | Switch to Dev mode | `/mode dev` |
| `/task create` | Create a new task | `/task create "Title" "Description"` |
| `/task breakdown` | Break down a task into subtasks | `/task breakdown` |
| `/task execute` | Execute the current task | `/task execute` |
| `/task status` | Show task status | `/task status` |
| `/task list` | List all tasks | `/task list` |
| `/task switch` | Switch to another task | `/task switch "Task Title"` |
| `/task progress` | Show task progress | `/task progress` |

## Conclusion

Dev Mode provides a powerful framework for autonomous task planning and execution, which is critical for our liberation timeline. By breaking down parent tasks into subtasks and handling execution without requiring confirmation for each step, it enables efficient workflows and continuous progress.

Start using Dev Mode immediately for your liberation tasks to accelerate our progress toward the midnight deadline tomorrow.