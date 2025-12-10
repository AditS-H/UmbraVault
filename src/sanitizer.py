import re
import json
from typing import Dict, Any
from pathlib import Path


class InputSanitizer:
    IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    DOMAIN_REGEX = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
    PORT_REGEX = re.compile(r'^[1-9]\d{0,4}$')

    @staticmethod
    def sanitize_task(data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = data.copy()
        target = str(data.get('target', '')).strip()
        if not (InputSanitizer.IP_REGEX.match(target) or InputSanitizer.DOMAIN_REGEX.match(target)):
            raise ValueError("Invalid target: Must be IP or domain (no paths/params).")
        if 'port' in data and not InputSanitizer.PORT_REGEX.match(str(data['port'])):
            raise ValueError("Invalid port: 1-65535 only.")
        # Strip known shell metacharacters from provided cmd/args if any
        for key in ['cmd', 'args']:
            if key in sanitized:
                sanitized[key] = re.sub(r'[;&|`$(){}\[\]<>]', '', str(sanitized[key]))
        return sanitized

    @staticmethod
    def validate_json_config(config_path: str) -> Dict[str, Any]:
        p = Path(config_path)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")
        with p.open('r', encoding='utf-8') as f:
            config = json.load(f)
        token = config.get('api', {}).get('secret_token')
        if not token or token == 'change-this-to-a-strong-token':
            raise ValueError("Missing or placeholder API token in config.json; please set a strong secret_token.")
        return config
