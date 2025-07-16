#!/bin/bash

# Build configuration for deployment
export NODE_ENV=production
export CI=true
export DISABLE_ESLINT_PLUGIN=true
export GENERATE_SOURCEMAP=false
export INLINE_RUNTIME_CHUNK=false

# Clear any existing installations
rm -rf node_modules yarn.lock package-lock.json .next .cache

# Install dependencies with exact versions
yarn install --frozen-lockfile --production=false --network-timeout 300000

# Build the application
yarn build

echo "Build completed successfully!"