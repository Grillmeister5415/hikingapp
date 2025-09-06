const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: 'all',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: false,
        ws: true,
        // no pathRewrite — Django serves /api/ correctly
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: false,
      },
      // optional, only if you ever fetch Django /static from the FE:
      // '/static': {
      //   target: 'http://localhost:8000',
      //   changeOrigin: false,
      // },
    },
  },
});
