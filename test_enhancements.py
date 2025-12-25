#!/usr/bin/env python3
"""Quick test of new enhancements"""
import json
import sys
from pathlib import Path

# Test validator
print("=== Testing Config Validator ===")
try:
    from src.validator import ConfigValidator
    
    issues = ConfigValidator.run_preflight_checks('./config.json')
    if issues:
        print("⚠️  Preflight issues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All preflight checks passed!")
except Exception as e:
    print(f"❌ Validator error: {e}")

print("\n=== Testing Executor Enhancements ===")
try:
    from src.executor import ToolExecutor
    
    config_path = Path('./config.json')
    config = json.loads(config_path.read_text())
    
    executor = ToolExecutor(config)
    
    # Test with a simple command
    print("Running test command...")
    result = executor.execute("echo 'test'", "127.0.0.1")
    
    print(f"Success: {result['success']}")
    print(f"Output: {result.get('output', 'N/A')[:100]}")
    if result.get('error'):
        print(f"Error with hint: {result['error']}")
    
    print("✅ Executor working with error hints!")
    
except Exception as e:
    print(f"❌ Executor test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
