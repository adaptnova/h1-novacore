const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy all backend requests
  const backendProxy = createProxyMiddleware({
    target: 'https://nova-backend:8000',
    changeOrigin: true,
    ws: true,
    secure: false,
    onProxyRes: function(proxyRes, req, res) {
      proxyRes.headers['Access-Control-Allow-Origin'] = '*';
      if (!req.url.startsWith('/ws')) {
        proxyRes.headers['x-response-time'] = Date.now() - req._startTime;
      }
    },
    onProxyReq: function(proxyReq, req, res) {
      req._startTime = Date.now();
    }
  });

  // Apply proxy to all relevant paths
  app.use(['/api', '/ws', '/health', '/metrics'], backendProxy);

  // Proxy Alert Manager requests
  app.use(
    '/alerts',
    createProxyMiddleware({
      target: 'https://nova-backend:9093',
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/alerts': '/api/v1/alerts'
      }
    })
  );
};
