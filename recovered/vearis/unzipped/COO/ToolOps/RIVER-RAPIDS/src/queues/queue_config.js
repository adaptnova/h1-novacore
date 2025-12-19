/**
 * Queue Configuration for ToolOps RabbitMQ Implementation
 * Version: 1.0.7 - Enhanced Monitoring
 * RabbitMQ Version: 3.12.1
 */

const QUEUE_CONFIG = {
  // System configuration
  system: {
    version: '3.12.1',
    prometheus: {
      target: '10.10.0.19:15692',
      scrapeInterval: '15s'
    },
    monitoring: {
      queues: {
        depth: {
          warning: 10000,
          critical: 50000
        },
        messageRate: {
          warning: 1000,  // msg/s
          critical: 5000  // msg/s
        },
        consumerCount: {
          warning: 2,     // minimum
          critical: 0     // none
        },
        messageAge: {
          warning: 1800,  // 30 minutes in seconds
          critical: 7200  // 2 hours in seconds
        }
      },
      resources: {
        memory: {
          process: {
            warning: 0.70,  // 70% of limit
            critical: 0.85  // 85% of limit
          },
          node: {
            warning: 0.75,  // 75% usage
            critical: 0.90  // 90% usage
          }
        },
        disk: {
          freeSpace: {
            warning: 5,    // GB
            critical: 2    // GB
          },
          growthRate: {
            warning: 1,    // GB/hour
            critical: 2    // GB/hour
          }
        },
        cpu: {
          process: {
            warning: 70,   // %
            critical: 90   // %
          },
          system: {
            warning: 80,   // %
            critical: 95   // %
          }
        }
      },
      connections: {
        total: {
          warning: 0.80,   // 80% of limit
          critical: 0.90   // 90% of limit
        },
        rate: {
          warning: 100,    // per minute
          critical: 500    // per minute
        },
        channels: {
          warning: 8000,
          critical: 12000
        }
      }
    }
  },

  // Virtual host configurations
  vhosts: {
    ai_tasks: {
      maxConnections: 200,
      monitoring: {
        queueCount: {
          warning: 100,
          critical: 200
        },
        messageRate: {
          warning: 2000,   // per second
          critical: 5000   // per second
        }
      }
    },
    ai_results: {
      maxConnections: 200,
      monitoring: {
        queueCount: {
          warning: 100,
          critical: 200
        },
        messageRate: {
          warning: 2000,   // per second
          critical: 5000   // per second
        }
      }
    }
  },

  // Alert routing configuration
  alerts: {
    critical: {
      primary: '#rmq-911',
      secondary: 'on-call-phone',
      escalation: {
        timeout: 1800,    // 30 minutes
        target: 'team-leads'
      },
      sla: 900           // 15 minutes
    },
    warning: {
      primary: '#rabbitmq-team',
      secondary: 'email',
      escalation: {
        timeout: 7200,    // 2 hours
        target: '#rmq-911'
      }
    }
  },

  // Core exchanges
  exchanges: {
    command: {
      name: 'tools.command',
      type: 'direct',
      options: {
        durable: true,
        autoDelete: false
      }
    },
    event: {
      name: 'tools.event',
      type: 'fanout',
      options: {
        durable: true,
        autoDelete: false
      }
    },
    deadLetter: {
      name: 'dlx.tools',
      type: 'direct',
      options: {
        durable: true,
        autoDelete: false
      }
    }
  },

  // Dead letter queue configuration
  deadLetterQueue: {
    name: 'dlq.tools',
    options: {
      durable: true,
      autoDelete: false,
      messageTtl: 604800000 // 7 days
    }
  }
};

// Export configurations
module.exports = {
  QUEUE_CONFIG,
  
  // Helper function to get virtual host configuration
  getVhostConfig: (vhost) => {
    const config = QUEUE_CONFIG.vhosts[vhost];
    if (!config) {
      throw new Error('Invalid virtual host');
    }
    return config;
  },

  // Helper function to get monitoring thresholds
  getMonitoringThresholds: (type, metric) => {
    const path = type.split('.');
    let config = QUEUE_CONFIG.system.monitoring;
    for (const key of path) {
      config = config[key];
      if (!config) {
        throw new Error(`Invalid monitoring path: ${type}`);
      }
    }
    return config[metric] || null;
  },

  // Helper function to get alert configuration
  getAlertConfig: (severity) => {
    const config = QUEUE_CONFIG.alerts[severity];
    if (!config) {
      throw new Error('Invalid alert severity');
    }
    return config;
  },

  // Helper function to get exchange configuration
  getExchangeConfig: (type) => {
    const exchange = QUEUE_CONFIG.exchanges[type];
    if (!exchange) {
      throw new Error('Invalid exchange type');
    }
    return exchange;
  }
};