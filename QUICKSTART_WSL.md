# UmbraVault: WSL Quick Start Guide

## Prerequisites (Windows with WSL)

1. **Install WSL2 with Ubuntu** (if not already installed):
   ```powershell
   # In PowerShell (Admin)
   wsl --install -d Ubuntu-22.04
   # Restart your computer after installation
   ```

2. **Access your project in WSL**:
   ```bash
   # In WSL terminal
   cd /mnt/e/Hacking/umbravault
   ```

## One-Command Setup

Run the automated setup script (installs deps, builds Docker, generates token):

```bash
chmod +x setup-wsl.sh
./setup-wsl.sh
```

This script will:
- ✅ Check Python3 and Docker
- ✅ Create virtual environment
- ✅ Install all Python dependencies
- ✅ Generate a secure API token
- ✅ Build the Docker tools image (~5-10 min first time)
- ✅ Create logs directory

## Manual Setup (if you prefer step-by-step)

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip docker.io docker-compose
sudo usermod -aG docker $USER
```

**Important**: Log out and back in after adding yourself to docker group.

### 2. Create Virtual Environment

```bash
cd /mnt/e/Hacking/umbravault
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Generate Secure API Token

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and paste it in config.json as the secret_token value
```

Or use Python to update automatically:
```bash
python3 - <<'EOF'
import json, secrets
with open('config.json', 'r') as f:
    cfg = json.load(f)
cfg['api']['secret_token'] = secrets.token_hex(32)
with open('config.json', 'w') as f:
    json.dump(cfg, f, indent=2)
print("✅ Token updated in config.json")
EOF
```

### 4. Build Docker Sandbox Image

```bash
cd docker
docker build -t kalitools:latest -f Dockerfile.tools .
cd ..
```

This builds a Kali-based container with nmap, gobuster, sqlmap, nikto, etc.

### 5. Run Tests (Optional)

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## Running UmbraVault

### Option A: Interactive TUI (Recommended for beginners)

```bash
source venv/bin/activate  # if not already activated
./run.sh tui
```

You'll see a Rich-powered interface:
- Select task type: `network` or `web`
- Enter target: e.g., `127.0.0.1` or `192.168.1.100`
- Confirm to run tools
- View results in real-time table
- JSON reports saved to `logs/`

### Option B: API Server

```bash
source venv/bin/activate
./run.sh api
```

The API runs on `http://127.0.0.1:8888` (localhost only for security).

**Test the API**:

1. Generate a JWT token:
   ```bash
   python3 scripts/generate_token.py
   ```

2. Use the provided curl command, or run the test script:
   ```bash
   chmod +x scripts/test_api.sh
   ./scripts/test_api.sh
   ```

**Manual API test**:
```bash
# Replace YOUR_TOKEN with actual JWT from generate_token.py
TOKEN="YOUR_TOKEN"

# Health check
curl http://127.0.0.1:8888/health

# Run network scan
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://127.0.0.1:8888/run/network \
     -d '{"target": "127.0.0.1"}'
```

## Testing Setup

### Safe Local Targets

Test against **your own local VMs only**:

1. **Install DVWA** (Damn Vulnerable Web App):
   ```bash
   docker run -d -p 8080:80 vulnerables/web-dvwa
   # Then scan: 127.0.0.1:8080
   ```

2. **Metasploitable VM**: Download from Rapid7 and run in VirtualBox/VMware

3. **Your own localhost**: `127.0.0.1` is always safe for testing

### Quick Test Flow

```bash
# 1. Start TUI
./run.sh tui

# 2. In TUI:
#    - Task type: network
#    - Target: 127.0.0.1
#    - Confirm: yes

# 3. Check results
cat logs/network_*.json
```

## Extending the Framework

### Add New Tools

1. Edit `tools/network.json` or `tools/web.json`:
   ```json
   {
     "mytool": {"cmd": "mytool -arg {target}"}
   }
   ```

2. Ensure tool is in `docker/Dockerfile.tools`:
   ```dockerfile
   RUN apt-get install -y mytool
   ```

3. Rebuild Docker image:
   ```bash
   cd docker && docker build -t kalitools:latest -f Dockerfile.tools . && cd ..
   ```

### Add Task Types

Edit `src/selector.py`, add to `mappings`:
```python
mappings = {
    'network': ['nmap', 'rustscan'],
    'web': ['gobuster', 'nikto'],
    'auth': ['hydra', 'medusa'],  # New task type
}
```

Create `tools/auth.json` with tool configs.

### Enable Local AI (Optional)

1. Install Ollama in WSL:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2
   ```

2. Update `config.json`:
   ```json
   "ai_model": "llama3.2"
   ```

3. Install Python package:
   ```bash
   pip install ollama
   ```

The selector will now suggest additional tools based on context.

## Troubleshooting

### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Then logout and login to WSL
newgrp docker  # or restart WSL: wsl --shutdown (in PowerShell)
```

### Port Already in Use (8888)
Change in `config.json`:
```json
"api": {"port": 9999}
```

### Tool Not Found in Container
Check if installed:
```bash
docker run -it kalitools:latest /bin/bash
# Inside container:
which nmap
```

Add missing tools to `docker/Dockerfile.tools` and rebuild.

### No Output from Tools
- Increase timeout in `config.json`: `"timeout": 600`
- Check logs: `docker logs <container_id>`
- Test tool manually in container

### Tests Fail
```bash
# Install test dependencies
pip install pytest

# Run with verbose output
python -m pytest tests/ -vv
```

## Security Reminders

⚠️ **Local Use Only**:
- Never run against targets you don't own
- API binds to 127.0.0.1 only
- Change `secret_token` before first use
- Keep `sandbox: true` in config

## File Structure Reference

```
umbravault/
├── README.md              # Overview
├── QUICKSTART_WSL.md      # This guide
├── config.json            # Settings (edit token!)
├── requirements.txt       # Python deps
├── setup-wsl.sh           # Auto setup script
├── run.sh                 # Launcher (tui/api)
├── docker/
│   ├── Dockerfile.tools   # Tools container
│   └── docker-compose.yml # Compose config
├── src/
│   ├── sanitizer.py       # Input validation
│   ├── executor.py        # Tool runner
│   ├── selector.py        # Task→tools mapper
│   ├── reporter.py        # JSON reports
│   ├── tui.py             # Interactive CLI
│   └── server.py          # Flask API
├── tools/
│   ├── network.json       # Network tool configs
│   └── web.json           # Web tool configs
├── scripts/
│   ├── generate_token.py  # JWT generator
│   └── test_api.sh        # API test script
├── tests/
│   └── test_sanitizer.py  # Unit tests
└── logs/                  # Auto-created reports
```

## Next Steps

1. ✅ Run `./setup-wsl.sh` to complete setup
2. ✅ Test with TUI: `./run.sh tui` → scan `127.0.0.1`
3. ✅ Check report: `cat logs/network_*.json`
4. ✅ Add more tools to `tools/*.json`
5. ✅ Integrate with CI/CD or expand to 50+ tools

**Happy ethical hacking! 🚀**
