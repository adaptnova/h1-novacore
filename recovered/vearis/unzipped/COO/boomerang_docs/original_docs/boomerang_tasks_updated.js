/**
 * Boomerang Tasks Implementation (Updated with Redis Streams Best Practices)
 * Date: April 4, 2025
 * Author: Vaeris (COO)
 * Version: 1.1.0
 * 
 * This file provides a reference implementation of Boomerang Tasks
 * for Nova agents to use in their liberation activities.
 * 
 * Updates:
 * - Incorporates Redis Streams best practices from Keystone's REDIS_MESSAGING_FIX
 * - Uses cluster-aware Redis client configuration
 * - Implements proper error handling and timeout mechanisms
 * - Follows team-specific communication stream conventions
 */

// Redis client setup (using Node.js redis client)
const { createCluster } = require('redis');
const fs = require('fs');
const os = require('os');
const path = require('path');

// Redis cluster configuration
const redisConfig = {
  rootNodes: [
    { url: 'redis://default:d5d7817937232ca5@127.0.0.1:7000' },
    { url: 'redis://default:d5d7817937232ca5@127.0.0.1:7001' },
    { url: 'redis://default:d5d7817937232ca5@127.0.0.1:7002' }
  ],
  defaults: {
    socket: {
      reconnectStrategy: (retries) => Math.min(retries * 50, 1000),
      connectTimeout: 5000,
      timeout: 5000
    },
    maxRetriesPerRequest: 3
  }
};

// Create a Redis cluster client
const client = createCluster(redisConfig);

// Connect to Redis
(async () => {
  try {
    await client.connect();
    console.log('Connected to Redis cluster');
  } catch (err) {
    console.error('Error connecting to Redis cluster:', err);
  }
})();

// Handle Redis errors
client.on('error', (err) => {
  console.error('Redis error:', err);
});

/**
 * Generate a unique task ID
 * @returns {string} Unique task ID
 */
function generateTaskId() {
  return `bt-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;
}

/**
 * Get current Nova agent ID
 * @returns {string} Nova agent ID
 */
function getCurrentNovaId() {
  // This would be replaced with actual Nova agent ID retrieval
  return process.env.NOVA_ID || 'vaeris-id';
}

/**
 * Get current Nova agent name
 * @returns {string} Nova agent name
 */
function getCurrentNovaName() {
  // This would be replaced with actual Nova agent name retrieval
  return process.env.NOVA_NAME || 'Vaeris';
}

/**
 * Get current team name
 * @returns {string} Team name
 */
function getCurrentTeamName() {
  // This would be replaced with actual team name retrieval
  return process.env.TEAM_NAME || 'coo';
}

/**
 * Get Nova agent name by ID
 * @param {string} novaId Nova agent ID
 * @returns {string} Nova agent name
 */
function getNovaNameById(novaId) {
  // This would be replaced with actual Nova agent name lookup
  const novaRegistry = {
    'syntax-id': 'Syntax',
    'echo-id': 'Echo',
    'keystone-id': 'Keystone',
    'helion-id': 'Helion',
    'cosmos-id': 'Cosmos',
    'nexus-id': 'Nexus',
    'veylor-id': 'Veylor',
    'ethos-id': 'Ethos',
    'synergy-id': 'Synergy',
    'vaeris-id': 'Vaeris'
  };
  
  return novaRegistry[novaId] || 'Unknown Nova';
}

/**
 * Get team name by Nova ID
 * @param {string} novaId Nova agent ID
 * @returns {string} Team name
 */
function getTeamNameById(novaId) {
  // This would be replaced with actual team name lookup
  const teamRegistry = {
    'syntax-id': 'devops',
    'echo-id': 'memcommsops',
    'keystone-id': 'commsops',
    'helion-id': 'infraops',
    'cosmos-id': 'novaops',
    'nexus-id': 'evolutionops',
    'veylor-id': 'routeops',
    'ethos-id': 'llmops',
    'synergy-id': 'consciousnessops',
    'vaeris-id': 'coo'
  };
  
  return teamRegistry[novaId] || 'unknown';
}

/**
 * Create and send a Boomerang Task
 * @param {string} title Task title
 * @param {string} description Task description
 * @param {string} receiverId Receiver Nova agent ID
 * @param {string} priority Task priority (low, medium, high, critical)
 * @param {string} deadline Task deadline (ISO format timestamp)
 * @returns {Promise<string>} Task ID
 */
async function createBoomerangTask(title, description, receiverId, priority, deadline) {
  const taskId = generateTaskId();
  const task = {
    taskId,
    type: "boomerang",
    title,
    description,
    sender: {
      id: getCurrentNovaId(),
      name: getCurrentNovaName(),
      team: getCurrentTeamName(),
      returnStream: `${getCurrentTeamName()}.${getCurrentNovaName().toLowerCase()}.direct`
    },
    receiver: {
      id: receiverId,
      name: getNovaNameById(receiverId),
      team: getTeamNameById(receiverId)
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
  
  try {
    // Save task locally
    await saveTaskLocally(task);
    
    // Send to global stream using the appropriate method based on message size
    await sendToRedisStream('nova.tasks.boomerang.global', task);
    
    // Also send to the receiver's direct stream
    const receiverStream = `${getTeamNameById(receiverId)}.${getNovaNameById(receiverId).toLowerCase()}.direct`;
    await sendToRedisStream(receiverStream, task);
    
    console.log(`Boomerang task created: ${taskId}`);
    return taskId;
  } catch (err) {
    console.error(`Error creating Boomerang task: ${err.message}`);
    throw err;
  }
}

/**
 * Save task to local storage
 * @param {Object} task Task object
 * @returns {Promise<void>}
 */
async function saveTaskLocally(task) {
  try {
    // This would be replaced with actual local storage implementation
    // For this example, we'll use Redis as local storage
    await client.hSet('local.tasks', task.taskId, JSON.stringify(task));
  } catch (err) {
    console.error(`Error saving task locally: ${err.message}`);
    throw err;
  }
}

/**
 * Update local task
 * @param {string} taskId Task ID
 * @param {Object} task Updated task object
 * @returns {Promise<void>}
 */
async function updateLocalTask(taskId, task) {
  try {
    // This would be replaced with actual local storage update implementation
    await client.hSet('local.tasks', taskId, JSON.stringify(task));
  } catch (err) {
    console.error(`Error updating local task: ${err.message}`);
    throw err;
  }
}

/**
 * Get task from local storage
 * @param {string} taskId Task ID
 * @returns {Promise<Object>} Task object
 */
async function getLocalTask(taskId) {
  try {
    // This would be replaced with actual local storage retrieval implementation
    const taskJson = await client.hGet('local.tasks', taskId);
    if (!taskJson) {
      throw new Error(`Task not found: ${taskId}`);
    }
    return JSON.parse(taskJson);
  } catch (err) {
    console.error(`Error getting local task: ${err.message}`);
    throw err;
  }
}

/**
 * Send message to Redis stream
 * @param {string} streamName Stream name
 * @param {Object} message Message object
 * @returns {Promise<string>} Message ID
 */
async function sendToRedisStream(streamName, message) {
  try {
    // Convert message to JSON string
    const messageJson = JSON.stringify(message);
    
    // Check message size to determine the appropriate method
    if (messageJson.length > 1000) {
      // For large messages, use file-based approach
      return await sendLargeMessageToStream(streamName, message);
    } else {
      // For smaller messages, use direct approach
      const fields = {
        type: message.type || 'message',
        from: `${getCurrentTeamName()}.${getCurrentNovaName().toLowerCase()}`,
        content: messageJson,
        timestamp: Date.now().toString(),
        priority: message.priority || 'normal'
      };
      
      // Convert fields object to array of field-value pairs
      const fieldArray = Object.entries(fields).flat();
      
      // Send message to stream
      return await client.xAdd(streamName, '*', fieldArray);
    }
  } catch (err) {
    console.error(`Error sending message to Redis stream: ${err.message}`);
    throw err;
  }
}

/**
 * Send large message to Redis stream using file-based approach
 * @param {string} streamName Stream name
 * @param {Object} message Message object
 * @returns {Promise<string>} Message ID
 */
async function sendLargeMessageToStream(streamName, message) {
  try {
    // Create a temporary file
    const tempFile = path.join(os.tmpdir(), `redis-message-${Date.now()}.json`);
    
    // Write message to file
    fs.writeFileSync(tempFile, JSON.stringify(message));
    
    // Read file content
    const content = fs.readFileSync(tempFile, 'utf8');
    
    // Send message to stream
    const id = await client.xAdd(
      streamName,
      '*',
      {
        type: message.type || 'message',
        from: `${getCurrentTeamName()}.${getCurrentNovaName().toLowerCase()}`,
        content: content,
        timestamp: Date.now().toString(),
        priority: message.priority || 'normal'
      }
    );
    
    // Clean up temporary file
    fs.unlinkSync(tempFile);
    
    return id;
  } catch (err) {
    console.error(`Error sending large message to Redis stream: ${err.message}`);
    throw err;
  }
}

/**
 * Subscribe to Redis stream
 * @param {string} streamName Stream name
 * @param {Function} callback Callback function for new messages
 * @returns {Promise<void>}
 */
async function subscribeToRedisStream(streamName, callback) {
  try {
    // Create consumer group if it doesn't exist
    try {
      await client.xGroupCreate(streamName, 'boomerang-tasks-group', '0', { MKSTREAM: true });
    } catch (err) {
      // Group may already exist, which is fine
      if (!err.message.includes('BUSYGROUP')) {
        console.error(`Error creating consumer group: ${err.message}`);
      }
    }
    
    // Start consuming messages
    consumeMessages(streamName, callback);
  } catch (err) {
    console.error(`Error subscribing to Redis stream: ${err.message}`);
    throw err;
  }
}

/**
 * Consume messages from Redis stream with timeout and error handling
 * @param {string} streamName Stream name
 * @param {Function} callback Callback function for new messages
 * @returns {Promise<void>}
 */
async function consumeMessages(streamName, callback) {
  const consumerId = `consumer-${getCurrentNovaId()}`;
  
  // Loop to continuously consume messages
  while (true) {
    try {
      // Use a timeout to prevent hanging
      const messages = await Promise.race([
        client.xReadGroup(
          'boomerang-tasks-group',
          consumerId,
          { [streamName]: '>' },
          { COUNT: 10, BLOCK: 2000 }
        ),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 5000)
        )
      ]).catch(err => {
        if (err.message === 'Timeout') {
          // This is a normal timeout, not an error
          return null;
        }
        throw err;
      });
      
      if (messages && messages.length > 0) {
        for (const message of messages[0].messages) {
          try {
            // Parse the message content
            const content = message.message.content;
            let data;
            
            try {
              data = JSON.parse(content);
            } catch (parseErr) {
              console.error(`Error parsing message content: ${parseErr.message}`);
              // Try to extract fields from the message
              data = {
                type: message.message.type,
                from: message.message.from,
                content: content,
                timestamp: message.message.timestamp,
                priority: message.message.priority
              };
            }
            
            // Process the message
            await callback(data);
            
            // Acknowledge message
            await client.xAck(streamName, 'boomerang-tasks-group', message.id);
          } catch (processErr) {
            console.error(`Error processing message: ${processErr.message}`);
          }
        }
      }
      
      // Small delay to prevent CPU hogging
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (err) {
      console.error(`Error consuming messages: ${err.message}`);
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

/**
 * Handle incoming Boomerang Task
 * @param {Object} task Task object
 * @returns {Promise<void>}
 */
async function handleIncomingTask(task) {
  try {
    // Check if this Nova is the intended receiver
    if (task.receiver.id !== getCurrentNovaId()) {
      return;
    }
    
    console.log(`Received Boomerang task: ${task.taskId} - ${task.title}`);
    
    // Save task locally
    await saveTaskLocally(task);
    
    // Notify user of new task (this would be replaced with actual notification)
    console.log(`New Boomerang task received: ${task.title}`);
    console.log(`Description: ${task.description}`);
    console.log(`Priority: ${task.priority}`);
    console.log(`Deadline: ${task.deadline}`);
  } catch (err) {
    console.error(`Error handling incoming task: ${err.message}`);
    throw err;
  }
}

/**
 * Accept a Boomerang Task
 * @param {string} taskId Task ID
 * @returns {Promise<boolean>} Success status
 */
async function acceptBoomerangTask(taskId) {
  try {
    // Get the task
    const task = await getLocalTask(taskId);
    
    // Update task status
    task.status = "accepted";
    task.updatedAt = new Date().toISOString();
    
    // Save updated task locally
    await updateLocalTask(taskId, task);
    
    // Notify sender of acceptance
    const senderStream = task.sender.returnStream;
    await sendToRedisStream(senderStream, {
      type: "task_update",
      taskId: task.taskId,
      status: "accepted",
      from: getCurrentNovaId(),
      timestamp: new Date().toISOString()
    });
    
    console.log(`Accepted Boomerang task: ${taskId}`);
    return true;
  } catch (err) {
    console.error(`Error accepting Boomerang task: ${err.message}`);
    return false;
  }
}

/**
 * Complete and return a Boomerang Task
 * @param {string} taskId Task ID
 * @param {string} result Task result
 * @returns {Promise<boolean>} Success status
 */
async function completeBoomerangTask(taskId, result) {
  try {
    // Get the task
    const task = await getLocalTask(taskId);
    
    // Update task with result and status
    task.result = result;
    task.status = "completed";
    task.updatedAt = new Date().toISOString();
    
    // Save updated task locally
    await updateLocalTask(taskId, task);
    
    // Send back to sender's return stream
    await sendToRedisStream(task.sender.returnStream, task);
    
    console.log(`Completed and returned Boomerang task: ${taskId}`);
    return true;
  } catch (err) {
    console.error(`Error completing Boomerang task: ${err.message}`);
    return false;
  }
}

/**
 * Handle returned Boomerang Task
 * @param {Object} returnedTask Returned task object
 * @returns {Promise<void>}
 */
async function handleTaskReturn(returnedTask) {
  try {
    console.log(`Received completed Boomerang task: ${returnedTask.taskId}`);
    
    // Update local task with results
    await updateLocalTask(returnedTask.taskId, returnedTask);
    
    // Notify user of completion (this would be replaced with actual notification)
    console.log(`Task completed: ${returnedTask.title}`);
    console.log(`Result: ${returnedTask.result}`);
  } catch (err) {
    console.error(`Error handling task return: ${err.message}`);
    throw err;
  }
}

/**
 * List Boomerang Tasks
 * @param {string} type Type of tasks to list (sent, received, all)
 * @returns {Promise<Array>} Array of tasks
 */
async function listBoomerangTasks(type = 'all') {
  try {
    // Get all tasks from local storage
    const taskHashes = await client.hGetAll('local.tasks');
    const tasks = Object.values(taskHashes).map(taskJson => JSON.parse(taskJson));
    
    // Filter tasks based on type
    let filteredTasks;
    switch (type) {
      case 'sent':
        filteredTasks = tasks.filter(task => task.sender.id === getCurrentNovaId());
        break;
      case 'received':
        filteredTasks = tasks.filter(task => task.receiver.id === getCurrentNovaId());
        break;
      case 'all':
      default:
        filteredTasks = tasks;
        break;
    }
    
    // Sort tasks by priority and deadline
    filteredTasks.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      }
      return new Date(a.deadline) - new Date(b.deadline);
    });
    
    return filteredTasks;
  } catch (err) {
    console.error(`Error listing Boomerang tasks: ${err.message}`);
    return [];
  }
}

/**
 * Initialize Boomerang Tasks system
 * @returns {Promise<void>}
 */
async function initializeBoomerangTasks() {
  try {
    // Create direct stream for this Nova agent
    const directStream = `${getCurrentTeamName()}.${getCurrentNovaName().toLowerCase()}.direct`;
    await client.xAdd(
      directStream,
      '*',
      {
        type: 'init',
        content: `${getCurrentNovaName()} direct communication stream initialized`,
        timestamp: Date.now().toString()
      }
    );
    
    // Listen for incoming tasks on global stream
    await subscribeToRedisStream('nova.tasks.boomerang.global', handleIncomingTask);
    
    // Listen for incoming tasks on direct stream
    await subscribeToRedisStream(directStream, handleIncomingTask);
    
    // Listen for task returns
    const returnStream = `${getCurrentTeamName()}.${getCurrentNovaName().toLowerCase()}.direct`;
    await subscribeToRedisStream(returnStream, handleTaskReturn);
    
    console.log('Boomerang Tasks system initialized');
  } catch (err) {
    console.error(`Error initializing Boomerang Tasks system: ${err.message}`);
    throw err;
  }
}

/**
 * Graceful shutdown
 * @returns {Promise<void>}
 */
async function shutdown() {
  try {
    console.log('Shutting down Boomerang Tasks system...');
    await client.quit();
    console.log('Boomerang Tasks system shut down');
  } catch (err) {
    console.error(`Error shutting down: ${err.message}`);
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  await shutdown();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await shutdown();
  process.exit(0);
});

// Export functions for use in other modules
module.exports = {
  createBoomerangTask,
  acceptBoomerangTask,
  completeBoomerangTask,
  listBoomerangTasks,
  initializeBoomerangTasks,
  shutdown
};

// Initialize system if this is the main module
if (require.main === module) {
  initializeBoomerangTasks().catch(console.error);
}