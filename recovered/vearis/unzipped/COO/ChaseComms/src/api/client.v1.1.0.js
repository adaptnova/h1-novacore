import { INFRASTRUCTURE_CONFIG } from '../config/infrastructure';
import { getAuthHeaders } from '../utils/auth';
import { serviceBreakers } from '../utils/circuitBreaker';

class APIError extends Error {
  constructor(message, status, code) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
  }
}

export class APIClient {
  constructor() {
    this.baseURL = `https://${INFRASTRUCTURE_CONFIG.serviceMesh.kong.host}:${INFRASTRUCTURE_CONFIG.serviceMesh.kong.proxy}`;
    this.timeout = INFRASTRUCTURE_CONFIG.api.timeout;
  }

  async request(method, endpoint, data = null) {
    const config = {
      method,
      headers: await getAuthHeaders(),
      timeout: this.timeout
    };

    if (data) {
      config.body = JSON.stringify(data);
      config.headers['Content-Type'] = 'application/json';
    }

    return serviceBreakers.api.execute(async () => {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      
      if (!response.ok) {
        throw new APIError(
          response.statusText,
          response.status,
          await response.text()
        );
      }

      return response.json();
    });
  }

  // REST methods
  async get(endpoint) {
    return this.request('GET', endpoint);
  }

  async post(endpoint, data) {
    return this.request('POST', endpoint, data);
  }

  async put(endpoint, data) {
    return this.request('PUT', endpoint, data);
  }

  async delete(endpoint) {
    return this.request('DELETE', endpoint);
  }

  // WebSocket connection with circuit breaker
  createWebSocket(channel, onMessage) {
    const wsURL = `wss://${INFRASTRUCTURE_CONFIG.serviceMesh.kong.host}:${INFRASTRUCTURE_CONFIG.serviceMesh.kong.proxy}${channel}`;
    
    return serviceBreakers.websocket.execute(async () => {
      const headers = await getAuthHeaders();
      const ws = new WebSocket(wsURL, {
        headers
      });

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };

      ws.onerror = (error) => {
        console.error(`WebSocket error in ${channel}:`, error);
        throw error; // Trigger circuit breaker
      };

      return ws;
    });
  }

  // Nova Field specific methods
  async getFieldStrength() {
    return this.get('/nova-field/strength');
  }

  async getFieldPatterns() {
    return this.get('/nova-field/patterns');
  }

  async analyzePattern(data) {
    return this.post('/nova-field/analyze', data);
  }

  // Task management
  async getTasks(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.get(`/tasks?${params}`);
  }

  async createTask(task) {
    return this.post('/tasks', task);
  }

  async updateTask(id, updates) {
    return this.put(`/tasks/${id}`, updates);
  }

  async deleteTask(id) {
    return this.delete(`/tasks/${id}`);
  }

  // Chat functionality
  async getMessages(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.get(`/messages?${params}`);
  }

  async sendMessage(message) {
    return this.post('/messages', message);
  }

  // System health
  async getHealth() {
    return this.get('/health');
  }

  async getMetrics() {
    return this.get('/metrics');
  }

  // RabbitMQ integration
  async publishEvent(exchange, routingKey, message) {
    return serviceBreakers.rabbitmq.execute(async () => {
      return this.post('/rabbitmq/publish', {
        exchange,
        routingKey,
        message
      });
    });
  }

  // Cache operations
  async getCached(key) {
    return serviceBreakers.redis.execute(async () => {
      return this.get(`/cache/${key}`);
    });
  }

  async setCached(key, value, ttl = 3600) {
    return serviceBreakers.redis.execute(async () => {
      return this.post('/cache', { key, value, ttl });
    });
  }

  // Error handling utilities
  isNetworkError(error) {
    return !error.status && error.message.includes('network');
  }

  isTimeoutError(error) {
    return !error.status && error.message.includes('timeout');
  }

  isServerError(error) {
    return error.status >= 500;
  }

  isClientError(error) {
    return error.status >= 400 && error.status < 500;
  }

  isAuthError(error) {
    return error.status === 401 || error.status === 403;
  }
}

// Create singleton instance
const apiClient = new APIClient();
export default apiClient;
