const path = require('path');
const { override, addWebpackResolve } = require('customize-cra');

module.exports = override(
  // Add webpack resolve configuration for production
  addWebpackResolve({
    fallback: {
      "crypto": require.resolve("crypto-browserify"),
      "stream": require.resolve("stream-browserify"),
      "buffer": require.resolve("buffer"),
      "process": require.resolve("process/browser"),
      "assert": false,
      "http": false,
      "https": false,
      "os": false,
      "url": false,
      "zlib": false,
      "util": false,
      "fs": false,
      "path": false
    }
  }),
  
  // Production optimizations
  (config) => {
    // Disable source maps for production
    if (process.env.NODE_ENV === 'production') {
      config.devtool = false;
    }
    
    // Optimize chunks for better caching
    if (config.optimization.splitChunks) {
      config.optimization.splitChunks.chunks = 'all';
      config.optimization.splitChunks.cacheGroups = {
        ...config.optimization.splitChunks.cacheGroups,
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
          enforce: true
        }
      };
    }
    
    return config;
  }
);