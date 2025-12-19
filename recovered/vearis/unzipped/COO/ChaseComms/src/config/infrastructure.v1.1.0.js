import { getAuthHeaders } from '../utils/auth';

export const INFRASTRUCTURE_CONFIG = {
  // Core Services
  backend: {
    host: 'nova-backend',
    port: 8000,
    ssl: true,
    baseUrl: 'https://nova-backend:8000'
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
    baseUrl: 'ws://nova-backend:8000',
    channels: {
      fieldStatus: '/ws/field-status',
      patterns: '/ws/patterns',
      system: '/ws/system'
    },
    reconnectInterval: 1000,
    maxRetries: 5
  },

  // API Configuration
  api: {
    baseUrl: 'https://nova-backend:8000/api',
    timeout: 5000,
    retries: 3,
    endpoints: {
      auth: '/auth/token',
      fieldStatus: '/nova-field/status'
    }
  },

  // Monitoring
  monitoring: {
    metrics: 'https://nova-backend:8000/metrics',
    alertManager: 'https://nova-backend:9093/api/v1/alerts'
  },

  // Support Channels
  support: {
    primary: '#nova-backend-primary',
    db: '#nova-backend-db',
    monitoring: '#nova-backend-monitoring',
    emergency: '#nova-911'
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
      headers,
      credentials: 'include'
    });
    return response.ok;
  } catch (error) {
    console.error(`Health check failed for ${service}:`, error);
    return false;
  }
};

export default INFRASTRUCTURE_CONFIG;
