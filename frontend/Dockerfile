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
RUN npm run build

# Production stage - copy built files to volume mount point
FROM alpine:latest

WORKDIR /app

# Copy built files
COPY --from=builder /app/dist ./dist

# Keep container running so volume mount works
CMD ["sh", "-c", "while true; do sleep 3600; done"]
