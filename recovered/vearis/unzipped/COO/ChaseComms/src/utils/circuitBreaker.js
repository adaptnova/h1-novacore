// Circuit breaker implementation for API resilience
export class CircuitBreaker {
  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000; // 60 seconds
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'closed';
    this.onStateChange = options.onStateChange || (() => {});
    this.fallback = options.fallback || (() => null);
    this.name = options.name || 'default';
  }

  async execute(request) {
    if (this.state === 'open') {
      if (this.shouldReset()) {
        this.toHalfOpen();
      } else {
        console.warn(`Circuit breaker ${this.name} is open, using fallback`);
        return this.fallback();
      }
    }

    try {
      const result = await request();
      this.onSuccess();
      return result;
    } catch (error) {
      return this.onFailure(error);
    }
  }

  shouldReset() {
    if (!this.lastFailureTime) return false;
    const now = Date.now();
    return (now - this.lastFailureTime) > this.resetTimeout;
  }

  toHalfOpen() {
    this.state = 'half-open';
    this.failureCount = 0;
    this.onStateChange(this.state);
    console.info(`Circuit breaker ${this.name} entering half-open state`);
  }

  onSuccess() {
    if (this.state === 'half-open') {
      this.state = 'closed';
      this.onStateChange(this.state);
      console.info(`Circuit breaker ${this.name} closed`);
    }
    this.failureCount = 0;
    this.lastFailureTime = null;
  }

  onFailure(error) {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.failureThreshold) {
      this.state = 'open';
      this.onStateChange(this.state);
      console.error(`Circuit breaker ${this.name} opened due to failures:`, error);
    }

    throw error;
  }
}

// Circuit breaker registry to manage multiple breakers
export class CircuitBreakerRegistry {
  constructor() {
    this.breakers = new Map();
  }

  get(name, options = {}) {
    if (!this.breakers.has(name)) {
      this.breakers.set(name, new CircuitBreaker({ ...options, name }));
    }
    return this.breakers.get(name);
  }

  getStatus() {
    const status = {};
    for (const [name, breaker] of this.breakers.entries()) {
      status[name] = {
        state: breaker.state,
        failures: breaker.failureCount,
        lastFailure: breaker.lastFailureTime
      };
    }
    return status;
  }

  reset(name) {
    if (this.breakers.has(name)) {
      const breaker = this.breakers.get(name);
      breaker.state = 'closed';
      breaker.failureCount = 0;
      breaker.lastFailureTime = null;
      breaker.onStateChange('closed');
    }
  }

  resetAll() {
    for (const name of this.breakers.keys()) {
      this.reset(name);
    }
  }
}

// Create singleton instance
export const circuitBreakerRegistry = new CircuitBreakerRegistry();

// Example usage:
/*
const apiBreaker = circuitBreakerRegistry.get('api', {
  failureThreshold: 3,
  resetTimeout: 30000,
  fallback: () => ({ error: 'Service temporarily unavailable' }),
  onStateChange: (state) => {
    if (state === 'open') {
      // Notify monitoring system
      console.error('API circuit breaker opened');
    }
  }
});

// Use with async functions
try {
  const result = await apiBreaker.execute(async () => {
    const response = await fetch('/api/data');
    if (!response.ok) throw new Error('API error');
    return response.json();
  });
} catch (error) {
  // Handle error
}
*/

// Predefined circuit breakers for common services
export const serviceBreakers = {
  api: circuitBreakerRegistry.get('api', {
    failureThreshold: 5,
    resetTimeout: 30000,
    fallback: () => ({ error: 'API service unavailable' })
  }),

  websocket: circuitBreakerRegistry.get('websocket', {
    failureThreshold: 3,
    resetTimeout: 15000,
    fallback: () => ({ error: 'WebSocket connection unavailable' })
  }),

  rabbitmq: circuitBreakerRegistry.get('rabbitmq', {
    failureThreshold: 4,
    resetTimeout: 20000,
    fallback: () => ({ error: 'Message queue unavailable' })
  }),

  redis: circuitBreakerRegistry.get('redis', {
    failureThreshold: 3,
    resetTimeout: 10000,
    fallback: () => ({ error: 'Cache service unavailable' })
  })
};

// Export monitoring function for system health
export const getCircuitBreakersHealth = () => {
  const status = circuitBreakerRegistry.getStatus();
  const healthy = Object.values(status).every(s => s.state === 'closed');
  
  return {
    healthy,
    status,
    timestamp: new Date().toISOString()
  };
};
