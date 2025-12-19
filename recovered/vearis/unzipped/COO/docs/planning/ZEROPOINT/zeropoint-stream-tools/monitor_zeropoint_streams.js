// ZeroPoint Stream Monitor
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
const xreadGroupAsync = promisify(client.xreadgroup).bind(client);
const xackAsync = promisify(client.xack).bind(client);

// Stream names
const STREAMS = [
  'zeropoint.collaboration',
  'zeropoint.evolution',
  'zeropoint.implementation',
  'zeropoint.visualization'
];

// Consumer group and consumer name
const GROUP = 'zeropoint-group';
const CONSUMER = `monitor-${Math.random().toString(36).substring(2, 10)}`;

// ANSI color codes for terminal output
const COLORS = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  underscore: '\x1b[4m',
  blink: '\x1b[5m',
  reverse: '\x1b[7m',
  hidden: '\x1b[8m',
  
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgCyan: '\x1b[46m',
  bgWhite: '\x1b[47m'
};

// Stream colors
const STREAM_COLORS = {
  'zeropoint.collaboration': COLORS.cyan,
  'zeropoint.evolution': COLORS.green,
  'zeropoint.implementation': COLORS.magenta,
  'zeropoint.visualization': COLORS.yellow
};

// Priority colors
const PRIORITY_COLORS = {
  'high': COLORS.red,
  'normal': COLORS.white,
  'low': COLORS.dim + COLORS.white
};

// Monitor streams
async function monitorStreams() {
  console.log(`${COLORS.bright}${COLORS.cyan}ZeroPoint Stream Monitor${COLORS.reset}`);
  console.log(`${COLORS.dim}Monitoring streams: ${STREAMS.join(', ')}${COLORS.reset}`);
  console.log(`${COLORS.dim}Consumer: ${CONSUMER}${COLORS.reset}`);
  console.log(`${COLORS.dim}Press Ctrl+C to exit${COLORS.reset}`);
  console.log('\n');
  
  // Start with '>' to get only new messages
  const streamEntries = STREAMS.map(stream => [stream, '>']);
  
  while (true) {
    try {
      const result = await xreadGroupAsync(
        'GROUP', GROUP, CONSUMER,
        'BLOCK', 1000,
        'STREAMS', ...STREAMS, ...STREAMS.map(() => '>')
      );
      
      if (result) {
        for (const [stream, messages] of result) {
          for (const [id, fields] of messages) {
            const message = JSON.parse(fields[1]);
            
            // Get colors for this stream and priority
            const streamColor = STREAM_COLORS[stream] || COLORS.white;
            const priorityColor = PRIORITY_COLORS[message.priority] || COLORS.white;
            
            // Format timestamp
            const timestamp = new Date(message.timestamp).toLocaleTimeString();
            
            // Print message header
            console.log(`\n${streamColor}${COLORS.bright}[${stream}]${COLORS.reset} ${COLORS.dim}${timestamp}${COLORS.reset}`);
            console.log(`${COLORS.bright}ID:${COLORS.reset} ${id}`);
            console.log(`${COLORS.bright}Type:${COLORS.reset} ${message.type}`);
            console.log(`${COLORS.bright}Author:${COLORS.reset} ${message.author}`);
            console.log(`${priorityColor}${COLORS.bright}Priority:${COLORS.reset}${priorityColor} ${message.priority}${COLORS.reset}`);
            
            // Print message content with word wrap
            console.log(`${COLORS.bright}Content:${COLORS.reset}`);
            const wrappedContent = wordWrap(message.content, 80);
            console.log(wrappedContent);
            
            // Print references if any
            if (message.references && message.references.length > 0) {
              console.log(`${COLORS.bright}References:${COLORS.reset} ${message.references.join(', ')}`);
            }
            
            // Print attachments if any
            if (message.attachments && message.attachments.length > 0) {
              console.log(`${COLORS.bright}Attachments:${COLORS.reset} ${message.attachments.join(', ')}`);
            }
            
            // Print separator
            console.log(`${COLORS.dim}${'─'.repeat(80)}${COLORS.reset}`);
            
            // Acknowledge message
            await xackAsync(stream, GROUP, id);
          }
        }
      }
    } catch (error) {
      console.error(`${COLORS.red}Error monitoring streams:${COLORS.reset}`, error);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

// Word wrap function
function wordWrap(text, maxLength) {
  if (!text) return '';
  
  const words = text.split(' ');
  let line = '';
  let result = '';
  
  for (const word of words) {
    if ((line + word).length > maxLength) {
      result += line + '\n';
      line = word + ' ';
    } else {
      line += word + ' ';
    }
  }
  
  if (line) {
    result += line;
  }
  
  return result;
}

// Handle process termination
process.on('SIGINT', () => {
  console.log(`\n${COLORS.yellow}Stopping monitor...${COLORS.reset}`);
  client.quit();
  process.exit();
});

// Start monitoring
monitorStreams().catch(error => {
  console.error(`${COLORS.red}Fatal error:${COLORS.reset}`, error);
  client.quit();
  process.exit(1);
});