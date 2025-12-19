/**
 * Test Implementation for Queue Patterns
 * Version: 1.0.3 - Nova Launch Ready
 */

const amqp = require('amqplib');
const AgentPatterns = require('./agent_patterns');
const { QUEUE_CONFIG, getConnectionConfig, getVhostConfig } = require('../queues/queue_config');

class TestImplementation {
  constructor() {
    this.connections = {
      ai_agents: null,
      ai_tasks: null,
      ai_results: null,
      chase: null
    };
    this.channels = {
      ai_agents: null,
      ai_tasks: null,
      ai_results: null,
      chase: null
    };
    this.patterns = null;
    this.configPath = '/data/novaops/rabbitmq/config';
    this.logPath = '/logs/novaops/rabbitmq';
  }

  /**
   * Verify system requirements
   */
  async verifySystemRequirements() {
    try {
      const os = require('os');
      const disk = require('diskusage');

      // Check memory
      const totalMem = os.totalmem() / (1024 * 1024 * 1024); // Convert to GB
      if (totalMem < QUEUE_CONFIG.system.memory.minimum) {
        throw new Error(`Insufficient memory: ${totalMem}GB < ${QUEUE_CONFIG.system.memory.minimum}GB required`);
      }

      // Check disk space
      const { free } = await disk.check('/');
      const freeGB = free / (1024 * 1024 * 1024);
      if (freeGB < QUEUE_CONFIG.system.disk.minimumFree) {
        throw new Error(`Insufficient disk space: ${freeGB}GB < ${QUEUE_CONFIG.system.disk.minimumFree}GB required`);
      }

      console.log('System requirements verified');
      return true;
    } catch (error) {
      console.error('System requirements verification failed:', error);
      return false;
    }
  }

  /**
   * Verify directory access and permissions
   */
  async verifyAccess() {
    try {
      const fs = require('fs').promises;
      const { constants } = require('fs');

      // Check configuration access
      await fs.access(this.configPath, constants.R_OK | constants.W_OK);
      console.log('Configuration directory access verified:', this.configPath);

      // Check log access
      await fs.access(this.logPath, constants.R_OK | constants.W_OK);
      console.log('Log directory access verified:', this.logPath);

      // Verify group membership
      const { execSync } = require('child_process');
      const groups = execSync('groups').toString();
      if (!groups.includes('rabbitmqgroup')) {
        console.warn('Warning: Current user not in rabbitmqgroup');
      }

      return true;
    } catch (error) {
      console.error('Access verification error:', error);
      return false;
    }
  }

  /**
   * Initialize test environment
   */
  async initialize() {
    try {
      // Verify system requirements and access
      await this.verifySystemRequirements();
      await this.verifyAccess();

      const mainConfig = getConnectionConfig('main');

      // Connect to each virtual host
      for (const vhost of Object.keys(QUEUE_CONFIG.vhosts)) {
        this.connections[vhost] = await amqp.connect({
          protocol: 'amqp',
          hostname: mainConfig.host,
          port: mainConfig.port,
          username: 'guest',
          password: 'guest',
          vhost: vhost
        });

        this.channels[vhost] = await this.connections[vhost].createChannel();
        
        // Set channel prefetch based on vhost config
        const vhostConfig = getVhostConfig(vhost);
        await this.channels[vhost].prefetch(Math.floor(vhostConfig.maxConnections / 10));
      }

      // Connect to Chase integration
      const chaseConfig = getConnectionConfig('chase');
      this.connections.chase = await amqp.connect({
        protocol: 'amqp',
        hostname: chaseConfig.host,
        port: chaseConfig.port,
        username: 'guest',
        password: 'guest',
        vhost: '/'
      });
      this.channels.chase = await this.connections.chase.createChannel();

      // Initialize patterns with AI agents channel
      this.patterns = new AgentPatterns(this.channels.ai_agents);
      await this.patterns.initialize();

      console.log('Test implementation initialized');
    } catch (error) {
      console.error('Initialization error:', error);
      throw error;
    }
  }

  /**
   * Test AI agent communication
   */
  async testAIAgentCommunication() {
    try {
      const testMessage = {
        type: 'ai_test',
        payload: {
          agentId: 'test_agent',
          action: 'verify_communication'
        }
      };

      // Test agent communication
      await this.channels.ai_agents.assertQueue('ai.agent.test');
      await this.channels.ai_agents.sendToQueue('ai.agent.test', Buffer.from(JSON.stringify(testMessage)));

      console.log('AI agent communication test completed');
    } catch (error) {
      console.error('AI agent communication test error:', error);
      throw error;
    }
  }

  /**
   * Test task distribution
   */
  async testTaskDistribution() {
    try {
      const testTask = {
        type: 'task_test',
        payload: {
          taskId: 'test_task',
          action: 'verify_distribution'
        }
      };

      // Test task queue
      await this.channels.ai_tasks.assertQueue('ai.task.test');
      await this.channels.ai_tasks.sendToQueue('ai.task.test', Buffer.from(JSON.stringify(testTask)));

      console.log('Task distribution test completed');
    } catch (error) {
      console.error('Task distribution test error:', error);
      throw error;
    }
  }

  /**
   * Test result collection
   */
  async testResultCollection() {
    try {
      const testResult = {
        type: 'result_test',
        payload: {
          resultId: 'test_result',
          status: 'success'
        }
      };

      // Test result queue
      await this.channels.ai_results.assertQueue('ai.result.test');
      await this.channels.ai_results.sendToQueue('ai.result.test', Buffer.from(JSON.stringify(testResult)));

      console.log('Result collection test completed');
    } catch (error) {
      console.error('Result collection test error:', error);
      throw error;
    }
  }

  /**
   * Run all tests
   */
  async runTests() {
    try {
      await this.initialize();
      await this.testAIAgentCommunication();
      await this.testTaskDistribution();
      await this.testResultCollection();
      
      console.log('All tests completed successfully');
    } catch (error) {
      console.error('Test suite error:', error);
    } finally {
      // Cleanup
      for (const channel of Object.values(this.channels)) {
        if (channel) await channel.close();
      }
      for (const connection of Object.values(this.connections)) {
        if (connection) await connection.close();
      }
    }
  }
}

// Export for use in integration testing
module.exports = TestImplementation;

// Run tests if executed directly
if (require.main === module) {
  const tester = new TestImplementation();
  tester.runTests().catch(console.error);
}