/**
 * Chase Communications Service for NovaComms GUI
 * Version: 1.0.0
 * Last Updated: 2024-12-15
 */

import { RABBITMQ_CONFIG } from '../config/rabbitmq';
import monitoringService from './MonitoringService';

class ChaseCommsService {
  constructor() {
    this.channel = null;
    this.connection = null;
    this.subscribers = new Set();
    this.monitoringSubscription = null;
    this.lastMessage = null;
  }

  async initialize() {
    try {
      // Subscribe to monitoring service for system events
      this.monitoringSubscription = monitoringService.subscribe(
        this.handleMonitoringEvent.bind(this)
      );

      // Set up RabbitMQ connection
      await this.setupRabbitMQ();
    } catch (error) {
      console.error('Failed to initialize Chase Comms Service:', error);
      throw error;
    }
  }

  async setupRabbitMQ() {
    try {
      // Connect to RabbitMQ
      const amqp = require('amqplib');
      const { connection, queues } = RABBITMQ_CONFIG;

      this.connection = await amqp.connect({
        hostname: connection.host,
        port: connection.port,
        vhost: connection.vhost,
        username: process.env.REACT_APP_RABBITMQ_USER,
        password: process.env.REACT_APP_RABBITMQ_PASS,
        ssl: connection.ssl
      });

      // Create channel
      this.channel = await this.connection.createChannel();

      // Setup Chase comms queue
      const { chaseComms } = queues;
      await this.channel.assertQueue(chaseComms.name, {
        durable: chaseComms.durable,
        arguments: chaseComms.arguments
      });

      // Bind queue to exchange
      const binding = chaseComms.bindings[0];
      await this.channel.bindQueue(
        chaseComms.name,
        binding.exchange,
        binding.routingKey
      );

      // Set up consumer
      await this.channel.consume(
        chaseComms.name,
        this.handleMessage.bind(this),
        { noAck: false }
      );

      console.log('Chase Comms Service initialized successfully');
    } catch (error) {
      console.error('Failed to setup RabbitMQ:', error);
      throw error;
    }
  }

  handleMessage(msg) {
    if (!msg) return;

    try {
      const message = JSON.parse(msg.content.toString());
      const timestamp = Date.now();

      // Add visual effect metadata
      const visualEffect = this.getVisualEffect(message.type);

      this.lastMessage = {
        ...message,
        timestamp,
        visualEffect,
        priority: message.priority || this.calculatePriority(message)
      };

      // Process message based on type
      switch (message.type) {
        case 'chase.comms.status':
          this.handleStatusMessage(message);
          break;
        case 'chase.comms.update':
          this.handleUpdateMessage(message);
          break;
        case 'chase.comms.priority':
          this.handlePriorityMessage(message);
          break;
        case 'chase.comms.alert':
          this.handleAlertMessage(message);
          break;
        case 'chase.comms.burst':
          this.handleBurstMessage(message);
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }

      // Notify subscribers with enhanced message
      this.notifySubscribers('message', this.lastMessage);

      // Acknowledge message
      this.channel.ack(msg);
    } catch (error) {
      console.error('Error processing message:', error);
      // Reject message and requeue
      this.channel.nack(msg, false, true);
    }
  }

  getVisualEffect(messageType) {
    const effects = {
      'chase.comms.status': 'pulse',
      'chase.comms.update': 'glow',
      'chase.comms.priority': 'burst',
      'chase.comms.alert': 'alert',
      'chase.comms.burst': 'energyBurst'
    };
    return effects[messageType] || 'none';
  }

  calculatePriority(message) {
    if (message.type === 'chase.comms.alert') return 'high';
    if (message.type === 'chase.comms.priority') return message.level || 'medium';
    if (message.type === 'chase.comms.burst') return 'high';
    return 'low';
  }

  handleAlertMessage(message) {
    const { alert, source, details } = message;
    console.log(`Alert message received from ${source}: ${alert}`, details);
    this.notifySubscribers('alert', { alert, source, details });
  }

  handleBurstMessage(message) {
    const { burst, target, intensity } = message;
    console.log(`Burst message received for ${target}: ${burst}`, intensity);
    this.notifySubscribers('burst', { burst, target, intensity });
  }

  handleStatusMessage(message) {
    const { target, status } = message;
    console.log(`Status message received for ${target}: ${status}`);
    // Implement status message handling
  }

  handleUpdateMessage(message) {
    const { target, update, parameters } = message;
    console.log(`Update message received for ${target}: ${update}`, parameters);
    // Implement update message handling
  }

  handlePriorityMessage(message) {
    const { target, level, reason } = message;
    console.log(`Priority message received for ${target}: Level ${level}`, reason);
    // Implement priority message handling
  }

  handleMonitoringEvent(type, data) {
    if (!data) return;

    // Handle relevant monitoring events
    if (type === 'system.alert' && data.priority === 'high') {
      this.sendResponse({
        type: 'chase.comms.status',
        status: 'alert',
        details: data
      });
    }
  }

  async sendResponse(response) {
    try {
      const { comms } = RABBITMQ_CONFIG.exchanges.nova;
      await this.channel.publish(
        comms.name,
        'chase.response',
        Buffer.from(JSON.stringify({
          ...response,
          timestamp: Date.now()
        })),
        { persistent: true }
      );
    } catch (error) {
      console.error('Failed to send response:', error);
    }
  }

  getLastMessage() {
    return this.lastMessage;
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notifySubscribers(type, data) {
    this.subscribers.forEach(callback => callback(type, data));
  }

  async cleanup() {
    if (this.monitoringSubscription) {
      this.monitoringSubscription();
      this.monitoringSubscription = null;
    }

    if (this.channel) {
      await this.channel.close();
      this.channel = null;
    }

    if (this.connection) {
      await this.connection.close();
      this.connection = null;
    }

    this.subscribers.clear();
    this.lastMessage = null;
  }
}

// Create singleton instance
const chaseCommsService = new ChaseCommsService();
export default chaseCommsService;