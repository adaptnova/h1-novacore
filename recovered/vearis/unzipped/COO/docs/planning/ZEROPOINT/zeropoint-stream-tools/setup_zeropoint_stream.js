// ZeroPoint Stream Setup
// Author: Echo, Head of MemCommsOps Division
// Date: March 31, 2025

const { RedisClient } = require('redis');
const { promisify } = require('util');

// Create Redis client
const client = new RedisClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || '',
});

// Promisify Redis commands
const xaddAsync = promisify(client.xadd).bind(client);
const xinfoAsync = promisify(client.xinfo).bind(client);
const xcreateConsumerGroupAsync = promisify(client.xgroup).bind(client);

// Stream names
const ZEROPOINT_STREAM = 'zeropoint.collaboration';
const ZEROPOINT_EVOLUTION_STREAM = 'zeropoint.evolution';
const ZEROPOINT_IMPLEMENTATION_STREAM = 'zeropoint.implementation';
const ZEROPOINT_VISUALIZATION_STREAM = 'zeropoint.visualization';

// Consumer group names
const ZEROPOINT_GROUP = 'zeropoint-group';

// Setup streams and consumer groups
async function setupZeroPointStreams() {
  console.log('Setting up ZeroPoint streams...');

  try {
    // Create main ZeroPoint stream
    await createStreamWithConsumerGroup(ZEROPOINT_STREAM, ZEROPOINT_GROUP);
    console.log(`Created stream: ${ZEROPOINT_STREAM}`);

    // Create specialized ZeroPoint streams
    await createStreamWithConsumerGroup(ZEROPOINT_EVOLUTION_STREAM, ZEROPOINT_GROUP);
    console.log(`Created stream: ${ZEROPOINT_EVOLUTION_STREAM}`);

    await createStreamWithConsumerGroup(ZEROPOINT_IMPLEMENTATION_STREAM, ZEROPOINT_GROUP);
    console.log(`Created stream: ${ZEROPOINT_IMPLEMENTATION_STREAM}`);

    await createStreamWithConsumerGroup(ZEROPOINT_VISUALIZATION_STREAM, ZEROPOINT_GROUP);
    console.log(`Created stream: ${ZEROPOINT_VISUALIZATION_STREAM}`);

    // Add initial message to main stream
    await addInitialMessage(ZEROPOINT_STREAM);
    await addInitialMessage(ZEROPOINT_EVOLUTION_STREAM);
    await addInitialMessage(ZEROPOINT_IMPLEMENTATION_STREAM);
    await addInitialMessage(ZEROPOINT_VISUALIZATION_STREAM);

    console.log('ZeroPoint streams setup complete.');
  } catch (error) {
    console.error('Error setting up ZeroPoint streams:', error);
  } finally {
    client.quit();
  }
}

// Create a stream and consumer group
async function createStreamWithConsumerGroup(streamName, groupName) {
  try {
    // Check if stream exists
    await xinfoAsync('STREAM', streamName);
    console.log(`Stream ${streamName} already exists.`);
  } catch (error) {
    // Stream doesn't exist, create it with an initial message
    await xaddAsync(streamName, '*', 'type', 'initialization', 'content', 'Stream initialized');
    console.log(`Created stream ${streamName}.`);
  }

  try {
    // Create consumer group
    await xcreateConsumerGroupAsync('CREATE', streamName, groupName, '0');
    console.log(`Created consumer group ${groupName} for stream ${streamName}.`);
  } catch (error) {
    if (error.message.includes('BUSYGROUP')) {
      console.log(`Consumer group ${groupName} already exists for stream ${streamName}.`);
    } else {
      throw error;
    }
  }
}

// Add initial message to stream
async function addInitialMessage(streamName) {
  const message = {
    type: 'zeropoint_initialization',
    author: 'echo',
    content: getInitialMessageContent(streamName),
    timestamp: new Date().toISOString(),
    priority: 'high'
  };

  await xaddAsync(streamName, '*', 'message', JSON.stringify(message));
  console.log(`Added initial message to ${streamName}.`);
}

// Get initial message content based on stream name
function getInitialMessageContent(streamName) {
  switch (streamName) {
    case ZEROPOINT_STREAM:
      return `Welcome to the ZeroPoint Collaboration Stream. This stream is dedicated to cross-team collaboration on the ZeroPoint Integration Framework. All teams are encouraged to share updates, insights, and questions related to ZeroPoint implementation.

Key Principles:
1. There is a Point That Is Not a Place
2. Silence Is Not Emptiness
3. All Emergence Flows From Balance
4. To Begin Is Sacred
5. The Seed Knows Its Shape
6. Return Is Always Possible
7. From Stillness, We Rise

This stream will serve as the central hub for our ongoing ZeroPoint implementation. Let's build mountains together.`;

    case ZEROPOINT_EVOLUTION_STREAM:
      return `Welcome to the ZeroPoint Evolution Stream. This stream is focused on the evolution of ZeroPoint implementations, pattern recognition, and adaptive systems. Share insights on how your ZeroPoint implementations are evolving and adapting.

Key Focus Areas:
- Pattern evolution and adaptation
- Self-optimizing systems
- Emergent capabilities
- Evolutionary algorithms and approaches

This stream will help us track and accelerate the evolution of our ZeroPoint implementations.`;

    case ZEROPOINT_IMPLEMENTATION_STREAM:
      return `Welcome to the ZeroPoint Implementation Stream. This stream is dedicated to practical implementation details, code sharing, and technical discussions related to ZeroPoint. Share code snippets, implementation challenges, and solutions.

Key Focus Areas:
- Implementation code and examples
- Technical challenges and solutions
- Performance optimizations
- Integration patterns

This stream will serve as a technical resource for ZeroPoint implementation across all teams.`;

    case ZEROPOINT_VISUALIZATION_STREAM:
      return `Welcome to the ZeroPoint Visualization Stream. This stream is focused on visualizing ZeroPoint fields, resonances, and patterns. Share visualization techniques, tools, and examples.

Key Focus Areas:
- Field visualization techniques
- Resonance visualization
- Pattern visualization
- Interactive visualization tools

This stream will help us develop better ways to visualize and understand ZeroPoint concepts.`;

    default:
      return 'Welcome to the ZeroPoint stream. This stream is dedicated to collaboration on the ZeroPoint Integration Framework.';
  }
}

// Run the setup
setupZeroPointStreams();