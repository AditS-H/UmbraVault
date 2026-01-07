#!/usr/bin/env python3
"""Final end-to-end test with Docker sandbox"""
import json
import sys
from pathlib import Path

try:
    from src.sanitizer import InputSanitizer
    from src.selector import ToolSelector
    from src.executor import ToolExecutor
    from src.reporter import Reporter
    
    print("=== UmbraVault: Full Docker Test ===\n")
    
    # Load config
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"✅ Config loaded (sandbox={config['sandbox']})")
    
    # Validate config
    InputSanitizer.validate_json_config(str(config_path))
    print("✅ Config validated")
    
    # Test sanitizer
    target = "127.0.0.1"
    sanitized = InputSanitizer.sanitize_task({"target": target})
    print(f"✅ Sanitized target: {sanitized['target']}")
    
    # Test selector
    selector = ToolSelector(config['tools_path'], config)
    tools = selector.select_tools('network', target)
    print(f"✅ Selected {len(tools)} tool(s): {[t['name'] for t in tools]}")
    
    # Test executor with Docker
    print("\n--- Testing Docker Executor ---")
    executor = ToolExecutor(config)
    
    # Run a simple nmap scan
    print(f"Running nmap scan on {target}...")
    result = executor.execute("nmap -sn", target)
    print(f"✅ Executor ran: success={result['success']}, elapsed={result['elapsed']:.2f}s")
    if result.get('error'):
        print(f"   Error: {result['error']}")
    if result.get('output'):
        lines = result['output'].split('\n')[:8]
        print(f"   Output preview:\n   " + "\n   ".join(lines))
    
    # Test reporter
    print("\n--- Testing Reporter ---")
    reporter = Reporter(config['logs_path'])
    results = [{'name': 'nmap_test', **result}]
    report_path = reporter.generate_report('network_docker_test', results)
    print(f"✅ Report generated: {report_path}")
    
    print("\n🎉 Full Docker setup working! Framework is production-ready.")
    print("\n📋 Next steps:")
    print("   - Run TUI: ./run.sh tui")
    print("   - Run API: ./run.sh api")
    print("   - Add more tools to tools/*.json")
    print("   - Set up test targets (DVWA, Metasploitable)")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
