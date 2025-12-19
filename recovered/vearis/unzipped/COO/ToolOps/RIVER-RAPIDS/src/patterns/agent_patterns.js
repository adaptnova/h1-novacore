/**
 * Agent Communication Patterns Implementation
 * Version: 1.0.2 - Core Patterns Focus
 */

const { QUEUE_CONFIG, getCommandQueueOptions, getEventQueueOptions, getExchangeConfig, getRoutingPattern } = require('../queues/queue_config');

class AgentPatterns {
  constructor(channel) {
    this.channel = channel;
    this.initialized = false;
    this.metrics = {
      connectionCount: 0,
      messageRate: 0
    };
  }

  /**
   * Initialize essential queues and exchanges
   */
  async initialize() {
    if (this.initialized) return;

    // Setup core exchanges
    await Promise.all(Object.values(QUEUE_CONFIG.exchanges).map(async (exchange) => {
      await this.channel.assertExchange(
        exchange.name,
        exchange.type,
        exchange.options
      );
    }));

    // Setup command queue
    const commandQueue = getCommandQueueOptions();
    await this.channel.assertQueue(
      commandQueue.name,
      commandQueue.options
    );

    // Setup event queue
    const eventQueue = getEventQueueOptions('broadcast');
    await this.channel.assertQueue(
      eventQueue.name,
      eventQueue.options
    );

    // Setup dead letter queue
    await this.channel.assertQueue(
      QUEUE_CONFIG.deadLetterQueue.name,
      QUEUE_CONFIG.deadLetterQueue.options
    );

    this.startMetricsCollection();
    this.initialized = true;
  }

  /**
   * Core command pattern implementation
   */
  async sendCommand(command) {
    await this.initialize();
    const startTime = Date.now();
    
    try {
      const queue = getCommandQueueOptions();
      const exchange = getExchangeConfig('command');
      const routingKey = getRoutingPattern('command');

      const success = await this.channel.publish(exchange.name, routingKey, Buffer.from(JSON.stringify(command)), {
        persistent: true,
        expiration: queue.options.messageTtl,
        headers: {
          messageType: 'command',
          timestamp: new Date().toISOString()
        }
      });

      this.updateMetrics('command', success);
      return success;
    } catch (error) {
      this.updateMetrics('command', false);
      throw error;
    }
  }

  /**
   * Core event pattern implementation
   */
  async publishEvent(event) {
    await this.initialize();
    const startTime = Date.now();
    
    try {
      const queue = getEventQueueOptions('broadcast');
      const exchange = getExchangeConfig('event');

      const success = await this.channel.publish(exchange.name, '', Buffer.from(JSON.stringify(event)), {
        persistent: true,
        expiration: queue.options.messageTtl,
        headers: {
          messageType: 'event',
          timestamp: new Date().toISOString()
        }
      });

      this.updateMetrics('event', success);
      return success;
    } catch (error) {
      this.updateMetrics('event', false);
      throw error;
    }
  }

  /**
   * Setup consumer for command operations
   */
  async consumeCommands(handler) {
    await this.initialize();
    const queue = getCommandQueueOptions();

    return this.setupConsumer(queue.name, handler);
  }

  /**
   * Setup consumer for events
   */
  async consumeEvents(handler) {
    await this.initialize();
    const queue = getEventQueueOptions('broadcast');

    return this.setupConsumer(queue.name, handler);
  }

  /**
   * Basic consumer setup with retry logic
   */
  async setupConsumer(queueName, handler) {
    return this.channel.consume(queueName, async (msg) => {
      try {
        await handler(msg);
        this.channel.ack(msg);
      } catch (error) {
        const retryCount = (msg.properties.headers.retryCount || 0) + 1;
        
        if (retryCount <= QUEUE_CONFIG.retryConfig.attempts) {
          setTimeout(() => {
            this.channel.nack(msg, false, false);
          }, QUEUE_CONFIG.retryConfig.delays[retryCount - 1]);
        } else {
          this.channel.nack(msg, false, false);
        }
      }
    });
  }

  /**
   * Basic metrics collection
   */
  startMetricsCollection() {
    setInterval(() => {
      // Check thresholds
      if (this.metrics.connectionCount > QUEUE_CONFIG.monitoring.thresholds.connection_max ||
          this.metrics.messageRate > QUEUE_CONFIG.monitoring.thresholds.message_rate_max) {
        console.error('Threshold exceeded:', this.metrics);
      }

      // Reset counters
      this.metrics.messageRate = 0;
    }, QUEUE_CONFIG.monitoring.collection.interval);
  }

  updateMetrics(operation, success) {
    if (success) {
      this.metrics.messageRate++;
    }
  }
}

module.exports = AgentPatterns;