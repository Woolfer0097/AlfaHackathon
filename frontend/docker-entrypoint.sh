#!/bin/sh
set -e
# Entrypoint script to copy built files to volume mount

echo "🚀 Frontend container starting..."
echo "📦 Setting up frontend files..."

# Copy built files from backup location to volume mount point
if [ -d "/app/dist_backup" ] && [ "$(ls -A /app/dist_backup 2>/dev/null)" ]; then
    echo "✅ Found built files in image"
    echo "📋 Copying files from /app/dist_backup to /app/dist (volume)..."
    cp -r /app/dist_backup/* /app/dist/ 2>/dev/null || {
        echo "⚠️  Volume might be empty, initializing..."
        mkdir -p /app/dist
        cp -r /app/dist_backup/* /app/dist/
    }
    echo "📋 Files in /app/dist (volume):"
    ls -lh /app/dist/ | head -10
    echo "📊 Total size: $(du -sh /app/dist | cut -f1)"
    echo "✅ Files copied successfully to volume"
else
    echo "⚠️  No files found in /app/dist_backup"
fi

echo "✅ Frontend container ready"
echo "📋 Container running (volume mounted at /app/dist)"
echo "🔄 Starting keep-alive loop..."

# Keep container running and log periodically
while true; do
    sleep 3600
    echo "$(date): Frontend container still running"
done

