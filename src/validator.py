"""
Configuration validator for UmbraVault
Validates config.json and runtime environment before task execution
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


class ConfigValidator:
    """Validates config and environment prerequisites"""
    
    @staticmethod
    def validate_config_file(config_path: str) -> Dict[str, Any]:
        """Load and validate config.json structure and values"""
        issues = []
        config_path_obj = Path(config_path)
        
        if not config_path_obj.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            config = json.loads(config_path_obj.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config: {e}")
        
        # Validate API secret token
        secret = config.get('api', {}).get('secret_token', '')
        if not secret or len(secret) < 32:
            issues.append("⚠️  secret_token is missing or too short (min 32 chars). Run: python3 scripts/generate_token.py")
        
        # Validate sandbox setting
        if 'sandbox' not in config:
            issues.append("⚠️  'sandbox' setting missing in config. Add 'sandbox: true' for Docker isolation.")
        
        # Validate Docker image name
        if config.get('sandbox', True):
            image = config.get('docker', {}).get('image', '')
            if not image:
                issues.append("⚠️  Docker image name missing. Set 'docker.image' in config.")
        
        # Validate paths
        tools_path = Path(config.get('tools_path', './tools/'))
        if not tools_path.exists():
            issues.append(f"⚠️  Tools directory not found: {tools_path}")
        
        logs_path = Path(config.get('logs_path', './logs/'))
        logs_path.mkdir(parents=True, exist_ok=True)  # Auto-create if missing
        
        return {'config': config, 'issues': issues}
    
    @staticmethod
    def check_docker_available() -> Dict[str, Any]:
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return {'available': False, 'error': 'Docker command failed'}
            
            # Check if daemon is running
            ping_result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ping_result.returncode != 0:
                return {
                    'available': False,
                    'error': 'Docker daemon not running. Start with: sudo service docker start'
                }
            
            return {'available': True, 'version': result.stdout.strip()}
        except FileNotFoundError:
            return {
                'available': False,
                'error': 'Docker not installed. See QUICKSTART_WSL.md for installation steps.'
            }
        except subprocess.TimeoutExpired:
            return {'available': False, 'error': 'Docker command timed out'}
    
    @staticmethod
    def check_docker_image(image_name: str) -> Dict[str, Any]:
        """Check if specified Docker image exists locally"""
        try:
            result = subprocess.run(
                ['docker', 'images', '-q', image_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            exists = bool(result.stdout.strip())
            if not exists:
                return {
                    'exists': False,
                    'error': f'Image {image_name} not found. Build with: cd docker && docker build -t {image_name} -f Dockerfile.tools .'
                }
            return {'exists': True}
        except Exception as e:
            return {'exists': False, 'error': f'Failed to check image: {e}'}
    
    @staticmethod
    def run_preflight_checks(config_path: str = './config.json') -> List[str]:
        """Run all validation checks and return issues/warnings"""
        all_issues = []
        
        # 1. Config validation
        try:
            result = ConfigValidator.validate_config_file(config_path)
            config = result['config']
            all_issues.extend(result['issues'])
        except Exception as e:
            all_issues.append(f"❌ Config validation failed: {e}")
            return all_issues
        
        # 2. Docker availability (if sandbox enabled)
        if config.get('sandbox', True):
            docker_check = ConfigValidator.check_docker_available()
            if not docker_check['available']:
                all_issues.append(f"❌ Docker: {docker_check['error']}")
            
            # 3. Docker image check
            if docker_check.get('available'):
                image_name = config.get('docker', {}).get('image', 'kalitools:latest')
                image_check = ConfigValidator.check_docker_image(image_name)
                if not image_check['exists']:
                    all_issues.append(f"❌ {image_check['error']}")
        
        return all_issues


if __name__ == '__main__':
    """Run preflight checks from command line"""
    config_file = sys.argv[1] if len(sys.argv) > 1 else './config.json'
    print("🔍 Running UmbraVault preflight checks...\n")
    
    issues = ConfigValidator.run_preflight_checks(config_file)
    
    if not issues:
        print("✅ All checks passed! Ready to run.")
        sys.exit(0)
    else:
        print("⚠️  Issues found:\n")
        for issue in issues:
            print(f"  {issue}")
        print("\n❌ Fix issues above before running tasks.")
        sys.exit(1)
