#!/usr/bin/env bash
# Test API endpoints with generated token

if [[ ! -f "../config.json" ]]; then
    echo "❌ config.json not found. Run from project root."
    exit 1
fi

TOKEN=$(python3 scripts/generate_token.py | grep -oP 'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*' | head -1)

if [[ -z "$TOKEN" ]]; then
    echo "❌ Failed to generate token"
    exit 1
fi

echo "=== Testing HexStrike-Local API ==="
echo ""

# Test health endpoint
echo "1. Testing /health endpoint..."
curl -s http://127.0.0.1:8888/health | python3 -m json.tool
echo ""

# Test network scan (change target as needed)
echo "2. Testing /run/network endpoint..."
echo "   Target: 127.0.0.1"
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://127.0.0.1:8888/run/network \
     -d '{"target": "127.0.0.1"}' | python3 -m json.tool
echo ""

echo "✅ API test complete. Check logs/ for reports."
