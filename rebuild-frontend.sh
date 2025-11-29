#!/bin/bash
# Complete frontend rebuild script

echo "🛑 Stopping frontend container..."
docker-compose stop frontend

echo "🗑️  Removing frontend container..."
docker-compose rm -f frontend

echo "🗑️  Removing frontend_dist volume (old build)..."
docker volume rm hackathon_frontend_dist 2>/dev/null || echo "Volume already removed or doesn't exist"

echo "🧹 Cleaning local frontend build artifacts..."
cd frontend
rm -rf dist node_modules .vite

echo "🔨 Rebuilding frontend container (no cache)..."
cd ..
docker-compose build --no-cache frontend

echo "🚀 Starting frontend container..."
docker-compose up -d frontend

echo "✅ Frontend rebuild complete!"
echo "📋 Check logs with: docker-compose logs -f frontend"

