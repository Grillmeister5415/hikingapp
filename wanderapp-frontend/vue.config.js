const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  devServer: {
    host: '0.0.0.0',     // reachable from other devices
    port: 8080,
    allowedHosts: 'all',
    proxy: {
      '/api': {
        target: 'http://192.168.178.65:8000', // ok since proxy runs on your Mac
        changeOrigin: true,
        ws: true,
        // IMPORTANT: no pathRewrite here since Django serves /api/...
        // pathRewrite: { '^/api': '' }  // <-- leave this OUT
      },
    },
  },
});
