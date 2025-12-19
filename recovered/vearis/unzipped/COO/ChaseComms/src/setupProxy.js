const WebSocket = require('ws');

let wss;

module.exports = function(app) {
  // Create WebSocket server if not exists
  if (!wss) {
    wss = new WebSocket.Server({ noServer: true });

    // Handle WebSocket connections
    wss.on('connection', (ws, req) => {
      console.log('WebSocket connected:', req.url);

      // Send mock system events periodically
      const interval = setInterval(() => {
        const mockEvent = {
          type: 'system_event',
          timestamp: Date.now(),
          data: {
            postgresql: {
              healthy: true,
              responseTime: `${40 + Math.floor(Math.random() * 10)}ms`,
              connections: 10 + Math.floor(Math.random() * 5)
            },
            redis: {
              healthy: true,
              memory: `${20 + Math.floor(Math.random() * 10)}%`,
              keys: 1000 + Math.floor(Math.random() * 100)
            },
            rabbitmq: {
              healthy: true,
              messages: 95 + Math.floor(Math.random() * 10),
              channels: 5
            }
          }
        };

        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(mockEvent));
        }
      }, 5000);

      ws.on('close', () => {
        clearInterval(interval);
      });
    });
  }

  // Mock middleware for development
  app.use((req, res, next) => {
    // Add CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.setHeader('x-response-time', '45ms');

    // Handle OPTIONS requests
    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // Mock responses based on Backend Team's format
    if (req.url.startsWith('/health')) {
      res.setHeader('Content-Type', 'application/json');
      let mockData = {};

      if (req.url.includes('postgresql')) {
        mockData = {
          healthy: true,
          responseTime: '45ms',
          connections: 10,
          timestamp: Date.now()
        };
      } else if (req.url.includes('redis')) {
        mockData = {
          healthy: true,
          memory: '25%',
          keys: 1000,
          timestamp: Date.now()
        };
      } else if (req.url.includes('rabbitmq')) {
        mockData = {
          healthy: true,
          messages: 100,
          channels: 5,
          timestamp: Date.now()
        };
      } else {
        // Base health check
        mockData = {
          healthy: true,
          services: {
            postgresql: { healthy: true },
            redis: { healthy: true },
            rabbitmq: { healthy: true }
          },
          timestamp: Date.now()
        };
      }

      res.end(JSON.stringify(mockData));
      return;
    }

    // Mock metrics response
    if (req.url === '/metrics') {
      res.setHeader('Content-Type', 'application/json');
      const mockMetrics = {
        timestamp: Date.now(),
        responseTimes: {
          avg: 87,
          p95: 150,
          p99: 200
        },
        errorRates: {
          total: 0.01,
          byService: {
            postgresql: 0.0,
            redis: 0.0,
            rabbitmq: 0.0
          }
        },
        resourceUsage: {
          cpu: 23,
          memory: 45,
          network: 30
        }
      };
      res.end(JSON.stringify(mockMetrics));
      return;
    }

    // Mock alerts response
    if (req.url.startsWith('/alerts')) {
      res.setHeader('Content-Type', 'application/json');
      const mockAlerts = {
        alerts: [],
        timestamp: Date.now()
      };
      res.end(JSON.stringify(mockAlerts));
      return;
    }

    // Mock API response
    if (req.url.startsWith('/api')) {
      res.setHeader('Content-Type', 'application/json');
      const mockApiResponse = {
        status: 'success',
        data: {
          version: 'v2.1.0',
          timestamp: Date.now()
        }
      };
      res.end(JSON.stringify(mockApiResponse));
      return;
    }

    // Pass through for other requests
    next();
  });

  // Return upgrade handler for WebSocket
  return {
    upgrade: (req, socket, head) => {
      if (req.url.startsWith('/ws')) {
        wss.handleUpgrade(req, socket, head, (ws) => {
          wss.emit('connection', ws, req);
        });
      }
    }
  };
};
