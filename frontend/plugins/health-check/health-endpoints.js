/**
 * Health Check Endpoints
 * Sets up health check endpoints for the dev server
 */

module.exports = function setupHealthEndpoints(devServer, healthPluginInstance) {
  if (!devServer || !devServer.app) {
    console.warn('Dev server not available for health check endpoints');
    return;
  }

  const app = devServer.app;

  // Health check endpoint
  app.get('/health', (req, res) => {
    const status = healthPluginInstance ? healthPluginInstance.getStatus() : { status: 'ok' };
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      webpack: status,
    });
  });

  // Ready check endpoint
  app.get('/ready', (req, res) => {
    const status = healthPluginInstance ? healthPluginInstance.getStatus() : { ready: true };
    res.json({
      ready: status.ready !== false,
      timestamp: new Date().toISOString(),
    });
  });

  console.log('✅ Health check endpoints registered: /health, /ready');
};
