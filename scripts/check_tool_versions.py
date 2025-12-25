#!/usr/bin/env python3
"""
Tool version checker for HexStrike-Local
Displays versions of installed pentesting tools in Docker image
"""
import subprocess
import sys
from rich.console import Console
from rich.table import Table


def get_tool_version(tool_name, version_flag='--version', image='kalitools:latest'):
    """Get version info for a tool in the Docker image"""
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', image, tool_name, version_flag],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Extract first meaningful line
            output = result.stdout.strip()
            if not output:
                output = result.stderr.strip()
            version_line = output.split('\n')[0] if output else 'installed'
            return version_line[:80]  # Truncate long outputs
        return '❌ Failed to get version'
    except subprocess.TimeoutExpired:
        return '⏱️  Timeout'
    except Exception as e:
        return f'❌ {str(e)[:40]}'


def main():
    console = Console()
    image_name = sys.argv[1] if len(sys.argv) > 1 else 'kalitools:latest'
    
    console.print(f"\n[bold cyan]🔧 Tool Versions in {image_name}[/bold cyan]\n")
    
    # Check if image exists
    try:
        check = subprocess.run(
            ['docker', 'images', '-q', image_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if not check.stdout.strip():
            console.print(f"[red]❌ Image {image_name} not found. Build it first.[/red]\n")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Docker error: {e}[/red]\n")
        sys.exit(1)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tool", style="cyan", width=20)
    table.add_column("Version", width=70)
    
    # Define tools and their version flags
    tools = [
        ('nmap', '--version'),
        ('masscan', '--version'),
        ('gobuster', 'version'),
        ('nikto', '-Version'),
        ('sqlmap', '--version'),
        ('hydra', '-h'),  # hydra shows version in help
        ('john', '--version'),
        ('hashcat', '--version'),
        ('nuclei', '-version'),
        ('ffuf', '-V'),
        ('curl', '--version'),
    ]
    
    for tool, flag in tools:
        version = get_tool_version(tool, flag, image_name)
        # Clean up version string for better display
        if 'version' in version.lower() or tool in version.lower():
            # Extract just version number if possible
            parts = version.split()
            if len(parts) > 1 and any(c.isdigit() for c in parts[1]):
                version = ' '.join(parts[:3])  # Tool name + version
        table.add_row(tool, version)
    
    console.print(table)
    console.print()


if __name__ == '__main__':
    main()
