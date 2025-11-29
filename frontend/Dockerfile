# Frontend Dockerfile
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with retry and longer timeout
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm ci --prefer-offline --no-audit

# Copy source code
COPY . .

# Build application with production API URL
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN echo "Building frontend with VITE_API_BASE_URL=$VITE_API_BASE_URL" && \
    npm run build && \
    echo "Frontend build completed successfully" && \
    ls -la dist/

# Production stage - copy built files to volume mount point
FROM alpine:latest

WORKDIR /app

# Install bash for better scripting
RUN apk add --no-cache bash

# Copy built files to backup location (volume will mount over /app/dist)
COPY --from=builder /app/dist ./dist_backup

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Use entrypoint to copy files and log
ENTRYPOINT ["/docker-entrypoint.sh"]
