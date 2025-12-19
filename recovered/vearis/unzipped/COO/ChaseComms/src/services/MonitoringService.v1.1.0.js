import { INFRASTRUCTURE_CONFIG } from '../config/infrastructure';
import { circuitBreakerRegistry } from '../utils/circuitBreaker';

class MonitoringService {
  constructor() {
    this.metrics = {
      api: new Map(),
      websocket: new Map(),
      circuitBreakers: new Map(),
      patterns: new Map(),
      memory: new Map(),
      performance: new Map(),
      services: new Map()
    };

    this.intervals = new Map();
    this.subscribers = new Set();
    this.ws = null;
  }

  async initialize() {
    // Start collecting metrics
    this.startMetricsCollection();

    // Connect to metrics WebSocket
    try {
      this.ws = await this.createWebSocketConnection();
    } catch (error) {
      console.error('Failed to connect to metrics WebSocket:', error);
    }

    // Initialize circuit breaker monitoring
    this.monitorCircuitBreakers();
  }

  startMetricsCollection() {
    // Collect service metrics
    this.intervals.set('services', setInterval(async () => {
      try {
        const metrics = await this.collectServiceMetrics();
        this.metrics.services.set(Date.now(), metrics);
        this.pruneMetrics('services');
        this.notifySubscribers('services', metrics);
      } catch (error) {
        console.error('Failed to collect service metrics:', error);
      }
    }, 5000));

    // Collect performance metrics
    this.intervals.set('performance', setInterval(async () => {
      try {
        const metrics = await this.collectPerformanceMetrics();
        this.metrics.performance.set(Date.now(), metrics);
        this.pruneMetrics('performance');
        this.notifySubscribers('performance', metrics);
      } catch (error) {
        console.error('Failed to collect performance metrics:', error);
      }
    }, 10000));

    // Collect pattern metrics
    this.intervals.set('patterns', setInterval(async () => {
      try {
        const metrics = await this.collectPatternMetrics();
        this.metrics.patterns.set(Date.now(), metrics);
        this.pruneMetrics('patterns');
        this.notifySubscribers('patterns', metrics);
      } catch (error) {
        console.error('Failed to collect pattern metrics:', error);
      }
    }, 5000));
  }

  async collectServiceMetrics() {
    const breaker = circuitBreakerRegistry.get('services');
    return breaker.execute(async () => {
      const metrics = {};

      // PostgreSQL
      try {
        const pgResponse = await fetch(`${INFRASTRUCTURE_CONFIG.backend.baseUrl}/health/postgresql`);
        metrics.postgresql = {
          healthy: pgResponse.ok,
          responseTime: pgResponse.headers.get('x-response-time'),
          connections: await pgResponse.json().then(data => data.connections)
        };
      } catch (error) {
        metrics.postgresql = { healthy: false };
      }

      // Redis
      try {
        const redisResponse = await fetch(`${INFRASTRUCTURE_CONFIG.backend.baseUrl}/health/redis`);
        metrics.redis = {
          healthy: redisResponse.ok,
          memory: await redisResponse.json().then(data => data.memory),
          keys: await redisResponse.json().then(data => data.keys)
        };
      } catch (error) {
        metrics.redis = { healthy: false };
      }

      // RabbitMQ
      try {
        const rmqResponse = await fetch(`${INFRASTRUCTURE_CONFIG.backend.baseUrl}/health/rabbitmq`);
        metrics.rabbitmq = {
          healthy: rmqResponse.ok,
          messages: await rmqResponse.json().then(data => data.messages),
          channels: await rmqResponse.json().then(data => data.channels)
        };
      } catch (error) {
        metrics.rabbitmq = { healthy: false };
      }

      return metrics;
    });
  }

  async collectPerformanceMetrics() {
    const breaker = circuitBreakerRegistry.get('performance');
    return breaker.execute(async () => {
      try {
        const response = await fetch(`${INFRASTRUCTURE_CONFIG.backend.baseUrl}/metrics`);
        return await response.json();
      } catch (error) {
        console.error('Failed to collect performance metrics:', error);
        return {
          healthy: false,
          error: error.message
        };
      }
    });
  }

  async collectPatternMetrics() {
    const breaker = circuitBreakerRegistry.get('patterns');
    return breaker.execute(async () => {
      try {
        const response = await fetch(`${INFRASTRUCTURE_CONFIG.api.baseUrl}/nova-field/status`);
        return await response.json();
      } catch (error) {
        console.error('Failed to collect pattern metrics:', error);
        return {
          healthy: false,
          error: error.message
        };
      }
    });
  }

  async createWebSocketConnection() {
    const ws = new WebSocket(`${INFRASTRUCTURE_CONFIG.websockets.baseUrl}/ws/system`);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleWebSocketMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed, attempting to reconnect...');
      setTimeout(() => this.createWebSocketConnection(), INFRASTRUCTURE_CONFIG.websockets.reconnectInterval);
    };

    return ws;
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case 'system_event':
        this.metrics.websocket.set(Date.now(), data);
        this.notifySubscribers('websocket', data);
        break;
      default:
        console.warn('Unknown WebSocket message type:', data.type);
    }
  }

  getSystemHealth() {
    const services = this.getLatestMetric('services') || {};
    const performance = this.getLatestMetric('performance');
    const patterns = this.getLatestMetric('patterns');

    return {
      timestamp: Date.now(),
      healthy: services.postgresql?.healthy && services.redis?.healthy && services.rabbitmq?.healthy,
      components: {
        ...services,
        performance,
        patterns
      }
    };
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notifySubscribers(type, data) {
    this.subscribers.forEach(callback => callback(type, data));
  }

  pruneMetrics(type, maxAge = 3600000) { // 1 hour
    const now = Date.now();
    for (const [timestamp] of this.metrics[type]) {
      if (now - timestamp > maxAge) {
        this.metrics[type].delete(timestamp);
      }
    }
  }

  cleanup() {
    // Clear all intervals
    for (const [name, interval] of this.intervals) {
      clearInterval(interval);
    }
    this.intervals.clear();

    // Close WebSocket connection
    if (this.ws) {
      this.ws.close();
    }

    // Clear metrics and subscribers
    for (const type in this.metrics) {
      this.metrics[type].clear();
    }
    this.subscribers.clear();
  }
}

// Create singleton instance
const monitoringService = new MonitoringService();
export default monitoringService;
