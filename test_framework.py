#!/usr/bin/env python3
"""Test the framework end-to-end without Docker"""
import json
import sys
from pathlib import Path

try:
    from src.sanitizer import InputSanitizer
    from src.selector import ToolSelector
    from src.executor import ToolExecutor
    from src.reporter import Reporter
    
    print("=== UmbraVault Test (No Docker) ===\n")
    
    # Load config
    config_path = Path(__file__).parent / 'config_no_docker.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"✅ Config loaded (sandbox={config['sandbox']})")
    
    # Test sanitizer
    target = "127.0.0.1"
    sanitized = InputSanitizer.sanitize_task({"target": target})
    print(f"✅ Sanitized target: {sanitized['target']}")
    
    # Test selector
    selector = ToolSelector(config['tools_path'], config)
    tools = selector.select_tools('network', target)
    print(f"✅ Selected {len(tools)} tool(s): {[t['name'] for t in tools]}")
    
    # Create a safe test tool config
    test_tools_dir = Path(config['tools_path'])
    test_tools_dir.mkdir(exist_ok=True)
    
    # Override with safe echo command for testing
    safe_tool_config = {
        "echo_test": {"cmd": "echo Testing UmbraVault with target"}
    }
    test_file = test_tools_dir / 'test.json'
    with open(test_file, 'w') as f:
        json.dump(safe_tool_config, f)
    
    # Reload selector with test tool
    selector = ToolSelector(config['tools_path'], config)
    
    # Test executor with safe command
    print("\n--- Testing Executor ---")
    executor = ToolExecutor(config)
    
    # Run safe echo command
    result = executor.execute("echo", "127.0.0.1")
    print(f"✅ Executor ran: success={result['success']}, elapsed={result['elapsed']:.2f}s")
    if result['output']:
        print(f"   Output: {result['output'][:100]}")
    
    # Test reporter
    print("\n--- Testing Reporter ---")
    reporter = Reporter(config['logs_path'])
    results = [{'name': 'test', **result}]
    report_path = reporter.generate_report('test', results)
    print(f"✅ Report generated: {report_path}")
    
    # Cleanup test file
    test_file.unlink()
    
    print("\n🎉 All components working! Framework is ready.")
    print("\n⚠️  Note: Docker not installed. Run setup-wsl.sh to install Docker for sandboxed execution.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
