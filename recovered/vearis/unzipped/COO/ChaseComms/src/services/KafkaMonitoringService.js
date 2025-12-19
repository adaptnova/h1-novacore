/**
 * Kafka Monitoring Service for NovaComms GUI
 * Version: 1.0.0
 * Last Updated: 2024-12-15
 */

import monitoringService from './MonitoringService';

class KafkaMonitoringService {
  constructor() {
    this.metrics = {
      brokers: new Map(),
      topics: new Map(),
      consumers: new Map(),
      producers: new Map()
    };

    this.subscribers = new Set();
    this.monitoringSubscription = null;
  }

  async initialize() {
    // Subscribe to monitoring service for Kafka metrics
    this.monitoringSubscription = monitoringService.subscribe(
      this.handleMonitoringEvent.bind(this)
    );
  }

  handleMonitoringEvent(type, data) {
    if (!data) return;

    if (type.startsWith('kafka.')) {
      const [_, component, metric] = type.split('.');

      switch (component) {
        case 'broker':
          this.updateBrokerMetrics(data);
          break;
        case 'topic':
          this.updateTopicMetrics(data);
          break;
        case 'consumer':
          this.updateConsumerMetrics(data);
          break;
        case 'producer':
          this.updateProducerMetrics(data);
          break;
      }

      this.notifySubscribers(type, data);
    }
  }

  updateBrokerMetrics(data) {
    const { brokerId, metrics } = data;
    this.metrics.brokers.set(brokerId, {
      ...metrics,
      timestamp: Date.now()
    });
  }

  updateTopicMetrics(data) {
    const { topic, metrics } = data;
    this.metrics.topics.set(topic, {
      ...metrics,
      timestamp: Date.now()
    });
  }

  updateConsumerMetrics(data) {
    const { groupId, metrics } = data;
    this.metrics.consumers.set(groupId, {
      ...metrics,
      timestamp: Date.now()
    });
  }

  updateProducerMetrics(data) {
    const { clientId, metrics } = data;
    this.metrics.producers.set(clientId, {
      ...metrics,
      timestamp: Date.now()
    });
  }

  getSystemHealth() {
    const brokerHealth = Array.from(this.metrics.brokers.values())
      .every(broker => broker.status === 'healthy');

    const consumerLag = Array.from(this.metrics.consumers.values())
      .reduce((maxLag, consumer) => Math.max(maxLag, consumer.lag || 0), 0);

    return {
      healthy: brokerHealth && consumerLag < 1000,
      components: {
        brokers: {
          healthy: brokerHealth,
          count: this.metrics.brokers.size
        },
        topics: {
          count: this.metrics.topics.size,
          totalPartitions: Array.from(this.metrics.topics.values())
            .reduce((sum, topic) => sum + (topic.partitions || 0), 0)
        },
        consumers: {
          count: this.metrics.consumers.size,
          maxLag: consumerLag
        },
        producers: {
          count: this.metrics.producers.size,
          activeConnections: Array.from(this.metrics.producers.values())
            .filter(producer => producer.connected).length
        }
      },
      timestamp: Date.now()
    };
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notifySubscribers(type, data) {
    this.subscribers.forEach(callback => callback(type, data));
  }

  cleanup() {
    if (this.monitoringSubscription) {
      this.monitoringSubscription();
      this.monitoringSubscription = null;
    }

    this.subscribers.clear();
    this.metrics.brokers.clear();
    this.metrics.topics.clear();
    this.metrics.consumers.clear();
    this.metrics.producers.clear();
  }
}

// Create singleton instance
const kafkaMonitoringService = new KafkaMonitoringService();
export default kafkaMonitoringService;