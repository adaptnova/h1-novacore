import { getAuthHeaders } from '../utils/auth';

export const INFRASTRUCTURE_CONFIG = {
  // Core Services
  backend: {
    host: 'nova-backend',
    port: 8000,
    ssl: true,
    baseUrl: 'https://nova-backend:8000/api/v1'
  },

  // Health Check Endpoints
  healthChecks: {
    base: '/health',
    postgresql: '/health/postgresql',
    redis: '/health/redis',
    rabbitmq: '/health/rabbitmq'
  },

  // WebSocket Configuration
  websockets: {
    baseUrl: 'wss://nova-backend:8000/ws',
    channels: {
      fieldStatus: '/ws/field-status',
      patterns: '/ws/patterns',
      system: '/ws/system',
      alerts: '/ws/alerts',
      metrics: '/ws/metrics'
    },
    reconnectInterval: 1000,
    maxRetries: 3,
    reconnectStrategy: {
      initialDelay: 1000,
      maxDelay: 30000,
      backoff: 'exponential'
    }
  },

  // API Configuration
  api: {
    baseUrl: 'https://nova-backend:8000/api/v1',
    timeout: 5000,
    retries: 3,
    endpoints: {
      auth: '/api/auth/token',
      fieldStatus: '/nova-field',
      fieldMetrics: '/nova-field/{id}/metrics',
      fieldAlerts: '/nova-field/{id}/alerts',
      batchOperations: '/nova-field/batch'
    },
    rateLimits: {
      default: 1000,  // requests per minute
      websocket: 100  // connections per minute
    }
  },

  // Monitoring
  monitoring: {
    metrics: '/metrics',
    alertManager: '/alerts',
    logs: '/logs/nova-backend',
    thresholds: {
      apiResponseTime: 150,    // ms
      websocketLatency: 50,    // ms
      errorRate: 0.1,          // %
      capacity: 350            // field instances
    }
  },

  // Support Channels
  support: {
    primary: '#nova-backend-primary',
    db: '#dataops',
    monitoring: '#framework-launch',
    emergency: '#nova-911',
    rayFlow: '#ray-flow-emergence'
  },

  // Alert Thresholds
  thresholds: {
    responseTimes: {
      warning: 150,    // ms
      critical: 200    // ms
    },
    errorRates: {
      warning: 0.3,    // %
      critical: 0.5    // %
    },
    fieldMetrics: {
      strength: {
        warning: 0.85,
        critical: 0.75
      },
      stability: {
        warning: 0.90,
        critical: 0.80
      }
    }
  }
};

// Health check function
export const checkServiceHealth = async (service) => {
  try {
    const headers = await getAuthHeaders();
    const endpoint = service ?
      `${INFRASTRUCTURE_CONFIG.backend.baseUrl}${INFRASTRUCTURE_CONFIG.healthChecks[service]}` :
      `${INFRASTRUCTURE_CONFIG.backend.baseUrl}${INFRASTRUCTURE_CONFIG.healthChecks.base}`;

    const response = await fetch(endpoint, {
      headers: {
        ...headers,
        'Authorization': `Bearer ${process.env.REACT_APP_NOVA_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    const data = await response.json();
    return {
      healthy: data.status === 'healthy',
      version: data.version,
      timestamp: data.timestamp
    };
  } catch (error) {
    console.error(`Health check failed for ${service}:`, error);
    return {
      healthy: false,
      error: error.message
    };
  }
};

export default INFRASTRUCTURE_CONFIG;
