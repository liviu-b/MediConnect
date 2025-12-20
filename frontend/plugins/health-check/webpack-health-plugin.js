/**
 * Webpack Health Plugin
 * Monitors webpack compilation status for health checks
 */

class WebpackHealthPlugin {
  constructor() {
    this.status = {
      ready: false,
      lastCompileTime: null,
      errors: [],
      warnings: [],
    };
  }

  apply(compiler) {
    compiler.hooks.done.tap('WebpackHealthPlugin', (stats) => {
      const info = stats.toJson();

      this.status = {
        ready: !stats.hasErrors(),
        lastCompileTime: new Date().toISOString(),
        errors: info.errors || [],
        warnings: info.warnings || [],
        compilationTime: stats.endTime - stats.startTime,
      };

      if (stats.hasErrors()) {
        console.error('❌ Webpack compilation failed');
      } else {
        console.log('✅ Webpack compilation successful');
      }
    });

    compiler.hooks.invalid.tap('WebpackHealthPlugin', () => {
      this.status.ready = false;
      console.log('🔄 Webpack recompiling...');
    });
  }

  getStatus() {
    return this.status;
  }
}

module.exports = WebpackHealthPlugin;
