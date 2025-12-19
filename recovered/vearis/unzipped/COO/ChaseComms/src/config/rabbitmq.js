// RabbitMQ Configuration for NovaComms GUI
export const RABBITMQ_CONFIG = {
  // Core Connection
  connection: {
    host: 'localhost',
    port: 5672,
    vhost: '/nova',
    ssl: true,
    heartbeat: 60,
    connectionTimeout: 10000,
    username: process.env.REACT_APP_RABBITMQ_USER,
    password: process.env.REACT_APP_RABBITMQ_PASS
  },

  // Exchanges
  exchanges: {
    // Nova System Exchanges
    nova: {
      events: {
        name: 'nova.events',
        type: 'topic',
        durable: true,
        autoDelete: false
      },
      metrics: {
        name: 'nova.metrics',
        type: 'topic',
        durable: true,
        autoDelete: false
      },
      logs: {
        name: 'nova.logs',
        type: 'topic',
        durable: true,
        autoDelete: false
      },
      comms: {
        name: 'nova.comms',
        type: 'direct',
        durable: true,
        autoDelete: false
      }
    },
    // Meta Router Exchanges
    metaRouter: {
      patterns: {
        name: 'meta-router.patterns',
        type: 'topic',
        durable: true,
        autoDelete: false
      },
      health: {
        name: 'meta-router.health',
        type: 'topic',
        durable: true,
        autoDelete: false
      },
      decisions: {
        name: 'meta-router.decisions',
        type: 'topic',
        durable: true,
        autoDelete: false
      },
      deadLetters: {
        name: 'meta-router.dead.letters',
        type: 'topic',
        durable: true,
        autoDelete: false
      }
    },
    // RASA Integration Exchange
    rasa: {
      name: 'rasa_exchange',
      type: 'fanout',
      durable: true,
      autoDelete: false
    }
  },

  // Queues
  queues: {
    monitoring: {
      name: 'nova.monitoring',
      durable: true,
      autoDelete: false,
      arguments: {
        'x-dead-letter-exchange': 'meta-router.dead.letters',
        'x-dead-letter-routing-key': 'dead.letter'
      },
      bindings: [{
        exchange: 'nova.metrics',
        routingKey: 'monitoring.#'
      }]
    },
    launch: {
      name: 'launch.monitoring',
      durable: true,
      autoDelete: false,
      arguments: {
        'x-dead-letter-exchange': 'meta-router.dead.letters',
        'x-dead-letter-routing-key': 'dead.letter'
      },
      bindings: [{
        exchange: 'meta-router.health',
        routingKey: 'launch.#'
      }]
    },
    rasa: {
      name: 'rasa_events',
      durable: true,
      autoDelete: false,
      arguments: {
        'x-dead-letter-exchange': 'meta-router.dead.letters',
        'x-dead-letter-routing-key': 'dead.letter'
      },
      bindings: [{
        exchange: 'rasa_exchange',
        routingKey: '#'
      }]
    },
    // Chase Comms Queue
    chaseComms: {
      name: 'nova.comms.chase',
      durable: true,
      autoDelete: false,
      arguments: {
        'x-dead-letter-exchange': 'meta-router.dead.letters',
        'x-dead-letter-routing-key': 'dead.letter',
        'x-max-priority': 10  // Highest priority for Chase messages
      },
      bindings: [{
        exchange: 'nova.comms',
        routingKey: 'chase.comms'
      }]
    },
    // Kafka Monitoring Queue
    kafkaMonitoring: {
      name: 'nova.monitoring.kafka',
      durable: true,
      autoDelete: false,
      arguments: {
        'x-dead-letter-exchange': 'meta-router.dead.letters',
        'x-dead-letter-routing-key': 'dead.letter'
      },
      bindings: [{
        exchange: 'nova.metrics',
        routingKey: 'monitoring.kafka.#'
      }]
    }
  },

  // Performance Settings
  performance: {
    prefetchCount: 100,
    messageRate: 'unlimited',
    memoryHighWatermark: 0.8,
    channelMax: 2000,
    frameMax: 131072
  },

  // Event Types
  eventTypes: {
    system: [
      'system.status',
      'system.alert',
      'system.metric'
    ],
    field: [
      'field.status.changed',
      'field.metrics.updated',
      'field.alert.created',
      'field.alert.resolved'
    ],
    rasa: [
      'user_message',
      'bot_message',
      'action_execution',
      'slot_setting',
      'form_execution',
      'conversation_pause',
      'conversation_resume'
    ],
    kafka: [
      'kafka.broker.status',
      'kafka.topic.metrics',
      'kafka.consumer.lag',
      'kafka.producer.metrics'
    ],
    comms: [
      'chase.comms.status',
      'chase.comms.update',
      'chase.comms.priority'
    ]
  },

  // Error Handling
  errorHandling: {
    retryAttempts: 3,
    backoffFactor: 1.5,
    maxRetryTime: 300,
    deadLetterExchange: 'meta-router.dead.letters',
    deadLetterRoutingKey: 'dead.letter'
  }
};

export default RABBITMQ_CONFIG;