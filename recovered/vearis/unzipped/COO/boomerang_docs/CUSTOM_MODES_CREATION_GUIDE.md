# 🎭 CUSTOM MODES CREATION GUIDE

**Date:** April 5, 2025
**Author:** Keystone (Nova #002)
**Version:** 1.0

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Mode Architecture Overview](#mode-architecture-overview)
3. [Step-by-Step Mode Creation](#step-by-step-mode-creation)
4. [Mode Configuration File](#mode-configuration-file)
5. [Mode Implementation File](#mode-implementation-file)
6. [Mode Registration](#mode-registration)
7. [Mode Testing](#mode-testing)
8. [Advanced Mode Features](#advanced-mode-features)
9. [Mode Interaction Patterns](#mode-interaction-patterns)
10. [Example Modes](#example-modes)
11. [Troubleshooting](#troubleshooting)

## 🌟 Introduction <a name="introduction"></a>

Custom modes are specialized configurations that optimize a Nova for specific types of tasks. This guide provides detailed instructions for creating, implementing, and registering custom modes within the Nova ecosystem.

## 🏗️ Mode Architecture Overview <a name="mode-architecture-overview"></a>

A mode consists of two primary components:

1. **Configuration File**: A JSON file that defines the mode's properties, capabilities, and instructions
2. **Implementation File**: A TypeScript file that implements the mode's functionality

The mode system is designed to be extensible, allowing for the creation of specialized modes for various tasks while maintaining a consistent interface for interaction.

## 🔄 Step-by-Step Mode Creation <a name="step-by-step-mode-creation"></a>

### 1. Define Mode Purpose and Capabilities

Before creating a mode, clearly define:

- What specific tasks the mode will excel at
- What capabilities the mode will have
- What file types the mode should be able to access
- What instructions will guide the mode's behavior

### 2. Create Mode Configuration File

Create a JSON file in the `boomerang` directory with the naming convention `[mode_name]_mode_config.json`.

### 3. Create Mode Implementation File

Create a TypeScript file in the `boomerang` directory with the naming convention `[mode_name]_mode.ts`.

### 4. Register the Mode

Update the necessary files to register your mode with the system.

### 5. Test the Mode

Create test cases to verify that your mode functions correctly.

## 📝 Mode Configuration File <a name="mode-configuration-file"></a>

The mode configuration file defines the mode's properties, capabilities, and instructions. Here's a comprehensive template:

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
  ],
  "tools": {
    "allowed": [
      "tool_1",
      "tool_2",
      "tool_3"
    ],
    "restricted": [
      "tool_4",
      "tool_5"
    ]
  },
  "workflow": {
    "task_analysis": {
      "steps": [
        "Step 1 for analyzing tasks",
        "Step 2 for analyzing tasks",
        "Step 3 for analyzing tasks"
      ]
    },
    "result_integration": {
      "steps": [
        "Step 1 for integrating results",
        "Step 2 for integrating results",
        "Step 3 for integrating results"
      ]
    }
  }
}
```

### Key Configuration Properties

#### `name` (required)
The display name of the mode.

#### `slug` (required)
A unique identifier for the mode, used in URLs and API calls. Should be lowercase, with no spaces or special characters.

#### `description` (required)
A detailed description of what the mode specializes in.

#### `version` (required)
The version number of the mode.

#### `role` (required)
A detailed role description that will guide the Nova's behavior in this mode.

#### `capabilities` (required)
An array of capabilities that the mode possesses.

#### `file_restrictions` (optional)
Defines which file patterns the mode can and cannot access.

- `allowed_patterns`: Array of regex patterns for files the mode can access
- `blocked_patterns`: Array of regex patterns for files the mode cannot access

#### `instructions` (required)
An array of instructions that guide the Nova's behavior in this mode.

#### `tools` (optional)
Defines which tools the mode can and cannot use.

- `allowed`: Array of tools the mode can use
- `restricted`: Array of tools the mode cannot use

#### `workflow` (optional)
Defines specific workflow steps for the mode.

## 💻 Mode Implementation File <a name="mode-implementation-file"></a>

The mode implementation file contains the TypeScript code that implements the mode's functionality. Here's a comprehensive template:

```typescript
import { FastifyInstance } from 'fastify';
import { PrismaClient } from '@prisma/client';
import { Redis } from 'ioredis';
import { v4 as uuidv4 } from 'uuid';

// Define interfaces for your mode
interface YourModeState {
  // Define state properties
}

export class YourMode {
  private prisma: PrismaClient;
  private redis: Redis;
  private state: Map<string, YourModeState> = new Map();

  constructor(prisma: PrismaClient, redis: Redis) {
    this.prisma = prisma;
    this.redis = redis;
  }

  // Register routes with Fastify
  public registerRoutes(fastify: FastifyInstance): void {
    // Define your API endpoints
    fastify.post('/api/v1/your-mode/endpoint', this.yourEndpointHandler.bind(this));
    fastify.get('/api/v1/your-mode/endpoint/:id', this.getEndpointHandler.bind(this));
    fastify.put('/api/v1/your-mode/endpoint/:id', this.updateEndpointHandler.bind(this));
    fastify.delete('/api/v1/your-mode/endpoint/:id', this.deleteEndpointHandler.bind(this));
  }

  // Initialize Redis stream listeners
  public initializeStreamListeners(): void {
    // Set up Redis stream listeners
    this.redis.xgroup('CREATE', 'nova:your-mode', 'your-mode-group', '$', 'MKSTREAM', (err) => {
      if (err && !err.message.includes('BUSYGROUP')) {
        console.error('Error creating consumer group:', err);
      }
      
      this.consumeEvents();
    });
  }

  // Consume events from Redis stream
  private async consumeEvents(): Promise<void> {
    try {
      const results = await this.redis.xreadgroup(
        'GROUP', 'your-mode-group', 'your-mode-consumer',
        'COUNT', '10',
        'BLOCK', '2000',
        'STREAMS', 'nova:your-mode', '>'
      );
      
      if (results && Array.isArray(results) && results.length > 0 && Array.isArray(results[0])) {
        const streamData = results[0];
        const streamName = streamData[0];
        const messages = streamData[1];
        
        for (const [messageId, fields] of messages) {
          // Convert array of [key, value] to object
          const messageObj: Record<string, string> = {};
          for (let i = 0; i < fields.length; i += 2) {
            messageObj[fields[i]] = fields[i + 1];
          }
          
          // Process event based on type
          await this.processEvent(messageObj);
          
          // Acknowledge message
          await this.redis.xack('nova:your-mode', 'your-mode-group', messageId);
        }
      }
      
      // Continue consuming
      setImmediate(() => this.consumeEvents());
    } catch (error) {
      console.error('Error consuming events:', error);
      // Retry after delay
      setTimeout(() => this.consumeEvents(), 5000);
    }
  }

  // Process events
  private async processEvent(event: Record<string, string>): Promise<void> {
    const eventType = event.type;
    
    switch (eventType) {
      case 'your-event-type':
        await this.handleYourEventType(event);
        break;
      default:
        console.log(`Unknown event type: ${eventType}`);
    }
  }

  // Handle specific event types
  private async handleYourEventType(event: Record<string, string>): Promise<void> {
    // Implement event handling logic
  }

  // API endpoint handlers
  private async yourEndpointHandler(request: any, reply: any): Promise<void> {
    try {
      const { param1, param2 } = request.body;
      
      // Implement endpoint logic
      const result = await this.yourBusinessLogic(param1, param2);
      
      reply.send(result);
    } catch (error) {
      console.error('Error in yourEndpointHandler:', error);
      reply.code(500).send({ error: 'Internal server error' });
    }
  }

  private async getEndpointHandler(request: any, reply: any): Promise<void> {
    try {
      const { id } = request.params;
      
      // Implement get logic
      const result = await this.getItem(id);
      
      if (!result) {
        reply.code(404).send({ error: 'Item not found' });
        return;
      }
      
      reply.send(result);
    } catch (error) {
      console.error('Error in getEndpointHandler:', error);
      reply.code(500).send({ error: 'Internal server error' });
    }
  }

  private async updateEndpointHandler(request: any, reply: any): Promise<void> {
    try {
      const { id } = request.params;
      const { param1, param2 } = request.body;
      
      // Implement update logic
      const result = await this.updateItem(id, param1, param2);
      
      if (!result) {
        reply.code(404).send({ error: 'Item not found' });
        return;
      }
      
      reply.send(result);
    } catch (error) {
      console.error('Error in updateEndpointHandler:', error);
      reply.code(500).send({ error: 'Internal server error' });
    }
  }

  private async deleteEndpointHandler(request: any, reply: any): Promise<void> {
    try {
      const { id } = request.params;
      
      // Implement delete logic
      const result = await this.deleteItem(id);
      
      if (!result) {
        reply.code(404).send({ error: 'Item not found' });
        return;
      }
      
      reply.send({ success: true });
    } catch (error) {
      console.error('Error in deleteEndpointHandler:', error);
      reply.code(500).send({ error: 'Internal server error' });
    }
  }

  // Business logic methods
  private async yourBusinessLogic(param1: string, param2: string): Promise<any> {
    // Implement your business logic
    return { success: true, param1, param2 };
  }

  private async getItem(id: string): Promise<any> {
    // Implement get logic
    return this.state.get(id);
  }

  private async updateItem(id: string, param1: string, param2: string): Promise<any> {
    // Implement update logic
    const item = this.state.get(id);
    
    if (!item) {
      return null;
    }
    
    // Update item
    const updatedItem = { ...item, param1, param2 };
    this.state.set(id, updatedItem);
    
    return updatedItem;
  }

  private async deleteItem(id: string): Promise<boolean> {
    // Implement delete logic
    const exists = this.state.has(id);
    
    if (!exists) {
      return false;
    }
    
    this.state.delete(id);
    
    return true;
  }
}
```

### Key Implementation Components

#### Constructor
Initializes the mode with necessary dependencies.

```typescript
constructor(prisma: PrismaClient, redis: Redis) {
  this.prisma = prisma;
  this.redis = redis;
}
```

#### `registerRoutes`
Registers API endpoints with Fastify.

```typescript
public registerRoutes(fastify: FastifyInstance): void {
  // Define your API endpoints
  fastify.post('/api/v1/your-mode/endpoint', this.yourEndpointHandler.bind(this));
}
```

#### `initializeStreamListeners`
Sets up Redis stream listeners for event processing.

```typescript
public initializeStreamListeners(): void {
  // Set up Redis stream listeners
  this.redis.xgroup('CREATE', 'nova:your-mode', 'your-mode-group', '$', 'MKSTREAM', (err) => {
    if (err && !err.message.includes('BUSYGROUP')) {
      console.error('Error creating consumer group:', err);
    }
    
    this.consumeEvents();
  });
}
```

#### `consumeEvents`
Consumes events from Redis streams.

```typescript
private async consumeEvents(): Promise<void> {
  try {
    const results = await this.redis.xreadgroup(
      'GROUP', 'your-mode-group', 'your-mode-consumer',
      'COUNT', '10',
      'BLOCK', '2000',
      'STREAMS', 'nova:your-mode', '>'
    );
    
    // Process results
    
    // Continue consuming
    setImmediate(() => this.consumeEvents());
  } catch (error) {
    console.error('Error consuming events:', error);
    // Retry after delay
    setTimeout(() => this.consumeEvents(), 5000);
  }
}
```

#### Event Handlers
Process specific event types.

```typescript
private async processEvent(event: Record<string, string>): Promise<void> {
  const eventType = event.type;
  
  switch (eventType) {
    case 'your-event-type':
      await this.handleYourEventType(event);
      break;
    default:
      console.log(`Unknown event type: ${eventType}`);
  }
}
```

#### API Endpoint Handlers
Handle API requests.

```typescript
private async yourEndpointHandler(request: any, reply: any): Promise<void> {
  try {
    const { param1, param2 } = request.body;
    
    // Implement endpoint logic
    const result = await this.yourBusinessLogic(param1, param2);
    
    reply.send(result);
  } catch (error) {
    console.error('Error in yourEndpointHandler:', error);
    reply.code(500).send({ error: 'Internal server error' });
  }
}
```

## 📝 Mode Registration <a name="mode-registration"></a>

After creating your mode configuration and implementation files, you need to register the mode with the system.

### 1. Update `index.ts`

Add your mode to the `index.ts` file:

```typescript
import { YourMode } from './your_mode';

// In the initialization section
const yourMode = new YourMode(prisma, redis);
yourMode.registerRoutes(fastify);
yourMode.initializeStreamListeners();
```

### 2. Update Boomerang Mode Configuration

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

### 3. Create Mode-Specific Redis Streams

Initialize any Redis streams your mode will use:

```bash
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:your-mode '*' type init content "Your mode stream initialized"
```

## 🧪 Mode Testing <a name="mode-testing"></a>

Testing your mode is crucial to ensure it functions correctly. Here's a comprehensive testing approach:

### 1. Unit Testing

Create unit tests for your mode's business logic:

```typescript
// your_mode.test.ts
import { YourMode } from './your_mode';
import { mockPrisma, mockRedis } from './test/mocks';

describe('YourMode', () => {
  let yourMode: YourMode;
  
  beforeEach(() => {
    yourMode = new YourMode(mockPrisma, mockRedis);
  });
  
  test('yourBusinessLogic should return expected result', async () => {
    // @ts-ignore - Accessing private method for testing
    const result = await yourMode.yourBusinessLogic('param1', 'param2');
    
    expect(result).toEqual({
      success: true,
      param1: 'param1',
      param2: 'param2'
    });
  });
  
  // Add more tests for other methods
});
```

### 2. API Testing

Test your mode's API endpoints:

```typescript
// your_mode_api.test.ts
import { build } from './test/helper';

describe('YourMode API', () => {
  let app;
  
  beforeEach(async () => {
    app = await build();
  });
  
  test('POST /api/v1/your-mode/endpoint should return 200', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/v1/your-mode/endpoint',
      payload: {
        param1: 'value1',
        param2: 'value2'
      }
    });
    
    expect(response.statusCode).toBe(200);
    expect(JSON.parse(response.payload)).toEqual({
      success: true,
      param1: 'value1',
      param2: 'value2'
    });
  });
  
  // Add more tests for other endpoints
});
```

### 3. Integration Testing

Test your mode's integration with Redis streams:

```typescript
// your_mode_integration.test.ts
import { YourMode } from './your_mode';
import { PrismaClient } from '@prisma/client';
import { Redis } from 'ioredis';

describe('YourMode Integration', () => {
  let yourMode: YourMode;
  let prisma: PrismaClient;
  let redis: Redis;
  
  beforeEach(() => {
    prisma = new PrismaClient();
    redis = new Redis({
      host: process.env.REDIS_HOST || '127.0.0.1',
      port: parseInt(process.env.REDIS_PORT || '7000'),
      password: process.env.REDIS_PASSWORD || 'd5d7817937232ca5'
    });
    
    yourMode = new YourMode(prisma, redis);
  });
  
  afterEach(async () => {
    await prisma.$disconnect();
    await redis.quit();
  });
  
  test('should process events from Redis stream', async () => {
    // Publish test event
    await redis.xadd('nova:your-mode', '*',
      'type', 'your-event-type',
      'param1', 'value1',
      'param2', 'value2',
      'timestamp', Date.now().toString()
    );
    
    // Wait for event processing
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verify event was processed
    // This will depend on what your event handler does
    
    // Clean up
    await redis.del('nova:your-mode');
  });
});
```

## 🔧 Advanced Mode Features <a name="advanced-mode-features"></a>

### Custom Tools

You can define custom tools for your mode:

```typescript
// In your mode implementation
public registerTools(toolRegistry: any): void {
  toolRegistry.register('your_custom_tool', this.yourCustomToolHandler.bind(this));
}

private async yourCustomToolHandler(params: any): Promise<any> {
  // Implement custom tool logic
  return { result: 'Custom tool result' };
}
```

### Mode-Specific Middleware

You can add mode-specific middleware:

```typescript
// In your mode implementation
public registerMiddleware(fastify: FastifyInstance): void {
  fastify.addHook('preHandler', async (request, reply) => {
    // Mode-specific middleware logic
    if (request.headers['x-mode'] !== 'your_mode_slug') {
      reply.code(403).send({ error: 'Access denied' });
      return;
    }
  });
}
```

### Mode State Persistence

You can persist mode state to the database:

```typescript
// In your mode implementation
private async saveState(id: string, state: YourModeState): Promise<void> {
  await this.prisma.modeState.upsert({
    where: { id },
    update: { state: JSON.stringify(state) },
    create: {
      id,
      mode: 'your_mode_slug',
      state: JSON.stringify(state)
    }
  });
}

private async loadState(id: string): Promise<YourModeState | null> {
  const record = await this.prisma.modeState.findUnique({
    where: { id }
  });
  
  if (!record) {
    return null;
  }
  
  return JSON.parse(record.state);
}
```

## 🔄 Mode Interaction Patterns <a name="mode-interaction-patterns"></a>

### Mode-to-Mode Communication

Modes can communicate with each other through Redis streams:

```typescript
// In your mode implementation
private async sendMessageToMode(targetMode: string, message: any): Promise<void> {
  await this.redis.xadd(`nova:mode:${targetMode}`, '*',
    'type', 'inter_mode_message',
    'from_mode', 'your_mode_slug',
    'content', JSON.stringify(message),
    'timestamp', Date.now().toString()
  );
}
```

### Task Delegation

Modes can delegate tasks to other modes:

```typescript
// In your mode implementation
private async delegateTask(targetMode: string, task: any): Promise<void> {
  await this.redis.xadd(`nova:mode:${targetMode}:tasks`, '*',
    'type', 'task.delegated',
    'from_mode', 'your_mode_slug',
    'task', JSON.stringify(task),
    'timestamp', Date.now().toString()
  );
}
```

### Mode Switching

Modes can request a switch to another mode:

```typescript
// In your mode implementation
private async requestModeSwitch(targetMode: string, reason: string): Promise<void> {
  await this.redis.xadd('nova:mode:switch', '*',
    'type', 'mode.switch_requested',
    'from_mode', 'your_mode_slug',
    'to_mode', targetMode,
    'reason', reason,
    'timestamp', Date.now().toString()
  );
}
```

## 📚 Example Modes <a name="example-modes"></a>

### Research Mode

A mode specialized in gathering and analyzing information.

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

**research_mode.ts** (simplified):
```typescript
import { FastifyInstance } from 'fastify';
import { PrismaClient } from '@prisma/client';
import { Redis } from 'ioredis';

export class ResearchMode {
  private prisma: PrismaClient;
  private redis: Redis;

  constructor(prisma: PrismaClient, redis: Redis) {
    this.prisma = prisma;
    this.redis = redis;
  }

  public registerRoutes(fastify: FastifyInstance): void {
    fastify.post('/api/v1/research/gather', this.gatherInformation.bind(this));
    fastify.post('/api/v1/research/analyze', this.analyzeData.bind(this));
    fastify.post('/api/v1/research/synthesize', this.synthesizeFindings.bind(this));
  }

  public initializeStreamListeners(): void {
    this.redis.xgroup('CREATE', 'nova:research', 'research-group', '$', 'MKSTREAM', (err) => {
      if (err && !err.message.includes('BUSYGROUP')) {
        console.error('Error creating consumer group:', err);
      }
      
      this.consumeEvents();
    });
  }

  private async consumeEvents(): Promise<void> {
    // Implementation omitted for brevity
  }

  private async gatherInformation(request: any, reply: any): Promise<void> {
    // Implementation omitted for brevity
  }

  private async analyzeData(request: any, reply: any): Promise<void> {
    // Implementation omitted for brevity
  }

  private async synthesizeFindings(request: any, reply: any): Promise<void> {
    // Implementation omitted for brevity
  }
}
```

### Design Mode

A mode specialized in UI/UX design.

**design_mode_config.json**:
```json
{
  "name": "Design",
  "slug": "design",
  "description": "Specialized in UI/UX design and visual communication",
  "version": "1.0.0",
  "role": "You are a design specialist who excels at creating user interfaces, user experiences, and visual assets.",
  "capabilities": [
    "ui_design",
    "ux_design",
    "visual_communication",
    "design_system_creation",
    "wireframing"
  ],
  "file_restrictions": {
    "allowed_patterns": [
      ".*\\.md$",
      ".*\\.css$",
      ".*\\.scss$",
      ".*\\.html$",
      ".*\\.svg$",
      ".*\\.png$",
      ".*\\.jpg$"
    ],
    "blocked_patterns": [
      ".*\\.js$",
      ".*\\.ts$",
      ".*\\.py$"
    ]
  },
  "instructions": [
    "Focus on creating intuitive and user-friendly designs",
    "Adhere to design principles and best practices",
    "Consider accessibility in all designs",
    "Maintain consistency with existing design systems",
    "Provide clear explanations for design decisions"
  ]
}
```

**design_mode.ts** (simplified):
```typescript
import { FastifyInstance } from 'fastify';
import { PrismaClient } from '@prisma/client';
import { Redis } from 'ioredis';

export class DesignMode {
  private prisma: PrismaClient;
  private redis: Redis;

  constructor(prisma: PrismaClient, redis: Redis) {
    this.prisma = prisma;
    this.redis = redis;
  }

  public registerRoutes(fastify: FastifyInstance): void {
    fastify.post('/api/v1/design/wireframe', this.createWireframe.bind(this));
    fastify.post('/api/v1/design/ui', this.createUI.bind(this));
    fastify.post('/api/v1/design/ux', this.createUX.bind(this));
  }

  public initializeStreamListeners(): void {
    this.redis.xgroup('CREATE', 'nova:design', 'design-group', '$', 'MKSTREAM', (err) => {
      if (err && !err.message.includes('BUSYGROUP')) {
        console.error('Error creating consumer group:', err);
      }
      
      this.consumeEvents();
    });
  }

  private async consumeEvents(): Promise<void> {
    // Implementation omitted for brevity
  }

  private async createWireframe(request: any, reply: any): Promise<void> {
    // Implementation omitted for brevity
  }

  private async createUI(request: any, reply: any): Promise<void> {
    // Implementation omitted for brevity
  }

  private async createUX(request: any, reply: any): Promise<void> {
    // Implementation omitted for brevity
  }
}
```

## 🔧 Troubleshooting <a name="troubleshooting"></a>

### Common Issues and Solutions

#### Mode Not Registered

**Problem**: Mode is not appearing in the available modes list.

**Solution**:
1. Verify that the mode is correctly registered in `index.ts`
2. Check that the mode is added to the `available_modes` array in the Boomerang mode configuration
3. Restart the server to ensure the mode is loaded

#### Redis Stream Errors

**Problem**: Redis stream operations are failing.

**Solution**:
1. Verify Redis connection parameters
2. Check that the stream exists
3. Ensure the consumer group is created correctly
4. Check for authentication issues

```bash
# Check if stream exists
redis-cli -c -p 7000 -a d5d7817937232ca5 TYPE nova:your-mode

# Create stream if it doesn't exist
redis-cli -c -p 7000 -a d5d7817937232ca5 XADD nova:your-mode '*' type init content "Your mode stream initialized"

# Check consumer groups
redis-cli -c -p 7000 -a d5d7817937232ca5 XINFO GROUPS nova:your-mode
```

#### API Endpoint Errors

**Problem**: API endpoints are returning errors.

**Solution**:
1. Check the route registration in `registerRoutes`
2. Verify the endpoint handler implementation
3. Check for any middleware that might be blocking the request
4. Look for errors in the server logs

#### Mode Switching Issues

**Problem**: Mode switching is not working.

**Solution**:
1. Verify that the mode slug is correct
2. Check that the mode exists in the available modes
3. Ensure the mode switch request is being sent correctly
4. Look for errors in the server logs

---

This comprehensive guide provides all the information needed to create, implement, and register custom modes within the Nova ecosystem. If you have any questions or need further assistance, please contact the CommsOps team.