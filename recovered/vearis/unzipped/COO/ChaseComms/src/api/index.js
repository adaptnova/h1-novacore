import { API_CONFIG, WS_CONFIG } from '../config/connections';

// API client with interceptors for auth and error handling
class APIClient {
  constructor() {
    this.baseURL = API_CONFIG.baseUrl;
    this.timeout = API_CONFIG.timeout;
    this.retries = API_CONFIG.retries;
    this.connectionStatus = {
      api: false,
      ws: false,
      rabbitmq: false
    };
  }

  // Connection status monitoring
  async checkConnections() {
    try {
      // Check API health
      const apiHealth = await this.get('/health');
      this.connectionStatus.api = apiHealth.status === 'healthy';

      // Check WebSocket
      const ws = new WebSocket(`${WS_CONFIG.url}/health`);
      ws.onopen = () => {
        this.connectionStatus.ws = true;
        ws.close();
      };

      // Check RabbitMQ
      const rmqHealth = await this.get('/rabbitmq/health');
      this.connectionStatus.rabbitmq = rmqHealth.status === 'healthy';

      return this.connectionStatus;
    } catch (error) {
      console.error('Connection check failed:', error);
      return this.connectionStatus;
    }
  }

  // HTTP methods with retry logic
  async request(method, endpoint, data = null, headers = {}) {
    let attempts = 0;
    while (attempts < this.retries) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          method,
          headers: {
            'Content-Type': 'application/json',
            ...headers
          },
          body: data ? JSON.stringify(data) : undefined,
          timeout: this.timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        attempts++;
        if (attempts === this.retries) {
          throw error;
        }
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempts) * 1000));
      }
    }
  }

  async get(endpoint, headers = {}) {
    return this.request('GET', endpoint, null, headers);
  }

  async post(endpoint, data, headers = {}) {
    return this.request('POST', endpoint, data, headers);
  }

  async put(endpoint, data, headers = {}) {
    return this.request('PUT', endpoint, data, headers);
  }

  async delete(endpoint, headers = {}) {
    return this.request('DELETE', endpoint, null, headers);
  }

  // WebSocket connection with auto-reconnect
  createWebSocket(channel, onMessage) {
    const ws = new WebSocket(`${WS_CONFIG.url}${WS_CONFIG.channels[channel]}`);
    
    ws.onmessage = (event) => {
      onMessage(JSON.parse(event.data));
    };

    ws.onclose = () => {
      this.connectionStatus.ws = false;
      setTimeout(() => this.createWebSocket(channel, onMessage), WS_CONFIG.reconnectInterval);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error in ${channel}:`, error);
    };

    return ws;
  }

  // Expected API endpoints (to be configured with actual backend)
  endpoints = {
    // System health
    health: {
      check: () => this.get('/health'),
      metrics: () => this.get('/metrics')
    },

    // Nova Field
    novaField: {
      status: () => this.get('/nova-field/status'),
      metrics: () => this.get('/nova-field/metrics'),
      patterns: () => this.get('/nova-field/patterns')
    },

    // Tasks
    tasks: {
      list: () => this.get('/tasks'),
      create: (task) => this.post('/tasks', task),
      update: (id, task) => this.put(`/tasks/${id}`, task),
      delete: (id) => this.delete(`/tasks/${id}`)
    },

    // Chat
    messages: {
      list: () => this.get('/messages'),
      send: (message) => this.post('/messages', message),
      delete: (id) => this.delete(`/messages/${id}`)
    },

    // Model outputs
    model: {
      analyze: (data) => this.post('/model/analyze', data),
      status: () => this.get('/model/status')
    },

    // RabbitMQ
    rabbitmq: {
      status: () => this.get('/rabbitmq/status'),
      publish: (exchange, message) => this.post('/rabbitmq/publish', { exchange, message })
    }
  };
}

// Create singleton instance
const apiClient = new APIClient();
export default apiClient;
