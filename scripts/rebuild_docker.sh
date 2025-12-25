#!/bin/bash
# Rebuild Docker image with improvements
cd "$(dirname "$0")/../docker" || exit 1

echo "🔨 Rebuilding kalitools:latest with seclists and /app/logs..."
docker build -t kalitools:latest -f Dockerfile.tools .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image rebuilt successfully!"
    echo ""
    echo "Verifying seclists installation..."
    docker run --rm kalitools:latest ls -la /usr/share/seclists/Discovery/Web-Content/common.txt
    echo ""
    echo "Verifying /app/logs directory..."
    docker run --rm kalitools:latest ls -la /app/logs
    echo ""
    echo "✅ All set! Run: python3 scripts/check_tool_versions.py to see installed tools."
else
    echo "❌ Build failed. Check errors above."
    exit 1
fi
