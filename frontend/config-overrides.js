const path = require('path');
const { override, addWebpackPlugin, addWebpackResolve } = require('customize-cra');

module.exports = override(
  // Add webpack resolve configuration for production
  addWebpackResolve({
    fallback: {
      "crypto": require.resolve("crypto-browserify"),
      "stream": require.resolve("stream-browserify"),
      "assert": require.resolve("assert"),
      "http": false,
      "https": false,
      "os": false,
      "url": false,
      "zlib": false,
      "util": require.resolve("util"),
      "buffer": require.resolve("buffer"),
      "process": require.resolve("process/browser"),
      "fs": false,
      "path": false
    }
  }),
  
  // Production optimizations
  (config) => {
    // Enable source maps for production debugging
    if (process.env.NODE_ENV === 'production') {
      config.devtool = 'source-map';
    }
    
    // Optimize chunks for production
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...config.optimization.splitChunks,
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true
          }
        }
      }
    };
    
    return config;
  }
);