#!/usr/bin/env python3
"""
Pre-flight dependency checker for UmbraVault
Verifies Docker, wordlists, and tools are accessible
"""
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table


def check_docker():
    """Check Docker installation and daemon status"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {'status': '❌', 'detail': 'Docker installed but command failed'}
        
        daemon = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
        if daemon.returncode != 0:
            return {'status': '⚠️', 'detail': 'Docker not running. Start: sudo service docker start'}
        
        return {'status': '✅', 'detail': result.stdout.strip().split()[2]}
    except FileNotFoundError:
        return {'status': '❌', 'detail': 'Not installed. See QUICKSTART_WSL.md'}
    except Exception as e:
        return {'status': '❌', 'detail': str(e)}


def check_docker_image(image_name='kalitools:latest'):
    """Check if Docker image is built"""
    try:
        result = subprocess.run(
            ['docker', 'images', '-q', image_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout.strip():
            return {'status': '✅', 'detail': f'{image_name} found'}
        return {
            'status': '❌',
            'detail': f'{image_name} not built. Run: cd docker && docker build -t {image_name} -f Dockerfile.tools .'
        }
    except Exception as e:
        return {'status': '❌', 'detail': str(e)}


def check_wordlists_in_container(image_name='kalitools:latest'):
    """Check if seclists wordlists are available in the Docker image"""
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', image_name, 'ls', '/usr/share/seclists/Discovery/Web-Content/common.txt'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return {'status': '✅', 'detail': 'SecLists installed'}
        
        # Fallback: check for dirb wordlists
        dirb_check = subprocess.run(
            ['docker', 'run', '--rm', image_name, 'ls', '/usr/share/wordlists/dirb/common.txt'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if dirb_check.returncode == 0:
            return {'status': '⚠️', 'detail': 'Only dirb wordlists found. Install seclists for better coverage.'}
        
        return {
            'status': '❌',
            'detail': 'No wordlists found. Add seclists to Dockerfile and rebuild.'
        }
    except Exception as e:
        return {'status': '❌', 'detail': str(e)}


def check_tool_in_container(tool_name, image_name='kalitools:latest'):
    """Check if a specific tool is installed in the container"""
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', image_name, 'which', tool_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Get version if possible
            ver_result = subprocess.run(
                ['docker', 'run', '--rm', image_name, tool_name, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = ver_result.stdout.strip().split('\n')[0][:40] if ver_result.returncode == 0 else 'installed'
            return {'status': '✅', 'detail': version}
        return {'status': '❌', 'detail': 'Not found'}
    except Exception as e:
        return {'status': '❌', 'detail': str(e)[:30]}


def main():
    console = Console()
    console.print("\n[bold cyan]🔍 UmbraVault Dependency Check[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="dim", width=25)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Details", width=60)
    
    # Docker checks
    docker_status = check_docker()
    table.add_row("Docker Engine", docker_status['status'], docker_status['detail'])
    
    if docker_status['status'] == '✅':
        image_status = check_docker_image()
        table.add_row("Docker Image", image_status['status'], image_status['detail'])
        
        if image_status['status'] == '✅':
            # Wordlist check
            wordlist_status = check_wordlists_in_container()
            table.add_row("Wordlists", wordlist_status['status'], wordlist_status['detail'])
            
            # Core tools check
            tools_to_check = ['nmap', 'gobuster', 'sqlmap', 'nikto', 'hydra']
            for tool in tools_to_check:
                tool_status = check_tool_in_container(tool)
                table.add_row(f"  └─ {tool}", tool_status['status'], tool_status['detail'])
    
    console.print(table)
    
    # Config check
    config_path = Path('./config.json')
    if config_path.exists():
        console.print("\n[green]✅ config.json found[/green]")
    else:
        console.print("\n[red]❌ config.json missing[/red]")
    
    console.print("\n[dim]Run: python3 src/validator.py for detailed config validation[/dim]\n")


if __name__ == '__main__':
    main()
