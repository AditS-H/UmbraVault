#!/usr/bin/env python3
"""Generate JWT token for API testing"""
import json
import jwt
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
config_path = project_root / 'config.json'

with config_path.open('r', encoding='utf-8') as f:
    config = json.load(f)

secret = config['api']['secret_token']
if secret == 'change-this-to-a-strong-token':
    print("❌ Error: Please run setup-wsl.sh first to generate a secure token")
    exit(1)

token = jwt.encode({'user': 'local', 'exp': 9999999999}, secret, algorithm='HS256')
print(f"JWT Token:\n{token}")
print(f"\nUse in API requests:")
print(f'curl -H "Authorization: Bearer {token}" -X POST http://127.0.0.1:8888/run/network -H "Content-Type: application/json" -d \'{{"target": "127.0.0.1"}}\'')
