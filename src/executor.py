import subprocess
import shlex
import time
import os
from typing import Dict, Any
from pathlib import Path

try:
    import docker
    from docker.errors import DockerException
except Exception:
    docker = None
    DockerException = Exception


class ToolExecutor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.image = config.get('docker', {}).get('image', 'kalitools:latest')
        self.timeout = int(config.get('docker', {}).get('timeout', 300))
        self.sandbox = bool(config.get('sandbox', True))
        self.logs_path = Path(config.get('logs_path', './logs'))
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def _run_subprocess(self, cmd_list, timeout) -> Dict[str, Any]:
        start = time.time()
        try:
            proc = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
            return {
                'success': proc.returncode == 0,
                'output': proc.stdout + ("\n" + proc.stderr if proc.stderr else ""),
                'elapsed': time.time() - start,
                'error': None if proc.returncode == 0 else f"Return code {proc.returncode}"
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'output': '', 'elapsed': timeout, 'error': 'Timeout'}

    def execute(self, tool_cmd: str, target: str, env: Dict[str, str] = None) -> Dict[str, Any]:
        # tool_cmd already formatted string (may contain args). We'll build safe list.
        cmd = (tool_cmd + ' ' + target).strip()
        start = time.time()
        if self.sandbox and docker is not None:
            try:
                # Prefer Unix socket in WSL/Linux to avoid Windows npipe from parent env
                client = None
                try:
                    # Try env first
                    client = docker.from_env()
                    # Trigger ping to validate
                    client.ping()
                except Exception:
                    # Fallback to default Unix socket
                    base_url = os.environ.get('DOCKER_HOST', 'unix:///var/run/docker.sock')
                    if not base_url.startswith('unix://'):
                        base_url = 'unix:///var/run/docker.sock'
                    client = docker.DockerClient(base_url=base_url)
                    client.ping()
                container = client.containers.run(
                    self.image,
                    command=["/bin/bash", "-lc", cmd],
                    detach=True,
                    remove=True,
                    network_mode="host",
                    environment=env or {},
                    mem_limit="512m",
                    stdout=True,
                    stderr=True,
                )
                # wait with timeout
                try:
                    result = container.wait(timeout=self.timeout)
                    status_code = result.get('StatusCode', 1) if isinstance(result, dict) else 1
                except Exception:
                    container.kill()
                    return {'success': False, 'output': '', 'error': 'Timeout', 'elapsed': self.timeout}
                logs = container.logs().decode('utf-8', errors='ignore')
                success = (status_code == 0)
                return {
                    'success': success,
                    'output': logs,
                    'elapsed': time.time() - start,
                    'error': None if success else f'Container exited with status {status_code}'
                }
            except DockerException as e:
                # Fallback to docker CLI if SDK cannot connect (common on mixed Windows/WSL envs)
                try:
                    cli_cmd = [
                        'docker', 'run', '--rm', '--network', 'host', self.image,
                        '/bin/bash', '-lc', cmd
                    ]
                    res = subprocess.run(cli_cmd, capture_output=True, text=True, timeout=self.timeout)
                    output = res.stdout + ("\n" + res.stderr if res.stderr else "")
                    return {
                        'success': res.returncode == 0,
                        'output': output,
                        'elapsed': time.time() - start,
                        'error': None if res.returncode == 0 else f'docker CLI exit {res.returncode}'
                    }
                except Exception as ce:
                    return {'success': False, 'output': '', 'error': f'Docker error: {e}; CLI error: {ce}', 'elapsed': time.time() - start}
        else:
            # fallback: run locally (unsafe for production)
            parts = shlex.split(cmd)
            return self._run_subprocess(parts, timeout=self.timeout)
