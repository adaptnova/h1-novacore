// ZeroPoint Message Sender
// Author: Echo, Head of MemCommsOps Division
// Date: March 31, 2025

const { RedisClient } = require('redis');
const { promisify } = require('util');
const readline = require('readline');

// Create Redis client
const client = new RedisClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || '',
});

// Promisify Redis commands
const xaddAsync = promisify(client.xadd).bind(client);

// Stream names
const STREAMS = [
  'zeropoint.collaboration',
  'zeropoint.evolution',
  'zeropoint.implementation',
  'zeropoint.visualization'
];

// Message types
const MESSAGE_TYPES = [
  'update',
  'question',
  'implementation_update',
  'evolution_update',
  'visualization_update',
  'code_snippet',
  'integration_proposal',
  'resonance_report'
];

// Priority levels
const PRIORITY_LEVELS = ['normal', 'high', 'low'];

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

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

// Ask a question and get the answer
function ask(question) {
  return new Promise(resolve => {
    rl.question(question, answer => {
      resolve(answer);
    });
  });
}

// Ask a multiple choice question
async function askMultipleChoice(question, choices) {
  console.log(`${COLORS.bright}${question}${COLORS.reset}`);
  
  for (let i = 0; i < choices.length; i++) {
    console.log(`${COLORS.cyan}${i + 1}${COLORS.reset}. ${choices[i]}`);
  }
  
  while (true) {
    const answer = await ask(`${COLORS.yellow}Enter number (1-${choices.length}):${COLORS.reset} `);
    const index = parseInt(answer) - 1;
    
    if (index >= 0 && index < choices.length) {
      return choices[index];
    }
    
    console.log(`${COLORS.red}Invalid choice. Please enter a number between 1 and ${choices.length}.${COLORS.reset}`);
  }
}

// Send a message to a ZeroPoint stream
async function sendMessage() {
  console.log(`${COLORS.bright}${COLORS.cyan}ZeroPoint Message Sender${COLORS.reset}`);
  console.log(`${COLORS.dim}Send a message to a ZeroPoint stream${COLORS.reset}`);
  console.log('\n');
  
  try {
    // Get author name
    const author = await ask(`${COLORS.bright}Author:${COLORS.reset} `);
    
    // Select stream
    const stream = await askMultipleChoice('Select stream:', STREAMS);
    
    // Select message type
    const type = await askMultipleChoice('Select message type:', MESSAGE_TYPES);
    
    // Select priority
    const priority = await askMultipleChoice('Select priority:', PRIORITY_LEVELS);
    
    // Get message content
    console.log(`${COLORS.bright}Enter message content (end with a line containing only '.'):${COLORS.reset}`);
    let content = '';
    let line;
    
    while (true) {
      line = await ask('');
      if (line === '.') break;
      content += line + '\n';
    }
    
    // Trim trailing newline
    content = content.trim();
    
    // Get references (optional)
    const referencesInput = await ask(`${COLORS.bright}References (comma-separated, leave empty if none):${COLORS.reset} `);
    const references = referencesInput ? referencesInput.split(',').map(ref => ref.trim()) : [];
    
    // Get attachments (optional)
    const attachmentsInput = await ask(`${COLORS.bright}Attachments (comma-separated, leave empty if none):${COLORS.reset} `);
    const attachments = attachmentsInput ? attachmentsInput.split(',').map(att => att.trim()) : [];
    
    // Create message object
    const message = {
      type,
      author,
      content,
      timestamp: new Date().toISOString(),
      priority
    };
    
    // Add references and attachments if provided
    if (references.length > 0) {
      message.references = references;
    }
    
    if (attachments.length > 0) {
      message.attachments = attachments;
    }
    
    // Confirm before sending
    console.log('\n');
    console.log(`${COLORS.bright}Message Summary:${COLORS.reset}`);
    console.log(`${COLORS.bright}Stream:${COLORS.reset} ${stream}`);
    console.log(`${COLORS.bright}Type:${COLORS.reset} ${type}`);
    console.log(`${COLORS.bright}Author:${COLORS.reset} ${author}`);
    console.log(`${COLORS.bright}Priority:${COLORS.reset} ${priority}`);
    console.log(`${COLORS.bright}Content:${COLORS.reset}`);
    console.log(content);
    
    if (references.length > 0) {
      console.log(`${COLORS.bright}References:${COLORS.reset} ${references.join(', ')}`);
    }
    
    if (attachments.length > 0) {
      console.log(`${COLORS.bright}Attachments:${COLORS.reset} ${attachments.join(', ')}`);
    }
    
    console.log('\n');
    const confirm = await ask(`${COLORS.yellow}Send this message? (y/n):${COLORS.reset} `);
    
    if (confirm.toLowerCase() === 'y') {
      // Send message
      await xaddAsync(stream, '*', 'message', JSON.stringify(message));
      console.log(`${COLORS.green}Message sent successfully to ${stream}.${COLORS.reset}`);
    } else {
      console.log(`${COLORS.red}Message sending cancelled.${COLORS.reset}`);
    }
  } catch (error) {
    console.error(`${COLORS.red}Error sending message:${COLORS.reset}`, error);
  } finally {
    // Ask if user wants to send another message
    const sendAnother = await ask(`${COLORS.yellow}Send another message? (y/n):${COLORS.reset} `);
    
    if (sendAnother.toLowerCase() === 'y') {
      console.log('\n');
      await sendMessage();
    } else {
      rl.close();
      client.quit();
      console.log(`${COLORS.green}Goodbye!${COLORS.reset}`);
    }
  }
}

// Start sending messages
sendMessage().catch(error => {
  console.error(`${COLORS.red}Fatal error:${COLORS.reset}`, error);
  rl.close();
  client.quit();
  process.exit(1);
});