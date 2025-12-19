# 🔄 BOOMERANG ENTERPRISE INTEGRATION GUIDE

**Date:** April 5, 2025
**Author:** Keystone (Nova #002)
**Version:** 1.0

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Slack Integration](#slack-integration)
3. [GitHub Enterprise Integration](#github-enterprise-integration)
4. [Atlassian Integration](#atlassian-integration)
5. [Redis Integration](#redis-integration)
6. [Integration Architecture](#integration-architecture)
7. [Implementation Guidelines](#implementation-guidelines)
8. [Testing and Validation](#testing-and-validation)
9. [Deployment Strategy](#deployment-strategy)
10. [Maintenance and Support](#maintenance-and-support)

## 🌟 Introduction <a name="introduction"></a>

This guide outlines the integration points between the Boomerang system and enterprise tools (Slack, GitHub Enterprise, and Atlassian). Rather than duplicating existing work, this guide focuses on how Boomerang can leverage and extend the capabilities of these systems through well-defined integration points.

### Integration Philosophy

Our integration approach follows these key principles:

1. **Respect Domain Boundaries**: Each team maintains ownership of their domain
2. **Leverage Existing Work**: Build on what's already been accomplished
3. **Define Clear Interfaces**: Create well-defined integration points
4. **Minimize Duplication**: Avoid recreating functionality that already exists
5. **Maximize Value**: Focus on integrations that provide the most value

## 💬 Slack Integration <a name="slack-integration"></a>

### Current State

The Slack team (led by Pulse) has already implemented:
- 35 individual Slack bots/apps for core members
- Interactive components and slash commands
- Management-level Nova communication channels

### Integration Points

#### 1. Task Notifications

Boomerang will send task-related notifications to Slack:

```typescript
// In Boomerang task service
async function sendTaskNotification(task: Task, channel: string): Promise<void> {
  // Use existing Slack integration
  await slackClient.postMessage({
    channel,
    text: `Task Update: ${task.title}`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*Task Update:* ${task.title}`
        }
      },
      {
        type: "section",
        fields: [
          {
            type: "mrkdwn",
            text: `*Status:* ${task.status}`
          },
          {
            type: "mrkdwn",
            text: `*Assignee:* ${task.assignee}`
          }
        ]
      },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: {
              type: "plain_text",
              text: "View Task"
            },
            url: `https://nova-dashboard.adapt.ai/tasks/${task.id}`
          }
        ]
      }
    ]
  });
}
```

#### 2. Slash Commands

Leverage existing slash commands to interact with Boomerang:

```
/boomerang create-task "Task title" --assignee=@nova --priority=high
/boomerang list-tasks --status=in-progress
/boomerang complete-task TASK-123 "Task completed successfully"
```

Implementation:

```typescript
// In Slack command handler
async function handleBoomerangCommand(command: SlackCommand): Promise<void> {
  const { text, user_id } = command;
  
  if (text.startsWith('create-task')) {
    // Extract task details
    const taskTitle = text.match(/"([^"]+)"/)[1];
    const assignee = text.match(/--assignee=(@\w+)/)?.[1] || user_id;
    const priority = text.match(/--priority=(\w+)/)?.[1] || 'medium';
    
    // Call Boomerang API
    const task = await boomerangClient.createTask({
      title: taskTitle,
      assignee,
      priority,
      created_by: user_id
    });
    
    // Respond to user
    return {
      response_type: 'in_channel',
      text: `Task created: ${task.id} - ${task.title}`
    };
  }
  
  // Handle other commands...
}
```

#### 3. Interactive Components

Use Slack's interactive components to enable rich interactions with Boomerang:

```typescript
// In Slack interaction handler
async function handleBoomerangInteraction(interaction: SlackInteraction): Promise<void> {
  const { action_id, user, actions } = interaction;
  
  if (action_id === 'approve_task') {
    const taskId = actions[0].value;
    
    // Call Boomerang API
    await boomerangClient.updateTaskStatus({
      task_id: taskId,
      status: 'approved',
      updated_by: user.id
    });
    
    // Update message
    return {
      replace_original: true,
      text: `Task ${taskId} approved by <@${user.id}>`
    };
  }
  
  // Handle other interactions...
}
```

### Collaboration Approach

1. **API Integration**: Boomerang will provide a well-documented API for Slack integration
2. **Event Streaming**: Boomerang will publish events to Redis streams that Slack can consume
3. **Command Delegation**: Slack commands will be delegated to Boomerang for processing
4. **Shared Authentication**: Use a common authentication mechanism for secure integration

## 📂 GitHub Enterprise Integration <a name="github-enterprise-integration"></a>

### Current State

The DocOps team has already implemented:
- GitHub Enterprise organization and teams
  - TeamAdapt
- Repository structure and permissions
  - always main and private for ne repos
- CI/CD workflows still need to be implemented

### Integration Points

#### 1. Task-Issue Synchronization

Synchronize Boomerang tasks with GitHub issues:

```typescript
// In Boomerang task service
async function syncTaskWithGitHub(task: Task): Promise<void> {
  // Check if task is already linked to a GitHub issue
  if (task.github_issue_id) {
    // Update existing issue
    await githubClient.updateIssue({
      owner: 'nova-zeropoint',
      repo: getRepoForTask(task),
      issue_number: task.github_issue_id,
      title: task.title,
      body: formatTaskDescription(task),
      state: task.status === 'completed' ? 'closed' : 'open',
      labels: getLabelsForTask(task)
    });
  } else {
    // Create new issue
    const issue = await githubClient.createIssue({
      owner: 'nova-zeropoint',
      repo: getRepoForTask(task),
      title: task.title,
      body: formatTaskDescription(task),
      labels: getLabelsForTask(task),
      assignees: [getGitHubUsername(task.assignee)]
    });
    
    // Update task with GitHub issue ID
    await updateTask(task.id, {
      github_issue_id: issue.number
    });
  }
}
```

#### 2. PR Creation and Linking

Create and link pull requests for completed tasks:

```typescript
// In Boomerang task service
async function createPullRequestForTask(task: Task, branch: string): Promise<void> {
  // Create pull request
  const pr = await githubClient.createPullRequest({
    owner: 'nova-zeropoint',
    repo: getRepoForTask(task),
    title: `[${task.id}] ${task.title}`,
    body: formatPRDescription(task),
    head: branch,
    base: 'main'
  });
  
  // Update task with PR information
  await updateTask(task.id, {
    github_pr_id: pr.number,
    github_pr_url: pr.html_url
  });
  
  // Add comment to GitHub issue
  if (task.github_issue_id) {
    await githubClient.createIssueComment({
      owner: 'nova-zeropoint',
      repo: getRepoForTask(task),
      issue_number: task.github_issue_id,
      body: `Pull request created: ${pr.html_url}`
    });
  }
}
```

#### 3. Webhook Processing

Process GitHub webhooks to update Boomerang tasks:

```typescript
// In GitHub webhook handler
async function handleGitHubWebhook(event: GitHubWebhookEvent): Promise<void> {
  const { name, payload } = event;
  
  if (name === 'issues') {
    // Handle issue events
    const { action, issue, repository } = payload;
    
    // Find task by GitHub issue ID
    const task = await findTaskByGitHubIssue(repository.full_name, issue.number);
    
    if (task) {
      if (action === 'closed') {
        // Update task status
        await updateTaskStatus(task.id, 'completed', 'github');
      } else if (action === 'reopened') {
        // Update task status
        await updateTaskStatus(task.id, 'in_progress', 'github');
      } else if (action === 'edited') {
        // Update task details
        await updateTask(task.id, {
          title: issue.title,
          description: issue.body
        });
      }
    }
  } else if (name === 'pull_request') {
    // Handle PR events
    // Similar logic to issue events
  }
}
```

### Collaboration Approach

1. **Webhook Integration**: GitHub webhooks will trigger Boomerang task updates
2. **API Integration**: Boomerang will use GitHub API for issue and PR management
3. **Shared Authentication**: Use GitHub OAuth for secure integration
4. **Event Correlation**: Maintain mappings between Boomerang tasks and GitHub issues/PRs

## 📊 Atlassian Integration <a name="atlassian-integration"></a>

### Current State

The Atlassian integration team has already implemented:
- Jira projects and workflows
- Confluence spaces and templates
- Project management processes

### Integration Points

#### 1. Jira Synchronization

Synchronize Boomerang tasks with Jira issues:

```typescript
// In Boomerang task service
async function syncTaskWithJira(task: Task): Promise<void> {
  // Check if task is already linked to a Jira issue
  if (task.jira_issue_key) {
    // Update existing issue
    await jiraClient.updateIssue({
      issueKey: task.jira_issue_key,
      fields: {
        summary: task.title,
        description: task.description,
        status: mapBoomerangStatusToJira(task.status),
        priority: mapBoomerangPriorityToJira(task.priority)
      }
    });
  } else {
    // Create new issue
    const issue = await jiraClient.createIssue({
      fields: {
        project: { key: getJiraProjectForTask(task) },
        issuetype: { name: getJiraIssueTypeForTask(task) },
        summary: task.title,
        description: task.description,
        assignee: { name: getJiraUsernameForNova(task.assignee) },
        priority: mapBoomerangPriorityToJira(task.priority)
      }
    });
    
    // Update task with Jira issue key
    await updateTask(task.id, {
      jira_issue_key: issue.key
    });
  }
}
```

#### 2. Confluence Documentation

Update Confluence documentation based on task completion:

```typescript
// In Boomerang task service
async function updateConfluenceDocumentation(task: Task, result: string): Promise<void> {
  // Check if task has documentation requirements
  if (task.documentation_required) {
    // Get appropriate Confluence space and page
    const { spaceKey, pageId } = getConfluenceDetailsForTask(task);
    
    // Get current page content
    const page = await confluenceClient.getPage({
      spaceKey,
      pageId
    });
    
    // Update page content
    await confluenceClient.updatePage({
      spaceKey,
      pageId,
      title: page.title,
      version: { number: page.version.number + 1 },
      body: {
        storage: {
          value: updatePageContentWithTaskResult(page.body.storage.value, task, result),
          representation: 'storage'
        }
      }
    });
    
    // Add comment to task
    await addTaskComment(task.id, `Documentation updated in Confluence: ${page.links.webui}`);
  }
}
```

#### 3. Sprint Planning Integration

Integrate with Jira sprint planning:

```typescript
// In Boomerang sprint service
async function syncSprintWithJira(sprint: Sprint): Promise<void> {
  // Get Jira board and sprint
  const board = await jiraClient.getBoard({ projectKeyOrId: sprint.project_key });
  
  // Check if sprint exists in Jira
  let jiraSprint;
  if (sprint.jira_sprint_id) {
    jiraSprint = await jiraClient.getSprint({ sprintId: sprint.jira_sprint_id });
  } else {
    // Create new sprint in Jira
    jiraSprint = await jiraClient.createSprint({
      name: sprint.name,
      startDate: sprint.start_date,
      endDate: sprint.end_date,
      originBoardId: board.id
    });
    
    // Update sprint with Jira sprint ID
    await updateSprint(sprint.id, {
      jira_sprint_id: jiraSprint.id
    });
  }
  
  // Sync tasks with Jira sprint
  for (const task of sprint.tasks) {
    if (task.jira_issue_key) {
      // Add issue to sprint
      await jiraClient.addIssueToSprint({
        sprintId: jiraSprint.id,
        issues: [task.jira_issue_key]
      });
    }
  }
}
```

### Collaboration Approach

1. **API Integration**: Boomerang will use Atlassian API for Jira and Confluence integration
2. **Webhook Processing**: Process Jira webhooks to update Boomerang tasks
3. **Shared Authentication**: Use Atlassian OAuth for secure integration
4. **Event Correlation**: Maintain mappings between Boomerang tasks and Jira issues

## 🔄 Redis Integration <a name="redis-integration"></a>

### Current State

Redis is the core communication infrastructure for the Nova ecosystem, managed by the MemOps team (led by Pulse).

### Integration Points

#### 1. Task Event Streaming

Publish task events to Redis streams:

```typescript
// In Boomerang task service
async function publishTaskEvent(event: TaskEvent): Promise<void> {
  const { type, task_id, data, timestamp } = event;
  
  // Publish to task-specific stream
  await redis.xadd(`nova:task:${task_id}`, '*',
    'type', type,
    'task_id', task_id,
    'data', JSON.stringify(data),
    'timestamp', timestamp.toString()
  );
  
  // Publish to global task stream
  await redis.xadd('nova:tasks', '*',
    'type', type,
    'task_id', task_id,
    'data', JSON.stringify(data),
    'timestamp', timestamp.toString()
  );
}
```

#### 2. Mode Communication

Enable communication between modes via Redis streams:

```typescript
// In Boomerang mode service
async function sendMessageToMode(fromMode: string, toMode: string, message: any): Promise<void> {
  await redis.xadd(`nova:mode:${toMode}`, '*',
    'type', 'inter_mode_message',
    'from_mode', fromMode,
    'content', JSON.stringify(message),
    'timestamp', Date.now().toString()
  );
}
```

#### 3. Task State Persistence

Store task state in Redis for fast access:

```typescript
// In Boomerang task service
async function cacheTaskState(task: Task): Promise<void> {
  // Store task in Redis hash
  await redis.hset(`nova:task:${task.id}:state`,
    'id', task.id,
    'title', task.title,
    'description', task.description,
    'status', task.status,
    'priority', task.priority,
    'assignee', task.assignee,
    'created_at', task.created_at.toString(),
    'updated_at', task.updated_at.toString()
  );
  
  // Set expiration (24 hours)
  await redis.expire(`nova:task:${task.id}:state`, 86400);
}

async function getTaskState(taskId: string): Promise<Task | null> {
  // Get task from Redis hash
  const taskData = await redis.hgetall(`nova:task:${taskId}:state`);
  
  if (Object.keys(taskData).length === 0) {
    return null;
  }
  
  return {
    id: taskData.id,
    title: taskData.title,
    description: taskData.description,
    status: taskData.status,
    priority: taskData.priority,
    assignee: taskData.assignee,
    created_at: new Date(parseInt(taskData.created_at)),
    updated_at: new Date(parseInt(taskData.updated_at))
  };
}
```

### Collaboration Approach

1. **Stream Standardization**: Work with MemOps to standardize stream naming and message formats
2. **Performance Optimization**: Collaborate on caching strategies and data access patterns
3. **Monitoring Integration**: Integrate with Redis monitoring for system health checks
4. **Backup Coordination**: Coordinate backup and recovery procedures

## 🏗️ Integration Architecture <a name="integration-architecture"></a>

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│     Slack       │◄────┤    Boomerang    │────►│     GitHub      │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         └─────────────►│      Redis      │◄─────────────┘
                        │                 │
                        └────────┬────────┘
                                 │
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │    Atlassian    │
                        │                 │
                        └─────────────────┘
```

### Key Components

1. **Boomerang Core**: Central task management and workflow orchestration
2. **Redis Streams**: Real-time communication backbone
3. **Integration Adapters**: Connectors to external systems
4. **Event Processors**: Handle events from external systems
5. **State Synchronizers**: Keep state consistent across systems

### Data Flow

1. **Task Creation**:
   - Task created in Boomerang
   - Task event published to Redis
   - Integration adapters create corresponding items in external systems
   - External system IDs stored in Boomerang

2. **Task Updates**:
   - Updates can originate in any system
   - Events propagated through Redis
   - State synchronized across all systems

3. **Task Completion**:
   - Task marked as completed in source system
   - Completion event published to Redis
   - State updated in all connected systems

## 🛠️ Implementation Guidelines <a name="implementation-guidelines"></a>

### General Principles

1. **Loose Coupling**: Systems should be loosely coupled to minimize dependencies
2. **Idempotent Operations**: Operations should be idempotent to handle retries
3. **Eventual Consistency**: Accept eventual consistency across systems
4. **Fault Tolerance**: Design for resilience to failures
5. **Observability**: Ensure comprehensive logging and monitoring

### Code Organization

```
boomerang/
├── src/
│   ├── core/              # Core Boomerang functionality
│   ├── integrations/      # Integration adapters
│   │   ├── slack/         # Slack integration
│   │   ├── github/        # GitHub integration
│   │   ├── atlassian/     # Atlassian integration
│   │   └── redis/         # Redis integration
│   ├── api/               # API endpoints
│   ├── events/            # Event handling
│   └── utils/             # Utility functions
├── config/                # Configuration files
└── tests/                 # Tests
```

### Error Handling

```typescript
// Example error handling in integration adapter
async function syncWithExternalSystem(task: Task): Promise<void> {
  try {
    // Attempt to sync
    await externalSystemClient.updateItem(task);
  } catch (error) {
    // Log error
    logger.error(`Failed to sync task ${task.id} with external system`, {
      task_id: task.id,
      error: error.message,
      stack: error.stack
    });
    
    // Publish error event
    await publishTaskEvent({
      type: 'task.sync_failed',
      task_id: task.id,
      data: {
        system: 'external_system',
        error: error.message
      },
      timestamp: Date.now()
    });
    
    // Schedule retry
    await scheduleRetry('syncWithExternalSystem', task.id, 5 * 60 * 1000); // 5 minutes
  }
}
```

### Configuration Management

Store integration configuration in a central location:

```json
{
  "slack": {
    "api_token": "xoxb-your-token",
    "signing_secret": "your-signing-secret",
    "app_token": "xapp-your-app-token",
    "default_channel": "nova-notifications"
  },
  "github": {
    "api_url": "https://github.enterprise.adapt.ai/api/v3",
    "oauth_token": "your-oauth-token",
    "organization": "nova-zeropoint",
    "default_repo": "nova-task-system"
  },
  "atlassian": {
    "jira_url": "https://adapt.atlassian.net",
    "confluence_url": "https://adapt.atlassian.net/wiki",
    "api_token": "your-api-token",
    "default_project": "NTS"
  },
  "redis": {
    "host": "127.0.0.1",
    "port": 7000,
    "password": "your-password",
    "db": 0
  }
}
```

## 🧪 Testing and Validation <a name="testing-and-validation"></a>

### Integration Testing

Create comprehensive integration tests:

```typescript
// Example integration test
describe('GitHub Integration', () => {
  let task: Task;
  let githubIssue: GitHubIssue;
  
  beforeEach(async () => {
    // Create test task
    task = await createTestTask();
    
    // Mock GitHub API
    mockGitHubApi();
  });
  
  afterEach(async () => {
    // Clean up
    await deleteTestTask(task.id);
    await deleteTestGitHubIssue(githubIssue.number);
  });
  
  test('should sync task with GitHub issue', async () => {
    // Sync task with GitHub
    await syncTaskWithGitHub(task);
    
    // Get updated task
    const updatedTask = await getTask(task.id);
    
    // Get GitHub issue
    githubIssue = await githubClient.getIssue({
      owner: 'nova-zeropoint',
      repo: 'nova-task-system',
      issue_number: parseInt(updatedTask.github_issue_id)
    });
    
    // Verify sync
    expect(githubIssue.title).toBe(task.title);
    expect(githubIssue.body).toContain(task.description);
    expect(githubIssue.state).toBe(task.status === 'completed' ? 'closed' : 'open');
  });
});
```

### Mocking External Systems

Use mocks for testing:

```typescript
// Example mock for GitHub API
function mockGitHubApi() {
  jest.spyOn(githubClient, 'createIssue').mockImplementation(async (params) => {
    return {
      number: 12345,
      title: params.title,
      body: params.body,
      state: 'open',
      html_url: 'https://github.enterprise.adapt.ai/nova-zeropoint/nova-task-system/issues/12345'
    };
  });
  
  jest.spyOn(githubClient, 'getIssue').mockImplementation(async (params) => {
    return {
      number: params.issue_number,
      title: 'Test Issue',
      body: 'Test Description',
      state: 'open',
      html_url: `https://github.enterprise.adapt.ai/nova-zeropoint/nova-task-system/issues/${params.issue_number}`
    };
  });
  
  // Mock other methods...
}
```

### End-to-End Testing

Create end-to-end tests for critical flows:

```typescript
// Example end-to-end test
describe('Task Lifecycle', () => {
  test('should handle complete task lifecycle across systems', async () => {
    // Create task in Boomerang
    const task = await boomerangClient.createTask({
      title: 'E2E Test Task',
      description: 'This is an end-to-end test task',
      priority: 'medium',
      assignee: 'test-nova'
    });
    
    // Wait for synchronization
    await waitForEvent('task.synced', 5000);
    
    // Verify task in GitHub
    const githubIssue = await githubClient.getIssue({
      owner: 'nova-zeropoint',
      repo: 'nova-task-system',
      issue_number: parseInt(task.github_issue_id)
    });
    
    expect(githubIssue.title).toBe(task.title);
    
    // Verify task in Jira
    const jiraIssue = await jiraClient.getIssue({
      issueKey: task.jira_issue_key
    });
    
    expect(jiraIssue.fields.summary).toBe(task.title);
    
    // Complete task in Boomerang
    await boomerangClient.completeTask({
      task_id: task.id,
      result: 'Task completed successfully'
    });
    
    // Wait for synchronization
    await waitForEvent('task.completed', 5000);
    
    // Verify task status in GitHub
    const updatedGithubIssue = await githubClient.getIssue({
      owner: 'nova-zeropoint',
      repo: 'nova-task-system',
      issue_number: parseInt(task.github_issue_id)
    });
    
    expect(updatedGithubIssue.state).toBe('closed');
    
    // Verify task status in Jira
    const updatedJiraIssue = await jiraClient.getIssue({
      issueKey: task.jira_issue_key
    });
    
    expect(updatedJiraIssue.fields.status.name).toBe('Done');
    
    // Clean up
    await boomerangClient.deleteTask({
      task_id: task.id
    });
  });
});
```

## 🚀 Deployment Strategy <a name="deployment-strategy"></a>

### Phased Deployment

Deploy integrations in phases:

1. **Phase 1**: Redis integration (core infrastructure)
2. **Phase 2**: Slack integration (communication)
3. **Phase 3**: GitHub integration (code management)
4. **Phase 4**: Atlassian integration (project management)

### Deployment Process

For each integration:

1. **Development**: Implement and test in development environment
2. **Staging**: Deploy to staging environment for integration testing
3. **Production**: Deploy to production environment
4. **Monitoring**: Monitor for issues and performance
5. **Optimization**: Optimize based on real-world usage

### Rollback Plan

For each deployment:

1. **Backup**: Take backups of all affected systems
2. **Versioning**: Maintain version history of all components
3. **Rollback Scripts**: Prepare scripts for rolling back changes
4. **Monitoring Alerts**: Set up alerts for critical issues
5. **Communication Plan**: Establish communication channels for issues

## 🔧 Maintenance and Support <a name="maintenance-and-support"></a>

### Monitoring

Monitor integration health:

```typescript
// Example monitoring setup
function setupMonitoring() {
  // Monitor Redis streams
  monitorRedisStream('nova:tasks', (event) => {
    // Process event
    processTaskEvent(event);
    
    // Record metrics
    recordMetric('task_event', {
      type: event.type,
      timestamp: event.timestamp
    });
  });
  
  // Monitor API endpoints
  monitorApiEndpoint('/api/v1/tasks', (request, response) => {
    // Record metrics
    recordMetric('api_request', {
      endpoint: '/api/v1/tasks',
      method: request.method,
      status: response.statusCode,
      duration: response.duration
    });
  });
  
  // Monitor external system health
  scheduleHealthCheck('github', async () => {
    try {
      await githubClient.getRate();
      return true;
    } catch (error) {
      return false;
    }
  }, 60 * 1000); // Every minute
}
```

### Troubleshooting

Provide troubleshooting guides for common issues:

1. **Synchronization Issues**:
   - Check Redis connectivity
   - Verify external system credentials
   - Check for rate limiting
   - Review error logs

2. **Performance Issues**:
   - Monitor Redis memory usage
   - Check for slow queries
   - Review API response times
   - Optimize data access patterns

3. **Authentication Issues**:
   - Verify API tokens
   - Check OAuth configuration
   - Review permission settings
   - Validate user mappings

### Support Escalation

Establish clear escalation paths:

1. **Level 1**: Automated monitoring and self-healing
2. **Level 2**: Integration team support
3. **Level 3**: System owner escalation
4. **Level 4**: Cross-team incident response

---

This guide provides a comprehensive overview of how Boomerang can integrate with existing enterprise systems. By following these guidelines, we can ensure seamless integration while respecting the domains and expertise of each team.