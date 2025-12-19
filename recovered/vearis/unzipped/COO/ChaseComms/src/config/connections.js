// Connection configuration for NOVA COMMS GUI
import { COLORS } from '../styles/GlobalStyles';

export const WS_CONFIG = {
  url: process.env.REACT_APP_WS_URL || 'ws://localhost:3001',
  reconnectInterval: 1000,
  maxRetries: 5,
  channels: {
    novaField: '/nova-field',
    patterns: '/patterns',
    metrics: '/metrics',
    chat: '/chat'
  }
};

export const RABBITMQ_CONFIG = {
  host: process.env.REACT_APP_RABBITMQ_HOST || 'localhost',
  port: process.env.REACT_APP_RABBITMQ_PORT || 5672,
  vhost: process.env.REACT_APP_RABBITMQ_VHOST || 'nova',
  exchanges: {
    events: 'nova.events',
    commands: 'nova.commands',
    status: 'nova.status'
  },
  queues: {
    gui: 'nova.events.gui',
    commands: 'nova.commands.gui'
  }
};

export const ATLASSIAN_CONFIG = {
  baseUrl: process.env.REACT_APP_ATLASSIAN_URL || 'https://nova-adapt.atlassian.net',
  apiVersion: 3,
  endpoints: {
    jira: '/rest/api/3',
    confluence: '/wiki/rest/api'
  }
};

export const SYSTEM_HEALTH_CONFIG = {
  updateInterval: 1000,
  thresholds: {
    cpu: {
      warning: 75,
      critical: 90,
      color: {
        normal: COLORS.success,
        warning: COLORS.warning,
        critical: COLORS.error
      }
    },
    memory: {
      warning: 75,
      critical: 90,
      color: {
        normal: COLORS.success,
        warning: COLORS.warning,
        critical: COLORS.error
      }
    },
    novaField: {
      warning: 0.85,
      critical: 0.80,
      color: {
        normal: COLORS.success,
        warning: COLORS.warning,
        critical: COLORS.error
      }
    }
  }
};

export const API_CONFIG = {
  baseUrl: process.env.REACT_APP_API_BASE || 'http://localhost:3001/api',
  timeout: 5000,
  retries: 3,
  endpoints: {
    health: '/health',
    metrics: '/metrics',
    tasks: '/tasks',
    messages: '/messages',
    patterns: '/patterns'
  }
};

export const AUTH_CONFIG = {
  tokenRefreshInterval: parseInt(process.env.REACT_APP_TOKEN_REFRESH_INTERVAL) || 840000, // 14 minutes
  endpoints: {
    login: '/auth/login',
    refresh: '/auth/refresh',
    logout: '/auth/logout'
  }
};

// WebSocket connection handler
export const createWebSocket = (channel) => {
  const ws = new WebSocket(`${WS_CONFIG.url}${WS_CONFIG.channels[channel]}`);
  
  ws.onopen = () => {
    console.log(`Connected to ${channel} channel`);
  };

  ws.onclose = () => {
    console.log(`Disconnected from ${channel} channel`);
    // Implement reconnection logic
    setTimeout(() => createWebSocket(channel), WS_CONFIG.reconnectInterval);
  };

  ws.onerror = (error) => {
    console.error(`WebSocket error in ${channel} channel:`, error);
  };

  return ws;
};

// RabbitMQ connection status checker
export const checkRabbitMQConnection = async () => {
  try {
    const response = await fetch(`http://${RABBITMQ_CONFIG.host}:15672/api/aliveness-test/%2f`, {
      headers: {
        'Authorization': `Basic ${btoa(`${process.env.RABBITMQ_USER}:${process.env.RABBITMQ_PASS}`)}`
      }
    });
    return response.ok;
  } catch (error) {
    console.error('RabbitMQ connection check failed:', error);
    return false;
  }
};

// Atlassian connection checker
export const checkAtlassianConnection = async () => {
  try {
    const response = await fetch(`${ATLASSIAN_CONFIG.baseUrl}/status`);
    return response.ok;
  } catch (error) {
    console.error('Atlassian connection check failed:', error);
    return false;
  }
};

// System health checker
export const checkSystemHealth = async () => {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/health`);
    return response.ok;
  } catch (error) {
    console.error('System health check failed:', error);
    return false;
  }
};
