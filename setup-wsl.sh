#!/usr/bin/env bash
# WSL Setup Script for UmbraVault
set -e

echo "=== UmbraVault WSL Setup ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo "✅ Python3 found: $(python3 --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install with:"
    echo "   sudo apt update && sudo apt install -y docker.io docker-compose"
    echo "   sudo usermod -aG docker \$USER"
    echo "   Then log out and back in."
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

# Create venv
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install deps
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate secure token
echo ""
echo "Generating secure API token..."
NEW_TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Generated token: $NEW_TOKEN"

# Update config.json with new token
if [[ -f config.json ]]; then
    python3 - <<PYEOF
import json
with open('config.json', 'r') as f:
    cfg = json.load(f)
cfg['api']['secret_token'] = '$NEW_TOKEN'
with open('config.json', 'w') as f:
    json.dump(cfg, f, indent=2)
PYEOF
    echo "✅ Updated config.json with new token"
fi

# Build Docker image
echo ""
echo "Building Docker tools image (this may take a few minutes)..."
cd docker
docker build -t kalitools:latest -f Dockerfile.tools .
cd ..
echo "✅ Docker image built: kalitools:latest"

# Create logs dir
mkdir -p logs

# Make run.sh executable
chmod +x run.sh

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "  1. Run TUI:  ./run.sh tui"
echo "  2. Run API:  ./run.sh api"
echo ""
echo "For API testing, use the token saved in config.json"
echo "Generate JWT with: python3 scripts/generate_token.py"
