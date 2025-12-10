# HexStrike-Local: IP Validation and Task Execution Details

## What It Checks For IPs
- **IPv4/IPv6 format**: Validates targets as IPv4 (e.g., `106.221.225.38`) or IPv6 using strict patterns.
- **Domain alternative**: Accepts domains matching safe hostname rules (letters, numbers, dots, hyphens).
- **Ports**: If provided, ensures they are integers in the range `1–65535`.
- **Sanitization**: Strips shell metacharacters to prevent command injection: `; | & $ ( ) > < \` " '`.
- **Local-only context**: Allows private/reserved ranges given the tool runs on localhost in a sandbox.

## How Network Tasks Run
- **Selection**: Picks `nmap` (and optionally `masscan`) based on the `tools/network.json` definitions.
- **Sandboxing**: Attempts Docker SDK; if unavailable, falls back to `docker run` using the `kalitools` image.
- **Command**: Example for IPv4 service detection:
  - `nmap -sV -T4 <IP> -oN /app/logs/nmap_<IP>.txt`
- **Resource limits**: Timeouts and restrained container resources enforced by the executor.
- **Reporting**: Captures command, exit code, stdout/stderr, elapsed time; writes JSON into `logs/`.
- **TUI display**: Shows a compact table with tool status and elapsed time via Rich.

## How Web Tasks Run
- **Selection**: Uses `gobuster`, `nikto`, and `sqlmap` as defined in `tools/web.json`.
- **Sandboxing**: Same Docker-first, CLI fallback approach.
- **Commands**:
  - `gobuster dir -u <TARGET_URL_OR_IP> -w <wordlist> -o /app/logs/gobuster_<IP>.txt`
  - `nikto -host <TARGET_URL_OR_IP> -output /app/logs/nikto_<IP>.txt`
  - `sqlmap -u <TARGET_URL_OR_IP> --batch --output-dir=/app/logs/sqlmap_<IP>`
- **Reporting**: One consolidated `web_*.json` capturing per-tool outcomes.

## Observed Results From Your Run (Dec 2–3, 2025)
- **Network (`106.221.225.38`)**
  - `nmap`: Failed because container path `/app/logs` did not exist. Error: `Failed to open normal output file /app/logs/... No such file or directory`.
- **Web (example run to `172.16.96.147`)**
  - `gobuster`: Failed due to missing wordlist: `/usr/share/wordlists/dirb/common.txt` not present in image.
  - `nikto`: Failed to write to `/app/logs/...` because directory not present in container.
  - `sqlmap`: Succeeded to run and wrote into `/app/logs/sqlmap_<IP>`; actual HTTP connection timed out for that target, but the tool executed and produced CSV output as designed.

## Why These Failures Happened
- **Missing logs directory in container**: Tools write to `/app/logs`, but the CLI fallback did not bind-mount or pre-create this directory inside the container.
- **Missing wordlist path**: The Kali image used does not include `dirb` wordlists at `/usr/share/wordlists/dirb/common.txt` by default.

## Quick Fixes (Recommended)
- **Bind-mount logs in CLI fallback**:
  - Add `-v <host_logs>:/app/logs:rw` to `docker run` in `src/executor.py` and ensure the host `logs/` exists.
  - Host path example on WSL: `/mnt/e/Hacking/hexstrike-local/logs`.
- **Create `/app/logs` inside image**:
  - In `Dockerfile.tools`, add `RUN mkdir -p /app/logs`.
- **Update gobuster wordlist**:
  - Use a wordlist that exists in the image, e.g., SecLists if installed: `/usr/share/seclists/Discovery/Web-Content/common.txt`.
  - Or install `seclists` in the Dockerfile (`apt-get install -y seclists`).

## End-to-End Flow On Success
- **Input**: IP/domain validated and sanitized.
- **Selection**: Appropriate tools chosen for task.
- **Execution**: Tools run in Docker; outputs saved to `/app/logs` and captured in executor.
- **Report**: JSON written in host `logs/` (e.g., `network_YYYYMMDD_HHMMSS.json`, `web_YYYYMMDD_HHMMSS.json`).
- **TUI**: Shows per-tool status; errors surface clearly with cause and remediation.

## Where To Look
- **Host logs**: `logs/` directory for JSON and tool artifacts.
- **Config**: `config.json` for sandbox settings and image name.
- **Tool defs**: `tools/*.json` for command templates and paths.
- **Executor**: `src/executor.py` for Docker/CLI behavior and mounts.

## Next Steps I Can Apply
1. Patch executor to bind-mount `logs/` and create `/app/logs` when needed.
2. Update Dockerfile to include `seclists` and pre-create `/app/logs`.
3. Adjust `tools/web.json` to point `gobuster` at a valid wordlist.
4. Rebuild the image and re-run the TUI to confirm clean success.
