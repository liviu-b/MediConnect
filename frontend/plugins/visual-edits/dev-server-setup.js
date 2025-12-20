/**
 * Dev Server Setup for Visual Edits
 * Configures the dev server to support visual editing features
 */

module.exports = function setupDevServer(devServerConfig) {
  // Add custom headers for visual editing
  devServerConfig.headers = {
    ...devServerConfig.headers,
    'X-Visual-Edits-Enabled': 'true',
  };

  // Enable CORS for visual editing tools
  devServerConfig.allowedHosts = 'all';

  // Add custom middleware for visual editing endpoints
  const originalSetupMiddlewares = devServerConfig.setupMiddlewares;

  devServerConfig.setupMiddlewares = (middlewares, devServer) => {
    if (originalSetupMiddlewares) {
      middlewares = originalSetupMiddlewares(middlewares, devServer);
    }

    // Add visual editing endpoint
    devServer.app.get('/visual-edits/status', (req, res) => {
      res.json({
        enabled: true,
        timestamp: new Date().toISOString(),
      });
    });

    console.log('✅ Visual edits dev server configured');

    return middlewares;
  };

  return devServerConfig;
};
