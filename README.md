
**Local-only, AI-powered pentesting framework with Docker sandboxing**

A secure, modular penetration testing toolkit that runs tools (nmap, gobuster, sqlmap, etc.) in isolated Docker containers with AI-assisted tool selection. Built for ethical hackers who want automation without the risks of unsandboxed execution.

## Key Features

✅ **Sandboxed Execution**: All tools run in Docker containers (Kali-based)  
✅ **Input Sanitization**: Strict IP/domain validation, no shell injection risks  
✅ **Dual Interface**: Rich TUI for interactive use + Flask API for automation  
✅ **Modular Tool System**: JSON configs for 20+ tools (easily expand to 150+)  
✅ **AI-Ready**: Optional local Ollama integration for smart tool suggestions  
✅ **Security-First**: JWT auth, localhost-only API, timeout limits  
✅ **Local Testing**: Designed for safe use against your own VMs/containers  

## Quick Start (WSL)

**Current Status**: ✅ Core framework tested and working! Docker setup required for full functionality.

**One-command setup** (installs Docker + builds tools):

```bash
cd /mnt/e/Hacking/hexstrike-local
chmod +x setup-wsl.sh
./setup-wsl.sh
```

**Test without Docker** (safe commands only):

```bash
source venv/bin/activate
python3 test_framework.py
```

**Run Interactive TUI**:

```bash
./run.sh tui
```

**Or Run API Server**:

```bash
./run.sh api
# Test: python3 scripts/generate_token.py
```

📖 **Full setup guide**: See [`QUICKSTART_WSL.md`](QUICKSTART_WSL.md) for detailed instructions.

## What's Included

- **Core Tools**: nmap, rustscan, gobuster, nikto, sqlmap, hydra, john, hashcat, nuclei, ffuf
- **Safe Defaults**: 300s timeout, 512MB memory limit per container
- **Auto Reports**: JSON logs with Rich table previews
- **Test Suite**: pytest validation for sanitizer and core modules

## Architecture

```
User Input → Sanitizer → Tool Selector → Docker Executor → Reporter
                              ↓
                      (Optional: Ollama AI)
```

All external tools execute inside `kalitools:latest` container with:
- Network isolation (host mode for local scans only)
- Resource limits (mem/timeout)
- Read-only mounts for configs

## Requirements

- **OS**: WSL2 (Ubuntu 22.04+) or native Linux
- **Python**: 3.10+
- **Docker**: 20.10+ with compose
- **Disk**: ~2GB for Docker image + tools

## Project Structure

```
hexstrike-local/
├── src/               # Core Python modules
├── docker/            # Sandbox container definitions
├── tools/             # JSON tool configs (network, web)
├── scripts/           # Token generator, API tests
├── tests/             # pytest test suite
├── logs/              # Auto-generated reports
├── config.json        # Settings (edit secret_token!)
└── setup-wsl.sh       # Automated installer
```

## Security Notes

⚠️ **Only scan targets you own or have permission to test**  
⚠️ API binds to `127.0.0.1` only—not exposed externally  
⚠️ Change `secret_token` in `config.json` before first use  
⚠️ Keep `sandbox: true` to enforce Docker isolation  

## Extending

Add tools to `tools/*.json`:
```json
{
  "mytool": {"cmd": "mytool --scan {target}"}
}
```

Add to `docker/Dockerfile.tools`, rebuild:
```bash
cd docker && docker build -t kalitools:latest -f Dockerfile.tools .
```

## License

Educational/research use. Always follow responsible disclosure and ethical hacking guidelines.

---

**Built with**: Flask, Rich, Docker, PyJWT | **Tested on**: WSL2 Ubuntu 22.04  
**Contributors welcome!** Open issues for bugs or feature requests.
